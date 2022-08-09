# -*- coding: utf-8 -*-
{
    'name': "Car Pooling",

    'summary': """
        An app to share the vehicles by Odoo users for free commuting.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Nima Farnoodian: UCLouvain",
    'website': "http://www.uclouvain.be",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/user_profile_updated.xml',
        'views/trips_view.xml',
        'views/trips_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
