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
    'name': 'Supplier Credit Limit',
    'version': '1.0',
    'description': """Supplier Credit Limit
    When approving a Purchase Order it computes the sum of:
        * The debit we have to pay
        * The amount of Purchase Orders aproved but not yet invoiced
        * The invoices that are in draft state
        * The amount of the Purchase Order to be approved
    and compares it with the credit limit of the partner. If the
    credit limit is less it does not allow to approve the Purchase
    Order""",
    'author': 'ECOSOFT',
    'website': 'http://www.ecosoft.co.th/',
    'depends': ['purchase'],
    'init_xml': [],
    'update_xml': ['purchase_workflow.xml',
                   'partner_view.xml'
                   ],
    'demo_xml': [],
    'test': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
