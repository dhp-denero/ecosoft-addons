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

import netsvc
from osv import osv, fields
from tools.translate import _
import openerp.addons.decimal_precision as dp
#class product_category(osv.osv):
#    
#    _inherit = "product.category"
#    _columns = {
#        'product_cat_code': fields.char('Category Code', size=3, help="Cateory Code Max Size = 3 characters"),
#    }
#
#product_category()

class product_product(osv.osv):

    #There are some copy from  get_product_available of stock/product 
    def _get_location(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        location_obj = self.pool.get('stock.location')
        warehouse_obj = self.pool.get('stock.warehouse')
        shop_obj = self.pool.get('sale.shop')
        
        if context.get('shop', False):
            warehouse_id = shop_obj.read(cr, uid, int(context['shop']), ['warehouse_id'])['warehouse_id'][0]
            if warehouse_id:
                context['warehouse'] = warehouse_id

        if context.get('warehouse', False):
            lot_id = warehouse_obj.read(cr, uid, int(context['warehouse']), ['lot_stock_id'])['lot_stock_id'][0]
            if lot_id:
                context['location'] = lot_id

        if context.get('location', False):
            if type(context['location']) == type(1):
                location_ids = [context['location']]
            elif type(context['location']) in (type(''), type(u'')):
                location_ids = location_obj.search(cr, uid, [('name','ilike',context['location'])], context=context)
            else:
                location_ids = context['location']
        else:
            location_ids = []
            wids = warehouse_obj.search(cr, uid, [], context=context)
            if wids:
                for w in warehouse_obj.browse(cr, uid, wids, context=context):
                    location_ids.append(w.lot_stock_id.id)

        # build the list of ids of children of the location given by id
        if context.get('compute_child',True):
            child_location_ids = location_obj.search(cr, uid, [('location_id', 'child_of', location_ids)])
            location_ids = child_location_ids or location_ids
        
        return location_ids
    
    def _get_reorder_summary(self, cr, uid, ids, name, arg, context=None):
         
        if not ids:
            ids = self.search(cr, uid, [])
        res = {}.fromkeys(ids, {'qty_reorder':False,'qty_diff_reroder':False})
        if not ids:
            return res
        
        location_ids = self._get_location(cr, uid, ids, context)
        
        reorder_obj = self.pool.get('stock.warehouse.orderpoint')
        
        if location_ids:#location done,it will filter by product and location
            reorder_ids = reorder_obj.search(cr, uid,[('product_id', 'in', ids),('location_id','in',location_ids)])
        else:
            reorder_ids = reorder_obj.search(cr, uid,[('product_id', 'in', ids)])
        
        #Get Reorder Point info        
        reorder_info = reorder_obj.browse(cr, uid, reorder_ids, context=context)
        
        # this will be a dictionary of the product UoM by product id
        product2uom = {}
        uom_ids = []
        for product in self.read(cr, uid, ids, ['uom_id'], context=context):
            product2uom[product['id']] = product['uom_id'][0]
            uom_ids.append(product['uom_id'][0])
        # this will be a dictionary of the UoM resources we need for conversion purposes, by UoM id
        uoms_o = {}
        for uom in self.pool.get('product.uom').browse(cr, uid, uom_ids, context=context):
            uoms_o[uom.id] = uom
            
        # Get the missing UoM resources
        uom_obj = self.pool.get('product.uom')
        uoms = [uom_id.product_uom.id for uom_id in reorder_info]
        if context.get('uom', False):
            uoms += [context['uom']]
        uoms = filter(lambda x: x not in uoms_o.keys(), uoms)
        if uoms:
            uoms = uom_obj.browse(cr, uid, list(set(uoms)), context=context)
            for o in uoms:
                uoms_o[o.id] = o
                 
        for obj in reorder_info:
            #Get Quantity On Hand
            product_info = self.browse(cr, uid, [obj.product_id.id], context=context)
            # Sum the reorder point QTY
            amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[obj.product_uom.id], obj.product_min_qty,
                     uoms_o[context.get('uom', False) or product2uom[obj.product_id.id]], context=context)
            #Put reorder point and difference into return object
            res[obj.product_id.id]={'qty_reorder':res[obj.product_id.id]['qty_reorder']+amount
                                    ,'qty_diff_reroder':product_info[0].qty_available -  (res[obj.product_id.id]['qty_reorder']+amount)}
#             item =  res[456]
#             item['qty_reorder']= obj.product_min_qty
#             res[456]=item
#             res[obj.product_id.id]['qty_diff_reroder']=0.0
            
#         summary = {obj.product_id.id: math.fsum(o2m for o2m in obj.product_min_qty)
#             for obj in reorder_obj.browse(cr, uid, reorder_ids, context=context)}
#         
#         res.update(summary)
            
        return res
    
    _inherit = "product.product"
    _columns = {
        'qty_reorder': fields.function(_get_reorder_summary, type='float', string='Reorder Point',multi="qty_reorder",digits_compute=dp.get_precision('Product Unit of Measure'),store=False),
        'qty_diff_reroder': fields.function(_get_reorder_summary, type='float', string='Difference',multi="qty_reorder",digits_compute=dp.get_precision('Product Unit of Measure')),
    }
product_product()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
