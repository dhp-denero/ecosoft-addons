# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Ecosoft Co., Ltd. (http://ecosoft.co.th).
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
    'name' : "Product Reorder Point",
    'author' : 'DBuasri',
    'summary': 'Summary Reorder point of product by location',
    'description': """
*Enhance Feature #1048, 
    Product Tree View to also show Reorder Point and Difference for its selected location.
* *  Ecosof-addons/
* * * product_reorder_summary module
* * * 1. New qty_reorder,qty_diff_reroder Name field
* * * 2. New _get_reorder_summary method for summary Min QTY in Reorder Point Rule and QTY is difference between QTY on hand  and Min QTY 
* * * 3. New _get_location method for retrieve location ids follow user selected
* * * product_reorder_summary/Wizard
* * * 1. New reorder_flag Name field
* * * 2. Override action_open_window method, add domain for checking product has reorder point rule  
    """,
    'category': 'Sales',
    'sequence': 8,
    'website' : 'http://www.ecosoft.co.th',
    'images' : [],
    'depends' : ['product','stock'],
    'demo' : [],
    'data' : [
              'product_view.xml',
              'wizard/stock_location_product_view.xml',
    ],
    'test' : [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
