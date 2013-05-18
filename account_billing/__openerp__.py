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
    'name' : 'Billing Process',
    'version' : '1.0',
    'author' : 'Kitti U.',
    'summary': 'Adding billing process before payment',
    'description': """
Billing Process
======================================================
In some countries, at least for Thailand, there is a customary practice for companies to collect money 
from their customers only once in a month. For example, the customer has 3 payments due in a given month, 
the vendor or billing company should group all the due AR Invoices in a document call Billing Document 
and issue it with all the invoices consolidated to the customer on the Billing Day. 
The customer will be paying based on the payable amount shown in Billing Document in the following month.
    """,
    'category': 'Accounting & Finance',
    'sequence': 4,
    'website' : 'http://www.ecosoft.co.th',
    'images' : [
                #'images/customer_payment.jpeg',
                #'images/journal_voucher.jpeg',
                #'images/sales_receipt.jpeg',
                #'images/supplier_voucher.jpeg'
                ],
    'depends' : ['account','account_voucher','account_check_writing'],
    'demo' : [],
    'data' : [
        'security/ir.model.access.csv',
        'account_billing_sequence.xml',
        'account_billing_workflow.xml',
        'account_billing_view.xml',
        'voucher_payment_receipt_view.xml',
        'account_billing_data.xml',
    ],
    'test' : [
        #'test/case5_suppl_usd_usd.yml',
        #'test/account_voucher.yml',
        #'test/sales_receipt.yml',
        #'test/sales_payment.yml',
        #'test/account_voucher_report.yml',
        #'test/case1_usd_usd.yml',
        #'test/case2_usd_eur_debtor_in_eur.yml',
        #'test/case2_usd_eur_debtor_in_usd.yml',
        #'test/case3_eur_eur.yml',
        #'test/case4_cad_chf.yml',
        #'test/case_eur_usd.yml',
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
