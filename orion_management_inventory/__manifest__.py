{
    "name": "Orion Management Inventory",
    "version": "16.0.1.0.0",
    "category": "Other",
    "author": "Unai Nieto y María López",
    "website": " ",
    "license": "LGPL-3",
    "summary": "Module for managing inventory, loans, returns, and reservations of materials.",
    "description": """
        This module provides functionalities for managing inventory, including:
        - Adding and updating materials
        - Lend materials to users
        - Return materials from users
        - Reserve materials for future use
        - Scheduled task to delete discarded materials
    """,
    "depends": [
        "base",
        "orion_base_module",
    ],
    "data": [
        "views/inventory_views.xml",
        "views/loans_views.xml",
        "views/returns_views.xml",
        "views/reserved_views.xml",
        "views/lend_wizards_views.xml",
        "views/returns_wizards_views.xml",
        "views/reserved_wizards_views.xml",
        "security/ir.model.access.csv",
        "data/cron.xml"
    ],
    "installable": True,
    "application": True,
}