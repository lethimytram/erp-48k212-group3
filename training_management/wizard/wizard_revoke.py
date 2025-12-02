# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrainingCertificateRevokeWizard(models.TransientModel):
    _name = 'training.certificate.revoke.wizard'
    _description = 'Wizard thu hồi chứng chỉ'

    certificate_id = fields.Many2one('training.certificate', string='Chứng chỉ', required=True, readonly=True)
    revoke_reason = fields.Text(string='Lý do thu hồi', required=True, help="Vui lòng nhập lý do chi tiết (VD: Vi phạm kỷ luật, Nghỉ việc,...)")
    
    @api.constrains('revoke_reason')
    def _check_revoke_reason(self):
        for record in self:
            if not record.revoke_reason or len(record.revoke_reason.strip()) < 10:
                raise ValidationError(_('Lý do thu hồi phải có ít nhất 10 ký tự để đảm bảo tính minh bạch.'))
    
    def action_confirm_revoke(self):
        """Xác nhận thu hồi"""
        self.ensure_one()
        # Gọi hàm _revoke bên model chính để xử lý logic
        self.certificate_id._revoke(self.revoke_reason)
        
        # Đóng popup và reload lại giao diện
        return {
            'type': 'ir.actions.act_window_close',
            'infos': {
                'type': 'reload', # Reload để cập nhật trạng thái trên form chính
            }
        }