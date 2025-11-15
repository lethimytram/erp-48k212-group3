# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TrainingFeedback(models.Model):
    _name = 'training.feedback'
    _description = 'Khảo sát hài lòng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Tiêu đề', compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', string='Học viên', required=True, tracking=True)
    course_id = fields.Many2one('training.course', string='Khóa học', required=True, tracking=True)
    enrollment_id = fields.Many2one('training.enrollment', string='Đăng ký')
    trainer_id = fields.Many2one('training.trainer', string='Giảng viên đánh giá')
    
    # Đánh giá
    overall_rating = fields.Selection([
        ('1', 'Rất không hài lòng'),
        ('2', 'Không hài lòng'),
        ('3', 'Bình thường'),
        ('4', 'Hài lòng'),
        ('5', 'Rất hài lòng')
    ], string='Đánh giá chung', tracking=True)
    
    content_rating = fields.Integer(string='Nội dung (1-5)', default=3)
    trainer_rating = fields.Integer(string='Giảng viên (1-5)', default=3)
    material_rating = fields.Integer(string='Tài liệu (1-5)', default=3)
    organization_rating = fields.Integer(string='Tổ chức (1-5)', default=3)
    
    comments = fields.Text(string='Nhận xét')
    suggestions = fields.Text(string='Đề xuất cải tiến')
    
    feedback_date = fields.Date(string='Ngày phản hồi', default=fields.Date.today)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('submitted', 'Đã gửi'),
        ('reviewed', 'Đã xem xét')
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    # Các field khác sẽ được bổ sung trong Tính năng 12
    
    @api.depends('employee_id', 'course_id')
    def _compute_name(self):
        for record in self:
            if record.employee_id and record.course_id:
                record.name = f"Feedback - {record.employee_id.name} - {record.course_id.name}"
            else:
                record.name = "Feedback mới"
