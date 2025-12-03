# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TrainingQuestion(models.Model):
    _name = 'training.question'
    _description = 'Câu hỏi thi'
    _order = 'sequence, id'

    name = fields.Char('Câu hỏi', required=True)
    course_id = fields.Many2one('training.course', string='Khóa học', required=True, ondelete='cascade')
    sequence = fields.Integer('Thứ tự', default=1)
    
    question_type = fields.Selection([
        ('single', 'Một đáp án đúng'),
        ('multiple', 'Nhiều đáp án đúng'),
    ], string='Loại câu hỏi', required=True, default='single')
    
    answer_ids = fields.One2many('training.answer', 'question_id', string='Đáp án')
    
    points = fields.Float('Điểm', default=1.0)
    explanation = fields.Text('Giải thích')
    
    active = fields.Boolean('Active', default=True)


class TrainingAnswer(models.Model):
    _name = 'training.answer'
    _description = 'Đáp án câu hỏi'
    _order = 'sequence, id'

    question_id = fields.Many2one('training.question', string='Câu hỏi', required=True, ondelete='cascade')
    sequence = fields.Integer('Thứ tự', default=10)
    name = fields.Char('Nội dung đáp án', required=True)
    is_correct = fields.Boolean('Đáp án đúng', default=False)
