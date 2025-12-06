# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrainingEnrollment(models.Model):
    _name = 'training.enrollment'
    _description = 'Đăng ký học'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Mã đăng ký', required=True, copy=False, default='New', readonly=True)
    
    # Thông tin cơ bản
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, tracking=True)
    course_id = fields.Many2one('training.course', string='Khóa học', required=True, tracking=True)
    plan_id = fields.Many2one('training.plan', string='Kế hoạch đào tạo')
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Cửa hàng', store=True)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Vị trí', store=True)
    
    # Ngày tháng
    enroll_date = fields.Date('Ngày đăng ký', default=fields.Date.today, required=True)
    deadline = fields.Date('Hạn hoàn thành')
    complete_date = fields.Date('Ngày hoàn thành', readonly=True)
    
    # Tiến độ lý thuyết
    theory_state = fields.Selection([
        ('not_started', 'Chưa học'),
        ('in_progress', 'Đang học'),
        ('exam_ready', 'Sẵn sàng thi'),
        ('passed', 'Đã đạt'),
        ('failed', 'Chưa đạt'),
    ], string='Lý thuyết', default='not_started', tracking=True)
    
    exam_ids = fields.One2many('training.exam', 'enrollment_id', string='Bài thi')
    exam_count = fields.Integer('Số lần thi', compute='_compute_exam_count')
    best_exam_score = fields.Float('Điểm cao nhất', compute='_compute_best_exam_score')
    
    # Tiến độ thực hành
    practice_state = fields.Selection([
        ('not_started', 'Chưa bắt đầu'),
        ('in_progress', 'Đang luyện tập'),
        ('passed', 'Đã đạt'),
        ('failed', 'Chưa đạt'),
    ], string='Thực hành', default='not_started', tracking=True)
    
    practice_ids = fields.One2many('training.practice', 'enrollment_id', string='Đánh giá thực hành')
    practice_count = fields.Integer('Số lần đánh giá', compute='_compute_practice_count')
    practice_score = fields.Float('Điểm thực hành', compute='_compute_practice_score')
    
    # Trạng thái tổng thể
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('learning', 'Đang học'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy'),
    ], string='Trạng thái', default='draft', tracking=True)
    
    # Chứng nhận
    certificate_id = fields.Many2one('training.certificate', string='Chứng chỉ', readonly=True)
    
    # Nội dung khóa học (để hiển thị cho học viên)
    course_content_ids = fields.Many2many('training.content', string='Nội dung học tập', 
                                         compute='_compute_course_content_ids', readonly=True)
    
    @api.depends('course_id', 'course_id.content_ids')
    def _compute_course_content_ids(self):
        for record in self:
            record.course_content_ids = record.course_id.content_ids if record.course_id else False
    
    # Quản lý
    manager_id = fields.Many2one('hr.employee', string='Quản lý cửa hàng', compute='_compute_manager_id', store=True)
    notes = fields.Text('Ghi chú')
    
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('training.enrollment') or 'New'
        return super().create(vals_list)
    
    @api.depends('employee_id.department_id.manager_id')
    def _compute_manager_id(self):
        for rec in self:
            rec.manager_id = rec.employee_id.department_id.manager_id
    
    @api.depends('exam_ids')
    def _compute_exam_count(self):
        for rec in self:
            rec.exam_count = len(rec.exam_ids)
    
    @api.depends('exam_ids.score', 'exam_ids.state')
    def _compute_best_exam_score(self):
        for rec in self:
            passed_exams = rec.exam_ids.filtered(lambda e: e.state == 'graded')
            rec.best_exam_score = max(passed_exams.mapped('score')) if passed_exams else 0.0
    
    @api.depends('practice_ids')
    def _compute_practice_count(self):
        for rec in self:
            rec.practice_count = len(rec.practice_ids)
    
    @api.depends('practice_ids.score', 'practice_ids.state')
    def _compute_practice_score(self):
        for rec in self:
            passed_practices = rec.practice_ids.filtered(lambda p: p.state == 'done')
            rec.practice_score = max(passed_practices.mapped('score')) if passed_practices else 0.0
    
    def action_start_learning(self):
        self.state = 'learning'
        self.theory_state = 'in_progress'
    
    def action_ready_exam(self):
        self.theory_state = 'exam_ready'
    
    def action_start_exam(self):
        """Tạo bài thi mới"""
        self.ensure_one()
        if self.theory_state not in ['exam_ready', 'failed']:
            raise ValidationError(_('Bạn chưa sẵn sàng để thi!'))
        
        # Kiểm tra số câu hỏi
        if len(self.course_id.question_ids) < self.course_id.exam_question_count:
            raise ValidationError(_('Khóa học chưa đủ câu hỏi để thi!'))
        
        # Tạo bài thi mới
        exam = self.env['training.exam'].create({
            'enrollment_id': self.id,
            'course_id': self.course_id.id,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'training.exam',
            'res_id': exam.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_check_completion(self):
        """Kiểm tra và hoàn thành khóa học"""
        for rec in self:
            if rec.theory_state == 'passed' and rec.practice_state == 'passed':
                rec.state = 'completed'
                rec.complete_date = fields.Date.today()
                
                # Tạo chứng chỉ nếu chưa có
                if not rec.certificate_id:
                    certificate = self.env['training.certificate'].create({
                        'employee_id': rec.employee_id.id,
                        'course_id': rec.course_id.id,
                        'enrollment_id': rec.id,
                        'issue_date': fields.Date.today(),
                    })
                    rec.certificate_id = certificate.id
    
    def action_cancel(self):
        self.state = 'cancelled'
