{
    "name": "Advance and Additional discount",
    "version": "1.0",
    "depends": ["base","sale","purchase","account",
                "stock","picking_invoice_rel"
                ],
    "author": "Ecosoft",
    "category": "Sales",
    "description": """
This module add 2 new features, Additional Discount and Advance Amount.

For Additional Discount, it is the same as additional_discount module, and quite easy to use by self.

For Advance Amount, following are how it works,

* First, Accounting or Advancement need to be assigned in Settings > Configurations > Accounting
* Once this module, Create Invoice options on Sales Order will list Advance Method (Fixed and Percentage) only for the first invoice creation (was freely available without this module).
* If user select the first invoice as Advance invoice with percentage or fixed amount, the percentage will be kept in Advance Percentage field in that Sales Order.
* All the followings invoices from that Sales Order will be deducted with the percentage specified on Sales order
* Accounting for invoice will be posted in regards to the deducted amount.

    """,
    "init_xml": [],
    'update_xml': ['all_view.xml','partner_view.xml','res_config_view.xml',
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
