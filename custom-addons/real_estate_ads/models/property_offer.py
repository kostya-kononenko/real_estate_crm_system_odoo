from odoo import fields, models, api, _
from datetime import timedelta

from odoo.exceptions import ValidationError, UserError


class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offers'
    _order = 'price desc'

    @api.depends('property_id', 'partner_id')
    def _compute_name(self):
        for rec in self:
            if rec.property_id and rec.partner_id:
                rec.name = f"{rec.property_id.name} - {rec.partner_id.name}"
            else:
                rec.name = False

    name = fields.Char(string='Description', compute=_compute_name)
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

    def _validate_accepted_offer(self):
        offer_ids = self.env['estate.property.offer'].search([
            ('property_id', '=', self.property_id.id),
            ('status', '=', 'accepted'),
        ])
        if offer_ids:
            raise ValidationError("Offer already accepted")

    def _validate_accepted_price_offer(self, expected_price, selling_price):
        if selling_price < expected_price * 0.9:
            raise ValidationError("Selling Price cannot be 90% or more below Expected Price.")

    def action_accept_offers(self):
        if self.property_id:
            self._validate_accepted_offer()
            self._validate_accepted_price_offer(self.property_id.expected_price, self.price)
            self.property_id.write({
                'selling_price': self.price,
                'state': 'accepted',
            })
        self.status = 'accepted'

    def action_decline_offers(self):
        self.status = 'refused'
        if all(self.property_id.offer_ids.mapped('status')):
            self.property_id.write({
                'selling_price': 0,
                'state': 'received'
            })
