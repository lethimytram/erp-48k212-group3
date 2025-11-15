# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TrainingEnrollment(models.Model):
    _name = 'training.enrollment'
    _description = 'Đăng ký khóa học'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Mã đăng ký', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Học viên', required=True, tracking=True)
    course_id = fields.Many2one('training.course', string='Khóa học', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('waiting', 'Chờ duyệt'),
        ('approved', 'Phê duyệt'),
        ('rejected', 'Từ chối'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy bỏ')
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    enrollment_date = fields.Date(string='Ngày đăng ký', default=fields.Date.today)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    # Các field khác sẽ được bổ sung trong Tính năng 3
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('training.enrollment') or _('New')
        return super(TrainingEnrollment, self).create(vals_list)
