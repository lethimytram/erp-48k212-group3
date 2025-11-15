# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    # Gán tag Trainer và Trainee
    is_trainer = fields.Boolean(
        string='Là giảng viên',
        help='Nhân viên này có thể đảm nhận vai trò giảng viên'
    )
    is_trainee = fields.Boolean(
        string='Là học viên',
        default=True,
        help='Nhân viên này có thể tham gia các khóa đào tạo'
    )
    
    # Liên kết với trainer
    trainer_id = fields.Many2one(
        'training.trainer',
        string='Hồ sơ giảng viên',
        help='Hồ sơ giảng viên nếu là trainer'
    )
    
    # Thống kê đào tạo
    enrollment_ids = fields.One2many(
        'training.enrollment',
        'employee_id',
        string='Khóa học đã đăng ký'
    )
    enrollment_count = fields.Integer(
        string='Số khóa đã đăng ký',
        compute='_compute_training_stats'
    )
    completed_course_count = fields.Integer(
        string='Số khóa đã hoàn thành',
        compute='_compute_training_stats'
    )
    # Tạm tắt - Certificate fields
    # certificate_ids = fields.One2many(
    #     'training.certificate',
    #     'employee_id',
    #     string='Chứng chỉ'
    # )
    # certificate_count = fields.Integer(
    #     string='Số chứng chỉ',
    #     compute='_compute_training_stats'
    # )
    
    @api.depends('enrollment_ids')  # Removed certificate_ids dependency
    def _compute_training_stats(self):
        for employee in self:
            employee.enrollment_count = len(employee.enrollment_ids)
            employee.completed_course_count = len(
                employee.enrollment_ids.filtered(lambda e: e.state == 'completed')
            )
            # employee.certificate_count = len(employee.certificate_ids)  # Tạm tắt
    
    def action_view_enrollments(self):
        """Xem các khóa học đã đăng ký"""
        self.ensure_one()
        return {
            'name': 'Khóa học đã đăng ký',
            'type': 'ir.actions.act_window',
            'res_model': 'training.enrollment',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id}
        }
    
    # Tạm tắt - Certificate action
    # def action_view_certificates(self):
    #     """Xem chứng chỉ"""
    #     self.ensure_one()
    #     return {
    #         'name': 'Chứng chỉ',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'training.certificate',
    #         'view_mode': 'tree,form',
    #         'domain': [('employee_id', '=', self.id)],
    #         'context': {'default_employee_id': self.id}
    #     }
