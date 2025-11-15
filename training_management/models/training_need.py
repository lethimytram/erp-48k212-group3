# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TrainingNeed(models.Model):
    _name = 'training.need'
    _description = 'Nhu cầu đào tạo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Tiêu đề', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Phòng ban', related='employee_id.department_id', store=True)
    description = fields.Text(string='Mô tả nhu cầu')
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('submitted', 'Đã gửi'),
        ('approved', 'Phê duyệt'),
        ('rejected', 'Từ chối')
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    # Các field khác sẽ được bổ sung
