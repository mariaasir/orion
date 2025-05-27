from odoo import models, fields, api
from odoo.exceptions import UserError

class ReturnWizard(models.TransientModel):
    _name = 'orion_management_inventory.returns_wizard'
    _description = 'Wizard for returning loaned materials'

    material_id = fields.Many2one('orion_management_inventory.orion_inventory_materials', string="Material", required=True)
    max_quantity = fields.Integer(string="Loaned Quantity", readonly=True)
    return_quantity = fields.Integer(string="Quantity to Return", required=True)
    location = fields.Char(string="Return Location", required=True, help="Location where the material will be stored after return.")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        material = self.env['orion_management_inventory.orion_inventory_materials'].browse(self.env.context.get('default_material_id'))
        res['material_id'] = material.id
        res['max_quantity'] = material.quantity
        return res

    def action_confirm_returns(self):
        self.ensure_one()
        material = self.material_id
        if self.return_quantity > material.quantity or self.return_quantity <= 0:
            raise UserError("Invalid return quantity.")
        material_returned = material.copy({
            'quantity': self.return_quantity,
            'condition': 'available',
            'location': self.location,
            'loaned_to': False,
            'date': False,
        })

        material.quantity -= self.return_quantity
        if material.quantity == 0:
            material.unlink()
        return {'type': 'ir.actions.act_window_close'}