from odoo import models, fields, api
import secrets

class ResUsers(models.Model):
    _name = 'users.profile'
    _description = 'Perfil de Usuario'

    # Campos personalizados
    profile_type = fields.Selection([
        ('monitor', 'Monitor'),
        ('padre', 'Padre/Madre/Tutor'),
    ], string="Tipo de Usuario", default='padre', required=True)

    name = fields.Char(string="Nombre", required=True)
    last_name = fields.Char(string="Apellidos", required=True)
    dni = fields.Char(string="DNI")
    birth_date = fields.Date(string="Fecha de Nacimiento")
    address = fields.Char(string="Dirección")
    email = fields.Char(string="Email")
    phone_mobile = fields.Char(string="Teléfono")
    children_ids = fields.One2many('res.children', 'parent_id', string="Hijos")

    # Asociar el modelo con el usuario de Odoo
    login_name = fields.Char(string="Nombre de Usuario", required=True)