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
    'name' : 'No Deletion for Documents with assigned number',
    'version' : '1.0',
    'author' : 'Kitti U.',
    'summary': 'No Deletion for Documents with assigned number, since it will break the accounting control concept.',
    'description': """

The objects includes:

* sale.order (name)
* purchase.order (name)
* account.invoice (number)
* account.voucher (number)
* account.billing (number)
* stock.picking (name)
* stock.picking.out (name)
* stock.picking.in (name)
* payment.register (number)

    """,
    'category': 'Accounting',
    'website' : 'http://www.ecosoft.co.th',
    'images' : [],
    'depends' : ['sale',
                 'purchase',
                 'account',
                 'account_voucher',
                 'account_billing',
                 'stock',
                 'payment_register'],
    'demo' : [],
    'data' : [
    ],
    'test' : [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
