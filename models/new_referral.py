from odoo import http, SUPERUSER_ID
from odoo import fields,models,api
from odoo.exceptions import ValidationError

class NewReferral(models.Model):
    _name = 'new.referral'
    _description = 'New Referral'
    _inherit = 'mail.thread'

    name = fields.Char(string='Opportunity', compute='_compute_name', store=True)
    customer_name = fields.Char(string='Customer', required=True)
    phone = fields.Char(string='Phone')
    course_id = fields.Many2one('product.product', string='Course', required=True)
    email = fields.Char(string='Email')
    state = fields.Selection(selection=[('draft', 'Draft'), ('submitted', 'Submitted')], string='State',
                             default='draft', tracking=True)
    location = fields.Char(string='Location')
    user = fields.Many2one('res.users', string='Lead By', default=lambda self: self.env.user)
    salesperson = fields.Many2one('res.users', string='Salesperson', compute='_compute_salesperson')
    lead_id = fields.Many2one('crm.lead', string='Related Lead', readonly=True)  # Link to the related CRM lead

    stage = fields.Char(string='Lead Stage', readonly=True, compute='_compute_stage', store=True)
    last_update = fields.Datetime(string='Last Update', readonly=True, compute='_compute_last_update', store=True)
    is_changed_user = fields.Boolean(string='Change user', default=False)

    @api.depends('customer_name')
    def _compute_name(self):
        for rec in self:
            if rec.customer_name:
                rec.name = f"Referral Lead - {rec.customer_name}"
            else:
                rec.name = "Referral Lead"

    @api.constrains('phone')
    def _check_duplicate_phone(self):
        for record in self:
            if record.phone:
                # Search for existing referrals with the same phone number
                existing_referral = self.env['new.referral'].search([
                    ('phone', '=', record.phone),
                    ('id', '!=', record.id)  # Exclude current record
                ], limit=1)
                
                if existing_referral:
                    # Get the employee name who created the original referral
                    creator = existing_referral.user.name
                    raise ValidationError(
                        f"A referral with this phone number already exists! "
                        f"It was created by {creator}."
                    )

    @api.depends('lead_id.stage_id')
    def _compute_stage(self):
        """Compute the current stage of the associated lead."""
        for rec in self:
            # Use sudo to bypass security restrictions if needed
            rec.stage = rec.lead_id.sudo().stage_id.name if rec.lead_id and rec.lead_id.stage_id else 'Not Submitted'

    @api.depends('lead_id.write_date')
    def _compute_last_update(self):
        """Compute the last update date."""
        for rec in self:
            # Use sudo to bypass security restrictions if needed
            rec.last_update = rec.lead_id.sudo().write_date

    @api.depends('lead_id.user_id')
    def _compute_salesperson(self):
        for rec in self:
            rec.salesperson = rec.lead_id.sudo().user_id.id

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
            source_id = self.env['utm.source'].sudo().search([('name','=','Online SBU Referral')])
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

    def action_change_user(self):
        self.is_changed_user = True

    @api.model
    def write(self, vals):
        """Reset `is_changed_user` after saving the record."""
        res = super(NewReferral, self).write(vals)
        if 'user' in vals:  # Reset only if the user field was changed
            self.is_changed_user = False
        return res
















