# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class TrainingEnrollment(models.Model):
    _name = 'training.enrollment'
    _description = 'Hồ sơ học tập & Đăng ký'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Mã hồ sơ', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Học viên', required=True, tracking=True)
    
    # Thông tin khóa học & Vị trí
    course_id = fields.Many2one('training.course', string='Khóa học (SOP)', required=True, tracking=True)
    job_position_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Vị trí công việc', readonly=True)
    
    # --- TÍCH HỢP QUY TRÌNH PHÊ DUYỆT (Giai đoạn 1 & 2) ---
    # TODO: Implement approval workflow
    # approval_id = fields.Many2one('training.approval', string='Yêu cầu duyệt học', readonly=True, copy=False)
    
    # --- TRẠNG THÁI BLENDED LEARNING (Core Logic) ---
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('approval_requested', 'Chờ duyệt'),      # Gửi sếp duyệt cho đi học
        ('learning', 'Đang học lý thuyết'),       # Đã duyệt -> Đang xem video/tài liệu
        ('theory_test', 'Sát hạch lý thuyết'),    # Đang làm bài thi trắc nghiệm
        ('practical_test', 'Sát hạch thực hành'), # Đậu lý thuyết -> Chờ CHT chấm OJT
        ('completed', 'Hoàn thành'),              # Đậu cả 2 -> Hệ thống cấp bằng
        ('cancelled', 'Hủy bỏ')
    ], string='Tiến độ đào tạo', default='draft', required=True, tracking=True, group_expand='_expand_states')

    # --- KẾT QUẢ ĐÀO TẠO ---
    # Lý thuyết (Tự động chấm)
    theory_exam_ids = fields.One2many('training.exam.attempt', 'enrollment_id', string='Lịch sử thi lý thuyết')
    theory_score = fields.Float(string='Điểm lý thuyết cao nhất', compute='_compute_scores', store=True)
    is_theory_passed = fields.Boolean(string='Đậu lý thuyết', compute='_compute_scores', store=True)
    
    # Thực hành (Cửa hàng trưởng chấm)
    practical_exam_ids = fields.One2many('training.practical.attempt', 'enrollment_id', string='Lịch sử thi thực hành')
    practical_score = fields.Float(string='Điểm thực hành cao nhất', compute='_compute_scores', store=True)
    is_practical_passed = fields.Boolean(string='Đậu thực hành', compute='_compute_scores', store=True)

    # Chứng chỉ
    certificate_id = fields.Many2one('training.certificate', string='Chứng chỉ được cấp', readonly=True)
    
    enrollment_date = fields.Date(string='Ngày bắt đầu', default=fields.Date.today)
    completion_date = fields.Date(string='Ngày hoàn thành')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)

    _sql_constraints = [
        ('employee_course_unique', 'UNIQUE(employee_id, course_id)', 'Nhân viên này đang học/đã học khóa này rồi!'),
    ]

    @api.model
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('training.enrollment') or _('New')
        return super(TrainingEnrollment, self).create(vals_list)

    # --- TÍNH ĐIỂM & LOGIC CHUYỂN GIAI ĐOẠN ---
    @api.depends('theory_exam_ids.state', 'theory_exam_ids.score', 
                 'practical_exam_ids.state', 'practical_exam_ids.score')
    def _compute_scores(self):
        for record in self:
            # Lấy điểm lý thuyết cao nhất của các lần thi Đạt
            passed_theory = record.theory_exam_ids.filtered(lambda x: x.state == 'passed')
            record.theory_score = max(passed_theory.mapped('score')) if passed_theory else 0.0
            record.is_theory_passed = bool(passed_theory)

            # Lấy điểm thực hành cao nhất
            passed_practical = record.practical_exam_ids.filtered(lambda x: x.state == 'passed')
            record.practical_score = max(passed_practical.mapped('score')) if passed_practical else 0.0
            record.is_practical_passed = bool(passed_practical)

    # --- CÁC HÀM XỬ LÝ WORKFLOW ---

    def action_submit_approval(self):
        """Gửi yêu cầu duyệt (Bước 1)"""
        self.ensure_one()
        # ... (Giữ nguyên logic gọi module Approval của bạn) ...
        self.write({'state': 'approval_requested'})
        # Giả lập đã tạo Approval record...

    def action_approve(self):
        """Callback: Sếp đã duyệt -> Nhân viên bắt đầu học (Bước 2)"""
        self.write({'state': 'learning'})

    def action_start_theory_test(self):
        """Nhân viên bấm 'Thi ngay' trên Portal"""
        self.ensure_one()
        if self.state != 'learning':
            raise UserError(_('Bạn chưa hoàn thành bài học hoặc chưa được duyệt.'))
        self.state = 'theory_test'
        # Logic mở popup bài thi sẽ viết ở Controller/Wizard

    def action_move_to_practical(self):
        """Chuyển sang giai đoạn thực hành (Bước 3) - Chỉ khi đậu lý thuyết"""
        self.ensure_one()
        if not self.is_theory_passed:
            raise UserError(_('Bạn phải ĐẬU bài thi lý thuyết trước khi chuyển sang thực hành.'))
        self.state = 'practical_test'

    def action_complete(self):
        """Hoàn tất & Cấp chứng chỉ (Bước 4)"""
        self.ensure_one()
        if not self.is_practical_passed:
            raise UserError(_('Kết quả thực hành chưa đạt. Vui lòng nhờ Cửa hàng trưởng chấm lại.'))
        
        self.write({
            'state': 'completed',
            'completion_date': fields.Date.today()
        })
        # Gọi hàm tạo chứng chỉ tự động (đã có ở bài trước)
        self._create_certificate()

    def _create_certificate(self):
        """Tạo chứng chỉ cho học viên khi hoàn thành khóa học"""
        self.ensure_one()
        if not self.certificate_id:
            self.certificate_id = self.env['training.certificate'].create({
                'enrollment_id': self.id,
                'employee_id': self.employee_id.id,
                'course_id': self.course_id.id,
                'issue_date': fields.Date.today(),
                'state': 'valid',
            })

    def action_open_feedback(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Đánh giá khóa học',
            'res_model': 'training.feedback',
            'view_mode': 'form',
            'context': {'default_enrollment_id': self.id},
            'target': 'new', # Mở popup
        }