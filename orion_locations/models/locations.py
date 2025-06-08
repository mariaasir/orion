from odoo import models, fields, api
import re
from odoo.exceptions import ValidationError

class OrionLocations(models.Model):
    _name = "orion.locations"
    _description = "Orion Locations"

    name = fields.Char(string="Location Name", required=True)
    description = fields.Text(string="Description")
    address = fields.Char(string="Address", required=True)
    city = fields.Char(string="City", required=True)
    province = fields.Char(string="Province", required=True)
    postal_code = fields.Integer(string="Postal Code")
    coordinates = fields.Char(string="Coordinates", help="Latitude, Longitude format")
    owner = fields.Char(string="Owner")
    phone_owner = fields.Char(string="Owner Phone")
    cost = fields.Float(string="Cost", default=0.0)

    _sql_constraints = [
        ('cost_positive', 'CHECK(cost >= 0)', 'The cost cannot be less than 0.'),
    ]

    @api.constrains('cost')
    def _check_cost(self):
        for record in self:
            if record.cost < 0:
                raise ValidationError("The cost cannot be less than 0.")

    @api.constrains('phone_owner')
    def _check_phone_owner(self):
        for record in self:
            if record.phone_owner and not re.fullmatch(r'\d{9}', record.phone_owner):
                raise ValidationError("The owner's phone must be exactly 9 digits.")
            
    