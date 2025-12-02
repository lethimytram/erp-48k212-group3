# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrainingMaterial(models.Model):
    _name = 'training.material'
    _description = 'Tài liệu đào tạo / Công thức'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    # --- THÔNG TIN CƠ BẢN ---
    name = fields.Char(string='Tên tài liệu', required=True, tracking=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(default=True)
    
    course_id = fields.Many2one(
        'training.course',
        string='Thuộc khóa học',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    # --- PHÂN LOẠI & NỘI DUNG (F&B Logic) ---
    material_type = fields.Selection([
        ('recipe', 'Công thức định lượng (Recipe)'), # Quan trọng cho F&B
        ('video', 'Video hướng dẫn'),
        ('document', 'Tài liệu (PDF/Word)'),
        ('presentation', 'Slide bài giảng'),
        ('quiz', 'Bài kiểm tra'),
        ('link', 'Liên kết ngoài')
    ], string='Loại tài liệu', default='recipe', required=True, tracking=True)

    # 1. Dành cho Recipe (Soạn thảo trực tiếp)
    content = fields.Html(
        string='Nội dung công thức', 
        help='Soạn thảo trực tiếp công thức, chèn ảnh minh họa...'
    )

    # 2. Dành cho Video/Link
    url = fields.Char(string='Đường dẫn (URL/Youtube)')

    # 3. Dành cho Document (Upload)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'training_material_attachment_rel',
        'material_id',
        'attachment_id',
        string='File đính kèm'
    )
    
    # --- CẤU HÌNH HỌC TẬP ---
    required_reading = fields.Boolean(string='Bắt buộc xem', default=True)
    is_public = fields.Boolean(string='Công khai', default=False)
    duration = fields.Float(string='Thời lượng (phút)', help='Thời gian dự kiến để hoàn thành')

    # --- THỐNG KÊ (Giữ nguyên logic hay của bạn) ---
    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Số file')
    download_count = fields.Integer(string='Lượt tải', default=0)
    view_count = fields.Integer(string='Lượt xem', default=0)
    
    # Metadata hiển thị đẹp trên Kanban
    file_size = fields.Char(string='Dung lượng', compute='_compute_file_info')
    
    author_id = fields.Many2one('res.users', string='Người tạo', default=lambda self: self.env.user)
    tag_ids = fields.Many2many('training.material.tag', string='Tags')
    notes = fields.Text(string='Ghi chú')

    # --- LOGIC TÍNH TOÁN ---
    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = len(record.attachment_ids)
    
    @api.depends('attachment_ids')
    def _compute_file_info(self):
        for record in self:
            if record.attachment_ids:
                total_size = sum(record.attachment_ids.mapped('file_size'))
                if total_size > 1024 * 1024:
                    record.file_size = f"{total_size / (1024 * 1024):.2f} MB"
                elif total_size > 1024:
                    record.file_size = f"{total_size / 1024:.2f} KB"
                else:
                    record.file_size = f"{total_size} bytes"
            else:
                record.file_size = "0 KB"
    
    @api.constrains('url')
    def _check_url(self):
        for record in self:
            if record.url and not record.url.startswith(('http://', 'https://')):
                raise ValidationError(_('URL phải bắt đầu bằng http:// hoặc https://'))
    
    # --- ACTIONS ---
    def action_download(self):
        self.ensure_one()
        self.download_count += 1
        if self.attachment_ids:
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{self.attachment_ids[0].id}?download=true',
                'target': 'new',
            }
    
    def action_view(self):
        self.ensure_one()
        self.view_count += 1
        if self.url:
            return {
                'type': 'ir.actions.act_url',
                'url': self.url,
                'target': 'new',
            }
        return True

# --- TAGS ---
class TrainingMaterialTag(models.Model):
    _name = 'training.material.tag'
    _description = 'Tag tài liệu'
    _order = 'name'
    
    name = fields.Char(string='Tag', required=True, translate=True)
    color = fields.Integer(string='Màu sắc')
    active = fields.Boolean(default=True)
    
    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Tag phải là duy nhất!')]