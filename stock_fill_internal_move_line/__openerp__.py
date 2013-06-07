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
    'name' : 'Sale Stock Extension for MH',
    'version' : '1.0',
    'author' : 'Kitti U.',
    'summary': 'Miscellenous Extension to Sale Stock Module for MH',
    'description': """

In MH, step before deliver product is as following

1. Complete Sale Order create Delivery Order
2. Stock people do internal move from "Stock" location to "Output" location.
3. The Delivery Order's Source Location should be "Output" location.

Modification List:

* Adding new "Location Delivery Source" in Warehouse
* If DO is created by Sales Order, force Source location to "Location Delivery Source".
* In Internal Move window, add a feature to automatically list all the pending move finished goods.
* 2 new fields 1) Stock at Origin and 2) Stock at Destination

    """,
    'category': 'Warehouse Management',
    'website' : 'http://www.ecosoft.co.th',
    'images' : [],
    'depends' : ['stock','sale_stock'],
    'demo' : [],
    'data' : [
        'wizard/stock_fill_move_view.xml',
        'stock_view.xml',
    ],  
    'test' : [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
