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
from lxml import etree

class product_product(osv.osv):

    
    def _search_reorder_summary(self, cr, uid, obj, name, args, domain=None, context=None):
        
        if not len(args) and len(args[0]) <3:
            return []
        
        res=[]
        reorder_obj = self.pool.get('stock.warehouse.orderpoint')
         
        location_ids = self._get_location(cr, uid, [], context)
                  
        if location_ids:#location done,it will filter by product and location
            reorder_ids = reorder_obj.search(cr, uid,[('location_id','in',location_ids)])
        else:
            reorder_ids = reorder_obj.search(cr, uid,[])
        
        #Get Product in Reorder Point Table        
        reorder_info = reorder_obj.read(cr, uid, reorder_ids,['product_id'], context=context)
         
        ids = [x['product_id'][0] for x in reorder_info]
        product_reorder = self._get_common_reorder(cr, uid, ids, name, args, True, context)
       
        for id in ids:
            #Concatenate is condition 
            con = str(product_reorder[id]["qty_diff_reroder"]) + str(args[0][1]) + str(args[0][2])
            if eval(con):
                res.append(id)
        return [('id', 'in', res)]
    
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
    
    def _get_common_reorder(self, cr, uid, ids, name, arg, is_search=False, context=None):
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
#             if is_search:
#                 res[obj.product_id.id]={'qty_reorder':res[obj.product_id.id]['qty_reorder']+amount
#                                     ,'qty_diff_reroder':product_info[0].qty_available - (res[obj.product_id.id]['qty_reorder']+amount)
#                                     ,}
#             else:
            res[obj.product_id.id]={'qty_reorder':res[obj.product_id.id]['qty_reorder']+amount
                                ,'qty_diff_reroder':product_info[0].qty_available - (res[obj.product_id.id]['qty_reorder']+amount)
                                ,}
        return res
    
    def _get_reorder_summary(self, cr, uid, ids, name, arg, context=None):
        return self._get_common_reorder(cr, uid, ids, name, arg, is_search=False, context=context)
    
    #Overriding from product_product Class
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        
        result = super(product_product, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if not context:
            context={}
            
        doc = etree.XML(result['arch'])
        for node in doc.xpath("//tree[@string='Products']"):            
            if context.get('reorder_flag',False) : #Set red color if QTY of product less than reorder point
                node.set('colors', "red:qty_diff_reroder and qty_diff_reroder<0;blue:virtual_available>=0 and state in ('draft', 'end', 'obsolete');black:virtual_available>=0 and state not in ('draft', 'end', 'obsolete')")
        result['arch'] = etree.tostring(doc)
 
        return result
    
    _inherit = "product.product"
    _columns = {
        'qty_reorder': fields.function(_get_reorder_summary, type='float', string='Reorder Point',multi="qty_reorder",digits_compute=dp.get_precision('Product Unit of Measure'),store=False),
        'qty_diff_reroder': fields.function(_get_reorder_summary, type='float', fnct_search=_search_reorder_summary, string='Difference',multi="qty_reorder",digits_compute=dp.get_precision('Product Unit of Measure')),
    }
    
product_product()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
