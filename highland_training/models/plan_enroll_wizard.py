# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TrainingPlanEnrollWizard(models.TransientModel):
    _name = 'training.plan.enroll.wizard'
    _description = 'Wizard ghi danh nhân viên vào khóa học'

    plan_id = fields.Many2one('training.plan', string='Kế hoạch', required=True, ondelete='cascade')
    course_id = fields.Many2one('training.course', string='Khóa học', required=True)
    department_id = fields.Many2one('hr.department', string='Phòng ban/Cửa hàng')
    employee_ids = fields.Many2many('hr.employee', string='Nhân viên', required=True)

    @api.onchange('department_id')
    def _onchange_department(self):
        """Khi chọn phòng ban, lấy danh sách nhân viên của phòng ban đó"""
        if self.department_id:
            employees = self.env['hr.employee'].search([
                ('department_id', '=', self.department_id.id)
            ])
            self.employee_ids = employees
        else:
            self.employee_ids = []

    def action_enroll(self):
        """Ghi danh hàng loạt nhân viên vào khóa học"""
        enrollment_obj = self.env['training.enrollment']
        
        for employee in self.employee_ids:
            # Kiểm tra đã có enrollment chưa
            existing = enrollment_obj.search([
                ('employee_id', '=', employee.id),
                ('course_id', '=', self.course_id.id),
                ('plan_id', '=', self.plan_id.id)
            ], limit=1)
            
            if not existing:
                enrollment_obj.create({
                    'employee_id': employee.id,
                    'course_id': self.course_id.id,
                    'plan_id': self.plan_id.id,
                })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': f'Đã ghi danh {len(self.employee_ids)} nhân viên vào khóa học {self.course_id.name}',
                'type': 'success',
                'sticky': False,
            }
        }
