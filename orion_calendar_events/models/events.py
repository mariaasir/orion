from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Events(models.Model):
    _name = "orion.calendar.events"
    _description = "Orion Calendar Events"

    name = fields.Char(string="Activity Name", required=True)
    description = fields.Text(string="Description")
    date = fields.Date(string="Date", required=True)
    section_ids = fields.Many2many(
        "orion.calendar.section",
        string="Sections"
    )
    cost = fields.Float(string="Cost")

    _sql_constraints = [
        ('cost_positive', 'CHECK(cost >= 0)', 'El coste no puede ser menor que 0.'),
    ]

    @api.constrains('cost')
    def _check_cost(self):
        for record in self:
            if record.cost < 0:
                raise ValidationError("El coste no puede ser menor que 0.")