from odoo import models, fields, api
import random
import string

def _default_password(self):
    return ''.join(random.choices(string.ascii_letters, k=5)) + ''.join(random.choices(string.digits, k=3))

class ResUsersExtension(models.Model):
    _inherit = 'res.users'

    image = fields.Image()  
    name = fields.Char(required = True)
    dni = fields.Char(string='DNI', required=True)
    birthdate = fields.Date(string='Birth Date', required=True)
    phone = fields.Char(string='Phone')
    plain_password = fields.Char(string='Password', readonly=True, default=_default_password)
    user_type = fields.Selection([
        ('monitor', 'Monitor'),
        ('parent', 'Padre-Madre'),
    ], string='User Type', required=True)

    seccion = fields.Selection([
        ('mambos', 'Mambos'),
        ('ryhings', 'Ryhings'),
        ('tribu', 'Tribu'),
    ], string='Section')

    child_ids = fields.One2many(
        'orion_base_module.childs',
        'parent_id',
        string='Childs',
        compute='_compute_child_ids',
        store=False,
    )

    def _compute_child_ids(self):
        for user in self:
            user.child_ids = self.env['orion_base_module.childs'].search([('parent_id', '=', user.id)])

  

    @api.model
    def create(self, vals):
        if vals.get('email'):
            vals['login'] = vals['email']

        if not vals.get('password'):
            password = ''.join(random.choices(string.ascii_letters, k=5)) + ''.join(random.choices(string.digits, k=3))
            vals['password'] = password
            vals['plain_password'] = password  

        return super().create(vals)

    def write(self, vals):
        # Si se cambia el email, actualizar login
        if vals.get('email'):
            vals['login'] = vals['email']
        return super().write(vals)

    def action_generate_login_report(self):
        return self.env.ref('orion_base_module.action_report_login_user').report_action(self)
