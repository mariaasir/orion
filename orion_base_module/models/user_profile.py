from odoo import models, fields, api
import random
import string

class ResUsersExtension(models.Model):
    _inherit = 'res.users'

    image = fields.Image()  
    name = fields.Char(required = True)
    dni = fields.Char(string='DNI', required=True)
    birthdate = fields.Date(string='Birth Date', required=True)
    phone = fields.Char(string='Phone')
    plain_password = fields.Char(string='Password', readonly=False)
    user_type = fields.Selection([
        ('monitor', 'Monitor'),
        ('parent', 'Padre-Madre'),
    ], string='User Type', required=True)

    seccion = fields.Selection([
        ('mambos', 'Mambos'),
        ('ryhings', 'Ryhings'),
        ('tribu', 'Tribu'),
    ], string='Sección')

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
        # Sincronizar email y login para que se use el email para login
        if vals.get('email'):
            vals['login'] = vals['email']

        # Generar password si no existe
        if not vals.get('password'):
            password = ''.join(random.choices(string.ascii_letters, k=5)) + ''.join(random.choices(string.digits, k=3))
            vals['password'] = password
            vals['plain_password'] = password  # Guardar la contraseña generada para mostrar

        return super().create(vals)

    def write(self, vals):
        # Si se cambia el email, actualizar login
        if vals.get('email'):
            vals['login'] = vals['email']
        return super().write(vals)

    def print_user_login_report(self):
        return self.env.ref('orion_base_module.action_report_user_login').report_action(self)
