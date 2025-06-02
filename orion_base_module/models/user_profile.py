from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import random
import string
import re

def _default_password():
    return ''.join(random.choices(string.ascii_letters, k=5)) + ''.join(random.choices(string.digits, k=3))

class ResUsersExtension(models.Model):
    _inherit = 'res.users'

    image = fields.Image()
    name = fields.Char(required=True)
    dni = fields.Char(string='DNI', required=True)
    birthdate = fields.Date(string='Birth Date', required=True)
    phone = fields.Char(string='Phone')
    plain_password = fields.Char(string='Password', readonly=True, default=_default_password)
    user_type = fields.Selection([
        ('monitor', 'Monitor'),
        ('parent', 'Parent'),
    ], string='User Type', required=True)

    section = fields.Selection([
        ('mambos', 'Mambos'),
        ('ryhings', 'Ryhings'),
        ('tribu', 'Tribu'),
    ], string='Section')

    child_ids = fields.Many2many(
        'orion_base_module.childs',
        'child_parent_rel',   
        'parent_id',           
        'child_id',          
        string='Childs',
    )

    is_blocked = fields.Boolean(string="Blocked")
    password_changed = fields.Boolean(default=False)

    def _compute_child_ids(self):
        for user in self:
            user.child_ids = self.env['orion_base_module.childs'].search([('parent_id', '=', user.id)])

    @api.constrains('dni')
    def _check_dni(self):
        for record in self:
            if not re.match(r'^\d{8}[A-Za-z]$', record.dni or ''):
                raise ValidationError("El DNI debe tener 8 números seguidos de una letra (ejemplo: 12345678A).")
            # Unicidad de DNI
            if self.search_count([('dni', '=', record.dni), ('id', '!=', record.id)]):
                raise ValidationError("El DNI ya está registrado.")

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone and not re.match(r'^\d{9}$', record.phone):
                raise ValidationError("El número de teléfono debe tener 9 dígitos.")
            # Unicidad de teléfono
            if record.phone and self.search_count([('phone', '=', record.phone), ('id', '!=', record.id)]):
                raise ValidationError("El número de teléfono ya está registrado.")

    @api.constrains('birthdate')
    def _check_birthdate(self):
        for record in self:
            if record.birthdate and record.birthdate > fields.Date.today():
                raise ValidationError("La fecha de nacimiento no puede ser en el futuro.")
            if record.birthdate:
                age = (fields.Date.today() - record.birthdate).days // 365
                if age < 18:
                    raise ValidationError("El usuario debe ser mayor de 18 años.")
                if age > 120:
                    raise ValidationError("La edad máxima permitida es 120 años.")

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$', record.name or ''):
                raise ValidationError("El nombre solo puede contener letras y espacios.")
            if record.name and (record.name != record.name.strip()):
                raise ValidationError("El nombre no debe tener espacios al inicio o al final.")


    def write(self, vals):
        res = super().write(vals)
        for user in self:
            if 'password' in vals and vals['password'] and user.is_blocked:
                user.password_changed = True
                user.is_blocked = False
                user.plain_password = ''
        return res

    @api.model
    def create(self, vals):
        if vals.get('email'):
            vals['login'] = vals['email']
        if not vals.get('password'):
            password = _default_password()
            vals['password'] = password
            vals['plain_password'] = password
        vals['password_changed'] = False
        vals['is_blocked'] = False
        return super().create(vals)

    def action_check_and_block_parents(self):
        seven_days_ago = datetime.now() - timedelta(days=7)
        parents_to_block = self.search([
            ('user_type', '=', 'parent'),
            ('create_date', '<=', seven_days_ago.strftime('%Y-%m-%d %H:%M:%S')),
            ('password_changed', '=', False),
            ('is_blocked', '=', False),
        ])
        for parent in parents_to_block:
            new_password = _default_password()
            parent.write({
                'password': new_password,
                'plain_password': new_password,
                'is_blocked': True,
                'password_changed': False,
            })

    def check_credentials(self, password):
        self.ensure_one()
        if self.is_blocked:
            raise AccessDenied(_("Your account is blocked. Please contact the administrator."))
        return super().check_credentials(password)