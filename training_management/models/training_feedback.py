# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TrainingFeedback(models.Model):
    _name = 'training.feedback'
    _description = 'Khảo sát chất lượng đào tạo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'enrollment_id'

    # Liên kết dữ liệu
    enrollment_id = fields.Many2one('training.enrollment', string='Mã đăng ký', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', related='enrollment_id.employee_id', string='Học viên', store=True, readonly=True)
    course_id = fields.Many2one('training.course', related='enrollment_id.course_id', string='Khóa học', store=True, readonly=True)
    trainer_id = fields.Many2one('hr.employee', string='Giảng viên/Người hướng dẫn') # Có thể là Cửa hàng trưởng
    
    # Tiêu chí đánh giá (Dùng Selection để hiển thị sao/radio button)
    # Quy ước: '0' là chưa đánh giá, '1'-'5' là điểm
    RATING_SELECTION = [
        ('0', 'Không ý kiến'),
        ('1', 'Rất tệ'),
        ('2', 'Tệ'),
        ('3', 'Bình thường'),
        ('4', 'Tốt'),
        ('5', 'Xuất sắc'),
    ]

    overall_rating = fields.Selection(RATING_SELECTION, string='Đánh giá chung', default='3', required=True, tracking=True)
    content_rating = fields.Selection(RATING_SELECTION, string='Nội dung bài học', default='3')
    trainer_rating = fields.Selection(RATING_SELECTION, string='Giảng viên/Hướng dẫn', default='3')
    material_rating = fields.Selection(RATING_SELECTION, string='Tài liệu/Hệ thống', default='3')
    organization_rating = fields.Selection(RATING_SELECTION, string='Công tác tổ chức', default='3')
    
    comments = fields.Text(string='Nhận xét chi tiết')
    suggestions = fields.Text(string='Đề xuất cải tiến')
    
    feedback_date = fields.Date(string='Ngày gửi', default=fields.Date.today, readonly=True)
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('submitted', 'Đã gửi'),
        ('cancel', 'Hủy')
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    # Ràng buộc: Một lần đăng ký học chỉ có 1 feedback
    _sql_constraints = [
        ('enrollment_uniq', 'unique(enrollment_id)', 'Bạn đã gửi đánh giá cho khóa học này rồi!'),
    ]

    def action_submit(self):
        """Học viên gửi đánh giá"""
        self.ensure_one()
        self.write({
            'state': 'submitted',
            'feedback_date': fields.Date.today()
        })
    
    def action_cancel(self):
        self.write({'state': 'cancel'})