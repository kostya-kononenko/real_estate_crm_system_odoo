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
    deadline = fields.Date(string='Deadline')

