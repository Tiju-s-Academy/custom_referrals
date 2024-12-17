{
    'name': 'Referrals',
    'version': '17.0.1.0.0',
    'summary': 'This Apps for students Referrals',
    'author': 'Tijus Academy',
    'depends': ['base', 'web', 'mail', 'crm','product'],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/new_referral_view.xml',
        'views/referrals_menu.xml',
    ],

    'application': True,
    'license': 'LGPL-3',
}