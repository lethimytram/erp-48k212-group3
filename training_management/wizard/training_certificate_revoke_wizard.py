# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TrainingCertificateRevokeWizard(models.TransientModel):
    _name = 'training.certificate.revoke.wizard'
    _description = 'Wizard thu hồi chứng chỉ'

    certificate_id = fields.Many2one('training.certificate', string='Chứng chỉ', required=True)
    revoke_reason = fields.Text(string='Lý do thu hồi', required=True)
    
    @api.constrains('revoke_reason')
    def _check_revoke_reason(self):
        for record in self:
            if not record.revoke_reason or len(record.revoke_reason.strip()) < 10:
                raise ValidationError(_('Lý do thu hồi phải có ít nhất 10 ký tự.'))
    
    def action_confirm_revoke(self):
        """Xác nhận thu hồi"""
        self.ensure_one()
        self.certificate_id._revoke(self.revoke_reason)
        return {'type': 'ir.actions.act_window_close'}
