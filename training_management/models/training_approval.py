# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class TrainingApprovalConfig(models.Model):
    _name = 'training.approval.config'
    _description = 'Training Approval Configuration'
    _order = 'sequence'

    name = fields.Char(string='Tên cấu hình', required=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    
    # Điều kiện áp dụng
    course_category_ids = fields.Many2many('training.course.category', string='Danh mục khóa học')
    min_duration = fields.Integer(string='Thời lượng tối thiểu (giờ)')
    max_duration = fields.Integer(string='Thời lượng tối đa (giờ)')
    min_cost = fields.Float(string='Chi phí tối thiểu')
    max_cost = fields.Float(string='Chi phí tối đa')
    
    # Quy trình phê duyệt
    approval_step_ids = fields.One2many('training.approval.step', 'config_id', string='Các bước phê duyệt')
    
    active = fields.Boolean(string='Kích hoạt', default=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    @api.model
    def get_approval_config(self, enrollment):
        """Lấy cấu hình phê duyệt phù hợp cho đăng ký"""
        domain = [('active', '=', True)]
        
        # Lọc theo danh mục
        if enrollment.course_id.category_id:
            domain.append(('course_category_ids', 'in', enrollment.course_id.category_id.ids))
        
        # Lọc theo thời lượng
        if enrollment.course_id.duration:
            domain.append('|')
            domain.append(('min_duration', '<=', enrollment.course_id.duration))
            domain.append(('min_duration', '=', False))
            domain.append('|')
            domain.append(('max_duration', '>=', enrollment.course_id.duration))
            domain.append(('max_duration', '=', False))
        
        configs = self.search(domain, order='sequence', limit=1)
        return configs[0] if configs else False


class TrainingApprovalStep(models.Model):
    _name = 'training.approval.step'
    _description = 'Training Approval Step'
    _order = 'sequence'

    name = fields.Char(string='Tên bước', required=True)
    sequence = fields.Integer(string='Thứ tự', required=True, default=10)
    
    config_id = fields.Many2one('training.approval.config', string='Cấu hình', required=True, ondelete='cascade')
    
    # Người phê duyệt
    approver_type = fields.Selection([
        ('manager', 'Quản lý trực tiếp'),
        ('hr_manager', 'HR Manager'),
        ('training_manager', 'Training Manager'),
        ('director', 'Giám đốc'),
        ('specific_user', 'Người dùng cụ thể'),
    ], string='Loại người phê duyệt', required=True, default='manager')
    
    user_id = fields.Many2one('res.users', string='Người dùng cụ thể')
    
    # Cài đặt
    can_edit = fields.Boolean(string='Cho phép chỉnh sửa', default=False)
    required_note = fields.Boolean(string='Bắt buộc ghi chú', default=False)
    
    company_id = fields.Many2one('res.company', string='Công ty', related='config_id.company_id', store=True)


class TrainingApproval(models.Model):
    _name = 'training.approval'
    _description = 'Training Approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Tên', compute='_compute_name', store=True)
    
    enrollment_id = fields.Many2one('training.enrollment', string='Đăng ký', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', related='enrollment_id.employee_id', store=True)
    course_id = fields.Many2one('training.course', string='Khóa học', related='enrollment_id.course_id', store=True)
    
    # Workflow
    config_id = fields.Many2one('training.approval.config', string='Cấu hình phê duyệt')
    approval_line_ids = fields.One2many('training.approval.line', 'approval_id', string='Chi tiết phê duyệt')
    current_step_id = fields.Many2one('training.approval.line', string='Bước hiện tại', compute='_compute_current_step', store=True)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('pending', 'Chờ phê duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    
    # Thông tin
    request_date = fields.Datetime(string='Ngày yêu cầu', default=fields.Datetime.now, tracking=True)
    approval_date = fields.Datetime(string='Ngày phê duyệt', readonly=True, tracking=True)
    rejection_date = fields.Datetime(string='Ngày từ chối', readonly=True, tracking=True)
    
    notes = fields.Text(string='Ghi chú')
    rejection_reason = fields.Text(string='Lý do từ chối', tracking=True)
    
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    @api.depends('enrollment_id', 'employee_id', 'course_id')
    def _compute_name(self):
        for record in self:
            if record.employee_id and record.course_id:
                record.name = f"Phê duyệt: {record.employee_id.name} - {record.course_id.name}"
            else:
                record.name = "Phê duyệt đào tạo"
    
    @api.depends('approval_line_ids.state')
    def _compute_current_step(self):
        for record in self:
            pending_line = record.approval_line_ids.filtered(lambda l: l.state == 'pending')
            record.current_step_id = pending_line[0] if pending_line else False
    
    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo các bước phê duyệt khi tạo approval"""
        approvals = super().create(vals_list)
        for approval in approvals:
            approval._create_approval_lines()
        return approvals
    
    def _create_approval_lines(self):
        """Tạo các bước phê duyệt theo config"""
        self.ensure_one()
        
        # Lấy config phê duyệt
        config = self.env['training.approval.config'].get_approval_config(self.enrollment_id)
        if not config:
            raise UserError(_('Không tìm thấy cấu hình phê duyệt phù hợp cho khóa học này.'))
        
        self.config_id = config
        
        # Tạo approval lines
        for step in config.approval_step_ids.sorted('sequence'):
            approver = self._get_approver_for_step(step)
            if approver:
                self.env['training.approval.line'].create({
                    'approval_id': self.id,
                    'step_id': step.id,
                    'sequence': step.sequence,
                    'approver_id': approver.id,
                    'state': 'pending' if step.sequence == config.approval_step_ids[0].sequence else 'waiting',
                })
    
    def _get_approver_for_step(self, step):
        """Lấy người phê duyệt cho bước"""
        self.ensure_one()
        
        if step.approver_type == 'manager':
            return self.employee_id.parent_id.user_id if self.employee_id.parent_id else False
        elif step.approver_type == 'hr_manager':
            hr_manager_group = self.env.ref('hr.group_hr_manager', raise_if_not_found=False)
            if hr_manager_group:
                return hr_manager_group.users[0] if hr_manager_group.users else False
        elif step.approver_type == 'training_manager':
            training_manager_group = self.env.ref('training_management.group_training_manager', raise_if_not_found=False)
            if training_manager_group:
                return training_manager_group.users[0] if training_manager_group.users else False
        elif step.approver_type == 'director':
            # Tìm CEO/Director
            ceo = self.env['hr.employee'].search([('job_id.name', 'ilike', 'director')], limit=1)
            return ceo.user_id if ceo else False
        elif step.approver_type == 'specific_user':
            return step.user_id
        
        return False
    
    def action_submit(self):
        """Gửi yêu cầu phê duyệt"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Chỉ có thể gửi yêu cầu ở trạng thái Nháp.'))
            
            record.write({
                'state': 'pending',
                'request_date': fields.Datetime.now(),
            })
            
            # Gửi thông báo cho người phê duyệt đầu tiên
            if record.current_step_id:
                record.current_step_id._send_approval_notification()
    
    def action_cancel(self):
        """Hủy yêu cầu"""
        for record in self:
            if record.state in ['approved', 'rejected']:
                raise UserError(_('Không thể hủy yêu cầu đã được phê duyệt hoặc từ chối.'))
            
            record.write({'state': 'cancelled'})
            record.approval_line_ids.write({'state': 'cancelled'})
    
    def action_reset_to_draft(self):
        """Đặt lại về nháp"""
        for record in self:
            if record.state not in ['cancelled', 'rejected']:
                raise UserError(_('Chỉ có thể đặt lại yêu cầu đã hủy hoặc từ chối.'))
            
            record.write({'state': 'draft'})
            record.approval_line_ids.write({'state': 'waiting'})
            
            # Reset bước đầu tiên về pending
            first_line = record.approval_line_ids.sorted('sequence')[0]
            if first_line:
                first_line.write({'state': 'pending'})


class TrainingApprovalLine(models.Model):
    _name = 'training.approval.line'
    _description = 'Training Approval Line'
    _order = 'sequence'

    approval_id = fields.Many2one('training.approval', string='Phê duyệt', required=True, ondelete='cascade')
    step_id = fields.Many2one('training.approval.step', string='Bước', required=True)
    sequence = fields.Integer(string='Thứ tự', required=True)
    
    approver_id = fields.Many2one('res.users', string='Người phê duyệt', required=True)
    
    state = fields.Selection([
        ('waiting', 'Chờ'),
        ('pending', 'Đang chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='waiting', required=True)
    
    approval_date = fields.Datetime(string='Ngày phê duyệt', readonly=True)
    rejection_date = fields.Datetime(string='Ngày từ chối', readonly=True)
    
    notes = fields.Text(string='Ghi chú')
    rejection_reason = fields.Text(string='Lý do từ chối')
    
    company_id = fields.Many2one('res.company', string='Công ty', related='approval_id.company_id', store=True)
    
    def action_approve(self):
        """Phê duyệt bước"""
        for record in self:
            if record.state != 'pending':
                raise UserError(_('Chỉ có thể phê duyệt bước đang chờ duyệt.'))
            
            if record.approver_id != self.env.user:
                raise UserError(_('Bạn không có quyền phê duyệt bước này.'))
            
            record.write({
                'state': 'approved',
                'approval_date': fields.Datetime.now(),
            })
            
            # Chuyển sang bước tiếp theo hoặc hoàn thành
            record._process_next_step()
    
    def action_reject(self):
        """Từ chối"""
        for record in self:
            if record.state != 'pending':
                raise UserError(_('Chỉ có thể từ chối bước đang chờ duyệt.'))
            
            if record.approver_id != self.env.user:
                raise UserError(_('Bạn không có quyền từ chối bước này.'))
            
            # Mở wizard để nhập lý do
            return {
                'name': _('Lý do từ chối'),
                'type': 'ir.actions.act_window',
                'res_model': 'training.approval.rejection.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_approval_line_id': record.id,
                },
            }
    
    def _process_rejection(self, reason):
        """Xử lý từ chối"""
        self.ensure_one()
        
        self.write({
            'state': 'rejected',
            'rejection_date': fields.Datetime.now(),
            'rejection_reason': reason,
        })
        
        # Cập nhật trạng thái approval
        self.approval_id.write({
            'state': 'rejected',
            'rejection_date': fields.Datetime.now(),
            'rejection_reason': reason,
        })
        
        # Cập nhật enrollment
        self.approval_id.enrollment_id.write({'state': 'refused'})
        
        # Gửi thông báo
        self._send_rejection_notification(reason)
    
    def _process_next_step(self):
        """Xử lý bước tiếp theo"""
        self.ensure_one()
        
        # Tìm bước tiếp theo
        next_line = self.approval_id.approval_line_ids.filtered(
            lambda l: l.sequence > self.sequence and l.state == 'waiting'
        ).sorted('sequence')
        
        if next_line:
            # Chuyển sang bước tiếp theo
            next_line[0].write({'state': 'pending'})
            next_line[0]._send_approval_notification()
        else:
            # Hoàn thành phê duyệt
            self.approval_id.write({
                'state': 'approved',
                'approval_date': fields.Datetime.now(),
            })
            
            # Cập nhật enrollment
            self.approval_id.enrollment_id.write({'state': 'confirmed'})
            
            # Gửi thông báo hoàn thành
            self._send_completion_notification()
    
    def _send_approval_notification(self):
        """Gửi thông báo yêu cầu phê duyệt"""
        self.ensure_one()
        
        template = self.env.ref('training_management.email_template_approval_request', raise_if_not_found=False)
        if template and self.approver_id.email:
            template.send_mail(self.id, force_send=True)
        
        # Tạo activity
        self.approval_id.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=self.approver_id.id,
            summary=f'Phê duyệt đào tạo: {self.approval_id.course_id.name}',
        )
    
    def _send_rejection_notification(self, reason):
        """Gửi thông báo từ chối"""
        self.ensure_one()
        
        template = self.env.ref('training_management.email_template_approval_rejected', raise_if_not_found=False)
        if template:
            template.send_mail(self.approval_id.id, force_send=True)
    
    def _send_completion_notification(self):
        """Gửi thông báo hoàn thành phê duyệt"""
        self.ensure_one()
        
        template = self.env.ref('training_management.email_template_approval_approved', raise_if_not_found=False)
        if template:
            template.send_mail(self.approval_id.id, force_send=True)


class TrainingEnrollmentApproval(models.Model):
    _inherit = 'training.enrollment'

    approval_id = fields.Many2one('training.approval', string='Phê duyệt', readonly=True)
    approval_state = fields.Selection(related='approval_id.state', string='Trạng thái phê duyệt', store=True)
    
    def action_submit_approval(self):
        """Gửi yêu cầu phê duyệt"""
        for record in self:
            if record.approval_id:
                raise UserError(_('Yêu cầu phê duyệt đã tồn tại.'))
            
            # Tạo approval
            approval = self.env['training.approval'].create({
                'enrollment_id': record.id,
            })
            
            record.approval_id = approval
            
            # Gửi phê duyệt
            approval.action_submit()
    
    def action_view_approval(self):
        """Xem chi tiết phê duyệt"""
        self.ensure_one()
        return {
            'name': _('Phê duyệt đào tạo'),
            'type': 'ir.actions.act_window',
            'res_model': 'training.approval',
            'res_id': self.approval_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
