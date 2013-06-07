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

from osv import fields, osv

class stock_move(osv.osv):
    
    _inherit = "stock.move"
    
    def _get_stock_real(self, cr, uid, ids, name, args, context=None):
        res = {}
        product_obj = self.pool.get('product.product')
        for line in self.browse(cr, uid, ids, context=context):
            c = context.copy()
            c['uom'] = line.product_uom.id
            if name == 'location_stock_real':
                c['location'] = line.location_id.id
                product = product_obj.browse(cr, uid, line.product_id.id, context=c)
                res[line.id] = product.qty_available
            elif name == 'location_dest_stock_real':
                c['location'] = line.location_dest_id.id
                product = product_obj.browse(cr, uid, line.product_id.id, context=c)
                res[line.id] = product.qty_available
        return res
    
    _columns = {
        'location_stock_real': fields.function(_get_stock_real, string="Stock at Origin", type="float", store=True, readonly=True),
        'location_dest_stock_real': fields.function(_get_stock_real, string="Stock at Destination", type="float", store=True, readonly=True),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
