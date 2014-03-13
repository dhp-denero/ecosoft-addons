{
    'name': 'Product Stock Card',
    'version': '1.0',
    'category': 'Warehouse',
    'description': """
Module adds Product Stock Card view.\n
    """,
    'author': 'Ecosoft',
    'website': 'http://www.openerp.com',
    'depends': ['stock', 'product', 'jasper_reports', 'report_menu_restriction'],
    'data': [
             'product_stock_card_view.xml',
             'wizard/product_stock_card_location_view.xml',
             'security/ir.model.access.csv',
             'product_view.xml',
             'reports.xml',
    ],
    'active': False,
    'installable': True
}