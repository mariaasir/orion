from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class ReservedWizard(models.TransientModel):
    _name = 'orion_management_inventory.reserve_wizard'
    _description = 'Reserve Material Wizard'

    material_id = fields.Many2one('orion_management_inventory.orion_inventory_materials', string="Material", required=True)
    reserve_quantity = fields.Integer(string="Quantity to Reserve", required=True)
    reserved_by = fields.Char(string="Reserved By", required=True)
    reserve_date = fields.Date(string="Reserve Date", required=True)

    @api.constrains('reserve_quantity')
    def _check_reserve_quantity(self):
        for rec in self:
            if rec.reserve_quantity > rec.material_id.quantity:
                raise ValidationError("You cannot reserve more than the available quantity.")
    
    @api.constrains('reserve_date')
    def _check_reserve_date(self):
        for rec in self:
            if rec.reserve_date:
                today = date.today()
                if rec.reserve_date < today or rec.reserve_date > today + timedelta(days=30):
                    raise ValidationError("The reserve date must be today or within the next 30 days.")

    def action_confirm_reserve(self):
        material = self.material_id
        if self.reserve_quantity >= material.quantity:
            material.write({
                'condition': 'reserved',
                'loaned_to': self.reserved_by,
                'date': self.reserve_date,
                'quantity': self.reserve_quantity,
            })
        else:
            available_qty = material.quantity - self.reserve_quantity
            material.write({
                'quantity': available_qty,
            })
            material.copy({
                'quantity': self.reserve_quantity,
                'condition': 'reserved',
                'loaned_to': self.reserved_by,
                'date': self.reserve_date,
            })
        return {'type': 'ir.actions.act_window_close'}