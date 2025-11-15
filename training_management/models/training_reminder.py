# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

class TrainingReminder(models.Model):
    _name = 'training.reminder'
    _description = 'Training Reminder'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'reminder_date desc'

    name = fields.Char(string='Tên nhắc nhở', required=True)
    reminder_type = fields.Selection([
        ('session', 'Buổi học'),
        ('enrollment', 'Đăng ký'),
        # ('test', 'Kiểm tra'),  # Tạm tắt
        ('deadline', 'Deadline'),
        # ('certificate', 'Chứng chỉ'),  # Tạm tắt
    ], string='Loại nhắc nhở', required=True)
    
    session_id = fields.Many2one('training.session', string='Buổi học')
    enrollment_id = fields.Many2one('training.enrollment', string='Đăng ký')
    # test_id = fields.Many2one('training.test', string='Bài kiểm tra')  # Tạm tắt
    
    reminder_date = fields.Datetime(string='Ngày nhắc nhở', required=True)
    sent_date = fields.Datetime(string='Ngày đã gửi', readonly=True)
    
    state = fields.Selection([
        ('pending', 'Chờ gửi'),
        ('sent', 'Đã gửi'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='pending', required=True)
    
    recipient_ids = fields.Many2many('res.partner', string='Người nhận')
    employee_ids = fields.Many2many('hr.employee', string='Nhân viên')
    
    message = fields.Html(string='Nội dung nhắc nhở')
    notes = fields.Text(string='Ghi chú')
    
    # Cài đặt nhắc nhở
    send_email = fields.Boolean(string='Gửi Email', default=True)
    send_notification = fields.Boolean(string='Gửi thông báo', default=True)
    
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)

    def action_send_reminder(self):
        """Gửi nhắc nhở"""
        for reminder in self:
            if reminder.state != 'pending':
                continue
                
            # Gửi email
            if reminder.send_email and reminder.recipient_ids:
                reminder._send_email_reminder()
            
            # Gửi thông báo nội bộ
            if reminder.send_notification:
                reminder._send_notification_reminder()
            
            # Cập nhật trạng thái
            reminder.write({
                'state': 'sent',
                'sent_date': fields.Datetime.now(),
            })
    
    def _send_email_reminder(self):
        """Gửi email nhắc nhở"""
        self.ensure_one()
        template = self.env.ref('training_management.email_template_training_reminder', raise_if_not_found=False)
        if template:
            for recipient in self.recipient_ids:
                template.send_mail(self.id, force_send=True, email_values={
                    'email_to': recipient.email,
                })
    
    def _send_notification_reminder(self):
        """Gửi thông báo nội bộ"""
        self.ensure_one()
        # Gửi thông báo cho nhân viên
        for employee in self.employee_ids:
            if employee.user_id:
                self.message_post(
                    body=self.message,
                    partner_ids=employee.user_id.partner_id.ids,
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment',
                )
    
    def action_cancel(self):
        """Hủy nhắc nhở"""
        self.write({'state': 'cancelled'})
    
    @api.model
    def _cron_send_pending_reminders(self):
        """Cron job: Gửi các nhắc nhở đang chờ"""
        now = fields.Datetime.now()
        pending_reminders = self.search([
            ('state', '=', 'pending'),
            ('reminder_date', '<=', now),
        ])
        pending_reminders.action_send_reminder()


class TrainingReminderTemplate(models.Model):
    _name = 'training.reminder.template'
    _description = 'Training Reminder Template'

    name = fields.Char(string='Tên mẫu', required=True)
    reminder_type = fields.Selection([
        ('session', 'Buổi học'),
        ('enrollment', 'Đăng ký'),
        ('test', 'Kiểm tra'),
        ('deadline', 'Deadline'),
        ('certificate', 'Chứng chỉ'),
    ], string='Loại nhắc nhở', required=True)
    
    days_before = fields.Integer(string='Số ngày trước', default=1, help='Gửi nhắc nhở trước bao nhiêu ngày')
    
    subject = fields.Char(string='Tiêu đề', required=True)
    message_template = fields.Html(string='Mẫu nội dung', required=True)
    
    send_email = fields.Boolean(string='Gửi Email', default=True)
    send_notification = fields.Boolean(string='Gửi thông báo', default=True)
    
    active = fields.Boolean(string='Kích hoạt', default=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)


class TrainingSessionReminder(models.Model):
    _inherit = 'training.session'

    reminder_ids = fields.One2many('training.reminder', 'session_id', string='Nhắc nhở')
    reminder_count = fields.Integer(string='Số lượng nhắc nhở', compute='_compute_reminder_count')
    
    auto_create_reminder = fields.Boolean(string='Tự động tạo nhắc nhở', default=True)
    
    @api.depends('reminder_ids')
    def _compute_reminder_count(self):
        for session in self:
            session.reminder_count = len(session.reminder_ids)
    
    def action_view_reminders(self):
        """Xem danh sách nhắc nhở"""
        self.ensure_one()
        return {
            'name': 'Nhắc nhở',
            'type': 'ir.actions.act_window',
            'res_model': 'training.reminder',
            'view_mode': 'list,form',
            'domain': [('session_id', '=', self.id)],
            'context': {'default_session_id': self.id},
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo nhắc nhở khi tạo buổi học"""
        sessions = super().create(vals_list)
        for session in sessions:
            if session.auto_create_reminder and session.start_date:
                session._create_auto_reminders()
        return sessions
    
    def write(self, vals):
        """Cập nhật nhắc nhở khi thay đổi ngày"""
        res = super().write(vals)
        if 'start_date' in vals:
            for session in self:
                if session.auto_create_reminder:
                    # Hủy nhắc nhở cũ chưa gửi
                    session.reminder_ids.filtered(lambda r: r.state == 'pending').action_cancel()
                    # Tạo nhắc nhở mới
                    session._create_auto_reminders()
        return res
    
    def _create_auto_reminders(self):
        """Tạo nhắc nhở tự động"""
        self.ensure_one()
        if not self.start_date:
            return
        
        # Lấy template nhắc nhở
        templates = self.env['training.reminder.template'].search([
            ('reminder_type', '=', 'session'),
            ('active', '=', True),
        ])
        
        # Lấy danh sách người nhận
        recipients = self.env['res.partner']
        employees = self.env['hr.employee']
        
        # Thêm giảng viên
        if self.trainer_id and self.trainer_id.partner_id:
            recipients |= self.trainer_id.partner_id
            employees |= self.env['hr.employee'].search([('user_id.partner_id', '=', self.trainer_id.partner_id.id)], limit=1)
        
        # Thêm học viên
        for enrollment in self.enrollment_ids:
            if enrollment.employee_id:
                employees |= enrollment.employee_id
                if enrollment.employee_id.user_id:
                    recipients |= enrollment.employee_id.user_id.partner_id
        
        # Tạo nhắc nhở theo template
        for template in templates:
            reminder_date = self.start_date - timedelta(days=template.days_before)
            
            # Chỉ tạo nếu ngày nhắc nhở trong tương lai
            if reminder_date > fields.Datetime.now():
                message = template.message_template
                # Replace placeholders
                message = message.replace('{session_name}', self.name or '')
                message = message.replace('{course_name}', self.course_id.name or '')
                message = message.replace('{date}', self.start_date.strftime('%d/%m/%Y %H:%M') if self.start_date else '')
                message = message.replace('{location}', self.location or '')
                
                self.env['training.reminder'].create({
                    'name': f"{template.subject} - {self.name}",
                    'reminder_type': 'session',
                    'session_id': self.id,
                    'reminder_date': reminder_date,
                    'state': 'pending',
                    'recipient_ids': [(6, 0, recipients.ids)],
                    'employee_ids': [(6, 0, employees.ids)],
                    'message': message,
                    'send_email': template.send_email,
                    'send_notification': template.send_notification,
                })
    
    def action_create_reminder(self):
        """Tạo nhắc nhở thủ công"""
        self.ensure_one()
        return {
            'name': 'Tạo nhắc nhở',
            'type': 'ir.actions.act_window',
            'res_model': 'training.reminder',
            'view_mode': 'form',
            'context': {
                'default_session_id': self.id,
                'default_reminder_type': 'session',
                'default_name': f"Nhắc nhở: {self.name}",
            },
            'target': 'new',
        }


class TrainingEnrollmentReminder(models.Model):
    _inherit = 'training.enrollment'

    reminder_ids = fields.One2many('training.reminder', 'enrollment_id', string='Nhắc nhở')
    
    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo nhắc nhở khi đăng ký"""
        enrollments = super().create(vals_list)
        for enrollment in enrollments:
            if enrollment.state == 'draft':
                enrollment._create_enrollment_reminder()
        return enrollments
    
    def _create_enrollment_reminder(self):
        """Tạo nhắc nhở phê duyệt đăng ký"""
        self.ensure_one()
        
        # Nhắc nhở người quản lý phê duyệt
        manager_partner = self.env.ref('base.user_admin').partner_id
        
        self.env['training.reminder'].create({
            'name': f"Phê duyệt đăng ký: {self.employee_id.name} - {self.course_id.name}",
            'reminder_type': 'enrollment',
            'enrollment_id': self.id,
            'reminder_date': fields.Datetime.now() + timedelta(hours=1),
            'state': 'pending',
            'recipient_ids': [(6, 0, [manager_partner.id])],
            'message': f"""
                <p>Có đơn đăng ký khóa học mới cần phê duyệt:</p>
                <ul>
                    <li><strong>Nhân viên:</strong> {self.employee_id.name}</li>
                    <li><strong>Khóa học:</strong> {self.course_id.name}</li>
                    <li><strong>Ngày đăng ký:</strong> {self.enrollment_date.strftime('%d/%m/%Y') if self.enrollment_date else ''}</li>
                </ul>
            """,
            'send_email': True,
            'send_notification': True,
        })


# Tạm tắt - Class inherit training.test
# class TrainingTestReminder(models.Model):
#     _inherit = 'training.test'

#     reminder_ids = fields.One2many('training.reminder', 'test_id', string='Nhắc nhở')
    
#     def _create_test_deadline_reminder(self):
#         """Tạo nhắc nhở deadline bài kiểm tra"""
#         self.ensure_one()
#         if not self.deadline:
#             return
        
#         # Nhắc trước 2 ngày
#         reminder_date = self.deadline - timedelta(days=2)
#         if reminder_date > fields.Datetime.now():
#             # Lấy danh sách học viên
#             employees = self.enrollment_id.mapped('employee_id')
#             recipients = employees.mapped('user_id.partner_id')
            
#             self.env['training.reminder'].create({
#                 'name': f"Deadline bài kiểm tra: {self.name}",
#                 'reminder_type': 'test',
#                 'test_id': self.id,
#                 'reminder_date': reminder_date,
#                 'state': 'pending',
#                 'recipient_ids': [(6, 0, recipients.ids)],
#                 'employee_ids': [(6, 0, employees.ids)],
#                 'message': f"""
#                     <p><strong>Nhắc nhở:</strong> Bài kiểm tra sắp hết hạn!</p>
#                     <ul>
#                         <li><strong>Bài kiểm tra:</strong> {self.name}</li>
#                         <li><strong>Deadline:</strong> {self.deadline.strftime('%d/%m/%Y %H:%M')}</li>
#                     </ul>
#                     <p>Vui lòng hoàn thành bài kiểm tra trước thời hạn.</p>
#                 """,
#                 'send_email': True,
#                 'send_notification': True,
#             })
