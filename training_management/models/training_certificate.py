# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import qrcode
from io import BytesIO
from datetime import datetime, timedelta


class TrainingCertificate(models.Model):
    _name = 'training.certificate'
    _description = 'Chứng chỉ đào tạo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'issue_date desc'

    name = fields.Char(string='Số chứng chỉ', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Học viên', required=True, tracking=True)
    course_id = fields.Many2one('training.course', string='Khóa học', required=True, tracking=True)
    enrollment_id = fields.Many2one('training.enrollment', string='Đăng ký')
    test_result_id = fields.Many2one('training.test.result', string='Kết quả thi')
    
    # Thông tin chứng chỉ
    issue_date = fields.Date(string='Ngày cấp', default=fields.Date.today, tracking=True)
    expiry_date = fields.Date(string='Ngày hết hạn')
    valid_years = fields.Integer(string='Hiệu lực (năm)', default=0, help="0 = Vô thời hạn")
    is_expired = fields.Boolean(string='Hết hạn', compute='_compute_is_expired')
    
    # Điểm số
    test_score = fields.Float(string='Điểm thi (%)')
    grade = fields.Selection([
        ('excellent', 'Xuất sắc'),
        ('good', 'Giỏi'),
        ('average', 'Khá'),
        ('pass', 'Đạt'),
    ], string='Xếp loại', compute='_compute_grade', store=True)
    
    # Template và file
    template_id = fields.Many2one('training.certificate.template', string='Mẫu chứng chỉ')
    certificate_html = fields.Html(string='Nội dung chứng chỉ', compute='_compute_certificate_html')
    attachment_id = fields.Many2one('ir.attachment', string='File PDF')
    
    # QR Code
    qr_code = fields.Binary(string='QR Code', compute='_compute_qr_code', store=True)
    verification_url = fields.Char(string='Link xác thực', compute='_compute_verification_url')
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('issued', 'Đã cấp'),
        ('revoked', 'Thu hồi')
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    
    revoke_reason = fields.Text(string='Lý do thu hồi')
    revoke_date = fields.Date(string='Ngày thu hồi')
    
    # Chữ ký
    signed_by = fields.Many2one('res.users', string='Người ký')
    signature = fields.Binary(string='Chữ ký')
    
    # Email
    email_sent = fields.Boolean(string='Đã gửi email', default=False)
    email_sent_date = fields.Datetime(string='Ngày gửi email')
    
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('training.certificate') or _('New')
            
            # Tính expiry_date nếu có valid_years
            if vals.get('valid_years', 0) > 0:
                issue_date = vals.get('issue_date', fields.Date.today())
                if isinstance(issue_date, str):
                    issue_date = fields.Date.from_string(issue_date)
                vals['expiry_date'] = issue_date + timedelta(days=365 * vals['valid_years'])
        
        return super(TrainingCertificate, self).create(vals_list)
    
    def write(self, vals):
        # Cập nhật expiry_date khi thay đổi valid_years hoặc issue_date
        if 'valid_years' in vals or 'issue_date' in vals:
            for record in self:
                valid_years = vals.get('valid_years', record.valid_years)
                if valid_years > 0:
                    issue_date = vals.get('issue_date', record.issue_date)
                    if isinstance(issue_date, str):
                        issue_date = fields.Date.from_string(issue_date)
                    vals['expiry_date'] = issue_date + timedelta(days=365 * valid_years)
        
        return super(TrainingCertificate, self).write(vals)
    
    @api.depends('expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for record in self:
            record.is_expired = record.expiry_date and record.expiry_date < today
    
    @api.depends('test_score')
    def _compute_grade(self):
        for record in self:
            if record.test_score >= 90:
                record.grade = 'excellent'
            elif record.test_score >= 80:
                record.grade = 'good'
            elif record.test_score >= 70:
                record.grade = 'average'
            else:
                record.grade = 'pass'
    
    @api.depends('name')
    def _compute_verification_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.name and record.name != 'New':
                record.verification_url = f"{base_url}/certificate/verify/{record.name}"
            else:
                record.verification_url = False
    
    @api.depends('verification_url')
    def _compute_qr_code(self):
        for record in self:
            if record.verification_url:
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(record.verification_url)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                record.qr_code = base64.b64encode(buffer.getvalue())
            else:
                record.qr_code = False
    
    @api.depends('template_id', 'employee_id', 'course_id', 'issue_date', 'test_score')
    def _compute_certificate_html(self):
        for record in self:
            if record.template_id and record.template_id.layout:
                html = record.template_id.layout
                
                # Replace placeholders
                html = html.replace('{employee_name}', record.employee_id.name or '')
                html = html.replace('{course_name}', record.course_id.name or '')
                html = html.replace('{certificate_number}', record.name or '')
                html = html.replace('{issue_date}', record.issue_date.strftime('%d/%m/%Y') if record.issue_date else '')
                html = html.replace('{expiry_date}', record.expiry_date.strftime('%d/%m/%Y') if record.expiry_date else 'Vô thời hạn')
                html = html.replace('{test_score}', f"{record.test_score:.1f}" if record.test_score else '')
                html = html.replace('{grade}', dict(record._fields['grade'].selection).get(record.grade, '') if record.grade else '')
                html = html.replace('{company_name}', record.company_id.name or '')
                
                # Add QR code
                if record.qr_code:
                    qr_img = f'<img src="data:image/png;base64,{record.qr_code.decode()}" style="width: 100px; height: 100px;"/>'
                    html = html.replace('{qr_code}', qr_img)
                
                record.certificate_html = html
            else:
                record.certificate_html = False
    
    def action_issue(self):
        """Cấp chứng chỉ"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Chỉ có thể cấp chứng chỉ ở trạng thái Nháp!'))
            
            record.write({
                'state': 'issued',
                'signed_by': self.env.user.id,
            })
            
            # Tạo PDF
            record._generate_pdf()
    
    def action_revoke(self):
        """Thu hồi chứng chỉ"""
        return {
            'name': _('Thu hồi chứng chỉ'),
            'type': 'ir.actions.act_window',
            'res_model': 'training.certificate.revoke.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_certificate_id': self.id,
            },
        }
    
    def _revoke(self, reason):
        """Thu hồi chứng chỉ với lý do"""
        self.ensure_one()
        
        if self.state != 'issued':
            raise UserError(_('Chỉ có thể thu hồi chứng chỉ đã cấp!'))
        
        self.write({
            'state': 'revoked',
            'revoke_reason': reason,
            'revoke_date': fields.Date.today(),
        })
    
    def action_send_email(self):
        """Gửi email chứng chỉ"""
        for record in self:
            if record.state != 'issued':
                raise UserError(_('Chỉ có thể gửi chứng chỉ đã cấp!'))
            
            if not record.employee_id.work_email:
                raise UserError(_('Nhân viên chưa có email!'))
            
            template = self.env.ref('training_management.email_template_certificate', raise_if_not_found=False)
            if template:
                template.send_mail(record.id, force_send=True)
                record.write({
                    'email_sent': True,
                    'email_sent_date': fields.Datetime.now(),
                })
    
    def _generate_pdf(self):
        """Tạo file PDF chứng chỉ"""
        self.ensure_one()
        
        if not self.certificate_html:
            return
        
        # Generate PDF from HTML
        pdf_content = self.env['ir.actions.report']._render_qweb_pdf(
            'training_management.report_training_certificate',
            self.id,
            data={'html': self.certificate_html}
        )[0]
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'Certificate_{self.name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })
        
        self.attachment_id = attachment.id
    
    def action_download_certificate(self):
        """Tải chứng chỉ"""
        self.ensure_one()
        
        if not self.attachment_id:
            raise UserError(_('Chưa có file chứng chỉ!'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self.attachment_id.id}?download=true',
            'target': 'self',
        }
    
    def action_print_certificate(self):
        """In chứng chỉ"""
        self.ensure_one()
        return self.env.ref('training_management.action_report_training_certificate').report_action(self)


class TrainingCertificateTemplate(models.Model):
    _name = 'training.certificate.template'
    _description = 'Mẫu chứng chỉ'
    _order = 'name'

    name = fields.Char(string='Tên mẫu', required=True)
    description = fields.Text(string='Mô tả')
    layout = fields.Html(string='Bố cục', help="""
        Các biến có thể dùng:
        - {employee_name}: Tên học viên
        - {course_name}: Tên khóa học
        - {certificate_number}: Số chứng chỉ
        - {issue_date}: Ngày cấp
        - {expiry_date}: Ngày hết hạn
        - {test_score}: Điểm thi
        - {grade}: Xếp loại
        - {company_name}: Tên công ty
        - {qr_code}: Mã QR
    """)
    
    # Preview
    preview_image = fields.Binary(string='Hình ảnh mẫu')
    
    # Settings
    orientation = fields.Selection([
        ('portrait', 'Dọc'),
        ('landscape', 'Ngang')
    ], string='Hướng giấy', default='landscape')
    
    paper_size = fields.Selection([
        ('A4', 'A4'),
        ('A5', 'A5'),
        ('Letter', 'Letter')
    ], string='Kích thước giấy', default='A4')
    
    active = fields.Boolean(string='Hoạt động', default=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
