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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc

class mrp_bom(osv.osv):
    
    _inherit = "mrp.bom"
    
    def action_product_bom_create(self, cr, uid, product_ids, data, context=None):
        if context == None:
            context = {}
        products = context.get('products', False)
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
        for product in product_obj.browse(cr, uid, product_ids):
            self.create(cr, uid, {
                    'bom_id': bom_id,
                    'product_id': product.id,       
                    'name': product.name,
                    'product_qty': products and products[product.id] and products[product.id]['product_qty'] or 1.0,
                    'product_uom': products and products[product.id] and products[product.id]['product_uom'] or product.uom_id.id,
                    'type': 'normal',
                })
        return product_id, bom_id
    
    # Create from Order Line
    def action_product_bom_create_from_order_line(self, cr, uid, order_ids, data, context=None):
        if context == None:
            context = {}
        # Get list of products
        assert len(order_ids) == 1, 'This option should only be used for a single id at a time.'
        order = self.pool.get('sale.order').browse(cr, uid, order_ids[0])
        ids = []
        products = {}
        for line in order.order_line:
            if line.product_id:
                ids.append(line.product_id.id)
                products[line.product_id.id] = {
                                        'name': line.product_id.name,
                                        'product_qty': line.product_uom_qty,
                                        'product_uom': line.product_uom.id,
                                        }
        if len(ids) == 0:
            raise osv.except_osv(_('Error!'), _('No Product Lines!'))
        ctx = context.copy()
        ctx.update({'products': products})
        return self.action_product_bom_create(cr, uid, ids, data, context=ctx)

mrp_bom()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
