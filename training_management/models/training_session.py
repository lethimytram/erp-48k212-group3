# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TrainingSession(models.Model):
    _name = 'training.session'
    _description = 'Lớp học tập trung / Workshop'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, name'

    name = fields.Char(string='Tên buổi học', required=True, tracking=True, 
                       default=lambda self: _('Lớp học mới'))
    
    course_id = fields.Many2one('training.course', string='Nội dung đào tạo', required=True, tracking=True)
    
    # Giảng viên có thể là nhân viên nội bộ hoặc thuê ngoài
    trainer_id = fields.Many2one('hr.employee', string='Giảng viên', required=True, tracking=True)
    
    # Thời gian & Địa điểm
    start_date = fields.Datetime(string='Bắt đầu', required=True, tracking=True)
    end_date = fields.Datetime(string='Kết thúc', required=True, tracking=True)
    duration = fields.Float(string='Thời lượng (giờ)', compute='_compute_duration', store=True)
    location = fields.Char(string='Địa điểm/Phòng họp', help="VD: Phòng Training Hội sở, Cửa hàng A...")
    
    # Quản lý học viên (Quan trọng)
    enrollment_ids = fields.Many2many('training.enrollment', string='Danh sách học viên')
    attendees_count = fields.Integer(string='Sĩ số', compute='_compute_attendees_count')
    
    # Tích hợp Odoo Calendar
    calendar_event_id = fields.Many2one('calendar.event', string='Sự kiện lịch', readonly=True)
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('scheduled', 'Đã lên lịch'),
        ('in_progress', 'Đang diễn ra'),
        ('done', 'Đã dạy xong'),
        ('cancelled', 'Hủy bỏ')
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)

    # --- LOGIC ---

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                diff = record.end_date - record.start_date
                record.duration = diff.total_seconds() / 3600
            else:
                record.duration = 0

    @api.depends('enrollment_ids')
    def _compute_attendees_count(self):
        for record in self:
            record.attendees_count = len(record.enrollment_ids)

    # --- ACTION WORKFLOW ---

    def action_schedule(self):
        """Xác nhận lên lịch và tạo Calendar Event"""
        self.ensure_one()
        if not self.trainer_id.user_id:
             # Warning nếu giảng viên không có User để nhận thông báo lịch
             pass 

        # Tạo sự kiện trên lịch Odoo
        event = self.env['calendar.event'].create({
            'name': f"[Training] {self.name}",
            'start': self.start_date,
            'stop': self.end_date,
            'location': self.location,
            'user_id': self.trainer_id.user_id.id if self.trainer_id.user_id else self.env.user.id,
            'description': f"Lớp đào tạo: {self.course_id.name}",
            # Add học viên vào danh sách mời họp (Optional)
            'partner_ids': [(6, 0, self.enrollment_ids.mapped('employee_id.user_id.partner_id').ids)]
        })
        
        self.write({
            'state': 'scheduled',
            'calendar_event_id': event.id
        })

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_finish(self):
        """Kết thúc buổi học"""
        self.write({'state': 'done'})

    def action_cancel(self):
        """Hủy buổi học và xóa lịch"""
        if self.calendar_event_id:
            self.calendar_event_id.unlink()
        self.write({'state': 'cancelled'})