# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TrainingCourse(models.Model):
    _name = 'training.course'
    _description = 'Khóa học đào tạo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    # Thông tin cơ bản
    name = fields.Char(
        string='Tên khóa học',
        required=True,
        tracking=True,
        help='Tên đầy đủ của khóa học'
    )
    code = fields.Char(
        string='Mã khóa học',
        required=True,
        copy=False,
        tracking=True,
        help='Mã định danh duy nhất cho khóa học'
    )
    sequence = fields.Integer(
        string='Thứ tự',
        default=10,
        help='Thứ tự hiển thị'
    )
    active = fields.Boolean(
        string='Hoạt động',
        default=True,
        tracking=True
    )
    
    # Mô tả và nội dung
    description = fields.Html(
        string='Mô tả khóa học',
        tracking=True,
        help='Mô tả chi tiết về nội dung và mục tiêu khóa học'
    )
    objectives = fields.Text(
        string='Mục tiêu học tập',
        help='Mục tiêu học viên đạt được sau khóa học'
    )
    prerequisites = fields.Text(
        string='Điều kiện tiên quyết',
        help='Kiến thức hoặc kỹ năng cần có trước khi tham gia'
    )
    
    # Phân loại
    category_id = fields.Many2one(
        'training.course.category',
        string='Danh mục',
        tracking=True,
        help='Phân loại khóa học theo lĩnh vực'
    )
    level = fields.Selection([
        ('beginner', 'Cơ bản'),
        ('intermediate', 'Trung cấp'),
        ('advanced', 'Nâng cao'),
        ('expert', 'Chuyên gia')
    ], string='Cấp độ', default='beginner', required=True, tracking=True)
    
    type = fields.Selection([
        ('internal', 'Nội bộ'),
        ('external', 'Bên ngoài'),
        ('online', 'Trực tuyến'),
        ('blended', 'Kết hợp')
    ], string='Loại hình', default='internal', required=True, tracking=True)
    
    # Thời gian và địa điểm
    duration = fields.Float(
        string='Thời lượng (giờ)',
        help='Tổng số giờ học'
    )
    duration_days = fields.Integer(
        string='Số ngày',
        compute='_compute_duration_days',
        store=True,
        help='Số ngày học (8 giờ/ngày)'
    )
    location = fields.Char(
        string='Địa điểm',
        help='Địa điểm tổ chức khóa học'
    )
    
    # Giảng viên
    trainer_ids = fields.Many2many(
        'training.trainer',
        'training_course_trainer_rel',
        'course_id',
        'trainer_id',
        string='Giảng viên',
        tracking=True
    )
    main_trainer_id = fields.Many2one(
        'training.trainer',
        string='Giảng viên chính',
        tracking=True
    )
    
    # Tài liệu
    material_ids = fields.One2many(
        'training.material',
        'course_id',
        string='Tài liệu khóa học'
    )
    material_count = fields.Integer(
        string='Số tài liệu',
        compute='_compute_material_count'
    )
    
    # Học viên và đăng ký
    max_participants = fields.Integer(
        string='Số học viên tối đa',
        default=30,
        help='Số lượng học viên tối đa cho mỗi khóa'
    )
    min_participants = fields.Integer(
        string='Số học viên tối thiểu',
        default=5,
        help='Số lượng học viên tối thiểu để mở khóa'
    )
    enrollment_ids = fields.One2many(
        'training.enrollment',
        'course_id',
        string='Đăng ký'
    )
    enrollment_count = fields.Integer(
        string='Số đăng ký',
        compute='_compute_enrollment_count'
    )
    
    # Buổi học
    session_ids = fields.One2many(
        'training.session',
        'course_id',
        string='Buổi học'
    )
    session_count = fields.Integer(
        string='Số buổi học',
        compute='_compute_session_count'
    )
    
    # Đánh giá và chứng chỉ
    has_test = fields.Boolean(
        string='Có bài kiểm tra',
        default=True,
        help='Khóa học có bài kiểm tra cuối khóa'
    )
    passing_score = fields.Float(
        string='Điểm đạt (%)',
        default=70.0,
        help='Điểm tối thiểu để đạt khóa học'
    )
    
    # Certificate fields
    issue_certificate = fields.Boolean(
        string='Cấp chứng chỉ',
        default=True,
        help='Cấp chứng chỉ khi hoàn thành'
    )
    certificate_template_id = fields.Many2one(
        'training.certificate.template',
        string='Mẫu chứng chỉ'
    )
    
    # Kỹ năng liên quan
    skill_ids = fields.Many2many(
        'hr.skill',
        'training_course_skill_rel',
        'course_id',
        'skill_id',
        string='Kỹ năng đạt được',
        help='Kỹ năng học viên sẽ có sau khi hoàn thành'
    )
    
    # Chi phí
    cost = fields.Monetary(
        string='Chi phí',
        currency_field='currency_id',
        help='Chi phí tổ chức khóa học'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id
    )
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('published', 'Công bố'),
        ('in_progress', 'Đang diễn ra'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy bỏ')
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    
    # Người phụ trách
    responsible_id = fields.Many2one(
        'res.users',
        string='Người phụ trách',
        default=lambda self: self.env.user,
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Công ty',
        default=lambda self: self.env.company
    )
    
    # Ghi chú
    notes = fields.Text(string='Ghi chú')
    
    # Constraints
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Mã khóa học phải là duy nhất!'),
        ('check_participants', 'CHECK(max_participants >= min_participants)',
         'Số học viên tối đa phải lớn hơn hoặc bằng số tối thiểu!'),
        ('check_passing_score', 'CHECK(passing_score >= 0 AND passing_score <= 100)',
         'Điểm đạt phải từ 0 đến 100!'),
    ]
    
    @api.depends('duration')
    def _compute_duration_days(self):
        for record in self:
            record.duration_days = int(record.duration / 8) if record.duration else 0
    
    @api.depends('material_ids')
    def _compute_material_count(self):
        for record in self:
            record.material_count = len(record.material_ids)
    
    @api.depends('enrollment_ids')
    def _compute_enrollment_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)
    
    @api.depends('session_ids')
    def _compute_session_count(self):
        for record in self:
            record.session_count = len(record.session_ids)
    
    @api.constrains('max_participants', 'min_participants')
    def _check_participants(self):
        for record in self:
            if record.max_participants < record.min_participants:
                raise ValidationError(_('Số học viên tối đa phải lớn hơn hoặc bằng số tối thiểu!'))
    
    @api.constrains('passing_score')
    def _check_passing_score(self):
        for record in self:
            if record.passing_score < 0 or record.passing_score > 100:
                raise ValidationError(_('Điểm đạt phải từ 0 đến 100!'))
    
    def action_publish(self):
        """Công bố khóa học"""
        self.write({'state': 'published'})
        
    def action_start(self):
        """Bắt đầu khóa học"""
        self.write({'state': 'in_progress'})
        
    def action_complete(self):
        """Hoàn thành khóa học"""
        self.write({'state': 'completed'})
        
    def action_cancel(self):
        """Hủy bỏ khóa học"""
        self.write({'state': 'cancelled'})
        
    def action_reset_to_draft(self):
        """Đưa về nháp"""
        self.write({'state': 'draft'})
    
    def action_view_materials(self):
        """Xem tài liệu"""
        self.ensure_one()
        return {
            'name': _('Tài liệu khóa học'),
            'type': 'ir.actions.act_window',
            'res_model': 'training.material',
            'view_mode': 'tree,form',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id}
        }
    
    def action_view_enrollments(self):
        """Xem đăng ký"""
        self.ensure_one()
        return {
            'name': _('Đăng ký khóa học'),
            'type': 'ir.actions.act_window',
            'res_model': 'training.enrollment',
            'view_mode': 'tree,form',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id}
        }
    
    def action_view_sessions(self):
        """Xem buổi học"""
        self.ensure_one()
        return {
            'name': _('Buổi học'),
            'type': 'ir.actions.act_window',
            'res_model': 'training.session',
            'view_mode': 'tree,form,calendar',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id}
        }


class TrainingCourseCategory(models.Model):
    _name = 'training.course.category'
    _description = 'Danh mục khóa học'
    _order = 'name'
    
    name = fields.Char(string='Tên danh mục', required=True, translate=True)
    code = fields.Char(string='Mã danh mục')
    parent_id = fields.Many2one('training.course.category', string='Danh mục cha')
    child_ids = fields.One2many('training.course.category', 'parent_id', string='Danh mục con')
    description = fields.Text(string='Mô tả')
    active = fields.Boolean(string='Hoạt động', default=True)
    course_ids = fields.One2many('training.course', 'category_id', string='Khóa học')
    course_count = fields.Integer(string='Số khóa học', compute='_compute_course_count')
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Mã danh mục phải là duy nhất!'),
    ]
    
    @api.depends('course_ids')
    def _compute_course_count(self):
        for record in self:
            record.course_count = len(record.course_ids)
    
    @api.constrains('parent_id')
    def _check_parent_recursion(self):
        for record in self:
            if record.parent_id and record._has_cycle():
                raise ValidationError(_('Không thể tạo danh mục con đệ quy!'))
