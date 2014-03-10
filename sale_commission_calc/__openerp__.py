# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Sales Commission Calculations",
    'author': 'Ecosoft',
    'summary': '',
    'description': """
Commission Management.
======================

By using a Commission Calculation Worksheet, a salesperson/team will be able to calculate their commission in 1 period.
In short, one worksheet per salesperson/team per period. Given invoice has been paid, system can generate supplier invoice (as commisison) for that salesperson/team.

Key Features
------------
    * Manage Commission Rules
    * Manage Sale Teams / Salesperson VS Commission Rules
    * Invoices created, will be marked with those Sale Team / Salesperson and the Commission Rule to apply
    * Create Commission Work Sheet from open invoices by period
    * Create Supplier Invoice from Commission Work Sheet
    * Manage security, sales people can see only their own worksheet, while managers can manage all.

Available Rule Types
--------------------
    * Fixed Commission Rate
    * Product Category Commission Rate
    * Product Commission Rate
    * Commission Rate By Amount
    * Commission Rate By Monthly Accumulated Amount




TODO:
- Commission Worksheet, not deletable if already paid.
- Set to Draft, after confirmed. If not yet paid.
- Invoice created from SO, should have the Team/Commission
- Group Security
- Wizard to create commission worksheets for all sales and team with rules.
- Condition only not over dued invoice
- Template commission of all types
- Consider Refund

How to count due date?
- Use Invoice Due Date <-> Last Payment
- Use Invoice Date + Cust's Payment Term
- 1st Billing Date + Cust's Payment Term <-> Last Payment
- MH: 1st Collection Due Date <-> Last Payment

""",
    'category': 'Sales',
    'sequence': 8,
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': ['product', 'sale', 'account'],
    'demo': [],
    'init_xml': [
          'commission_data.xml',
          'product_data.xml',
    ],
    'data': [
          'commission_calc_view.xml',
          'account_invoice_view.xml',
          'commission_calc_sequence.xml',
          'product_view.xml',
          'wizard/update_invoice_commission_view.xml',
    ],
    'test': [
        #'/test/commission_calc_demo.yml'
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
