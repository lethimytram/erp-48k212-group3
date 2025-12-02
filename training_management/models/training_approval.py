# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class TrainingEnrollment(models.Model):
    _name = 'training.enrollment'
    _description = 'Hồ sơ học tập'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'
    _order = 'create_date desc'

    # --- 1. THÔNG TIN CHUNG ---
    course_id = fields.Many2one('training.course', string='Quy trình (SOP)', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, tracking=True)
    
    # Người phụ trách hướng dẫn (Thường là Cửa hàng trưởng)
    mentor_id = fields.Many2one('res.users', string='Người hướng dẫn (OJT)', 
                                default=lambda self: self.env.user)
    
    start_date = fields.Date(string='Ngày bắt đầu', default=fields.Date.today)
    completion_date = fields.Date(string='Ngày hoàn thành')

    # --- 2. TRẠNG THÁI (CORE WORKFLOW) ---
    state = fields.Selection([
        ('draft', 'Mới phân công'),
        ('theory', 'Đang học Lý thuyết'),
        ('practical', 'Sát hạch Thực hành'), # Chỉ hiện khi đậu lý thuyết
        ('done', 'Đã cấp chứng chỉ'),
        ('failed', 'Không đạt'),
        ('cancelled', 'Đã hủy')
    ], string='Tiến độ', default='draft', tracking=True, group_expand='_expand_states')

    # --- 3. KẾT QUẢ HỌC TẬP ---
    # Lý thuyết (Lấy từ bài Exam mới nhất)
    exam_attempt_ids = fields.One2many('training.exam.attempt', 'enrollment_id', string='Lịch sử thi')
    theory_score = fields.Float(string='Điểm Lý thuyết', compute='_compute_scores', store=True)
    is_theory_passed = fields.Boolean(string='Đậu Lý thuyết', compute='_compute_scores', store=True)

    # Thực hành (Sẽ làm module chấm điểm sau)
    practical_score = fields.Float(string='Điểm Thực hành', tracking=True)
    practical_feedback = fields.Text(string='Nhận xét thực hành')

    # --- LOGIC ---

    @api.depends('exam_attempt_ids.state', 'exam_attempt_ids.score')
    def _compute_scores(self):
        for record in self:
            # Lấy bài thi mới nhất đã nộp
            last_attempt = self.env['training.exam.attempt'].search([
                ('enrollment_id', '=', record.id),
                ('state', '=', 'submitted')
            ], order='create_date desc', limit=1)
            
            if last_attempt:
                record.theory_score = last_attempt.score
                record.is_theory_passed = last_attempt.is_passed
            else:
                record.theory_score = 0.0
                record.is_theory_passed = False

    def action_start_learning(self):
        """Bắt đầu học (Chuyển sang Giai đoạn 2)"""
        self.state = 'theory'

    def action_update_theory_result(self, score, is_passed):
        """
        Hàm này được gọi tự động từ module Exam khi nộp bài.
        Nếu đậu lý thuyết -> Tự động mở khóa phần Thực hành.
        """
        self.ensure_one()
        if is_passed:
            self.state = 'practical'
            # Gửi thông báo cho Cửa hàng trưởng (Mentor) để chấm thực hành
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=self.mentor_id.id,
                summary=f'Sát hạch thực hành cho {self.employee_id.name}',
                note=f'Nhân viên đã đậu lý thuyết ({score}%), vui lòng kiểm tra kỹ năng thực tế.'
            )
        else:
            # Nếu rớt, vẫn ở trạng thái theory để thi lại
            self.message_post(body=f"Thi trượt lý thuyết: {score}%. Vui lòng ôn tập và thi lại.")

    def action_pass_practical(self):
        """Xác nhận đậu thực hành (Cửa hàng trưởng bấm)"""
        self.state = 'done'
        self.completion_date = fields.Date.today()
        # Tại đây sẽ gọi hàm cấp chứng chỉ (Module Certificate)
        self.message_post(body="Đã hoàn thành khóa học và cấp chứng chỉ.")

    def action_fail(self):
        self.state = 'failed'

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]