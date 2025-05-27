from odoo import models, fields, api
from odoo.exceptions import UserError

class LoanWizard(models.TransientModel):
    _name = 'orion_management_inventory.lend_wizard'
    _description = 'Lend Wizard'

    material_id = fields.Many2one('orion_management_inventory.orion_inventory_materials', string="Material", required=True)
    max_quantity = fields.Integer(string="Available Quantity", readonly=True)
    lend_quantity = fields.Integer(string="Quantity to Lend", required=True)
    loaned_to = fields.Char(string="Loaned To", required=True, help="Name of the person or entity to whom the material is being loaned.")
    location = fields.Char(string="Location", required=True, help="Location where the material will be stored after lending.")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        material = self.env['orion_management_inventory.orion_inventory_materials'].browse(self.env.context.get('default_material_id'))
        res['material_id'] = material.id
        res['max_quantity'] = material.quantity
        return res

    def action_confirm_lend(self):
        self.ensure_one()
        material = self.material_id
        if self.lend_quantity > material.quantity or self.lend_quantity <= 0:
            raise UserError("Invalid quantity.")
        material_loaned = material.copy({
            'quantity': self.lend_quantity,
            'condition': 'loaned',
            'loaned_to': self.loaned_to,
            'location': self.location,
            'date': fields.Date.today(),
        })
        material.quantity -= self.lend_quantity
        if material.quantity == 0:
            material.unlink()
        return {'type': 'ir.actions.act_window_close'}