from odoo import fields, models


class Property(models.Model):
    _name = 'estate.property'
    _description = 'Estate Properties'
    _order = 'id desc'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(string='Available From')
    expected_price = fields.Float(string='Expected Price')
    best_offer = fields.Float(string='Best Offer', compute='_compute_best_price')
    selling_price = fields.Float(string='Selling Price', readonly=True)
    bedrooms = fields.Integer(string='Bedrooms')
    living_area = fields.Integer(string='Living Area(sqm)')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage', default=False)
    garden = fields.Boolean(string='Garden', default=False)
    garden_area = fields.Integer(string='Garden Area(sqm)')
    garden_orientation = fields.Selection([('north', 'North'),
                                           ('south', 'South'),
                                           ('east', 'East'),
                                           ('west', 'West')],
                                          string='Garden Orientation',
                                          default='north')
