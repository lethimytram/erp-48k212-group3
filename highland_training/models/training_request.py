# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TrainingRequest(models.Model):
    _name = 'training.request'
    _description = 'Nhu cầu đào tạo'
    _order = 'create_date desc'

    name = fields.Char('Mã yêu cầu', required=True, readonly=True, default='New')
    store_manager_id = fields.Many2one('hr.employee', string='Cửa hàng trưởng', required=True, default=lambda self: self.env.user.employee_id)
    course_ids = fields.Many2many('training.course', string='Khóa học yêu cầu', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Danh sách nhân viên cần đào tạo', required=True)
    reason = fields.Text('Lý do yêu cầu', required=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('submitted', 'Đã gửi'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ], default='draft', string='Trạng thái')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('training.request') or 'New'
        return super(TrainingRequest, self).create(vals)
    
    def action_submit(self):
        self.state = 'submitted'
    
    def action_approve(self):
        self.state = 'approved'
    
    def action_reject(self):
        self.state = 'rejected'
