from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError
import re

class Childs(models.Model):
    _name = 'orion_base_module.childs'
    _description = 'Childs of the association'

    name = fields.Char(string='Name', required=True)
    dni = fields.Char(string='DNI')
    birthdate = fields.Date(string='Birth Date', required=True)
    email = fields.Char(string='Email')
    parents_id = fields.Many2many(
            'res.users',
            'child_parent_rel', 
            'child_id',          
            'parent_id',         
            string='Parents',
            domain=[('user_type', '=', 'parent')],
        )    
    
    image = fields.Image()  

    section = fields.Selection([
        ('mambos', 'Mambos'),
        ('ryhings', 'Ryhings'),
        ('tribu', 'Tribu'),
    ], string='Section', compute='_compute_section', store=True)

    @api.depends('birthdate')
    def _compute_section(self):
        today = date.today()
        for child in self:
            if not child.birthdate:
                child.section = False
                continue
            sept_first = date(today.year, 9, 1)
            if today < sept_first:
                age = today.year - child.birthdate.year - ((today.month, today.day) < (child.birthdate.month, child.birthdate.day))
                if age in (16, 17, 18):
                    child.section = 'ryhings'
                elif age in (13, 14, 15):
                    child.section = 'mambos'
                elif age in (9, 10, 11, 12):
                    child.section = 'tribu'
                else:
                    child.section = False
            else:
                age = today.year - child.birthdate.year - ((today.month, today.day) < (child.birthdate.month, child.birthdate.day))
                if age in (15, 16, 17):
                    child.section = 'ryhings'
                elif age in (12, 13, 14):
                    child.section = 'mambos'
                elif age in (8, 9, 10, 11):
                    child.section = 'tribu'
                else:
                    child.section = False
    
    @api.constrains('birthdate')
    def _check_birthdate(self):
        for record in self:
            if record.birthdate and record.birthdate > date.today():
                raise ValidationError("La fecha de nacimiento no puede ser en el futuro.")
            if record.birthdate:
                age = (date.today() - record.birthdate).days // 365
                if age < 0 or age > 25:
                    raise ValidationError("La edad debe estar entre 0 y 25 años.")

    @api.constrains('dni')
    def _check_dni(self):
        for record in self:
            if record.dni and not re.match(r'^\d{8}[A-Za-z]$', record.dni):
                raise ValidationError("El DNI debe tener 8 números seguidos de una letra (ejemplo: 12345678A).")
            if record.dni and self.search_count([('dni', '=', record.dni), ('id', '!=', record.id)]):
                raise ValidationError("El DNI ya está registrado para otro niño.")

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', record.email):
                raise ValidationError("El correo electrónico no es válido.")
            if record.email and self.search_count([('email', '=', record.email), ('id', '!=', record.id)]):
                raise ValidationError("El correo electrónico ya está registrado para otro niño.")

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$', record.name or ''):
                raise ValidationError("El nombre solo puede contener letras y espacios.")
            if record.name and (record.name != record.name.strip()):
                raise ValidationError("El nombre no debe tener espacios al inicio o al final.")


