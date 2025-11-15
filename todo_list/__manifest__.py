# __manifest__.py
{
    'name': 'Todo List Custom Module',
    'version': '1.0',
    'summary': 'Simple To-Do List Module',
    'author': 'Lê Thị Mỹ Trâm - 48K21.2',
    'category': 'ThucHanhERP',
    'depends': ['base'],
    'data': [
        'views/todo_task_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}