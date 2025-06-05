from odoo import models, fields, api
import mimetypes
class LibraryDocument(models.Model):
    _name = 'library.document'
    _description = 'Library Document'

    name = fields.Char(string='Document Name', required=True)
    file = fields.Binary(string='File', required=True)
    file_name = fields.Char(string='File Name')
    mimetype = fields.Char(string='MIME Type')
    folder_id = fields.Many2one('library.folder', string='Folder')

    @api.onchange('file')
    def _onchange_file(self):
        if self.file:
            if self.file_name:
                mime, _ = mimetypes.guess_type(self.file_name)
                self.mimetype = mime or ''
            else:
                self.mimetype = ''

