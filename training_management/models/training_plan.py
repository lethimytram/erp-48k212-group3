# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TrainingPlan(models.Model):
    _name = 'training.plan'
    _description = 'Kế hoạch đào tạo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year desc, name'

    name = fields.Char(string='Tên kế hoạch', required=True, tracking=True)
    year = fields.Char(string='Năm', required=True, default=lambda self: str(fields.Date.today().year), tracking=True, size=4)
    department_id = fields.Many2one('hr.department', string='Phòng ban', tracking=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('approved', 'Phê duyệt'),
        ('in_progress', 'Đang thực hiện'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy bỏ')
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    description = fields.Html(string='Mô tả')
    responsible_id = fields.Many2one('res.users', string='Người phụ trách', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    # Các field khác sẽ được bổ sung trong Tính năng 2
