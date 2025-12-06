# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrainingPractice(models.Model):
    _name = 'training.practice'
    _description = 'Đánh giá thực hành'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Mã đánh giá', required=True, copy=False, default='New', readonly=True)
    
    enrollment_id = fields.Many2one('training.enrollment', string='Đăng ký học', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', related='enrollment_id.employee_id', string='Nhân viên', store=True)
    course_id = fields.Many2one('training.course', related='enrollment_id.course_id', string='Khóa học', store=True)
    
    # Người đánh giá (Quản lý cửa hàng)
    assessor_id = fields.Many2one('hr.employee', string='Người đánh giá', required=True, default=lambda self: self.env.user.employee_id)
    
    # Thời gian
    assessment_date = fields.Datetime('Thời gian đánh giá', default=fields.Datetime.now, required=True)
    
    # Chi tiết đánh giá
    line_ids = fields.One2many('training.practice.line', 'practice_id', string='Chi tiết đánh giá')
    
    # Kết quả
    total_items = fields.Integer('Tổng số tiêu chí', compute='_compute_score', store=True)
    passed_items = fields.Integer('Số tiêu chí đạt', compute='_compute_score', store=True)
    score = fields.Float('Điểm (%)', compute='_compute_score', store=True)
    pass_percent = fields.Float('Tỷ lệ đạt yêu cầu', related='course_id.practice_pass_percent')
    is_passed = fields.Boolean('Đạt', compute='_compute_is_passed', store=True)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('in_progress', 'Đang đánh giá'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Hủy'),
    ], string='Trạng thái', default='draft', tracking=True)
    
    notes = fields.Text('Nhận xét')
    
    @api.model
    def create_for_passed_enrollments(self):
        """Tạo practice assessment cho các enrollment đã đạt lý thuyết nhưng chưa có practice"""
        # Tìm các enrollment đã đạt lý thuyết nhưng chưa có practice
        enrollments = self.env['training.enrollment'].search([
            ('theory_state', '=', 'passed'),
            ('practice_ids', '=', False),  # Chưa có practice assessment
        ])
        
        created_count = 0
        for enrollment in enrollments:
            try:
                # Tạo practice assessment
                self.create({
                    'enrollment_id': enrollment.id,
                    'course_id': enrollment.course_id.id,
                    'assessor_id': enrollment.manager_id.id if enrollment.manager_id else False,
                })
                created_count += 1
                enrollment.practice_state = 'in_progress'
            except Exception as e:
                # Log lỗi nhưng không dừng lại
                continue
        
        return created_count
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('training.practice') or 'New'
        records = super().create(vals_list)
        
        # Tự động tạo các tiêu chí đánh giá
        for rec in records:
            rec._generate_checklist()
        
        return records
    
    def _generate_checklist(self):
        """Tạo danh sách tiêu chí từ checklist của khóa học"""
        self.ensure_one()
        
        checklists = self.course_id.checklist_ids.filtered(lambda c: c.active)
        
        if not checklists:
            raise ValidationError(_('Khóa học chưa có tiêu chí đánh giá!'))
        
        for checklist in checklists:
            self.env['training.practice.line'].create({
                'practice_id': self.id,
                'checklist_id': checklist.id,
                'sequence': checklist.sequence,
            })
    
    @api.depends('line_ids.is_passed')
    def _compute_score(self):
        for rec in self:
            rec.total_items = len(rec.line_ids)
            rec.passed_items = len(rec.line_ids.filtered(lambda l: l.is_passed))
            rec.score = (rec.passed_items / rec.total_items * 100) if rec.total_items > 0 else 0.0
    
    @api.depends('score', 'pass_percent')
    def _compute_is_passed(self):
        for rec in self:
            rec.is_passed = rec.score >= rec.pass_percent
    
    def action_start(self):
        """Bắt đầu đánh giá"""
        self.state = 'in_progress'
    
    def action_submit(self):
        """Hoàn thành đánh giá"""
        self.ensure_one()
        
        # Kiểm tra tất cả tiêu chí bắt buộc
        required_failed = self.line_ids.filtered(
            lambda l: l.checklist_id.is_required and not l.is_passed
        )
        
        if required_failed:
            raise ValidationError(_(
                'Các tiêu chí bắt buộc sau chưa đạt:\n%s'
            ) % '\n'.join(required_failed.mapped('checklist_id.name')))
        
        self.state = 'done'
        
        # Cập nhật trạng thái enrollment
        if self.is_passed:
            self.enrollment_id.practice_state = 'passed'
            # Kiểm tra và tạo certificate nếu cả lý thuyết và thực hành đều đạt
            self.enrollment_id.action_check_completion()
        else:
            self.enrollment_id.practice_state = 'failed'
    
    def action_cancel(self):
        self.state = 'cancelled'


class TrainingPracticeLine(models.Model):
    _name = 'training.practice.line'
    _description = 'Chi tiết đánh giá thực hành'
    _order = 'sequence, id'

    practice_id = fields.Many2one('training.practice', string='Đánh giá', required=True, ondelete='cascade')
    checklist_id = fields.Many2one('training.checklist', string='Tiêu chí', required=True)
    sequence = fields.Integer('Thứ tự', related='checklist_id.sequence', store=True)
    
    # Thông tin tiêu chí
    category = fields.Selection(related='checklist_id.category', string='Nhóm', readonly=True)
    is_required = fields.Boolean(related='checklist_id.is_required', string='Bắt buộc', readonly=True)
    
    # Kết quả đánh giá
    is_passed = fields.Boolean('Đạt', default=False)
    assessor_notes = fields.Text('Ghi chú của người đánh giá')
