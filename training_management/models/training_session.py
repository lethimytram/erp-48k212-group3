# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TrainingSession(models.Model):
    _name = 'training.session'
    _description = 'Buổi học'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date, name'

    name = fields.Char(string='Tên buổi học', required=True, tracking=True)
    course_id = fields.Many2one('training.course', string='Khóa học', required=True, tracking=True)
    trainer_id = fields.Many2one('training.trainer', string='Giảng viên', tracking=True)
    start_date = fields.Datetime(string='Thời gian bắt đầu', required=True, tracking=True)
    end_date = fields.Datetime(string='Thời gian kết thúc', required=True, tracking=True)
    location = fields.Char(string='Địa điểm')
    calendar_event_id = fields.Many2one('calendar.event', string='Sự kiện lịch')
    state = fields.Selection([
        ('scheduled', 'Đã lên lịch'),
        ('in_progress', 'Đang diễn ra'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy bỏ')
    ], string='Trạng thái', default='scheduled', required=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    # Các field khác sẽ được bổ sung trong Tính năng 5
