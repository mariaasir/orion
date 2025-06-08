{
    "name": "Orion Chat",
    "version": "16.0.1.0.0",
    "category": "Other",
    "author": "MariaLopez",
    "website": "",
    "license": "LGPL-3",
    "summary": "Chat management system for Odoo",
    "depends": ["base", "web", "mail", "website"],  
    "data": [
        #"security/chat_security.xml",
        "views/chat_templates.xml",
        "views/chat_menu.xml",
    ],
    "installable": True,
    "application": True,
}
