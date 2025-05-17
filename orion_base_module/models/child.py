from odoo import models, fields

class ResChildren(models.Model):
    _name = 'res.children'
    _description = 'Hijos de los padres/madres/tutores'

    name = fields.Char(string="Nombre", required=True)
    last_name = fields.Char(string="Apellidos", required=True)
    dni = fields.Char(string="DNI")
    birth_date = fields.Date(string="Fecha de Nacimiento")
    parent_id = fields.Many2one('res.users', string="Padre/Madre/Tutor")
