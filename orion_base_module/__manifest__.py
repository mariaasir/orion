{
    "name": "Orion Management Users",
    "version": "16.0.1.0.0",
    "category": "Other",
    "author": "FactorLibre",
    "website": "https://git.factorlibre.com",
    "license": "LGPL-3",
    "summary": "Description module",
    "depends": [
        "base",
    ],
    "data": [
        "views/user_profile_views.xml",
        "views/child_views.xml",
        "security/ir.model.access.csv",
        "templates/user_login_template.xml",
        "data/ir_cron_data.xml",
        "security/security.xml",

    ],
    "installable": True,
    "application": True,
}
