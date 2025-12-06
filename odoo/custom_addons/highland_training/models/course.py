# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TrainingCourse(models.Model):
    _name = 'training.course'
    _description = 'Khóa học'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char('Tên khóa học', required=True, tracking=True)
    code = fields.Char('Mã khóa học', required=True, copy=False, tracking=True)
    sequence = fields.Integer('Thứ tự', default=10)
    description = fields.Html('Mô tả')
    
    # Phân loại
    course_type = fields.Selection([
        ('new_product', 'Sản phẩm mới'),
        ('sop', 'Quy trình SOP'),
        ('skill', 'Kỹ năng nghề nghiệp'),
        ('service', 'Kỹ năng phục vụ'),
    ], string='Loại khóa học', required=True, default='sop')
    
    # Đối tượng học
    job_position_ids = fields.Many2many('hr.job', string='Vị trí công việc')
    employee_ids = fields.Many2many('hr.employee', 'course_employee_rel', 'course_id', 'employee_id', string='Nhân viên cần học')
    
    # Nội dung
    content_ids = fields.One2many('training.content', 'course_id', string='Nội dung đào tạo')
    content_count = fields.Integer('Số nội dung', compute='_compute_content_count')
    
    # Câu hỏi thi
    question_ids = fields.One2many('training.question', 'course_id', string='Ngân hàng câu hỏi')
    question_count = fields.Integer('Số câu hỏi', compute='_compute_question_count')
    
    # Checklist thực hành
    checklist_ids = fields.One2many('training.checklist', 'course_id', string='Checklist thực hành')
    checklist_count = fields.Integer('Số tiêu chí', compute='_compute_checklist_count')
    
    # Cấu hình thi
    exam_pass_score = fields.Float('Điểm đạt lý thuyết', default=80.0, help='Điểm tối thiểu để đạt (0-100)')
    exam_duration = fields.Integer('Thời gian thi (phút)', default=30)
    exam_question_count = fields.Integer('Số câu hỏi thi', default=20, help='Số câu hỏi random từ ngân hàng')
    
    # Cấu hình thực hành
    practice_pass_percent = fields.Float('Tỷ lệ đạt thực hành (%)', default=80.0)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('need_planning', 'Cần lập kế hoạch'),
        ('active', 'Đang hoạt động'),
        ('archived', 'Lưu trữ'),
    ], string='Trạng thái', default='draft', tracking=True)
    
    # Thống kê
    enrollment_count = fields.Integer('Số học viên', compute='_compute_enrollment_count')
    
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    @api.depends('content_ids')
    def _compute_content_count(self):
        for rec in self:
            rec.content_count = len(rec.content_ids)
    
    @api.depends('question_ids')
    def _compute_question_count(self):
        for rec in self:
            rec.question_count = len(rec.question_ids)
    
    @api.depends('checklist_ids')
    def _compute_checklist_count(self):
        for rec in self:
            rec.checklist_count = len(rec.checklist_ids)
    
    @api.depends()
    def _compute_enrollment_count(self):
        for rec in self:
            rec.enrollment_count = self.env['training.enrollment'].search_count([('course_id', '=', rec.id)])
    
    def action_activate(self):
        self.state = 'active'
    
    def action_archive_course(self):
        self.state = 'archived'
    
    def action_view_enrollments(self):
        return {
            'name': 'Danh sách học viên',
            'type': 'ir.actions.act_window',
            'res_model': 'training.enrollment',
            'view_mode': 'tree,form',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id},
        }
