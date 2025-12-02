# -*- coding: utf-8 -*-
{
    'name': 'Highlands Training',
    'version': '1.0',
    'category': 'ThucHanhERP',
    'summary': 'Module Đào tạo nội bộ Highlands',
    'description': """
        Hệ thống quản lý đào tạo nội bộ theo mô hình Blended Learning.
        Tính năng chính:
        - Quản lý Khóa học (SOP) & Tài liệu
        - Quản lý Hồ sơ Giảng viên (Tích hợp HR)
        - Lập Kế hoạch & Ngân sách đào tạo
        - Quy trình: Đăng ký -> Duyệt -> Học (E-learning) -> Thi Lý thuyết -> Thi Thực hành -> Cấp chứng chỉ
        - Tích hợp Lịch & Nhắc nhở tự động
        - Báo cáo & Đánh giá chất lượng
    """,
    'author': 'Nhóm 3 (Mỹ Trâm, Kim Cương, Thu Hà, Tố Như, Trọng Khang)',
    'website': 'https://www.highlandscoffee.com.vn/',
    'depends': [
        'base',
        'hr',          # Để kế thừa nhân viên
        'mail',        # Chat & Activity
        'calendar',    # Lịch đào tạo
        'web',         # Giao diện
    ],
    'data': [
        # 1. Security & Access Rights (Load đầu tiên)
        'security/training_security.xml',
        'security/ir.model.access.csv',

        # 2. Master Data (Dữ liệu nền)
        'data/training_data.xml',
        'data/training_reminder_data.xml',
        # TODO: Uncomment when approval workflow is implemented
        # 'data/training_approval_data.xml',
        'data/training_test_data.xml',

        # 3. Wizards (Popup)
        # TODO: Uncomment when approval workflow is implemented
        # 'wizard/wizard_rejection_views.xml',  # Thay vì training_approval_rejection...
        # TODO: Fix view validation error for grading wizard
        # 'wizard/wizard_grading_views.xml',    # Thay vì training_test_grading...
        'wizard/wizard_revoke_views.xml',

        # 4. Reports (Mẫu in)
        'reports/training_certificate_report.xml',

        # 5. Views (Giao diện)
        'views/training_course_views.xml',
        # TODO: Fix trainer view - missing is_trainer field
        # 'views/training_trainer_views.xml',
        'views/training_material_views.xml',
        'views/training_plan_views.xml',
        'views/training_need_views.xml',
        # TODO: Fix enrollment view - field validation issues
        # 'views/training_enrollment_views.xml',
        'views/training_session_views.xml',
        'views/training_quiz_views.xml',      
        'views/training_certificate_views.xml',
        'views/training_feedback_views.xml',
        'views/training_reminder_views.xml',
        # TODO: Uncomment when approval workflow is implemented
        # 'views/training_approval_views.xml',

        # 6. Menus (Load cuối cùng để đảm bảo action đã tồn tại)
        'views/training_menu_views.xml',
    ],
    'assets': {
        # Nếu có CSS/JS tùy chỉnh cho Odoo 18 thì khai báo ở đây
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}