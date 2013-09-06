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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class mrp_bom(osv.osv):
    
    _inherit = "mrp.bom"
    
    def action_product_bom_create(self, cr, uid, ids, data, context=None):
        if context == None:
            context = {}
        product_obj = self.pool.get('product.product')
        # Create product
        product_id = product_obj.create(cr, uid, {
                'name': data['product_name'],          
                'categ_id': data['product_categ_id'][0],    
                'uom_id': data['product_uom_id'][0],     
                'uom_po_id': data['product_uom_id'][0],      
                'type': data['type'],          
                'procure_method': data['procure_method'],          
                'supply_method': data['supply_method'],          
                'valuation': data['valuation'],
                'sale_ok': False,
                'purchase_ok': False,
            })
        # Create BOM
        product = product_obj.browse(cr, uid, product_id)
        bom_id = self.create(cr, uid, {
                'product_id': product_id,       
                'name': data['product_name'],   
                'product_qty': 1.0,
                'product_uom': data['product_uom_id'][0],
                'type': 'normal',
            })
        
        # Create BOM Line
        for product in product_obj.browse(cr, uid, ids):
            self.create(cr, uid, {
                    'bom_id': bom_id,
                    'product_id': product.id,       
                    'name': product.name,
                    'product_qty': 1.0,
                    'product_uom': product.uom_id.id,
                    'type': 'normal',
                })
        return product_id, bom_id

mrp_bom()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
