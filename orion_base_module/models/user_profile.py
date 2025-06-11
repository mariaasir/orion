from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import random
import string
import re


class ResUsersExtension(models.Model):
    _inherit = 'res.users' #Extiende del modelo res.users de Odoo

    #Campos del modelo extendido res.users que se encargrá de definir los usuarios de la aplicación
    image = fields.Image()
    name = fields.Char(required=True)
    dni = fields.Char(string='DNI', required=True)
    birthdate = fields.Date(string='Birth Date', required=True)
    phone = fields.Char(string='Phone')
    address = fields.Char(string='Address')
    plain_password = fields.Char(string='Password', default=lambda self: self._default_password())

    #Campo de tipo Selecionable, que será el encargado de definir el tipo de usuario que será.
    user_type = fields.Selection([
        ('monitor', 'Monitor'),
        ('parent', 'Parent-Mother'),
    ], string='User Type', required=True)

    #Campo de tipo Selecionable, que será el encargado de definir la sección a la que
    #pertenece el usuario, si se trata de un monitor.
    section = fields.Selection([
        ('mambos', 'Mambos'),
        ('ryhings', 'Ryhings'),
        ('tribu', 'Tribu'),
    ], string='Section')

    #Campo de tipo Many2many, que será el encargado de definir los 
    #hijos de un usuario de tipo 'parent'.
    child_ids = fields.Many2many(
        'orion_base_module.childs',
        'child_parent_rel',
        'parent_id',
        'child_id',
        string='Childs',
    )

    #Campos adicionales para la gestión de usuarios
    is_blocked = fields.Boolean(string="Blocked", default=False)
    #Campo boleano para indicar si la contraseña ha sido cambiada
    password_changed = fields.Boolean(default=False)

    #Método para crear un channel privado para monitores de una sección específica
    @api.model
    def _get_monitor_section_channel(self, section_code):
        section_name = dict(self._fields['section'].selection).get(section_code, section_code)
        channel_name = f"Monitors - {section_name} - Private Channel"
        channel = self.env['mail.channel'].search([('name', 'ilike', channel_name)], limit=1)
        if not channel:
            group_monitor = self.env.ref('orion_base_module.group_monitor')
            channel = self.env['mail.channel'].create({
                'name': channel_name,
                'channel_type': 'channel',
                'group_public_id': group_monitor.id,
            })
        return channel

    #Método para crear un channel privado para todos los usuarios de una seccion especifica.
    #Los padres se añadirán al canal de la sección a la que pertenecen sus hijos.
    @api.model
    def _get_channel_by_section(self, section_code):
        section_code_clean = section_code.strip()
        channel = self.env['mail.channel'].search([
            ('name', 'ilike', section_code_clean)
        ], limit=1)

        if not channel:
            raise ValidationError(_("There is no channel for section '%s'. Contact with the administrator.") % section_code)

        return channel

    #Método para crear un channel privado para todos los monitores.
    @api.model
    def _get_monitor_private_channel(self):
        channel_name = "Monitors-Private Channel"
        channel = self.env['mail.channel'].search([('name', '=', channel_name)], limit=1)
        if not channel:
            group_monitor = self.env.ref('orion_base_module.group_monitor')
            channel = self.env['mail.channel'].create({
                'name': channel_name,
                'channel_type': 'channel',
                'group_public_id': group_monitor.id, 
            })
        return channel

    #Métodos para asignar usuarios a canales según su tipo y sección
    def _add_user_to_channel(self, user, channel):
        if user.partner_id not in channel.channel_partner_ids:
            channel.write({'channel_partner_ids': [(4, user.partner_id.id)]})

    def _assign_user_to_section_channels(self):
        for user in self:
            if user.user_type == 'monitor':
                #Si el usuario es un monitor, se asigna a los canales correspondientes
                if user.section:
                    #Canal compartido entre padres y monitores
                    general_section_channel = user._get_channel_by_section(user.section)
                    user._add_user_to_channel(user, general_section_channel)

                    #Canal exclusivo para monitores de esa sección
                    monitor_section_channel = user._get_monitor_section_channel(user.section)
                    user._add_user_to_channel(user, monitor_section_channel)

                #Canal general de monitores
                monitor_general_channel = user._get_monitor_private_channel()
                user._add_user_to_channel(user, monitor_general_channel)

            #Si el usuario es un padre, se asigna a los canales de la sección de sus hijos
            elif user.user_type == 'parent':
                sections = user.child_ids.mapped('section')
                for section in sections:
                    if section:
                        channel = user._get_channel_by_section(section)
                        user._add_user_to_channel(user, channel)


    #Método para asignar todos los monitores al canal privado de monitores
    @api.model
    def assign_all_monitors_to_channel(self):
        channel_name = "Monitors-Private Channel"
        channel = self.env['mail.channel'].search([('name', '=', channel_name)], limit=1)
        if not channel:
            channel = self.env['mail.channel'].create({
                'name': channel_name,
                'channel_type': 'channel',
                'is_public': 'group',
            })

        monitors = self.env['res.users'].search([('user_type', '=', 'monitor')])

        for user in monitors:
            if user.partner_id and user.partner_id not in channel.channel_partner_ids:
                channel.write({'channel_partner_ids': [(4, user.partner_id.id)]})

        return True

    #----------------------------------------
    #           MÉTODOS AUXILIARES
    #----------------------------------------


    #Método para imprimir las credenciales del usuario
    def action_print_credentials(self):
        self.ensure_one()
        return self.env.ref('orion_base_module.action_report_user_credentials').report_action(self)

    #Método para generar una contraseña por defecto
    @staticmethod
    def _default_password():
        return ''.join(random.choices(string.ascii_letters, k=5)) + ''.join(random.choices(string.digits, k=3))


    #Métodos para validar los campos del modelo
    @api.constrains('dni')
    def _check_dni(self):
        for record in self:
            if not re.match(r'^\d{8}[A-Za-z]$', record.dni or ''):
                raise ValidationError("The DNI must be in the format 12345678A.")
            if self.search_count([('dni', '=', record.dni), ('id', '!=', record.id)]):
                raise ValidationError("The DNI is already registered.")

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone and not re.match(r'^\d{9}$', record.phone):
                raise ValidationError("The phone number must be 9 digits long.")
            if record.phone and self.search_count([('phone', '=', record.phone), ('id', '!=', record.id)]):
                raise ValidationError("The mobile number is already registered.")

    @api.constrains('birthdate')
    def _check_birthdate(self):
        for record in self:
            if record.birthdate:
                if record.birthdate > fields.Date.today():
                    raise ValidationError("The birth date cannot be in the future.")
                age = (fields.Date.today() - record.birthdate).days // 365
                if age < 18:
                    raise ValidationError("The user must be at least 18 years old.")
                if age > 99:
                    raise ValidationError("The user cannot be older than 99 years old.")

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$', record.name or ''):
                raise ValidationError("The name can only contain letters and spaces.")
            if record.name and record.name != record.name.strip():
                raise ValidationError("The name cannot start or end with spaces.")

 

    #Métodos para modificar los campos de un usuario
    #cuando es creado o es actualizado
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

        group_monitor = self.env.ref('orion_base_module.group_monitor')
        group_parent = self.env.ref('orion_base_module.group_parent')
        if vals.get('user_type') == 'monitor':
            user.write({'groups_id': [(3, group_parent.id), (4, group_monitor.id)]})
        elif vals.get('user_type') == 'parent':
            user.write({'groups_id': [(3, group_monitor.id), (4, group_parent.id)]})

        user._assign_user_to_section_channels()
        user.assign_all_monitors_to_channel()

        return user

    def write(self, vals):
        for user in self:
            if vals.get('is_blocked') and user.user_type == 'monitor':
                raise ValidationError("You cannot block a monitor user. Please contact the administrator.")

            if 'email' in vals and vals['email']:
                vals['login'] = vals['email']

        if 'password' in vals and vals['password']:
            vals['plain_password'] = vals['password']

        res = super().write(vals)

        group_monitor = self.env.ref('orion_base_module.group_monitor')
        group_parent = self.env.ref('orion_base_module.group_parent')
        for user in self:
            if 'password' in vals and vals['password'] and user.is_blocked:
                user.password_changed = True
                user.is_blocked = False

            if 'user_type' in vals:
                if vals['user_type'] == 'monitor':
                    user.write({'groups_id': [(3, group_parent.id), (4, group_monitor.id)]})
                elif vals['user_type'] == 'parent':
                    user.write({'groups_id': [(3, group_monitor.id), (4, group_parent.id)]})

        self._assign_user_to_section_channels()
        self.assign_all_monitors_to_channel()
        return res

    
    #Método para comprobar y bloquear a los padres que no han cambiado su contraseña en 7 días
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

    #Método para comprobar las credenciales del usuario
    def check_credentials(self, password):
        self.ensure_one()
        if self.is_blocked:
            raise ValidationError(_("Your account is blocked. Please contact the administrator."))
        return super().check_credentials(password)
