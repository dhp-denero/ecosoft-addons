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
    'name': "Sales Commission Calculations (In Progress)",
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
    * Process: Update Invoice Commission, go to each invoice that has not been assigned commission and assign it.
    * Process: Generate Commission Worksheet(s), look through team/commission worksheet that has not been created to date, and create them.
    * Feature: Ability to force allow/skip for the given commission regardless of the calculation result.

Available Rule Types
--------------------
    * Fixed Commission Rate
    * Product Category Commission Rate
    * Product Commission Rate
    * Commission Rate By Amount
    * Commission Rate By Monthly Accumulated Amount

Available Last Payment Date (to be eligible for commission)
-----------------------------------------------------------
    * Normal Invoice Due Date
    * Invoice Date + Customer Payment Term
    * Period + Months
    
TODO:
- Make sure that Refund Invoice will be used to deduct the commission (we may never pay back to cust?)
- Commission Worksheet, not deletable if already paid.
- Set to Draft, after confirmed. If not yet paid.
- Invoice created from SO, should have the Team/Commission
- Group Security
- Template commission of all types
- Consider Refund
- Make it easy to manage and view and grouping in worksheet
- Need to make method "check_commission_line_status()" a scheduled process, this is to ensure that wait_pay is working.
BUG:
- If still group by in worksheet, when generate invoice will have error.
- Why Due Payment Date always True???
MH
- Seperate VAT and No-VAT commission amount
- Product Price < Come Benchmark Amount that won't get commission
- Table for % by Product for easy update
- Progressive Rate for Product Commission
- Ability to edit commission amount
SQP
===
* Allow salesperson to see their own worksheet, all readonly
* Manager to be able to edit / every windows
* User to see only worksheets, but can confirm and create invoice

** In SO, will have a new field to says it is completed / amount -> Before Tax but after Discount
** Payment Detail to tell that it due, use Last Payment Item
** Add SO / Amount Overwrite in Worksheet Details
* p'Som to send commission approval form
** Add adjustment table (with checkbox) -> Commission Discount + Description in footer of worksheet.

* SO window, to have adjusted amount that will be used to determine paid mode
- Rule > Commission by margin, start from SO will have a new field "Cost"
  - This field will be visible only for selected salesperson

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
          'wizard/create_commission_invoice_view.xml',
          'commission_calc_view.xml',
          'commission_rule_view.xml',
          'account_invoice_view.xml',
          'commission_calc_sequence.xml',
          'product_view.xml',
          'wizard/update_invoice_commission_view.xml',
          'wizard/generate_commission_worksheet_view.xml',
    ],
    'test': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
