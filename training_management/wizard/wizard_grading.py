# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrainingExamGradingWizard(models.TransientModel):
    _name = 'training.exam.grading.wizard'
    _description = 'Wizard chấm điểm bài thi (Tự luận)'

    # Liên kết với model Lần thi (Exam Attempt)
    attempt_id = fields.Many2one('training.exam.attempt', string='Kết quả thi', required=True)
    employee_id = fields.Many2one('hr.employee', related='attempt_id.employee_id', string='Học viên', readonly=True)
    exam_id = fields.Many2one('training.exam', related='attempt_id.exam_id', string='Bài thi', readonly=True)
    
    # Danh sách các câu cần chấm
    grading_line_ids = fields.One2many('training.exam.grading.line', 'wizard_id', string='Chấm từng câu')
    
    # Tổng hợp điểm (trong wizard này)
    total_points_essay = fields.Float(string='Tổng điểm tự luận', compute='_compute_totals')
    points_earned_essay = fields.Float(string='Điểm đạt tự luận', compute='_compute_totals')
    
    teacher_notes = fields.Text(string='Ghi chú chung của Giáo viên')
    
    @api.model
    def default_get(self, fields_list):
        res = super(TrainingExamGradingWizard, self).default_get(fields_list)
        
        if self.env.context.get('active_id'):
            attempt = self.env['training.exam.attempt'].browse(self.env.context.get('active_id'))
            res['attempt_id'] = attempt.id
            res['teacher_notes'] = attempt.teacher_notes
            
            # Chỉ lấy các câu hỏi Tự luận (Essay) để chấm
            lines = []
            for answer in attempt.answer_ids:
                if answer.question_id.question_type == 'essay':
                    lines.append((0, 0, {
                        'answer_id': answer.id,
                        'question_content': answer.question_id.question_content,
                        'essay_answer': answer.essay_answer,
                        'max_points': answer.question_id.points,
                        'points_earned': answer.points_earned or 0, # Load điểm cũ nếu đã chấm
                        'teacher_comment': answer.teacher_comment or '',
                    }))
            
            res['grading_line_ids'] = lines
        
        return res
    
    @api.depends('grading_line_ids.points_earned', 'grading_line_ids.max_points')
    def _compute_totals(self):
        for wizard in self:
            wizard.total_points_essay = sum(wizard.grading_line_ids.mapped('max_points'))
            wizard.points_earned_essay = sum(wizard.grading_line_ids.mapped('points_earned'))
    
    def action_submit_grade(self):
        """Lưu điểm và tính lại tổng kết quả"""
        self.ensure_one()
        
        # 1. Cập nhật điểm cho từng câu tự luận
        for line in self.grading_line_ids:
            line.answer_id.write({
                'points_earned': line.points_earned,
                'teacher_comment': line.teacher_comment,
                'is_correct': line.points_earned >= (line.max_points / 2), # Tạm tính: trên 50% điểm câu đó là đúng
            })
        
        # 2. Tính lại TOÀN BỘ điểm của bài thi (Trắc nghiệm + Tự luận)
        attempt = self.attempt_id
        total_points = 0
        earned_points = 0
        
        for answer in attempt.answer_ids:
            total_points += answer.question_id.points
            earned_points += answer.points_earned or 0
        
        # Tính phần trăm
        score_percent = (earned_points / total_points * 100) if total_points > 0 else 0
        
        # 3. Cập nhật vào Lần thi (Exam Attempt)
        attempt.write({
            'score': earned_points,
            'score_percent': score_percent,
            'state': 'passed' if score_percent >= attempt.exam_id.min_pass_score else 'failed',
            'teacher_notes': self.teacher_notes,
        })
        
        # 4. Tự động cấp chứng chỉ nếu đậu (và chưa có chứng chỉ)
        if attempt.state == 'passed' and attempt.exam_id.auto_certificate:
            # Kiểm tra xem đã có chứng chỉ cho khóa học này chưa
            existing_cert = self.env['training.certificate'].search([
                ('employee_id', '=', attempt.employee_id.id),
                ('course_id', '=', attempt.exam_id.course_id.id),
                ('state', '=', 'issued')
            ], limit=1)
            
            if not existing_cert:
                self.env['training.certificate'].create({
                    'employee_id': attempt.employee_id.id,
                    'course_id': attempt.exam_id.course_id.id,
                    'enrollment_id': attempt.enrollment_id.id,
                    'exam_attempt_id': attempt.id,
                    'issue_date': fields.Date.today(),
                    'test_score': score_percent,
                    'state': 'draft' # Để nhân sự duyệt lần cuối rồi mới issue
                })
        
        return {'type': 'ir.actions.act_window_close'}


class TrainingExamGradingLine(models.TransientModel):
    _name = 'training.exam.grading.line'
    _description = 'Chi tiết chấm điểm (Dòng)'

    wizard_id = fields.Many2one('training.exam.grading.wizard', required=True, ondelete='cascade')
    answer_id = fields.Many2one('training.exam.answer', string='Câu trả lời gốc', required=True)
    
    question_content = fields.Html(string='Câu hỏi', readonly=True)
    essay_answer = fields.Text(string='Học viên trả lời', readonly=True)
    
    max_points = fields.Float(string='Điểm tối đa', readonly=True)
    points_earned = fields.Float(string='Điểm đạt được', required=True, default=0.0)
    teacher_comment = fields.Text(string='Nhận xét chi tiết')
    
    @api.constrains('points_earned', 'max_points')
    def _check_points(self):
        for line in self:
            if line.points_earned < 0:
                raise ValidationError(_('Điểm không được nhỏ hơn 0!'))
            if line.points_earned > line.max_points:
                raise ValidationError(_('Điểm đạt (%(earned)s) không được vượt quá điểm tối đa của câu hỏi (%(max)s)!', 
                                      earned=line.points_earned, max=line.max_points))