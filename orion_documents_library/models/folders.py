from odoo import models, fields, api
from odoo.exceptions import ValidationError
import mimetypes

class LibraryFolder(models.Model):
    _name = 'library.folder'
    _description = 'Library Folder'
    _parent_store = True
    _parent_name = 'parent_id'
    _order = 'parent_left'

    name = fields.Char(string='Folder Name', required=True)
    parent_id = fields.Many2one('library.folder', string='Parent Folder', index=True)
    child_ids = fields.One2many('library.folder', 'parent_id', string='Subfolders')
    parent_left = fields.Integer(index=True)
    parent_right = fields.Integer(index=True)
    parent_path = fields.Char(index=True)
    full_path = fields.Char(string='Full Path', compute='_compute_full_path', store=True)
    navigate_to = fields.Many2one('library.folder', compute='_compute_navigate_to', string='Open')
    document_ids = fields.One2many('library.document', 'folder_id', string='Documents')

    def action_open_folder_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'view_mode': 'form',
            'res_model': 'library.folder',
            'res_id': self.id,
            'target': 'current',  
        }

    @api.depends('parent_id', 'name', 'parent_id.full_path')
    def _compute_full_path(self):
        for rec in self:
            path = []
            parent = rec
            while parent:
                if parent.name:
                    path.insert(0, parent.name)
                parent = parent.parent_id
            rec.full_path = " / ".join(path)

    @api.depends('child_ids')
    def _compute_navigate_to(self):
        for rec in self:
            rec.navigate_to = False 

    @api.constrains('parent_id')
    def _check_not_circular(self):
        for folder in self:
            parent = folder.parent_id
            while parent:
                if parent == folder:
                    raise ValidationError("A folder cannot be its own parent or descendant.")
                parent = parent.parent_id
