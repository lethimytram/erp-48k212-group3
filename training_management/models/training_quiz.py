# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

# --- 1. ĐỀ THI / BÀI SÁT HẠCH ---
class TrainingExam(models.Model):
    _name = 'training.exam'
    _description = 'Bài sát hạch lý thuyết'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'course_id, name'

    name = fields.Char(string='Tên bài kiểm tra', required=True, tracking=True)
    exam_code = fields.Char(string='Mã đề', default='New', copy=False)
    
    # Liên kết Khóa học (SOP)
    course_id = fields.Many2one('training.course', string='Thuộc quy trình (SOP)', required=True)
    
    # Cấu hình thi (Đã bỏ shuffle)
    duration = fields.Integer(string='Thời gian làm bài (phút)', default=15, help="0 là không giới hạn")
    passing_score = fields.Float(string='Điểm đạt (%)', default=80.0)
    max_attempts = fields.Integer(string='Số lần thi tối đa', default=3, help="0 là không giới hạn")
    
    # Nội dung
    question_ids = fields.One2many('training.question', 'exam_id', string='Danh sách câu hỏi')
    question_count = fields.Integer(compute='_compute_question_count')
    
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('draft', 'Soạn thảo'),
        ('published', 'Đang áp dụng'),
        ('archived', 'Lưu trữ')
    ], string='Trạng thái', default='draft', tracking=True)

    @api.depends('question_ids')
    def _compute_question_count(self):
        for record in self:
            record.question_count = len(record.question_ids)

    def action_publish(self):
        if not self.question_ids:
            raise UserError(_('Đề thi phải có ít nhất 1 câu hỏi!'))
        self.state = 'published'

    def action_reset(self):
        self.state = 'draft'

# --- 2. CÂU HỎI (QUESTION) ---
class TrainingQuestion(models.Model):
    _name = 'training.question'
    _description = 'Câu hỏi'
    _order = 'sequence, id'

    exam_id = fields.Many2one('training.exam', string='Đề thi', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10, string="Thứ tự")
    
    name = fields.Text(string='Nội dung câu hỏi', required=True)
    
    # Đã xóa 'essay' (Tự luận)
    question_type = fields.Selection([
        ('single_choice', 'Chọn 1 đáp án đúng'),
        ('multiple_choice', 'Chọn nhiều đáp án'),
        ('true_false', 'Đúng / Sai')
    ], string='Loại câu hỏi', default='single_choice', required=True)
    
    points = fields.Float(string='Điểm số', default=1.0)
    explanation = fields.Text(string='Giải thích đáp án', help="Hiện ra khi học viên xem lại bài")
    
    option_ids = fields.One2many('training.question.option', 'question_id', string='Các phương án')

    # Validate: Phải có đáp án đúng để máy tự chấm
    @api.constrains('option_ids', 'question_type')
    def _check_correct_option(self):
        for record in self:
            correct = record.option_ids.filtered(lambda o: o.is_correct)
            if not correct:
                raise ValidationError(_('Câu hỏi "%s" chưa thiết lập đáp án đúng!') % record.name)
            if record.question_type in ['single_choice', 'true_false'] and len(correct) > 1:
                raise ValidationError(_('Câu hỏi "%s" (Chọn 1 đáp án) không được có nhiều hơn 1 đáp án đúng.') % record.name)

# --- 3. ĐÁP ÁN (OPTION) ---
class TrainingQuestionOption(models.Model):
    _name = 'training.question.option'
    _description = 'Lựa chọn đáp án'
    _order = 'sequence, id'
    
    question_id = fields.Many2one('training.question', ondelete='cascade')
    name = fields.Char(string='Nội dung đáp án', required=True)
    is_correct = fields.Boolean(string='Là đáp án ĐÚNG')
    sequence = fields.Integer(default=10)

# --- 4. LỊCH SỬ LÀM BÀI (ATTEMPT/RESULT) ---
class TrainingExamAttempt(models.Model):
    _name = 'training.exam.attempt'
    _description = 'Lịch sử làm bài thi'
    _rec_name = 'employee_id'
    _order = 'create_date desc'

    exam_id = fields.Many2one('training.exam', string='Đề thi', required=True)
    enrollment_id = fields.Many2one('training.enrollment', string='Hồ sơ học tập') 
    employee_id = fields.Many2one('res.users', string='Nhân viên', default=lambda self: self.env.user)
    
    start_time = fields.Datetime(default=fields.Datetime.now, string="Bắt đầu")
    end_time = fields.Datetime(string="Nộp bài")
    
    score = fields.Float(string='Điểm số (%)')
    is_passed = fields.Boolean(string='Kết quả', compute='_compute_is_passed', store=True)
    
    # Đã xóa trạng thái graded/manual scoring
    state = fields.Selection([
        ('in_progress', 'Đang làm'),
        ('submitted', 'Đã nộp')
    ], default='in_progress', string="Trạng thái")

    answer_ids = fields.One2many('training.exam.answer', 'attempt_id', string="Chi tiết trả lời")

    @api.depends('score', 'exam_id.passing_score')
    def _compute_is_passed(self):
        for record in self:
            record.is_passed = record.score >= record.exam_id.passing_score

    def action_submit(self):
        """100% Tự động chấm điểm"""
        self.ensure_one()
        total_score = 0
        max_score = sum(self.exam_id.question_ids.mapped('points'))
        
        for answer in self.answer_ids:
            question = answer.question_id
            selected = answer.selected_option_ids
            correct = question.option_ids.filtered(lambda o: o.is_correct)
            
            # Logic chấm điểm: Chọn ĐÚNG hết các đáp án đúng và KHÔNG chọn đáp án sai
            if set(selected.ids) == set(correct.ids):
                total_score += question.points
                answer.is_correct = True
            else:
                answer.is_correct = False
        
        final_percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        self.write({
            'state': 'submitted',
            'end_time': fields.Datetime.now(),
            'score': final_percentage
        })

        # Hook: Tự động update trạng thái Enrollment nếu có
        if self.enrollment_id and hasattr(self.enrollment_id, 'action_update_theory_result'):
            self.enrollment_id.action_update_theory_result(final_percentage, self.is_passed)

# --- 5. CHI TIẾT CÂU TRẢ LỜI ---
class TrainingExamAnswer(models.Model):
    _name = 'training.exam.answer'
    _description = 'Câu trả lời chi tiết'

    attempt_id = fields.Many2one('training.exam.attempt', ondelete='cascade')
    question_id = fields.Many2one('training.question')
    
    # Chỉ lưu đáp án trắc nghiệm
    selected_option_ids = fields.Many2many('training.question.option', string='Đáp án đã chọn')
    is_correct = fields.Boolean(string='Đúng/Sai', readonly=True)