# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TrainingCertificate(models.Model):
    _name = 'training.certificate'
    _description = 'Chứng nhận tay nghề'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'issue_date desc'

    name = fields.Char('Số chứng nhận', required=True, copy=False, default='New', readonly=True)
    
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True)
    course_id = fields.Many2one('training.course', string='Khóa học', required=True)
    enrollment_id = fields.Many2one('training.enrollment', string='Đăng ký học')
    
    # Thông tin chứng nhận
    issue_date = fields.Date('Ngày cấp', required=True, default=fields.Date.today)
    expiry_date = fields.Date('Ngày hết hạn', help='Để trống nếu không có hạn')
    
    # Kết quả
    theory_score = fields.Float('Điểm lý thuyết', related='enrollment_id.best_exam_score', store=True)
    practice_score = fields.Float('Điểm thực hành', related='enrollment_id.practice_score', store=True)
    
    # Trạng thái
    state = fields.Selection([
        ('valid', 'Còn hiệu lực'),
        ('expired', 'Hết hiệu lực'),
        ('revoked', 'Thu hồi'),
    ], string='Trạng thái', default='valid', tracking=True, compute='_compute_state', store=True)
    
    notes = fields.Text('Ghi chú')
    
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('training.certificate') or 'New'
        return super().create(vals_list)
    
    @api.depends('expiry_date')
    def _compute_state(self):
        today = fields.Date.today()
        for rec in self:
            if rec.state == 'revoked':
                continue
            if rec.expiry_date and rec.expiry_date < today:
                rec.state = 'expired'
            else:
                rec.state = 'valid'
    
    def action_revoke(self):
        """Thu hồi chứng nhận"""
        self.state = 'revoked'
    
    def action_reactivate(self):
        """Kích hoạt lại chứng nhận"""
        self.state = 'valid'
