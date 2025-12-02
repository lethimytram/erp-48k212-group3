# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TrainingNeed(models.Model):
    _name = 'training.need'
    _description = 'Đề xuất nhu cầu đào tạo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'urgency desc, create_date desc'

    name = fields.Char(string='Tiêu đề', required=True, tracking=True, default=lambda self: _('Đề xuất đào tạo mới'))
    employee_id = fields.Many2one('hr.employee', string='Nhân viên cần đào tạo', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Phòng ban/Cửa hàng', related='employee_id.department_id', store=True)
    
    # Chi tiết nhu cầu
    suggested_course_id = fields.Many2one('training.course', string='Khóa học đề xuất')
    description = fields.Text(string='Lý do/Mô tả chi tiết', required=True, help="Vd: Nhân viên pha chế chưa chuẩn công thức...")
    deadline = fields.Date(string='Mong muốn hoàn thành trước')
    
    urgency = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Bình thường'),
        ('2', 'Cao'),
        ('3', 'Rất gấp'),
    ], string='Mức độ ưu tiên', default='1', tracking=True)

    # Tích hợp Phê duyệt (TODO: Implement approval workflow)
    # approval_id = fields.Many2one('training.approval', string='Yêu cầu phê duyệt', readonly=True, copy=False)
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('waiting', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('done', 'Đã xử lý') # Trạng thái khi đã tạo Enrollment
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    
    # Link sang Enrollment nếu đã tạo
    enrollment_id = fields.Many2one('training.enrollment', string='Hồ sơ đăng ký', readonly=True)
    
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)

    def action_submit(self):
        """Gửi đề xuất đi phê duyệt"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Chỉ có thể gửi đề xuất ở trạng thái Nháp.'))

        # TODO: Implement approval workflow
        # Auto approve for now
        self.state = 'approved'
        
        # # Tìm quy trình duyệt cho Training Need
        # flow = self.env['training.approval.flow'].search([
        #     ('model_id.model', '=', self._name),
        #     ('active', '=', True)
        # ], limit=1)

        # if not flow:
        #     # Nếu không có quy trình, tự động duyệt
        #     self.state = 'approved'
        #     return

        # # Tạo Approval Record
        # approval_vals = {
        #     'name': f"Duyệt nhu cầu đào tạo: {self.name}",
        #     'flow_id': flow.id,
        #     'employee_id': self.env.user.employee_id.id, # Người tạo đề xuất (thường là Manager)
        #     'res_model': self._name,
        #     'res_id': self.id,
        # }
        # approval = self.env['training.approval'].create(approval_vals)
        # 
        # self.write({
        #     'approval_id': approval.id,
        #     'state': 'waiting'
        # })
        # approval.action_submit()

    def action_approve(self):
        """Callback: Khi được duyệt"""
        self.write({'state': 'approved'})

    def action_reject(self):
        """Callback: Khi bị từ chối"""
        self.write({'state': 'rejected'})

    def action_create_enrollment(self):
        """Chuyển nhu cầu thành Đăng ký khóa học chính thức"""
        self.ensure_one()
        if not self.suggested_course_id:
            raise UserError(_('Vui lòng chọn Khóa học đề xuất trước khi tạo đăng ký.'))
        
        # Tạo Enrollment
        enrollment = self.env['training.enrollment'].create({
            'employee_id': self.employee_id.id,
            'course_id': self.suggested_course_id.id,
            'state': 'draft', # Tạo nháp để kiểm tra lại
        })
        
        self.write({
            'state': 'done',
            'enrollment_id': enrollment.id
        })
        
        # Mở form Enrollment vừa tạo
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'training.enrollment',
            'res_id': enrollment.id,
            'view_mode': 'form',
            'target': 'current',
        }