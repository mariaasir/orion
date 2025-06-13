from odoo import http
from odoo.http import request

#Controlador HTTP para gestionar las funcionalidades del chat entre usuarios
class ChatController(http.Controller):

    @http.route('/chat', type='http', auth='user', website=True)  #Ruta para acceder a la página del chat


    #Comprueba si el usuario tiene permisos para acceder al chat
    # Si no tiene permisos lo redirige a la página principal y si los tiene le muestra la página del chat
    def chat_page(self, **kwargs):
        user = request.env.user
        
        if not (user.has_group('orion_base_module.group_parents') or user.has_group('orion_base_module.group_monitors')):
            return request.redirect('/web') 
        return request.render('orion_base_module.chat_page_template', {})

    #Obtiene los mensajes del chat en formato JSON. 
    @http.route('/chat/messages', type='json', auth='user')
    def get_messages(self, **kwargs):
        user = request.env.user
        if not (user.has_group('orion_base_module.group_parents') or user.has_group('orion_base_module.group_monitors')):
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

    #Envia un mensaje al receptor en formato JSON.
    @http.route('/chat/send_message', type='json', auth='user', methods=['POST'])
    def send_message(self, receiver_id, body, **kwargs):
        user = request.env.user
        if not (user.has_group('orion_base_module.group_parents') or user.has_group('orion_base_module.group_monitors')):
            return {'error': 'You do not have permission to send messages'}

        if not receiver_id or not body:
            return {'error': 'The receiver ID and message body are required'}

        receiver = request.env['res.users'].browse(int(receiver_id))
        if not receiver.exists():
            return {'error': 'Receptor not found'}

        request.env['chat.message'].sudo().create({
            'sender_id': user.id,
            'receiver_id': receiver.id,
            'body': body,
        })

        return {'success': True}
