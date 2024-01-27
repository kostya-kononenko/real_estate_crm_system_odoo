from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError


class Property(models.Model):
    _name = 'estate.property'
    _description = 'Estate Properties'
    _order = 'id desc'

    name = fields.Char(string='Name', required=True)
    state = fields.Selection(
        [
            ('new', 'New'),
            ('received', 'Offer Received'),
            ('accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancel', 'Cancel')
        ],
        default='new',
        string='Status')
    tag_ids = fields.Many2many('estate.property.tag', string='Property Tag')
    type_id = fields.Many2one('estate.property.type', string='Property Type')
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
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    sales_id = fields.Many2one('res.users', string='Salesman')
    buyer_id = fields.Many2one('res.partner', string='Buyer', domain=[('is_company', '=', True)])
    phone = fields.Char(string='Phone', related='buyer_id.phone')
    total_area = fields.Integer(string='Total Area', compute='_onchange_total_area')

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)

    offer_count = fields.Integer(string='Offer Count', compute=_compute_offer_count)

    @api.onchange('living_area', 'garden_area')
    def _onchange_total_area(self):
        self.total_area = self.living_area + self.garden_area

    def action_sold(self):
        self.state = 'sold'

    def action_cancel(self):
        self.state = 'cancel'

    def action_property_view_offers(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f"{self.name} - Offers",
            'domain': [('property_id', '=', self.id)],
            'view_mode': 'tree',
            'res_model': 'estate.property.offer'
        }

    @api.depends('offer_ids')
    def _compute_best_price(self):
        for rec in self:
            if rec.offer_ids:
                rec.best_offer = max(rec.offer_ids.mapped('price'))
            else:
                rec.best_offer = 0

    _sql_constraints = [
        ('positive_expected_price', 'CHECK(expected_price >= 0)', 'Expected Price must be positive.'),
        ('positive_best_offer', 'CHECK(best_offer >= 0)', 'Best Offer must be positive.'),
        ('positive_selling_price', 'CHECK(selling_price >= 0)', 'Selling Price must be positive.'),
    ]

    def unlink(self):
        if not set(self.mapped("state")) <= {"new", "canceled"}:
            raise UserError("Cannot delete offer with status 'received' or 'accepted' or 'sold'.")
        return super().unlink()


class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Properties Type'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Name must be unique.'),
    ]


class PropertyTags(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Properties Tag'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color')

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'Name must be unique.'),
    ]