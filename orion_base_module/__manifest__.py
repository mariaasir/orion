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
        "security/security.xml",
        "security/ir.model.access.csv",
        'views/user_report_template.xml',
        "views/user_login_report.xml",
        "data/ir_cron_data.xml",
    ],
    "installable": True,
    "application": True,
}
