# -*- coding: utf-8 -*-
# TODO: Implement approval workflow models first
# This wizard depends on training.approval and training.approval.line models

# from odoo import models, fields, api, _
# from odoo.exceptions import ValidationError

# class TrainingApprovalRejectionWizard(models.TransientModel):
#     _name = 'training.approval.rejection.wizard'
#     _description = 'Wizard từ chối phê duyệt'

#     approval_line_id = fields.Many2one('training.approval.line', string='Bước phê duyệt', required=True, readonly=True)
#     rejection_reason = fields.Text(string='Lý do từ chối', required=True, help="Vui lòng nhập lý do cụ thể để người gửi nắm thông tin.")

#     @api.model
#     def default_get(self, fields_list):
#         """Tự động lấy ID của dòng phê duyệt đang chọn"""
#         res = super(TrainingApprovalRejectionWizard, self).default_get(fields_list)
#         if self.env.context.get('active_model') == 'training.approval.line' and self.env.context.get('active_id'):
#             res['approval_line_id'] = self.env.context.get('active_id')
#         return res

#     @api.constrains('rejection_reason')
#     def _check_rejection_reason(self):
#         for record in self:
#             if not record.rejection_reason or len(record.rejection_reason.strip()) < 10:
#                 raise ValidationError(_('Lý do từ chối phải có ít nhất 10 ký tự để đảm bảo tính minh bạch.'))

#     def action_confirm_rejection(self):
#         """Xác nhận từ chối"""
#         self.ensure_one()
#         # Gọi hàm xử lý từ chối bên model chính
#         self.approval_line_id._process_rejection(self.rejection_reason)
#         
#         # Đóng wizard và reload lại giao diện
#         return {
#             'type': 'ir.actions.act_window_close',
#             'infos': {'type': 'reload'}
#         }