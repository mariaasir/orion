{
    "name": "Orion Management Users",
    "version": "16.0.1.0.0",
    "category": "Other",
    "author": "María López Patón",
    "website": "",
    "license": "LGPL-3",
    "summary": "Module for managing users in Orion, including user profiles, child management, and login functionality.",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "data/companies.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "templates/user_login_template.xml",
        "views/user_profile_views.xml",
        "views/own_user_parent_views.xml",
        "views/child_views.xml",
        "data/ir_cron_data.xml",

    ],
    "installable": True,
    "application": True,
}
