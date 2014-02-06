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

class stock_location_product(osv.osv_memory):
    _inherit = "stock.location.product"
    _columns = {
        'location_id': fields.many2one('stock.location', string='Location',),
    }

    def action_open_window(self, cr, uid, ids, context=None):
        
        def get_product_id(lines, product_field):
            field_name = product_field.pop()           
            if product_field:
                for line  in lines:
                    return get_product_id((eval('line.'+field_name)), product_field)
            else:
                res = []
                for line in lines:
                    res.append((eval('line.'+ field_name +'.id')))               
            return res
    
        res = super(stock_location_product, self).action_open_window(cr, uid, ids,  context=context)
        product_field_lv = context.get('product_field',False)
        product_field_lv.reverse()
        model_name  = context.get('active_model',False)
        active_id = context.get('active_id',False)
        
        if  product_field_lv and model_name and active_id:
            obj = self.pool.get(model_name)
            lines = obj.browse(cr, uid, [active_id],context)
            product_ids = get_product_id(lines, product_field_lv)            
            display_conditions = self.read(cr, uid, ids, ['location_id'], context=context)
            if display_conditions:
                ctx = res.get('context', {})
                #add filter by location
                if  display_conditions[0]['location_id']:
                    ctx.update({'location': display_conditions[0]['location_id'][0]})

                res.update({'context': ctx})
                
                #add filter by product id
                domain =  res.get('domain',{})
                res['domain'] += [tuple(['id','=',product_ids])]
                res.update({'domain': domain})
                
        return res
    
stock_location_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
