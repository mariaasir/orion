from odoo import models, fields

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
    location = fields.Char(string="Location")
    notes = fields.Text(string="Notes")
    loaned_to = fields.Char(string="Loaned/Reserved To")
