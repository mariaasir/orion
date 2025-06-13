from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError
import re

class Childs(models.Model):
    _name = 'orion_base_module.childs'
    _description = 'Childs of the association'

    #Definicion de los campos del modelo child
    name = fields.Char(string='Name', required=True)
    dni = fields.Char(string='DNI')
    birthdate = fields.Date(string='Birth Date', required=True)
    email = fields.Char(string='Email')
    image = fields.Image()  

    #Relacion Many2Many entre los niños de la asociacion y los usuarios
    # de tipo 'parent'
    parents_id = fields.Many2many(
            'res.users',
            'child_parent_rel', 
            'child_id',          
            'parent_id',         
            string='Parents',
            domain=[('user_type', '=', 'parent')],
        )    
    
    
    #Campo computado que determina la sección del niño, según su año de nacimiento.
    section = fields.Selection([
        ('mambos', 'Mambos'),
        ('ryhings', 'Ryhings'),
        ('tribu', 'Tribu'),
    ], string='Section', compute='_compute_section', store=True)

    #Método para calcular la sección del niño según su fecha de nacimiento.
        #Tribu: 8–12 años.
        #Mambos: 13–14 o 12–14 años.
        #Ryhings: 15–18 años.

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
    

    #Validaciones de los campos del modelo child
    @api.constrains('birthdate')
    def _check_birthdate(self):
        for record in self:
            if record.birthdate and record.birthdate > date.today():
                raise ValidationError("The birth date cannot be in the future.")
            if record.birthdate:
                age = (date.today() - record.birthdate).days // 365
                if age < 0 or age > 25:
                    raise ValidationError("The child must be between 0 and 25 years old.")

    @api.constrains('dni')
    def _check_dni(self):
        for record in self:
            if record.dni and not re.match(r'^\d{8}[A-Za-z]$', record.dni):
                raise ValidationError("The DNI must be in the format 12345678A.")
            if record.dni and self.search_count([('dni', '=', record.dni), ('id', '!=', record.id)]):
                raise ValidationError("The DNI is already registered for another child.")

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', record.email):
                raise ValidationError("The email must be in a valid format (e.g.,")
            if record.email and self.search_count([('email', '=', record.email), ('id', '!=', record.id)]):
                raise ValidationError("The email is already registered for another child.")

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$', record.name or ''):
                raise ValidationError("The name must only contain letters and spaces.")
            if record.name and (record.name != record.name.strip()):
                raise ValidationError("The name cannot start or end with spaces.")


    @api.model
    def create(self, vals):
        res = super().create(vals)
        if 'parents_id' in vals:
            for parent in res.parents_id:
                parent._add_parent_to_all_child_sections()
        return res

    def write(self, vals):
        res = super().write(vals)
        if 'parents_id' in vals:
            for record in self:
                for parent in record.parents_id:
                    parent._add_parent_to_all_child_sections()
        return res



