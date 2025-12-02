# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta

class TrainingReminder(models.Model):
    _name = 'training.reminder'
    _description = 'Hệ thống nhắc nhở đào tạo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'reminder_date desc'

    name = fields.Char(string='Tiêu đề', required=True)
    reminder_type = fields.Selection([
        ('session', 'Lớp học tập trung'),
        ('enrollment', 'Hạn hoàn thành khóa học'),
        ('exam', 'Hạn kiểm tra'),
        ('general', 'Thông báo chung'),
    ], string='Loại nhắc nhở', required=True)
    
    # Liên kết các object
    session_id = fields.Many2one('training.session', string='Lớp học')
    enrollment_id = fields.Many2one('training.enrollment', string='Hồ sơ học tập')
    exam_id = fields.Many2one('training.exam', string='Bài kiểm tra') 
    
    reminder_date = fields.Datetime(string='Thời điểm nhắc', required=True)
    sent_date = fields.Datetime(string='Đã gửi lúc', readonly=True)
    
    state = fields.Selection([
        ('pending', 'Chờ gửi'),
        ('sent', 'Đã gửi'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='pending', required=True, tracking=True)
    
    # Người nhận
    recipient_ids = fields.Many2many('res.partner', string='Người nhận (Partner)')
    employee_ids = fields.Many2many('hr.employee', string='Nhân viên nhận')
    
    message = fields.Html(string='Nội dung thông báo')
    
    # Cấu hình gửi (Đã xóa send_email)
    send_notification = fields.Boolean(string='Gửi thông báo hệ thống', default=True)
    
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)

    def action_send_reminder(self):
        """Hàm xử lý gửi (Được gọi bởi nút bấm hoặc Cron)"""
        for reminder in self:
            if reminder.state != 'pending':
                continue
            
            # Chỉ gửi Notification (Quả chuông Odoo)
            if reminder.send_notification:
                reminder._send_notification_reminder()
            
            reminder.write({
                'state': 'sent',
                'sent_date': fields.Datetime.now(),
            })

    def _send_notification_reminder(self):
        """Gửi thông báo nội bộ (Chatter/Bell)"""
        self.ensure_one()
        # Gom người nhận từ Partner và Employee
        partners = self.recipient_ids | self.employee_ids.mapped('user_id.partner_id')
        
        if partners:
            self.message_post(
                body=self.message,
                partner_ids=partners.ids,
                message_type='notification', # Loại thông báo
                subtype_xmlid='mail.mt_comment', # Hiển thị popup quả chuông
                author_id=self.env.user.partner_id.id
            )

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    @api.model
    def _cron_send_pending_reminders(self):
        """CRON JOB: Quét các nhắc nhở đến hạn"""
        now = fields.Datetime.now()
        pending_reminders = self.search([
            ('state', '=', 'pending'),
            ('reminder_date', '<=', now),
        ])
        if pending_reminders:
            pending_reminders.action_send_reminder()

# --- MODEL TEMPLATE (Đã xóa cấu hình Email) ---
class TrainingReminderTemplate(models.Model):
    _name = 'training.reminder.template'
    _description = 'Mẫu cấu hình nhắc nhở'

    name = fields.Char(string='Tên mẫu', required=True)
    reminder_type = fields.Selection([
        ('session', 'Trước buổi học'),
        ('enrollment', 'Sau khi đăng ký'),
        ('exam', 'Deadline bài thi'),
    ], string='Loại sự kiện', required=True)
    
    days_before = fields.Integer(string='Thời gian (Ngày)', default=1, help='Số ngày Trước (hoặc Sau) sự kiện để gửi nhắc nhở')
    
    # Xóa Subject vì không gửi mail
    message_template = fields.Html(string='Mẫu nội dung', required=True, help="Dùng các biến {name}, {date}, {course}...")
    
    send_notification = fields.Boolean(default=True)
    active = fields.Boolean(default=True)


# --- TÍCH HỢP VÀO ENROLLMENT ---
class TrainingEnrollmentReminder(models.Model):
    _inherit = 'training.enrollment'

    reminder_ids = fields.One2many('training.reminder', 'enrollment_id', string='Lịch sử nhắc nhở')

    @api.model_create_multi
    def create(self, vals_list):
        enrollments = super().create(vals_list)
        for record in enrollments:
            if record.state == 'draft':
                record._create_approval_reminder()
        return enrollments

    def _create_approval_reminder(self):
        """Tạo nhắc nhở cho Admin/Manager duyệt bài"""
        manager_group = self.env.ref('training_management.group_training_manager', raise_if_not_found=False)
        managers = manager_group.users if manager_group else self.env.ref('base.user_admin')
        recipients = managers.mapped('partner_id')

        self.env['training.reminder'].create({
            'name': f"Yêu cầu duyệt: {self.employee_id.name} - {self.course_id.name}",
            'reminder_type': 'enrollment',
            'enrollment_id': self.id,
            'reminder_date': fields.Datetime.now(),
            'state': 'pending',
            'recipient_ids': [(6, 0, recipients.ids)],
            'message': f"<p>Nhân viên <b>{self.employee_id.name}</b> vừa đăng ký khóa học <b>{self.course_id.name}</b>. Vui lòng kiểm tra và phê duyệt.</p>",
            'send_notification': True,
        })