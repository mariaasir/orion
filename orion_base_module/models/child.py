from odoo import models, fields

from odoo import models, fields

class Childs(models.Model):
    _name = 'orion_base_module.childs'
    _description = 'Childs of the association'

    name = fields.Char(string='Name', required=True)
    dni = fields.Char(string='DNI')
    birthdate = fields.Date(string='Birth Date', required=True)
    email = fields.Char(string='Email')
    parent_id = fields.Many2one('res.users', string='Parents', domain=[('user_type', '=', 'parent')],)
    image = fields.Image()  
    section = fields.Selection([
        ('mambos', 'Mambos'),
        ('ryhings', 'Ryhings'),
        ('tribu', 'Tribu'),
    ], string='Section')
