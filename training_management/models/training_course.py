# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrainingCourse(models.Model):
    _name = 'training.course'
    _description = 'Quy trình vận hành chuẩn (SOP)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    # --- THÔNG TIN CƠ BẢN (F&B STYLE) ---
    name = fields.Char(
        string='Tên quy trình / SOP',
        required=True,
        tracking=True,
        help='Ví dụ: Quy trình Pha chế Phin Sữa Đá, Quy trình Vệ sinh máy Cafe'
    )
    code = fields.Char(
        string='Mã quy trình',
        required=True,
        copy=False,
        tracking=True,
        default=lambda self: _('New'),
        help='Mã định danh (Vd: SOP-BAR-01)'
    )
    sequence = fields.Integer(string='Thứ tự ưu tiên', default=10)
    active = fields.Boolean(string='Đang áp dụng', default=True, tracking=True)

    # --- PHÂN LOẠI & ĐỐI TƯỢNG ÁP DỤNG ---
    category_id = fields.Many2one(
        'training.course.category',
        string='Bộ phận (Bar/Bếp/Sảnh)',
        tracking=True
    )
    
    # [QUAN TRỌNG CHO F&B] Liên kết với Chức vụ
    job_ids = fields.Many2many(
        'hr.job',
        string='Vị trí áp dụng',
        help='Chỉ những nhân viên thuộc vị trí này mới cần học',
        tracking=True
    )

    level = fields.Selection([
        ('beginner', 'Hội nhập / Thử việc'),
        ('intermediate', 'Nhân viên chính thức'),
        ('advanced', 'Trưởng ca (Shift Leader)'),
        ('expert', 'Cửa hàng trưởng (SM)')
    ], string='Cấp độ yêu cầu', default='beginner', required=True, tracking=True)

    type = fields.Selection([
        ('internal', 'Đào tạo nội bộ (OJT)'),
        ('online', 'Học qua App (E-learning)'),
        ('blended', 'Kết hợp (Lý thuyết + Thực hành)')
    ], string='Hình thức', default='blended', required=True)

    # --- NỘI DUNG & THỜI LƯỢNG ---
    description = fields.Html(
        string='Nội dung chi tiết',
        help='Mô tả các bước thực hiện, hình ảnh minh họa...'
    )
    objectives = fields.Text(string='Yêu cầu đầu ra', help='Nhân viên phải làm được gì sau khi học?')
    prerequisites = fields.Text(string='Yêu cầu tiên quyết')

    duration = fields.Float(string='Thời lượng (giờ)', default=1.0, help='Thời gian dự kiến để học xong SOP này')
    
    # --- QUẢN LÝ (MENTORING) ---
    # Giả định bạn đã có model training.trainer, nếu chưa thì đổi thành res.users
    main_trainer_id = fields.Many2one(
        'res.users', 
        string='Người biên soạn / Mentor',
        tracking=True
    )
    # trainer_ids = fields.Many2many('training.trainer', string='Đội ngũ hỗ trợ')

    # --- TÀI NGUYÊN ---
    # Cần đảm bảo model training.material đã tồn tại
    material_ids = fields.One2many('training.material', 'course_id', string='Công thức & Video')
    material_count = fields.Integer(compute='_compute_material_count')

    # --- ĐĂNG KÝ & HỌC VIÊN ---
    # Cần đảm bảo model training.enrollment đã tồn tại
    enrollment_ids = fields.One2many('training.enrollment', 'course_id', string='Nhân viên đang học')
    enrollment_count = fields.Integer(compute='_compute_enrollment_count')
    
    max_participants = fields.Integer(string='Giới hạn học viên', default=0) 
    min_participants = fields.Integer(string='Tối thiểu', default=0)

    # --- SÁT HẠCH & CHỨNG CHỈ (F&B CORE) ---
    has_test = fields.Boolean(string='Yêu cầu sát hạch?', default=True)
    passing_score = fields.Float(string='Điểm đạt (%)', default=80.0)
    
    issue_certificate = fields.Boolean(string='Cấp chứng nhận?', default=True)
    # Cần đảm bảo model training.certificate.template đã tồn tại
    certificate_template_id = fields.Many2one('training.certificate.template', string='Mẫu chứng nhận')
    
    validity_months = fields.Integer(
        string='Hiệu lực (tháng)', 
        default=0, 
        help='0 là vĩnh viễn. Nhập số tháng để hệ thống nhắc thi lại.'
    )

    # --- LOGIC KHÁC ---
    skill_ids = fields.Many2many('hr.skill', string='Kỹ năng đạt được')
    cost = fields.Monetary(string='Chi phí tổ chức', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    state = fields.Selection([
        ('draft', 'Soạn thảo'),
        ('published', 'Ban hành'),
        ('archived', 'Lưu trữ')
    ], string='Trạng thái', default='draft', required=True, tracking=True)

    responsible_id = fields.Many2one('res.users', string='Phụ trách chuyên môn', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    notes = fields.Text(string='Ghi chú nội bộ')

    # --- CONSTRAINTS & COMPUTES ---
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Mã SOP phải là duy nhất!'),
        ('check_passing_score', 'CHECK(passing_score >= 0 AND passing_score <= 100)', 'Điểm đạt phải từ 0-100!'),
    ]

    @api.depends('material_ids')
    def _compute_material_count(self):
        for record in self:
            record.material_count = len(record.material_ids)

    @api.depends('enrollment_ids')
    def _compute_enrollment_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    # Các hàm Action button
    def action_publish(self):
        self.write({'state': 'published'})
        
    def action_archive(self):
        self.write({'state': 'archived'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    # Các hàm View
    def action_view_materials(self):
        self.ensure_one()
        return {
            'name': _('Công thức & Tài liệu'),
            'type': 'ir.actions.act_window',
            'res_model': 'training.material',
            'view_mode': 'tree,form',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id}
        }
    
    def action_view_enrollments(self):
        self.ensure_one()
        return {
            'name': _('Danh sách nhân viên'),
            'type': 'ir.actions.act_window',
            'res_model': 'training.enrollment',
            'view_mode': 'tree,form',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id}
        }

# --- MODEL DANH MỤC (ĐÃ THÊM SEQUENCE) ---
class TrainingCourseCategory(models.Model):
    _name = 'training.course.category'
    _description = 'Nhóm nghiệp vụ / Bộ phận'
    _order = 'sequence, name'
    
    # Đã thêm field sequence để fix lỗi XML
    sequence = fields.Integer(string='Thứ tự', default=10)
    
    name = fields.Char(string='Tên bộ phận', required=True, translate=True)
    code = fields.Char(string='Mã nhóm')
    parent_id = fields.Many2one('training.course.category', string='Thuộc khối')
    child_ids = fields.One2many('training.course.category', 'parent_id', string='Nhóm con')
    description = fields.Text(string='Mô tả chức năng')
    active = fields.Boolean(string='Đang hoạt động', default=True)
    course_ids = fields.One2many('training.course', 'category_id', string='Các quy trình (SOP)')
    course_count = fields.Integer(string='Số lượng SOP', compute='_compute_course_count')
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Mã nhóm phải là duy nhất!'),
    ]
    
    @api.depends('course_ids')
    def _compute_course_count(self):
        for record in self:
            record.course_count = len(record.course_ids)