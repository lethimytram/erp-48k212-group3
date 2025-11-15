# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TrainingTrainer(models.Model):
    _name = 'training.trainer'
    _description = 'Giảng viên đào tạo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Thông tin cơ bản
    name = fields.Char(
        string='Tên giảng viên',
        required=True,
        tracking=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân viên',
        tracking=True,
        help='Liên kết với nhân viên nếu là giảng viên nội bộ'
    )
    email = fields.Char(
        string='Email',
        required=True,
        tracking=True
    )
    phone = fields.Char(
        string='Điện thoại',
        tracking=True
    )
    image = fields.Binary(
        string='Ảnh',
        attachment=True
    )
    
    # Phân loại
    trainer_type = fields.Selection([
        ('internal', 'Nội bộ'),
        ('external', 'Bên ngoài')
    ], string='Loại giảng viên', default='internal', required=True, tracking=True)
    
    active = fields.Boolean(
        string='Hoạt động',
        default=True,
        tracking=True
    )
    
    # Chuyên môn
    specialization = fields.Char(
        string='Chuyên môn',
        help='Lĩnh vực chuyên môn của giảng viên'
    )
    bio = fields.Html(
        string='Tiểu sử',
        help='Thông tin chi tiết về giảng viên'
    )
    qualification = fields.Text(
        string='Bằng cấp & Chứng chỉ',
        help='Các bằng cấp và chứng chỉ của giảng viên'
    )
    experience_years = fields.Integer(
        string='Số năm kinh nghiệm',
        default=0
    )
    
    # Đánh giá
    rating = fields.Float(
        string='Đánh giá',
        compute='_compute_rating',
        store=True,
        help='Đánh giá trung bình từ học viên'
    )
    
    # Khóa học
    course_ids = fields.Many2many(
        'training.course',
        'training_course_trainer_rel',
        'trainer_id',
        'course_id',
        string='Khóa học đảm nhận'
    )
    main_course_ids = fields.One2many(
        'training.course',
        'main_trainer_id',
        string='Khóa học chính'
    )
    course_count = fields.Integer(
        string='Số khóa học',
        compute='_compute_course_count'
    )
    
    # Kỹ năng
    skill_ids = fields.Many2many(
        'hr.skill',
        'training_trainer_skill_rel',
        'trainer_id',
        'skill_id',
        string='Kỹ năng',
        help='Kỹ năng mà giảng viên có thể dạy'
    )
    
    # Lịch làm việc
    availability = fields.Text(
        string='Lịch có thể dạy',
        help='Thông tin về lịch giảng viên có thể dạy'
    )
    
    # Chi phí
    hourly_rate = fields.Monetary(
        string='Chi phí/giờ',
        currency_field='currency_id',
        help='Chi phí thuê giảng viên theo giờ'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id
    )
    
    # Thông tin công ty (cho giảng viên bên ngoài)
    company_name = fields.Char(
        string='Tên công ty',
        help='Tên công ty/tổ chức của giảng viên bên ngoài'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Đối tác',
        help='Đối tác liên quan đến giảng viên'
    )
    
    # Ghi chú
    notes = fields.Text(string='Ghi chú')
    
    company_id = fields.Many2one(
        'res.company',
        string='Công ty hệ thống',
        default=lambda self: self.env.company
    )
    
    _sql_constraints = [
        ('email_unique', 'UNIQUE(email)', 'Email giảng viên phải là duy nhất!'),
    ]
    
    @api.depends('course_ids', 'main_course_ids')
    def _compute_course_count(self):
        for record in self:
            all_courses = record.course_ids | record.main_course_ids
            record.course_count = len(all_courses)
    
    @api.depends('course_ids')
    def _compute_rating(self):
        # TODO: Tính toán rating từ feedback của học viên
        for record in self:
            record.rating = 0.0
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Tự động điền thông tin từ nhân viên"""
        if self.employee_id:
            self.name = self.employee_id.name
            self.email = self.employee_id.work_email
            self.phone = self.employee_id.work_phone
            self.image = self.employee_id.image_1920
            self.trainer_type = 'internal'
    
    def action_view_courses(self):
        """Xem các khóa học của giảng viên"""
        self.ensure_one()
        all_courses = self.course_ids | self.main_course_ids
        return {
            'name': _('Khóa học'),
            'type': 'ir.actions.act_window',
            'res_model': 'training.course',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', all_courses.ids)],
        }
