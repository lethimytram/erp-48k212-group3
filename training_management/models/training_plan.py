# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TrainingPlan(models.Model):
    _name = 'training.plan'
    _description = 'Kế hoạch đào tạo tổng thể'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year desc, create_date desc'

    name = fields.Char(string='Tên kế hoạch', required=True, tracking=True, default=lambda self: _('Kế hoạch đào tạo năm %s') % fields.Date.today().year)
    year = fields.Char(string='Năm tài chính', required=True, default=lambda self: str(fields.Date.today().year), size=4)
    
    # Phạm vi áp dụng
    department_id = fields.Many2one('hr.department', string='Phòng ban/Khu vực', help="Để trống nếu áp dụng toàn công ty")
    responsible_id = fields.Many2one('res.users', string='Người lập', default=lambda self: self.env.user)
    
    # Chi tiết kế hoạch (Quan trọng)
    line_ids = fields.One2many('training.plan.line', 'plan_id', string='Chi tiết các hạng mục')
    
    # Tổng hợp ngân sách & Chỉ số
    total_budget = fields.Float(string='Tổng ngân sách dự kiến', compute='_compute_totals', store=True)
    total_courses = fields.Integer(string='Số lượng khóa học', compute='_compute_totals', store=True)
    
    start_date = fields.Date(string='Bắt đầu', required=True, default=fields.Date.today)
    end_date = fields.Date(string='Kết thúc', required=True)

    # Tích hợp phê duyệt (TODO: Implement approval workflow)
    # approval_id = fields.Many2one('training.approval', string='Yêu cầu phê duyệt', readonly=True, copy=False)
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('waiting', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('in_progress', 'Đang triển khai'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy bỏ')
    ], string='Trạng thái', default='draft', required=True, tracking=True, group_expand='_expand_states')
    
    description = fields.Html(string='Ghi chú/Mục tiêu chiến lược')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', related='company_id.currency_id', readonly=True)

    @api.model
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.depends('line_ids.budget', 'line_ids')
    def _compute_totals(self):
        for record in self:
            record.total_budget = sum(record.line_ids.mapped('budget'))
            record.total_courses = len(record.line_ids)

    # --- ACTION WORKFLOW ---
    def action_submit(self):
        """Gửi kế hoạch đi duyệt"""
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_('Vui lòng thêm ít nhất một hạng mục đào tạo trước khi gửi duyệt.'))
            
        # TODO: Implement approval workflow
        # Auto approve for now
        self.state = 'approved'
        
        # # Tìm quy trình duyệt cho Kế hoạch
        # flow = self.env['training.approval.flow'].search([
        #     ('model_id.model', '=', self._name), ('active', '=', True)
        # ], limit=1)

        # if not flow:
        #     self.state = 'approved' # Auto approve if no flow
        #     return

        # # Tạo Approval
        # approval = self.env['training.approval'].create({
        #     'name': f"Duyệt kế hoạch: {self.name}",
        #     'flow_id': flow.id,
        #     'employee_id': self.env.user.employee_id.id,
        #     'res_model': self._name,
        #     'res_id': self.id,
        # })
        # self.write({'approval_id': approval.id, 'state': 'waiting'})
        # approval.action_submit()

    def action_approve(self):
        """Callback: Sếp duyệt -> Kế hoạch sẵn sàng triển khai"""
        self.write({'state': 'in_progress'})

    def action_reject(self):
        """Callback: Sếp từ chối"""
        self.write({'state': 'draft'}) # Quay về nháp để sửa lại

class TrainingPlanLine(models.Model):
    _name = 'training.plan.line'
    _description = 'Chi tiết hạng mục kế hoạch'

    plan_id = fields.Many2one('training.plan', string='Kế hoạch', required=True, ondelete='cascade')
    course_id = fields.Many2one('training.course', string='Khóa học', required=True)
    
    # Định lượng
    trainee_count = fields.Integer(string='Số lượng học viên dự kiến', default=10)
    period = fields.Selection([
        ('q1', 'Quý 1'), ('q2', 'Quý 2'), ('q3', 'Quý 3'), ('q4', 'Quý 4'),
        ('month', 'Hàng tháng'), ('adhoc', 'Đột xuất')
    ], string='Thời gian triển khai', default='adhoc', required=True)
    
    budget = fields.Float(string='Ngân sách dự trù')
    notes = fields.Char(string='Ghi chú')