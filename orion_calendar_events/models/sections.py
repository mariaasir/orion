from odoo import models, fields

class OrionCalendarSection(models.Model):
    _name = "orion.calendar.section"
    _description = "Sections of Orion"

    name = fields.Char(string="Nombre", required=True)