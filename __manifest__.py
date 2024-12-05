{
    'name': 'Referrals',
    'version': '17.0.1.0.0',
    'summary': 'This Apps for students Referrals',
    'author': 'Tijus Academy',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/new_lead_view.xml',
        'views/referrals_menu.xml',
    ],

    'application': True,
    'license': 'LGPL-3',
}