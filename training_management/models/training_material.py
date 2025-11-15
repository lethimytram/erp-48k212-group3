# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TrainingMaterial(models.Model):
    _name = 'training.material'
    _description = 'Tài liệu đào tạo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    # Thông tin cơ bản
    name = fields.Char(
        string='Tên tài liệu',
        required=True,
        tracking=True
    )
    sequence = fields.Integer(
        string='Thứ tự',
        default=10,
        help='Thứ tự hiển thị trong khóa học'
    )
    active = fields.Boolean(
        string='Hoạt động',
        default=True
    )
    
    # Liên kết với khóa học
    course_id = fields.Many2one(
        'training.course',
        string='Khóa học',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    # Mô tả
    description = fields.Html(
        string='Mô tả',
        help='Mô tả chi tiết về tài liệu'
    )
    
    # Loại tài liệu
    material_type = fields.Selection([
        ('document', 'Tài liệu'),
        ('video', 'Video'),
        ('presentation', 'Bài trình bày'),
        ('exercise', 'Bài tập'),
        ('test', 'Bài kiểm tra'),
        ('link', 'Liên kết'),
        ('other', 'Khác')
    ], string='Loại tài liệu', default='document', required=True, tracking=True)
    
    # File đính kèm
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'training_material_attachment_rel',
        'material_id',
        'attachment_id',
        string='File đính kèm'
    )
    attachment_count = fields.Integer(
        string='Số file',
        compute='_compute_attachment_count'
    )
    
    # Liên kết URL
    url = fields.Char(
        string='URL',
        help='Đường dẫn đến tài liệu online (video, slide, website...)'
    )
    
    # Quyền truy cập
    is_public = fields.Boolean(
        string='Công khai',
        default=False,
        help='Cho phép mọi người truy cập tài liệu'
    )
    required_reading = fields.Boolean(
        string='Bắt buộc',
        default=False,
        help='Học viên bắt buộc phải đọc/xem tài liệu này'
    )
    
    # Thống kê
    download_count = fields.Integer(
        string='Số lượt tải',
        default=0,
        help='Số lần tài liệu được tải xuống'
    )
    view_count = fields.Integer(
        string='Số lượt xem',
        default=0,
        help='Số lần tài liệu được xem'
    )
    
    # Metadata
    file_size = fields.Char(
        string='Kích thước',
        compute='_compute_file_info',
        help='Tổng kích thước các file đính kèm'
    )
    file_format = fields.Char(
        string='Định dạng',
        help='Định dạng file (pdf, doc, ppt, mp4...)'
    )
    duration = fields.Float(
        string='Thời lượng (phút)',
        help='Thời lượng video hoặc thời gian đọc ước tính'
    )
    
    # Người tạo
    author_id = fields.Many2one(
        'res.users',
        string='Người tạo',
        default=lambda self: self.env.user,
        tracking=True
    )
    create_date = fields.Datetime(
        string='Ngày tạo',
        readonly=True
    )
    
    # Tags
    tag_ids = fields.Many2many(
        'training.material.tag',
        string='Tags',
        help='Phân loại tài liệu theo tags'
    )
    
    # Ghi chú
    notes = fields.Text(string='Ghi chú')
    
    company_id = fields.Many2one(
        'res.company',
        string='Công ty',
        default=lambda self: self.env.company
    )
    
    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = len(record.attachment_ids)
    
    @api.depends('attachment_ids')
    def _compute_file_info(self):
        for record in self:
            if record.attachment_ids:
                total_size = sum(record.attachment_ids.mapped('file_size'))
                # Chuyển đổi bytes sang MB/KB
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
        """Kiểm tra định dạng URL"""
        for record in self:
            if record.url and not record.url.startswith(('http://', 'https://')):
                raise ValidationError(_('URL phải bắt đầu với http:// hoặc https://'))
    
    def action_download(self):
        """Tải tài liệu và tăng số lượt tải"""
        self.ensure_one()
        self.download_count += 1
        if self.attachment_ids:
            # Trả về file đầu tiên
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{self.attachment_ids[0].id}?download=true',
                'target': 'new',
            }
    
    def action_view(self):
        """Xem tài liệu và tăng số lượt xem"""
        self.ensure_one()
        self.view_count += 1
        
        if self.url:
            # Mở URL
            return {
                'type': 'ir.actions.act_url',
                'url': self.url,
                'target': 'new',
            }
        elif self.attachment_ids:
            # Xem file
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{self.attachment_ids[0].id}',
                'target': 'new',
            }
    
    def action_view_attachments(self):
        """Xem tất cả file đính kèm"""
        self.ensure_one()
        return {
            'name': _('File đính kèm'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.attachment_ids.ids)],
        }


class TrainingMaterialTag(models.Model):
    _name = 'training.material.tag'
    _description = 'Tag tài liệu'
    _order = 'name'
    
    name = fields.Char(string='Tag', required=True, translate=True)
    color = fields.Integer(string='Màu sắc')
    active = fields.Boolean(string='Hoạt động', default=True)
    
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Tag phải là duy nhất!'),
    ]
