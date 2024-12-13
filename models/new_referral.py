from odoo import http, SUPERUSER_ID
from odoo import fields,models,api
from odoo.exceptions import ValidationError


class NewReferral(models.Model):
    _name = 'new.referral'
    _description = 'New Referral'
    _inherit = 'mail.thread'
    _sql_constraints = [
        ('phone_unique', 'unique(phone)', 'This phone number is already used.'),
        ('email_unique', 'unique(email)', 'This email is already used.'),
    ]

    name = fields.Char(string='Opportunity', compute='_compute_name', store=True)
    customer_name = fields.Char(string='Customer', required=True)
    phone = fields.Char(string='Phone')
    course_id = fields.Many2one('product.product', string='Course', required=True)
    email = fields.Char(string='Email')
    state = fields.Selection(selection=[('draft', 'Draft'), ('submitted', 'Submitted')], string='State',
                             default='draft', tracking=True)
    location = fields.Char(string='Location')
    user = fields.Many2one('res.users', string='Request Owner', default=lambda self: self.env.user, readonly=True)
    salesperson = fields.Many2one('res.users', string='Salesperson')
    lead_id = fields.Many2one('crm.lead', string='Related Lead', readonly=True)  # Link to the related CRM lead

    stage = fields.Char(string='Lead Stage', readonly=True, compute='_compute_stage', store=True)
    last_update = fields.Datetime(string='Last Update', readonly=True, compute='_compute_last_update', store=True)


    @api.depends('customer_name')
    def _compute_name(self):
        for rec in self:
            if rec.customer_name:
                rec.name = f"Referral Lead - {rec.customer_name}"
            else:
                rec.name = "Referral Lead"

    @api.constrains('phone', 'email')
    def _check_phone_email_in_crm_lead(self):
        for record in self:
            # Check for duplicate phone in crm.lead
            if record.phone:
                crm_lead_with_same_phone = self.env['crm.lead'].sudo().search([('phone', '=', record.phone)], limit=1)
                if crm_lead_with_same_phone:
                    raise ValidationError(f"The phone number {record.phone} is already used in CRM Leads.")

            # Check for duplicate email in crm.lead
            if record.email:
                crm_lead_with_same_email = self.env['crm.lead'].sudo().search([('email_from', '=', record.email)], limit=1)
                if crm_lead_with_same_email:
                    raise ValidationError(f"The email address {record.email} is already used in CRM Leads.")

    @api.depends('lead_id.stage_id')
    def _compute_stage(self):
        """Compute the current stage of the associated lead."""
        for rec in self:
            rec.stage = rec.lead_id.stage_id.name if rec.lead_id and rec.lead_id.stage_id else 'Submitted'

    @api.depends('lead_id.write_date')
    def _compute_last_update(self):
        """Compute the last update date."""
        for rec in self:
            rec.last_update = rec.lead_id.write_date

    def action_submit(self):
        team = self.env['crm.team'].sudo().search([('name', '=', 'Sales Team Mavelikkara')], limit=1)
        print("team", team.member_ids)
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.user.id)])
        for record in self:
            superuser = record.env['res.users'].sudo().browse(SUPERUSER_ID)
            partner = self.env['res.partner'].sudo().create({
                'name': record.customer_name,
                'phone': record.phone,
                'email': record.email,
            })
            print("new partner", partner)
            source_id = self.env['utm.source'].sudo().search([('name','=','Employee Referral')])
            lead = self.env['crm.lead'].with_user(superuser).create({
                'name': record.name,
                'partner_id': partner.id,
                'referred_by': employee.id,
                'phone': record.phone,
                'user_id': False,
                'team_id': team.id,
                'course_id': record.course_id.id,
                'city': record.location,
                'email_from': record.email,
                'source_id': source_id.id,

            })
            record.lead_id = lead.id
            record.salesperson = lead.user_id.id
            record.stage = lead.stage_id.name if lead.stage_id else 'Not Assigned'
            record.state = 'submitted'
            return lead












