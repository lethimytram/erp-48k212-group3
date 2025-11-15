# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TrainingTestGradingWizard(models.TransientModel):
    _name = 'training.test.grading.wizard'
    _description = 'Wizard chấm điểm bài thi'

    result_id = fields.Many2one('training.test.result', string='Kết quả thi', required=True)
    employee_id = fields.Many2one('hr.employee', related='result_id.employee_id', string='Học viên', readonly=True)
    test_id = fields.Many2one('training.test', related='result_id.test_id', string='Bài thi', readonly=True)
    
    # Grading lines
    grading_line_ids = fields.One2many('training.test.grading.line', 'wizard_id', string='Chấm từng câu')
    
    # Overall
    total_points = fields.Float(string='Tổng điểm', compute='_compute_totals')
    points_earned = fields.Float(string='Điểm đạt', compute='_compute_totals')
    score_percentage = fields.Float(string='Điểm %', compute='_compute_totals')
    
    teacher_notes = fields.Text(string='Ghi chú chung')
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        
        if 'result_id' in res:
            result = self.env['training.test.result'].browse(res['result_id'])
            
            # Create grading lines
            lines = []
            for answer in result.answer_ids:
                if answer.question_id.question_type == 'essay':
                    lines.append((0, 0, {
                        'answer_id': answer.id,
                        'question': answer.question_id.question,
                        'essay_answer': answer.essay_answer,
                        'max_points': answer.question_id.points,
                        'points_earned': answer.points_earned or 0,
                        'teacher_comment': answer.teacher_comment or '',
                    }))
            
            res['grading_line_ids'] = lines
        
        return res
    
    @api.depends('grading_line_ids.points_earned')
    def _compute_totals(self):
        for wizard in self:
            wizard.total_points = sum(wizard.grading_line_ids.mapped('max_points'))
            wizard.points_earned = sum(wizard.grading_line_ids.mapped('points_earned'))
            
            if wizard.total_points > 0:
                wizard.score_percentage = (wizard.points_earned / wizard.total_points) * 100
            else:
                wizard.score_percentage = 0.0
    
    def action_submit_grade(self):
        """Lưu điểm"""
        self.ensure_one()
        
        # Update answers
        for line in self.grading_line_ids:
            line.answer_id.write({
                'points_earned': line.points_earned,
                'teacher_comment': line.teacher_comment,
                'is_correct': line.points_earned >= line.max_points,
            })
        
        # Calculate total score including multiple choice
        result = self.result_id
        total_points = 0
        earned_points = 0
        
        for answer in result.answer_ids:
            total_points += answer.question_id.points
            earned_points += answer.points_earned or 0
        
        score = (earned_points / total_points * 100) if total_points > 0 else 0
        
        # Update result
        result.write({
            'points_earned': earned_points,
            'score': score,
            'state': 'graded',
            'teacher_notes': self.teacher_notes,
        })
        
        # Create certificate if passed
        if result.passed and result.test_id.auto_certificate and not result.certificate_id:
            result._create_certificate()
        
        return {'type': 'ir.actions.act_window_close'}


class TrainingTestGradingLine(models.TransientModel):
    _name = 'training.test.grading.line'
    _description = 'Chi tiết chấm điểm'

    wizard_id = fields.Many2one('training.test.grading.wizard', required=True, ondelete='cascade')
    answer_id = fields.Many2one('training.test.answer', string='Câu trả lời', required=True)
    
    question = fields.Text(string='Câu hỏi', readonly=True)
    essay_answer = fields.Text(string='Câu trả lời', readonly=True)
    
    max_points = fields.Float(string='Điểm tối đa', readonly=True)
    points_earned = fields.Float(string='Điểm đạt được', required=True)
    teacher_comment = fields.Text(string='Nhận xét')
    
    @api.constrains('points_earned', 'max_points')
    def _check_points(self):
        for line in self:
            if line.points_earned < 0:
                raise ValidationError(_('Điểm không được âm!'))
            if line.points_earned > line.max_points:
                raise ValidationError(_('Điểm không được vượt quá điểm tối đa!'))
