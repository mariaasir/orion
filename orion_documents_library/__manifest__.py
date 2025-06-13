{
    "name": "Orion Documents Library",
    "version": "16.0.1.0.0",
    "category": "Other",
    "author": "Unai Nieto",
    "website": "",
    "license": "LGPL-3",
    "summary": "Orion Documents Library Module to manage all the documents of the association in the system.",
    "depends": [
        "base",
        "orion_base_module",
    ],
    "data": [
        'security/ir.model.access.csv',
        "views/library_views.xml",
    ],
    

    "stallable": True,
    "application": True,
}