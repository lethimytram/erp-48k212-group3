# -*- coding: utf-8 -*-
{
    'name': 'Training Management',
    'version': '18.0.1.0.1',
    'category': 'Human Resources',
    'summary': 'Module Đào tạo nội bộ cho nhân viên',
    'description': """
        Module quản lý đào tạo nội bộ
        ================================
        * Quản lý khóa học và tài liệu
        * Quản lý giảng viên và học viên
        * Lập kế hoạch đào tạo
        * Đăng ký và phê duyệt khóa học
        * Tích hợp lịch đào tạo
        * Đánh giá và cấp chứng chỉ
        * Khảo sát hài lòng
    """,
    'author': 'Nhóm 3 (Mỹ Trâm, Kim Cương, Thu Hà, Tố Như, Trọng Khang)',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'hr',
        'mail',
        'calendar',
        'survey',
        'hr_skills',
    ],
    'data': [
        'security/training_security.xml',
        'security/ir.model.access.csv',
        'data/training_data.xml',
        'data/training_reminder_data.xml',
        'data/training_approval_data.xml',
        'data/training_test_data.xml',
        'wizard/training_approval_rejection_wizard_views.xml',
        'wizard/training_test_grading_wizard_views.xml',
        'wizard/training_certificate_revoke_wizard_views.xml',
        'reports/training_certificate_report.xml',
        'views/training_course_views.xml',
        'views/training_trainer_views.xml',
        'views/training_material_views.xml',
        'views/training_plan_views.xml',
        'views/training_need_views.xml',
        'views/training_enrollment_views.xml',
        'views/training_session_views.xml',
        'views/training_test_views.xml',
        'views/training_certificate_views.xml',
        'views/training_feedback_views.xml',
        'views/training_reminder_views.xml',
        'views/training_approval_views.xml',
        'views/training_menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
