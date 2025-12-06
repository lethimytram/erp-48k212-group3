# -*- coding: utf-8 -*-
{
    'name': 'Highland Training',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Hệ thống đào tạo nội bộ Highland - Blended Learning',
    'description': """
        Hệ thống quản lý đào tạo nội bộ theo mô hình Blended Learning
        - Quản lý khóa học và nội dung đào tạo
        - Sát hạch lý thuyết trực tuyến
        - Đánh giá thực hành tại chỗ
        - Cấp chứng nhận tự động
        - Báo cáo và theo dõi tiến độ
    """,
    'author': 'Highland Coffee',
    'website': 'https://highlandscoffee.com.vn',
    'depends': ['base', 'hr', 'web'],
    'data': [
        # Security - Groups first
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/sequence.xml',
        'data/default_user_access.xml',
        
        # Views - Admin
        'views/course_views.xml',
        'views/content_views.xml',
        'views/question_views.xml',
        'views/checklist_views.xml',
        'views/training_request_views.xml',
        'views/training_plan_views.xml',
        'views/enrollment_views.xml',
        'views/exam_views.xml',
        'views/certificate_views.xml',
        'views/report_views.xml',
        
        # Views - Manager
        'views/manager_views.xml',
        
        # Menu
        'views/menu.xml',
        
        # Security - Record Rules (after models loaded)
        'security/rules.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
