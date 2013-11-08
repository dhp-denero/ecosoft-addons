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
from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_location_product(osv.osv_memory):
    _inherit = "stock.location.product"
    _description = "Products by Location"
    _columns = {
        #Show CheckBox in view
        'reorder_flag': fields.boolean('Show Product in Reorder'), 
    }
    
    def _get_reorder_action(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        
        if context is None:
            context = {}
        location_products = self.read(cr, uid, ids, ['from_date', 'to_date'], context=context)
        
        result = mod_obj.get_object_reference(cr, uid, 'product_reorder_summary', 'act_product_reorder_summary')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['context'] =  {'location': context['active_id'],
                       'from_date': location_products[0]['from_date'],
                       'to_date': location_products[0]['to_date']}
        result['domain']= [tuple(['type', '<>', 'service'])]
        return result
    
    #Overriding from stock/wizard/stock.location.product
    def action_open_window(self, cr, uid, ids, context=None):       
        
        location_products = self.read(cr, uid, ids, ['reorder_flag','negative_flag'], context=context)
        
        res = super(stock_location_product, self).action_open_window(cr, uid, ids,  context=context)
            
        if location_products:
            res['context'].update({'reorder_flag':location_products[0]['reorder_flag']})
            
        if not res.get('domain',False): 
            res['domain'] =[]
            
        if location_products[0]['reorder_flag']:        
            location_obj=  shop_obj = self.pool.get('product.product')
            location_ids = location_obj._get_location(cr, uid, ids, context=res['context'])
            # Data filter only "Reorder Point Rule"     
            res['domain']+=[tuple(['orderpoint_ids','<>',False])]+[tuple(['orderpoint_ids.location_id','in',location_ids])]
            
        return res
stock_location_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
