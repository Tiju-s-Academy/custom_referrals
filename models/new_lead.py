from odoo import fields,models,api


class NewLead(models.Model):
    _name = 'new.lead'
    _description = 'New Lead'

    name = fields.Char(string='Opportunity', compute='_compute_name', store=True)
    customer_name = fields.Char(string='Customer', required=True)
    phone = fields.Char(string='Phone')
    course_id = fields.Many2one('product.product', string='Course', required=True)
    email = fields.Char(string='Email')
    state = fields.Selection(selection=[('draft', 'Draft'), ('submitted', 'Submitted')], string='State',
                             default='draft', tracking=True)
    location = fields.Char(string='Location')
    user = fields.Many2one('res.users', string='Request Owner', default=lambda self: self.env.user, readonly=True)
