from odoo import fields, models, api, _
from datetime import timedelta

from odoo.exceptions import ValidationError, UserError


class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offers'
    _order = 'price desc'

    name = fields.Char(string='Description')
    price = fields.Float(string='Price')
    status = fields.Selection([('accepted', 'Accepted'),
                               ('refused', 'Refused')],
                              string='Status')
    partner_id = fields.Many2one('res.partner', string='Customer')
    property_id = fields.Many2one('estate.property', string='Property')
    validity = fields.Integer(string='Validity', default=7)
    deadline = fields.Date(string='Deadline', compute='_compute_deadline', inverse='_inverse_deadline')

    @api.model
    def _set_create_date(self):
        return fields.Date.today()
    creation_date = fields.Date(string='Creation Date', default=_set_create_date)

    @api.depends('validity', 'creation_date')
    def _compute_deadline(self):
        for rec in self:
            if rec.creation_date and rec.validity:
                rec.deadline = rec.creation_date + timedelta(days=rec.validity)
            else:
                rec.deadline = False

    def _inverse_deadline(self):
        for rec in self:
            if rec.deadline and rec.creation_date:
                rec.validity = (rec.deadline - rec.creation_date).days
            else:
                rec.validity = False

    @api.autovacuum
    def _clean_offers(self):
        self.search([('status', '=', 'refused')]).unlink()

    @api.constrains('validity')
    def _check_validity(self):
        for rec in self:
            if rec.deadline <= rec.creation_date:
                raise ValidationError(_("Deadline cannot be before creation date"))
