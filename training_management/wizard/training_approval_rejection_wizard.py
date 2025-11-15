# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrainingApprovalRejectionWizard(models.TransientModel):
    _name = 'training.approval.rejection.wizard'
    _description = 'Training Approval Rejection Wizard'

    approval_line_id = fields.Many2one('training.approval.line', string='Bước phê duyệt', required=True)
    rejection_reason = fields.Text(string='Lý do từ chối', required=True)

    @api.constrains('rejection_reason')
    def _check_rejection_reason(self):
        for record in self:
            if not record.rejection_reason or len(record.rejection_reason.strip()) < 10:
                raise ValidationError(_('Lý do từ chối phải có ít nhất 10 ký tự.'))

    def action_confirm_rejection(self):
        """Xác nhận từ chối"""
        self.ensure_one()
        self.approval_line_id._process_rejection(self.rejection_reason)
        return {'type': 'ir.actions.act_window_close'}
