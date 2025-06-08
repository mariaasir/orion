from odoo import models, fields, api

class ChatMessage(models.Model):
    _name = 'chat.message'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Mensaje de chat entre padres y monitores'
    _order = 'create_date asc'

    sender_id = fields.Many2one('res.users', string='Remitente', required=True, default=lambda self: self.env.user)
    receiver_id = fields.Many2one('res.users', string='Destinatario', required=True)
    body = fields.Text(string='Mensaje', required=True)
    create_date = fields.Datetime(string='Fecha de creación', readonly=True)
    channel_id = fields.Many2one('mail.channel', string='Canal', help="Canal de chat asociado")

    # Método para enviar mensaje y crear mail.message enlazado
    def send_message(self):
        self.ensure_one()
        # Crear un mail.message vinculado a este chat.message
        self.message_post(
            body=self.body,
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            author_id=self.sender_id.partner_id.id,
            partner_ids=[(4, self.receiver_id.partner_id.id)],
            channel_ids=[(4, self.channel_id.id)] if self.channel_id else False,
        )
