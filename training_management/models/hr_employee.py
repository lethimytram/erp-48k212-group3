# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

# --- 1. MỞ RỘNG HỒ SƠ NHÂN VIÊN (TRAINEE VIEW) ---
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    # Chỉ cần quan tâm nhân viên này ĐANG HỌC gì
    enrollment_ids = fields.One2many(
        'training.enrollment',
        'employee_id',
        string='Lịch sử đào tạo'
    )
    
    enrollment_count = fields.Integer(compute='_compute_training_stats', string="Khóa đang học")
    completed_course_count = fields.Integer(compute='_compute_training_stats', string="Khóa hoàn thành")
    
    @api.depends('enrollment_ids.state')
    def _compute_training_stats(self):
        for employee in self:
            employee.enrollment_count = len(employee.enrollment_ids)
            # Giả định trạng thái 'done' là hoàn thành
            employee.completed_course_count = len(
                employee.enrollment_ids.filtered(lambda e: e.state == 'done')
            )
    
    def action_view_enrollments(self):
        """Nút Smart Button trên form nhân viên"""
        self.ensure_one()
        return {
            'name': _('Hồ sơ học tập'),
            'type': 'ir.actions.act_window',
            'res_model': 'training.enrollment',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id}
        }

# --- 2. GIẢNG VIÊN (TRAINER / STORE MANAGER) ---
class TrainingTrainer(models.Model):
    _name = 'training.trainer'
    _description = 'Giảng viên / Mentor'
    _inherit = ['mail.thread', 'image.mixin'] # image.mixin hỗ trợ xử lý ảnh tốt hơn
    
    name = fields.Char(string='Tên giảng viên', required=True, translate=True)
    active = fields.Boolean(default=True)
    
    trainer_type = fields.Selection([
        ('internal', 'Nội bộ (Cửa hàng trưởng/Leader)'),
        ('external', 'Thuê ngoài (Chuyên gia)')
    ], string='Phân loại', default='internal', required=True)
    
    # Link với nhân viên nội bộ
    employee_id = fields.Many2one('hr.employee', string='Nhân viên')
    
    # Thông tin liên hệ
    email = fields.Char(related='employee_id.work_email', readonly=False, store=True)
    phone = fields.Char(related='employee_id.mobile_phone', readonly=False, store=True)
    
    # Chuyên môn
    specialization = fields.Char(string='Chuyên môn', help="Vd: Barista, Dịch vụ khách hàng")
    bio = fields.Html(string='Tiểu sử / Giới thiệu')
    
    # Khóa học phụ trách
    course_ids = fields.One2many('training.course', 'main_trainer_id', string='Khóa học phụ trách')
    course_count = fields.Integer(compute='_compute_course_count')
    
    @api.depends('course_ids')
    def _compute_course_count(self):
        for record in self:
            record.course_count = len(record.course_ids)

    # Tự động lấy tên/ảnh khi chọn nhân viên
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.name = self.employee_id.name
            self.image_1920 = self.employee_id.image_1920 # Lấy ảnh từ hồ sơ nhân sự