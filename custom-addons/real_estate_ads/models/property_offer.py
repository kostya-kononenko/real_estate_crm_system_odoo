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

    @api.model
    def create(self, vals):
        property_id = vals.get('property_id')
        if property_id:
            accepted_offer_exists = self.search([('property_id', '=', property_id), ('status', '=', 'accepted')],
                                                limit=1)
            if accepted_offer_exists:
                raise UserError("Cannot create a new offer. An accepted offer already exists.")

            property_sold = self.env['estate.property'].search([('id', '=', property_id), ('state', '=', 'sold')],
                                                               limit=1)
            if property_sold:
                raise UserError("It is not possible to create an offer if the property is sold.")

            property_cancel = self.env['estate.property'].search([('id', '=', property_id), ('state', '=', 'cancel')],
                                                               limit=1)
            if property_cancel:
                raise UserError("It is not possible to create an offer if the property is canceled")

            property_record = self.env['estate.property'].browse(property_id)

            min_price_offer = self.search([('property_id', '=', property_id)], order='price asc', limit=1)
            if min_price_offer and vals.get('price', 0) < min_price_offer.price:
                raise UserError("Cannot create a new offer. Price is below the minimum price.")

            property_record.write({'state': 'received'})

        return super(PropertyOffer, self).create(vals)

    @api.model
    def unlink(self):
        for offer in self:
            if offer.status == 'accepted' or offer.status == 'refused':
                raise UserError("Cannot delete offer with status 'accepted' or 'refused'.")
        return super(PropertyOffer, self).unlink()