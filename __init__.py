from . import models

def post_init_hook(cr, registry):
    """Create UTM source if it doesn't exist"""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    source_vals = [
        {'name': 'Online SBU Referral'},
        {'name': 'Organic Media Leads'}
    ]
    
    for vals in source_vals:
        existing_source = env['utm.source'].search([('name', '=', vals['name'])], limit=1)
        if not existing_source:
            env['utm.source'].create(vals)
