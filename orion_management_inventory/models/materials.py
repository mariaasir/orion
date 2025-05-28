from odoo import models, fields, api
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class Materials(models.Model):
    _name = 'orion_management_inventory.orion_inventory_materials'
    _description = 'Physical materials owned by the association'

    name = fields.Char(string="Description", required=True)
    condition = fields.Selection([
        ('available', 'Available'),
        ('loaned', 'Loaned'),
        ('reserved', 'Reserved'),
        ('under_repair', 'Under Repair'),
        ('damaged', 'Damaged'),
        ('obsolete', 'Obsolete'),
        ('lost', 'Lost / Misplaced'),
        ('discarded', 'Discarded / Donated / Sold'),
    ], string="Condition", default='available', required=True)

    type = fields.Selection([
        ('electronics', 'Electronics'), 
        ('furniture', 'Furniture'),
        ('tools', 'Tools'), 
        ('stationery', 'Stationery'), 
        ('sports', 'Sports'), 
        ('decoration', 'Decoration'), 
        ('kitchen', 'Kitchen Equipment'), 
        ('costumes', 'Costumes'),
        ('camping', 'Camping'), 
        ('others', 'Others'),
    ], string="Type", required=True)

    quantity = fields.Integer(string='Quantity', default=1)
    location = fields.Char(string="Location", required=True)
    notes = fields.Text(string="Notes")
    loaned_to = fields.Char(string="Loaned/Reserved To")
    date = fields.Date(string="Date")

    @api.constrains('quantity')
    def _check_quantity_non_negative(self):
        for record in self:
            if record.quantity is not None and record.quantity < 0:
                raise ValidationError("La cantidad debe ser 0 o positiva.")


    def action_open_lend_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lend Material',
            'res_model': 'orion_management_inventory.lend_wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_material_id': self.id,
                'default_max_quantity': self.quantity,
            }
        }
    
    def action_open_return_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Return Material',
            'res_model': 'orion_management_inventory.returns_wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_material_id': self.id,
                'default_max_quantity': self.quantity,
            }
        }
    def action_open_reserve_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reserve Material',
            'res_model': 'orion_management_inventory.reserve_wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_material_id': self.id,
            }
        }
    
    @api.model
    def create(self, vals):
        condition = vals.get('condition')
        if condition in ['loaned', 'reserved']:
            if not vals.get('loaned_to') or not vals.get('date'):
                raise ValidationError("Los campos 'Loaned/Reserved To' y 'Date' son obligatorios cuando el material está en estado 'Loaned' o 'Reserved'.")
        if vals.get('condition') == 'available':
            domain = [
                ('name', '=', vals.get('name')),
                ('location', '=', vals.get('location')),
                ('condition', '=', 'available'),
            ]
            existing = self.search(domain, limit=1)
            if existing:
                existing.quantity += vals.get('quantity', 1)
                return existing
        if vals.get('quantity', 1) == 0:
            vals['condition'] = 'discarded'
        return super().create(vals)
    
    def write(self, vals):
        condition = vals.get('condition') or self.condition
        loaned_to = vals.get('loaned_to') if 'loaned_to' in vals else self.loaned_to
        date_val = vals.get('date') if 'date' in vals else self.date
        if condition in ['loaned', 'reserved']:
            if not loaned_to or not date_val:
                raise ValidationError("Los campos 'Loaned/Reserved To' y 'Date' son obligatorios cuando el material está en estado 'Loaned' o 'Reserved'.")
        if 'quantity' in vals and vals['quantity'] == 0:
            vals['condition'] = 'discarded'
        return super().write(vals)

    @api.model
    def cron_delete_discarded_materials(self):
        days_limit = 30 
        limit_date = date.today() - timedelta(days=days_limit)
        materials = self.search([
            ('condition', '=', 'discarded'),
            ('date', '<=', limit_date)
        ])
        materials.unlink()

    @api.model
    def cron_mark_obsolete_lost_as_discarded(self):
        limit_date = date.today() - relativedelta(months=2)
        materials = self.search([
            ('condition', 'in', ['obsolete', 'lost']),
            ('date', '<=', limit_date)
        ])
        materials.write({'condition': 'discarded'})

    @api.model
    def cron_release_expired_reservations(self):
        today = date.today()
        materials = self.search([
            ('condition', '=', 'reserved'),
            ('date', '<', today)
        ])
        materials.write({'condition': 'available'})