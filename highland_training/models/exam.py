# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import random

class TrainingExam(models.Model):
    _name = 'training.exam'
    _description = 'Bài thi lý thuyết'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Mã bài thi', required=True, copy=False, default='New', readonly=True)
    
    enrollment_id = fields.Many2one('training.enrollment', string='Đăng ký học', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', related='enrollment_id.employee_id', string='Nhân viên', store=True)
    course_id = fields.Many2one('training.course', related='enrollment_id.course_id', string='Khóa học', store=True)
    
    # Thời gian
    start_time = fields.Datetime('Thời gian bắt đầu', readonly=True)
    end_time = fields.Datetime('Thời gian kết thúc', readonly=True)
    duration = fields.Integer('Thời gian làm bài (phút)', related='course_id.exam_duration')
    
    # Câu hỏi và câu trả lời
    answer_ids = fields.One2many('training.exam.answer', 'exam_id', string='Câu trả lời')
    
    # Kết quả
    score = fields.Float('Điểm số', readonly=True, compute='_compute_score', store=True)
    pass_score = fields.Float('Điểm đạt', related='course_id.exam_pass_score')
    is_passed = fields.Boolean('Đạt', compute='_compute_is_passed', store=True)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('in_progress', 'Đang thi'),
        ('submitted', 'Đã nộp bài'),
        ('graded', 'Đã chấm điểm'),
    ], string='Trạng thái', default='draft', tracking=True)
    
    notes = fields.Text('Ghi chú')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('training.exam') or 'New'
        records = super().create(vals_list)
        
        # Tự động tạo câu hỏi random
        for rec in records:
            rec._generate_exam_questions()
        
        return records
    
    def _generate_exam_questions(self):
        """Random câu hỏi từ ngân hàng câu hỏi"""
        self.ensure_one()
        
        # Lấy tất cả câu hỏi của khóa học
        questions = self.course_id.question_ids.filtered(lambda q: q.active)
        
        if not questions:
            raise ValidationError(_('Khóa học chưa có câu hỏi!'))
        
        # Random số lượng câu hỏi theo cấu hình
        question_count = min(self.course_id.exam_question_count, len(questions))
        selected_questions = random.sample(list(questions), question_count)
        
        # Tạo các câu trả lời trống
        for seq, question in enumerate(selected_questions, 1):
            self.env['training.exam.answer'].create({
                'exam_id': self.id,
                'question_id': question.id,
                'sequence': seq,
            })
    
    def action_start(self):
        """Bắt đầu làm bài"""
        self.ensure_one()
        self.write({
            'state': 'in_progress',
            'start_time': fields.Datetime.now(),
        })
    
    def action_submit(self):
        """Nộp bài và chấm điểm"""
        self.ensure_one()
        self.write({
            'state': 'submitted',
            'end_time': fields.Datetime.now(),
        })
        self._grade_exam()
    
    def _grade_exam(self):
        """Chấm điểm tự động"""
        self.ensure_one()
        
        total_points = 0
        earned_points = 0
        
        for answer in self.answer_ids:
            question = answer.question_id
            total_points += question.points
            
            if question.question_type == 'single':
                # Một đáp án đúng
                if answer.selected_answer_ids and len(answer.selected_answer_ids) == 1:
                    if answer.selected_answer_ids[0].is_correct:
                        earned_points += question.points
                        answer.is_correct = True
            else:
                # Nhiều đáp án đúng
                correct_answers = question.answer_ids.filtered(lambda a: a.is_correct)
                if set(answer.selected_answer_ids.ids) == set(correct_answers.ids):
                    earned_points += question.points
                    answer.is_correct = True
        
        # Tính điểm theo thang 100
        score = (earned_points / total_points * 100) if total_points > 0 else 0
        
        self.write({
            'state': 'graded',
            'score': score,
        })
        
        # Cập nhật trạng thái enrollment
        if self.is_passed:
            self.enrollment_id.theory_state = 'passed'
            self.enrollment_id.practice_state = 'in_progress'
            
            # Tự động tạo đánh giá thực hành
            self._create_practice_assessment()
        else:
            self.enrollment_id.theory_state = 'failed'
    
    def _create_practice_assessment(self):
        """Tự động tạo đánh giá thực hành khi đạt lý thuyết"""
        self.ensure_one()
        
        if not self.enrollment_id.practice_ids:
            # Chỉ tạo nếu chưa có đánh giá thực hành
            # Lấy manager user_id từ employee
            manager_employee = self.enrollment_id.manager_id
            manager_user = manager_employee.user_id if manager_employee else None
            
            practice = self.env['training.practice'].create({
                'enrollment_id': self.enrollment_id.id,
                'course_id': self.course_id.id,
                'assessor_id': manager_employee.id if manager_employee else self.env.user.employee_id.id,
            })
            return practice
    
    @api.depends('answer_ids.is_correct', 'answer_ids.question_id.points')
    def _compute_score(self):
        for rec in self:
            if rec.state != 'graded':
                rec.score = 0.0
                continue
            
            total_points = sum(rec.answer_ids.mapped('question_id.points'))
            earned_points = sum(
                answer.question_id.points 
                for answer in rec.answer_ids 
                if answer.is_correct
            )
            rec.score = (earned_points / total_points * 100) if total_points > 0 else 0.0
    
    @api.depends('score', 'pass_score')
    def _compute_is_passed(self):
        for rec in self:
            rec.is_passed = rec.score >= rec.pass_score


class TrainingExamAnswer(models.Model):
    _name = 'training.exam.answer'
    _description = 'Câu trả lời của học viên'
    _order = 'sequence, id'

    exam_id = fields.Many2one('training.exam', string='Bài thi', required=True, ondelete='cascade')
    question_id = fields.Many2one('training.question', string='Câu hỏi', required=True)
    sequence = fields.Integer('Thứ tự')
    
    # Đáp án được chọn
    selected_answer_ids = fields.Many2many('training.answer', string='Đáp án đã chọn')
    
    # Kết quả chấm
    is_correct = fields.Boolean('Trả lời đúng', readonly=True)
