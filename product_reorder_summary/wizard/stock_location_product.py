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
    #Overriding from stock/wizard/stock.location.product
    def action_open_window(self, cr, uid, ids, context=None):
        res = super(stock_location_product, self).action_open_window(cr, uid, ids,  context=context)
        
        location_products = self.read(cr, uid, ids, ['reorder_flag'], context=context)
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
