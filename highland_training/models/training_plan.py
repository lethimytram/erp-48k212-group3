# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TrainingPlan(models.Model):
    _name = 'training.plan'
    _description = 'Kế hoạch đào tạo'
    _order = 'create_date desc'

    name = fields.Char('Tên kế hoạch', required=True)
    quarter = fields.Selection([
        ('q1', 'Quý 1'),
        ('q2', 'Quý 2'),
        ('q3', 'Quý 3'),
        ('q4', 'Quý 4'),
    ], string='Quý', required=True)
    year = fields.Integer('Năm', required=True, default=lambda self: fields.Date.today().year)
    course_ids = fields.Many2many(
        'training.course', 
        string='Danh sách khóa học', 
        required=True,
        domain="[('state', '=', 'need_planning')]"
    )
    employee_ids = fields.Many2many('hr.employee', string='Danh sách nhân viên')
    department_ids = fields.Many2many('hr.department', string='Danh sách phòng ban/cửa hàng')
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('done', 'Hoàn thành'),
    ], default='draft', string='Trạng thái')
    
    enrollment_ids = fields.One2many('training.enrollment', 'plan_id', string='Danh sách ghi danh')
    total_enrollments = fields.Integer('Tổng số ghi danh', compute='_compute_stats')
    completed_enrollments = fields.Integer('Đã hoàn thành', compute='_compute_stats')
    completion_rate = fields.Float('Tỷ lệ hoàn thành (%)', compute='_compute_stats')
    
    @api.depends('enrollment_ids', 'enrollment_ids.state')
    def _compute_stats(self):
        for plan in self:
            total = len(plan.enrollment_ids)
            completed = len(plan.enrollment_ids.filtered(lambda e: e.state == 'completed'))
            plan.total_enrollments = total
            plan.completed_enrollments = completed
            plan.completion_rate = (completed / total * 100) if total > 0 else 0
    
    def action_confirm(self):
        """Xác nhận kế hoạch và chuyển khóa học sang 'Đang hoạt động'"""
        self.state = 'confirmed'
        
        # Chuyển các khóa học sang trạng thái 'Đang hoạt động'
        for course in self.course_ids:
            if course.state == 'need_planning':
                course.state = 'active'
        
        # Cập nhật các enrollment liên quan sang trạng thái 'learning'
        enrollments = self.env['training.enrollment'].search([
            ('course_id', 'in', self.course_ids.ids),
            ('state', '=', 'draft')
        ])
        for enrollment in enrollments:
            enrollment.plan_id = self.id
            enrollment.state = 'learning'
    
    def action_enroll_bulk(self):
        """Tự động ghi danh hàng loạt - theo đúng logic nghiệp vụ"""
        enrollment_obj = self.env['training.enrollment']
        created_count = 0
        missing_employees = []
        
        for course in self.course_ids:
            # Lấy danh sách nhân viên cho khóa học này
            employees_to_enroll = self.env['hr.employee']
            
            # Logic: Lấy nhân viên từ course.employee_ids (đã được gán từ nhu cầu hoặc thủ công)
            if course.employee_ids:
                employees_to_enroll = course.employee_ids
            else:
                # Nếu khóa học không có nhân viên, ghi nhận lỗi
                missing_employees.append(course.name)
                continue
            
            # Tạo enrollment cho từng nhân viên
            for employee in employees_to_enroll:
                # Kiểm tra đã có enrollment chưa
                existing = enrollment_obj.search([
                    ('employee_id', '=', employee.id),
                    ('course_id', '=', course.id),
                    ('plan_id', '=', self.id)
                ], limit=1)
                
                if not existing:
                    enrollment_obj.create({
                        'employee_id': employee.id,
                        'course_id': course.id,
                        'plan_id': self.id,
                    })
                    created_count += 1
        
        # Sau khi ghi danh xong, chuyển sang trạng thái Hoàn thành
        if not missing_employees:
            self.state = 'done'
        
        # Thông báo kết quả
        if missing_employees:
            message = f'Cảnh báo: {len(missing_employees)} khóa học chưa có danh sách nhân viên: {", ".join(missing_employees)}'
            notification_type = 'warning'
        else:
            message = f'Đã tạo {created_count} bản ghi enrollment và hoàn thành kế hoạch'
            notification_type = 'success'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Kết quả ghi danh',
                'message': message,
                'type': notification_type,
                'sticky': False,
            }
        }
