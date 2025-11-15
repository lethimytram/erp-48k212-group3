# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import random


class TrainingTest(models.Model):
    _name = 'training.test'
    _description = 'Bài kiểm tra'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Tên bài kiểm tra', required=True, tracking=True)
    description = fields.Text(string='Mô tả')
    course_id = fields.Many2one('training.course', string='Khóa học', required=True, tracking=True)
    session_id = fields.Many2one('training.session', string='Buổi học')
    
    # Cấu hình bài thi
    test_type = fields.Selection([
        ('quiz', 'Trắc nghiệm'),
        ('essay', 'Tự luận'),
        ('mixed', 'Kết hợp')
    ], string='Loại bài thi', default='quiz', required=True)
    
    duration = fields.Integer(string='Thời gian (phút)', default=60)
    passing_score = fields.Float(string='Điểm đạt (%)', default=70.0)
    max_attempts = fields.Integer(string='Số lần thi tối đa', default=3)
    shuffle_questions = fields.Boolean(string='Trộn câu hỏi', default=True)
    show_result_immediately = fields.Boolean(string='Hiện kết quả ngay', default=False)
    
    # Câu hỏi
    question_ids = fields.One2many('training.test.question', 'test_id', string='Câu hỏi')
    question_count = fields.Integer(string='Số câu hỏi', compute='_compute_question_count', store=True)
    total_points = fields.Float(string='Tổng điểm', compute='_compute_total_points', store=True)
    
    # Kết quả
    result_ids = fields.One2many('training.test.result', 'test_id', string='Kết quả')
    result_count = fields.Integer(string='Số lượt thi', compute='_compute_result_count')
    pass_rate = fields.Float(string='Tỷ lệ đạt (%)', compute='_compute_pass_rate')
    avg_score = fields.Float(string='Điểm TB', compute='_compute_avg_score')
    
    # Thời gian
    start_date = fields.Datetime(string='Ngày bắt đầu')
    end_date = fields.Datetime(string='Ngày kết thúc')
    
    # Chứng chỉ
    auto_certificate = fields.Boolean(string='Tự động cấp chứng chỉ', default=True)
    certificate_template_id = fields.Many2one('training.certificate.template', string='Mẫu chứng chỉ')
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('published', 'Công bố'),
        ('closed', 'Đóng')
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    @api.depends('question_ids')
    def _compute_question_count(self):
        for record in self:
            record.question_count = len(record.question_ids)
    
    @api.depends('question_ids.points')
    def _compute_total_points(self):
        for record in self:
            record.total_points = sum(record.question_ids.mapped('points'))
    
    def _compute_result_count(self):
        for record in self:
            record.result_count = len(record.result_ids)
    
    def _compute_pass_rate(self):
        for record in self:
            if record.result_ids:
                passed = len(record.result_ids.filtered('passed'))
                record.pass_rate = (passed / len(record.result_ids)) * 100
            else:
                record.pass_rate = 0.0
    
    def _compute_avg_score(self):
        for record in self:
            if record.result_ids:
                record.avg_score = sum(record.result_ids.mapped('score')) / len(record.result_ids)
            else:
                record.avg_score = 0.0
    
    def action_publish(self):
        """Công bố bài thi"""
        for record in self:
            if not record.question_ids:
                raise UserError(_('Bài thi phải có ít nhất 1 câu hỏi!'))
            record.state = 'published'
    
    def action_close(self):
        """Đóng bài thi"""
        self.write({'state': 'closed'})
    
    def action_draft(self):
        """Đặt về nháp"""
        self.write({'state': 'draft'})
    
    def action_start_test(self):
        """Bắt đầu làm bài"""
        self.ensure_one()
        
        if self.state != 'published':
            raise UserError(_('Bài thi chưa được công bố!'))
        
        # Kiểm tra thời gian
        now = fields.Datetime.now()
        if self.start_date and now < self.start_date:
            raise UserError(_('Bài thi chưa bắt đầu!'))
        if self.end_date and now > self.end_date:
            raise UserError(_('Bài thi đã kết thúc!'))
        
        # Kiểm tra số lần thi
        employee = self.env.user.employee_id
        if not employee:
            raise UserError(_('Bạn phải là nhân viên để làm bài thi!'))
        
        attempts = self.env['training.test.result'].search_count([
            ('test_id', '=', self.id),
            ('employee_id', '=', employee.id)
        ])
        
        if attempts >= self.max_attempts:
            raise UserError(_('Bạn đã hết số lần thi cho phép!'))
        
        # Tạo attempt mới
        result = self.env['training.test.result'].create({
            'test_id': self.id,
            'employee_id': employee.id,
            'enrollment_id': self.env['training.enrollment'].search([
                ('employee_id', '=', employee.id),
                ('course_id', '=', self.course_id.id)
            ], limit=1).id,
            'state': 'in_progress',
            'start_time': fields.Datetime.now(),
        })
        
        # Tạo câu trả lời cho từng câu hỏi
        questions = self.question_ids
        if self.shuffle_questions:
            questions = questions.sorted(lambda q: random.random())
        
        for seq, question in enumerate(questions, 1):
            self.env['training.test.answer'].create({
                'result_id': result.id,
                'question_id': question.id,
                'sequence': seq,
            })
        
        return {
            'name': _('Làm bài thi'),
            'type': 'ir.actions.act_window',
            'res_model': 'training.test.result',
            'res_id': result.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_results(self):
        """Xem kết quả"""
        self.ensure_one()
        return {
            'name': _('Kết quả thi'),
            'type': 'ir.actions.act_window',
            'res_model': 'training.test.result',
            'view_mode': 'list,form',
            'domain': [('test_id', '=', self.id)],
            'context': {'default_test_id': self.id},
        }
    
    def action_view_statistics(self):
        """Xem thống kê"""
        self.ensure_one()
        return {
            'name': _('Thống kê bài thi'),
            'type': 'ir.actions.act_window',
            'res_model': 'training.test',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }


class TrainingTestQuestion(models.Model):
    _name = 'training.test.question'
    _description = 'Câu hỏi bài kiểm tra'
    _order = 'sequence, id'

    test_id = fields.Many2one('training.test', string='Bài kiểm tra', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Thứ tự', default=10)
    
    question_type = fields.Selection([
        ('multiple_choice', 'Trắc nghiệm nhiều đáp án'),
        ('single_choice', 'Trắc nghiệm 1 đáp án'),
        ('true_false', 'Đúng/Sai'),
        ('essay', 'Tự luận'),
    ], string='Loại câu hỏi', required=True, default='single_choice')
    
    question = fields.Text(string='Câu hỏi', required=True)
    explanation = fields.Text(string='Giải thích')
    points = fields.Float(string='Điểm', default=1.0, required=True)
    
    # Đáp án trắc nghiệm
    option_ids = fields.One2many('training.test.option', 'question_id', string='Đáp án')
    
    # Đáp án tự luận
    essay_answer = fields.Text(string='Đáp án mẫu')
    
    # Media
    image = fields.Binary(string='Hình ảnh')
    attachment_ids = fields.Many2many('ir.attachment', string='Tài liệu đính kèm')
    
    company_id = fields.Many2one('res.company', related='test_id.company_id', store=True)
    
    @api.constrains('points')
    def _check_points(self):
        for record in self:
            if record.points <= 0:
                raise ValidationError(_('Điểm phải lớn hơn 0!'))
    
    @api.constrains('option_ids')
    def _check_options(self):
        for record in self:
            if record.question_type in ['multiple_choice', 'single_choice', 'true_false']:
                if not record.option_ids:
                    raise ValidationError(_('Câu hỏi trắc nghiệm phải có đáp án!'))
                
                correct_options = record.option_ids.filtered('is_correct')
                if not correct_options:
                    raise ValidationError(_('Phải có ít nhất 1 đáp án đúng!'))
                
                if record.question_type == 'single_choice' and len(correct_options) > 1:
                    raise ValidationError(_('Câu hỏi 1 đáp án chỉ được có 1 đáp án đúng!'))


class TrainingTestOption(models.Model):
    _name = 'training.test.option'
    _description = 'Đáp án trắc nghiệm'
    _order = 'sequence, id'

    question_id = fields.Many2one('training.test.question', string='Câu hỏi', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Thứ tự', default=10)
    option_text = fields.Text(string='Đáp án', required=True)
    is_correct = fields.Boolean(string='Đáp án đúng', default=False)
    
    company_id = fields.Many2one('res.company', related='question_id.company_id', store=True)


class TrainingTestResult(models.Model):
    _name = 'training.test.result'
    _description = 'Kết quả bài kiểm tra'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Tên', compute='_compute_name', store=True)
    test_id = fields.Many2one('training.test', string='Bài kiểm tra', required=True, ondelete='cascade')
    enrollment_id = fields.Many2one('training.enrollment', string='Đăng ký')
    employee_id = fields.Many2one('hr.employee', string='Học viên', required=True)
    
    # Thời gian
    start_time = fields.Datetime(string='Bắt đầu', default=fields.Datetime.now)
    end_time = fields.Datetime(string='Kết thúc')
    duration_minutes = fields.Integer(string='Thời gian làm bài (phút)', compute='_compute_duration')
    
    # Điểm số
    score = fields.Float(string='Điểm số (%)', tracking=True)
    points_earned = fields.Float(string='Điểm đạt được')
    total_points = fields.Float(string='Tổng điểm', related='test_id.total_points')
    passed = fields.Boolean(string='Đạt', compute='_compute_passed', store=True)
    
    # Trạng thái
    state = fields.Selection([
        ('in_progress', 'Đang làm'),
        ('submitted', 'Đã nộp'),
        ('graded', 'Đã chấm'),
    ], string='Trạng thái', default='in_progress', required=True, tracking=True)
    
    # Câu trả lời
    answer_ids = fields.One2many('training.test.answer', 'result_id', string='Câu trả lời')
    
    # Chứng chỉ
    certificate_id = fields.Many2one('training.certificate', string='Chứng chỉ')
    certificate_issued = fields.Boolean(string='Đã cấp chứng chỉ', compute='_compute_certificate_issued')
    
    # Ghi chú của giáo viên
    teacher_notes = fields.Text(string='Ghi chú của giáo viên')
    
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    @api.depends('test_id', 'employee_id', 'start_time')
    def _compute_name(self):
        for record in self:
            if record.test_id and record.employee_id:
                record.name = f"{record.test_id.name} - {record.employee_id.name}"
            else:
                record.name = "Kết quả thi"
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration_minutes = int(delta.total_seconds() / 60)
            else:
                record.duration_minutes = 0
    
    @api.depends('score', 'test_id.passing_score')
    def _compute_passed(self):
        for record in self:
            record.passed = record.score >= record.test_id.passing_score if record.test_id else False
    
    @api.depends('certificate_id')
    def _compute_certificate_issued(self):
        for record in self:
            record.certificate_issued = bool(record.certificate_id)
    
    def action_submit(self):
        """Nộp bài"""
        for record in self:
            if record.state != 'in_progress':
                raise UserError(_('Chỉ có thể nộp bài đang làm!'))
            
            record.write({
                'state': 'submitted',
                'end_time': fields.Datetime.now(),
            })
            
            # Auto grade nếu toàn trắc nghiệm
            if record.test_id.test_type in ['quiz', 'mixed']:
                record.action_auto_grade()
    
    def action_auto_grade(self):
        """Tự động chấm điểm trắc nghiệm"""
        for record in self:
            total_points = 0
            earned_points = 0
            
            for answer in record.answer_ids:
                question = answer.question_id
                total_points += question.points
                
                if question.question_type in ['single_choice', 'true_false']:
                    # Kiểm tra đáp án đúng
                    if answer.selected_option_id and answer.selected_option_id.is_correct:
                        earned_points += question.points
                        answer.is_correct = True
                    else:
                        answer.is_correct = False
                
                elif question.question_type == 'multiple_choice':
                    # Kiểm tra tất cả đáp án đúng
                    correct_options = question.option_ids.filtered('is_correct')
                    selected_correct = answer.selected_option_ids & correct_options
                    selected_wrong = answer.selected_option_ids - correct_options
                    
                    if len(selected_correct) == len(correct_options) and not selected_wrong:
                        earned_points += question.points
                        answer.is_correct = True
                    else:
                        answer.is_correct = False
            
            # Tính điểm %
            if total_points > 0:
                score = (earned_points / total_points) * 100
            else:
                score = 0
            
            record.write({
                'points_earned': earned_points,
                'score': score,
                'state': 'graded' if record.test_id.test_type == 'quiz' else 'submitted',
            })
            
            # Cấp chứng chỉ tự động nếu đạt
            if record.passed and record.test_id.auto_certificate and not record.certificate_id:
                record._create_certificate()
    
    def action_manual_grade(self):
        """Chấm điểm thủ công"""
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Chỉ có thể chấm bài đã nộp!'))
            
            # Mở wizard chấm điểm
            return {
                'name': _('Chấm bài'),
                'type': 'ir.actions.act_window',
                'res_model': 'training.test.grading.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_result_id': record.id,
                },
            }
    
    def _create_certificate(self):
        """Tạo chứng chỉ"""
        self.ensure_one()
        
        certificate = self.env['training.certificate'].create({
            'employee_id': self.employee_id.id,
            'course_id': self.test_id.course_id.id,
            'enrollment_id': self.enrollment_id.id,
            'test_result_id': self.id,
            'template_id': self.test_id.certificate_template_id.id,
            'test_score': self.score,
        })
        
        self.certificate_id = certificate.id
        
        # Tự động issue chứng chỉ
        certificate.action_issue()
        
        return certificate
    
    def action_view_certificate(self):
        """Xem chứng chỉ"""
        self.ensure_one()
        
        if not self.certificate_id:
            raise UserError(_('Chưa có chứng chỉ!'))
        
        return {
            'name': _('Chứng chỉ'),
            'type': 'ir.actions.act_window',
            'res_model': 'training.certificate',
            'res_id': self.certificate_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class TrainingTestAnswer(models.Model):
    _name = 'training.test.answer'
    _description = 'Câu trả lời'
    _order = 'sequence, id'

    result_id = fields.Many2one('training.test.result', string='Kết quả', required=True, ondelete='cascade')
    question_id = fields.Many2one('training.test.question', string='Câu hỏi', required=True)
    sequence = fields.Integer(string='Thứ tự')
    
    # Trắc nghiệm
    selected_option_id = fields.Many2one('training.test.option', string='Đáp án chọn')
    selected_option_ids = fields.Many2many('training.test.option', string='Đáp án chọn (nhiều)')
    
    # Tự luận
    essay_answer = fields.Text(string='Câu trả lời')
    
    # Chấm điểm
    is_correct = fields.Boolean(string='Đúng', default=False)
    points_earned = fields.Float(string='Điểm đạt được')
    teacher_comment = fields.Text(string='Nhận xét')
    
    company_id = fields.Many2one('res.company', related='result_id.company_id', store=True)
