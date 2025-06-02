from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import random
import string
import re


class ResUsersExtension(models.Model):
    _inherit = 'res.users'

    image = fields.Image()
    name = fields.Char(required=True)
    dni = fields.Char(string='DNI', required=True)
    birthdate = fields.Date(string='Birth Date', required=True)
    phone = fields.Char(string='Phone')
    plain_password = fields.Char(string='Password', default=lambda self: self._default_password())
    user_type = fields.Selection([
        ('monitor', 'Monitor'),
        ('parent', 'Padre-Madre'),
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
    is_blocked = fields.Boolean(string="Blocked", default=False)
    password_changed = fields.Boolean(default=False)

    # -------------------------
    # MÉTODOS AUXILIARES
    # -------------------------

    @staticmethod
    def _default_password():
        return ''.join(random.choices(string.ascii_letters, k=5)) + ''.join(random.choices(string.digits, k=3))

    # -------------------------
    # VALIDACIONES
    # -------------------------

    @api.constrains('dni')
    def _check_dni(self):
        for record in self:
            if not re.match(r'^\d{8}[A-Za-z]$', record.dni or ''):
                raise ValidationError("El DNI debe tener 8 números seguidos de una letra (ejemplo: 12345678A).")
            if self.search_count([('dni', '=', record.dni), ('id', '!=', record.id)]):
                raise ValidationError("El DNI ya está registrado.")

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone and not re.match(r'^\d{9}$', record.phone):
                raise ValidationError("El número de teléfono debe tener 9 dígitos.")
            if record.phone and self.search_count([('phone', '=', record.phone), ('id', '!=', record.id)]):
                raise ValidationError("El número de teléfono ya está registrado.")

    @api.constrains('birthdate')
    def _check_birthdate(self):
        for record in self:
            if record.birthdate:
                if record.birthdate > fields.Date.today():
                    raise ValidationError("La fecha de nacimiento no puede ser en el futuro.")
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
            if record.name and record.name != record.name.strip():
                raise ValidationError("El nombre no debe tener espacios al inicio o al final.")

    # -------------------------
    # CAMBIOS EN CREACIÓN Y ESCRITURA
    # -------------------------

    @api.model
    def create(self, vals):
        if vals.get('email'):
            vals['login'] = vals['email']

        if not vals.get('password'):
            password = self._default_password()
            vals['password'] = password
            vals['plain_password'] = password
        else:
            vals['plain_password'] = vals['password']

        vals['password_changed'] = False
        vals['is_blocked'] = False

        user = super().create(vals)

        if vals.get('user_type') == 'monitor':
            group_monitor = self.env.ref('orion_base_module.group_monitor')
            user.groups_id = [(4, group_monitor.id)]
        elif vals.get('user_type') == 'parent':
            group_parent = self.env.ref('orion_base_module.group_padre')
            user.groups_id = [(4, group_parent.id)]

        return user

    def write(self, vals):
        for user in self:
            if vals.get('is_blocked') and user.user_type == 'monitor':
                raise ValidationError("No se puede bloquear a un usuario de tipo Monitor.")

        if 'password' in vals and vals['password']:
            vals['plain_password'] = vals['password']

        res = super().write(vals)

        for user in self:
            if 'password' in vals and vals['password'] and user.is_blocked:
                user.password_changed = True
                user.is_blocked = False

            if 'user_type' in vals:
                if vals['user_type'] == 'monitor':
                    group_monitor = self.env.ref('orion_base_module.group_monitor')
                    user.groups_id = [(4, group_monitor.id)]
                elif vals['user_type'] == 'parent':
                    group_parent = self.env.ref('orion_base_module.group_padre')
                    user.groups_id = [(4, group_parent.id)]

        return res

    # -------------------------
    # ACCIONES PERSONALIZADAS
    # -------------------------

    def action_check_and_block_parents(self):
        seven_days_ago = datetime.now() - timedelta(days=7)
        parents_to_block = self.search([
            ('user_type', '=', 'parent'),
            ('create_date', '<=', seven_days_ago),
            ('password_changed', '=', False),
            ('is_blocked', '=', False),
        ])
        for parent in parents_to_block:
            new_password = self._default_password()
            parent.write({
                'password': new_password,
                'plain_password': new_password,
                'is_blocked': True,
                'password_changed': False,
            })

    def action_print_credentials(self):
        return self.env.ref('orion_base_module.action_report_user_credentials').report_action(self)

    def check_credentials(self, password):
        self.ensure_one()
        if self.is_blocked:
            raise ValidationError(_("Tu cuenta está bloqueada. Contacta con el administrador."))
        return super().check_credentials(password)
