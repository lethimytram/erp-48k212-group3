# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError

class TrainingPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'training_count' in counters:
            values['training_count'] = request.env['training.enrollment'].search_count([
                ('employee_id.user_id', '=', request.env.user.id)
            ])
        return values

    @http.route(['/my/trainings', '/my/trainings/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_trainings(self, page=1, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        Enrollment = request.env['training.enrollment']

        domain = [('employee_id.user_id', '=', request.env.user.id)]

        # Sorting
        searchbar_sortings = {
            'date': {'label': _('Ngày đăng ký'), 'order': 'enroll_date desc'},
            'name': {'label': _('Mã'), 'order': 'name'},
            'course': {'label': _('Khóa học'), 'order': 'course_id'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Filtering
        searchbar_filters = {
            'all': {'label': _('Tất cả'), 'domain': []},
            'learning': {'label': _('Đang học'), 'domain': [('state', '=', 'learning')]},
            'completed': {'label': _('Hoàn thành'), 'domain': [('state', '=', 'completed')]},
        }
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # Count
        training_count = Enrollment.search_count(domain)

        # Pager
        pager = portal_pager(
            url="/my/trainings",
            url_args={'sortby': sortby, 'filterby': filterby},
            total=training_count,
            page=page,
            step=self._items_per_page
        )

        # Content
        enrollments = Enrollment.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'enrollments': enrollments,
            'page_name': 'training',
            'pager': pager,
            'default_url': '/my/trainings',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
        })
        return request.render("highland_training.portal_my_trainings", values)

    @http.route(['/my/training/<int:enrollment_id>'], type='http', auth="user", website=True)
    def portal_training_detail(self, enrollment_id, access_token=None, **kw):
        try:
            enrollment_sudo = self._document_check_access('training.enrollment', enrollment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'enrollment': enrollment_sudo,
            'page_name': 'training',
        }
        return request.render("highland_training.portal_training_detail", values)

    @http.route(['/my/exam/<int:exam_id>'], type='http', auth="user", website=True)
    def portal_exam_detail(self, exam_id, access_token=None, **kw):
        try:
            exam_sudo = self._document_check_access('training.exam', exam_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # Check if exam belongs to current user
        if exam_sudo.employee_id.user_id != request.env.user:
            return request.redirect('/my')

        values = {
            'exam': exam_sudo,
            'page_name': 'training',
        }
        return request.render("highland_training.portal_exam_detail", values)

    @http.route(['/my/exam/<int:exam_id>/submit'], type='http', auth="user", website=True, csrf=True)
    def portal_exam_submit(self, exam_id, **post):
        exam = request.env['training.exam'].browse(exam_id)
        
        # Check access
        if exam.employee_id.user_id != request.env.user:
            return request.redirect('/my')
        
        if exam.state != 'in_progress':
            return request.redirect(f'/my/exam/{exam_id}')
        
        # Save answers
        for key, value in post.items():
            if key.startswith('answer_'):
                answer_id = int(key.replace('answer_', ''))
                answer = exam.answer_ids.filtered(lambda a: a.id == answer_id)
                if answer:
                    # Get selected answer IDs from checkbox/radio
                    selected_ids = request.httprequest.form.getlist(key)
                    if selected_ids:
                        answer.selected_answer_ids = [(6, 0, [int(i) for i in selected_ids])]
        
        # Submit exam
        exam.action_submit()
        
        return request.redirect(f'/my/exam/{exam_id}')

    @http.route(['/my/certificates'], type='http', auth="user", website=True)
    def portal_my_certificates(self, **kw):
        values = self._prepare_portal_layout_values()
        Certificate = request.env['training.certificate']

        certificates = Certificate.search([
            ('employee_id.user_id', '=', request.env.user.id)
        ], order='issue_date desc')

        values.update({
            'certificates': certificates,
            'page_name': 'certificate',
        })
        return request.render("highland_training.portal_my_certificates", values)
    
    @http.route(['/my/training/<int:enrollment_id>/start_exam'], type='http', auth="user", website=True, csrf=True, methods=['POST'])
    def portal_start_exam(self, enrollment_id, **kw):
        enrollment = request.env['training.enrollment'].browse(enrollment_id)
        
        # Check access
        if enrollment.employee_id.user_id != request.env.user:
            return request.redirect('/my')
        
        # Start exam
        action = enrollment.action_start_exam()
        if action and 'res_id' in action:
            exam_id = action['res_id']
            exam = request.env['training.exam'].browse(exam_id)
            exam.action_start()
            return request.redirect(f'/my/exam/{exam_id}')
        
        return request.redirect(f'/my/training/{enrollment_id}')
    
    @http.route(['/my/exam/start'], type='http', auth="user", website=True, csrf=True, methods=['POST'])
    def portal_exam_start(self, exam_id, **post):
        exam = request.env['training.exam'].browse(int(exam_id))
        
        # Check access
        if exam.employee_id.user_id != request.env.user:
            return request.redirect('/my')
        
        exam.action_start()
        return request.redirect(f'/my/exam/{exam_id}')
