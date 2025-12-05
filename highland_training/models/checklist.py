# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TrainingChecklist(models.Model):
    _name = 'training.checklist'
    _description = 'Tiêu chí đánh giá thực hành'
    _order = 'sequence, id'

    name = fields.Char('Tiêu chí đánh giá', required=True)
    course_id = fields.Many2one('training.course', string='Khóa học', required=True, ondelete='cascade')
    sequence = fields.Integer('Thứ tự', default=1)
    
    category = fields.Selection([
        ('recipe', 'Công thức & Định lượng'),
        ('hygiene', 'Vệ sinh an toàn'),
        ('technique', 'Kỹ thuật thao tác'),
        ('service', 'Thái độ phục vụ'),
        ('time', 'Thời gian hoàn thành'),
    ], string='Nhóm tiêu chí', required=True, default='technique')
    
    description = fields.Text('Mô tả chi tiết')
    is_required = fields.Boolean('Bắt buộc', default=True, help='Tiêu chí bắt buộc phải đạt')
    
    active = fields.Boolean('Active', default=True)
