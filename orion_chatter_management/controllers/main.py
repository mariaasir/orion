from odoo import http
from odoo.http import request

class ChatController(http.Controller):

    @http.route('/chat', type='http', auth='user', website=True)
    def chat_page(self, **kwargs):
        user = request.env.user
        if not (user.has_group('your_module.group_padres') or user.has_group('your_module.group_monitores')):
            return request.redirect('/web')
        return request.render('your_module.chat_page_template', {})

    @http.route('/chat/messages', type='json', auth='user')
    def get_messages(self, **kwargs):
        user = request.env.user
        if not (user.has_group('your_module.group_padres') or user.has_group('your_module.group_monitores')):
            return []
        interlocutor_id = int(kwargs.get('interlocutor_id', 0))
        domain = ['|',
                  ('sender_id', '=', user.id),
                  ('receiver_id', '=', user.id)]
        if interlocutor_id:
            domain += ['|',
                       ('sender_id', '=', interlocutor_id),
                       ('receiver_id', '=', interlocutor_id)]
        messages = request.env['chat.message'].search(domain, order='create_date asc')
        return [{
            'sender': msg.sender_id.name,
            'receiver': msg.receiver_id.name,
            'body': msg.body,
            'date': msg.create_date.strftime('%Y-%m-%d %H:%M:%S'),
        } for msg in messages]

    @http.route('/chat/send_message', type='json', auth='user', methods=['POST'])
    def send_message(self, receiver_id, body, **kwargs):
        user = request.env.user
        if not (user.has_group('your_module.group_padres') or user.has_group('your_module.group_monitores')):
            return {'error': 'No tienes permiso'}
        if not receiver_id or not body:
            return {'error': 'Faltan parámetros'}
        receiver = request.env['res.users'].browse(int(receiver_id))
        if not receiver.exists():
            return {'error': 'Receptor no encontrado'}
        request.env['chat.message'].sudo().create({
            'sender_id': user.id,
            'receiver_id': receiver.id,
            'body': body,
        })
        return {'success': True}
