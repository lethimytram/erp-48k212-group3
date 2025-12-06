# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TrainingRequest(models.Model):
    _name = 'training.request'
    _description = 'Nhu cầu đào tạo'
    _order = 'create_date desc'

    name = fields.Char('Mã yêu cầu', required=True, readonly=True, default='New')
    store_manager_id = fields.Many2one('hr.employee', string='Cửa hàng trưởng', required=True, default=lambda self: self.env.user.employee_id)
    
    course_selection_type = fields.Selection([
        ('existing', 'Sử dụng khóa học có sẵn'),
        ('new', 'Tạo khóa học mới'),
    ], string='Loại khóa học', required=True, default='existing')
    
    course_ids = fields.Many2many('training.course', string='Khóa học yêu cầu', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Danh sách nhân viên cần đào tạo')
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

    @api.onchange('course_selection_type')
    def _onchange_course_selection_type(self):
        """Khi chuyển loại khóa học, xóa dữ liệu không phù hợp"""
        if self.course_selection_type == 'new':
            self.employee_ids = [(5, 0, 0)]
    
    def action_submit(self):
        self.state = 'submitted'
    
    def action_approve(self):
        """Duyệt nhu cầu đào tạo, ghi danh nhân viên và chuyển khóa học sang 'Cần lập kế hoạch'"""
        self.state = 'approved'
        enrollment_obj = self.env['training.enrollment']
        
        for course in self.course_ids:
            if course.state == 'draft':
                course.state = 'need_planning'
            
            employees_to_enroll = self.env['hr.employee']
            
            if self.course_selection_type == 'existing':
                employees_to_enroll = self.employee_ids
                if self.employee_ids:
                    course.employee_ids = [(4, emp.id) for emp in self.employee_ids]
            else:
                employees_to_enroll = course.employee_ids
            
            for employee in employees_to_enroll:
                existing = enrollment_obj.search([
                    ('employee_id', '=', employee.id),
                    ('course_id', '=', course.id),
                ], limit=1)
                
                if not existing:
                    enrollment_obj.create({
                        'employee_id': employee.id,
                        'course_id': course.id,
                        'state': 'draft',
                    })
    
    def action_reject(self):
        self.state = 'rejected'
