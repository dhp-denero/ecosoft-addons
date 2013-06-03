{
    "name": "Advance and Additional discount",
    "version": "0.2",
    "depends": ["base","sale","purchase","account",
                "stock","picking_invoice_rel" # kittiu
                ],
    "author": "E-nova tecnologies Pvt. Ltd.",
    "category": "Sales",
    "description": """
    This module provide : additional discount at total sales order, purchase order and invoices instead of per order line,
    but there is no changes in existing discount on per order lines.
    Additional discount is fully integrated between sales, purchase and invoices.
    """,
    "init_xml": [],
    'update_xml': ['all_view.xml','partner_view.xml',
                   'wizard/sale_make_invoice_advance.xml'],
    'demo_xml': [],
    'test': [
        'test/scenario1.yml',
        'test/scenario2.yml',
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
#    'certificate': 'certificate',
}
