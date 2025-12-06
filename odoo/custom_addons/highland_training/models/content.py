# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TrainingContent(models.Model):
    _name = 'training.content'
    _description = 'Nội dung đào tạo'
    _order = 'sequence, id'

    name = fields.Char('Tiêu đề', required=True)
    course_id = fields.Many2one('training.course', string='Khóa học', required=True, ondelete='cascade')
    sequence = fields.Integer('Thứ tự', default=10)
    
    content_type = fields.Selection([
        ('video', 'Video hướng dẫn'),
        ('document', 'Tài liệu'),
        ('recipe', 'Công thức'),
    ], string='Loại nội dung', required=True, default='video')
    
    description = fields.Html('Nội dung')
    
    # File đính kèm
    video_url = fields.Char('URL Video')
    attachment_ids = fields.Many2many('ir.attachment', string='File đính kèm')
    
    # Recipe fields
    recipe_ingredients = fields.Text('Nguyên liệu & Định lượng')
    recipe_steps = fields.Html('Các bước thực hiện')
    
    duration = fields.Integer('Thời lượng (phút)', help='Thời gian ước tính để học')
    
    active = fields.Boolean('Active', default=True)
