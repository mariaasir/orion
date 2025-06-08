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
        "orion_base_module",
    ],
    "data": [
        "views/inventory_views.xml",
        "views/loans_views.xml",
        "views/returns_views.xml",
        "views/lend_wizards_views.xml",
        "views/returns_wizards_views.xml",
        "security/ir.model.access.csv",
        "data/cron.xml"
    ],
    "installable": True,
    "application": True,
}
