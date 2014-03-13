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
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


class product_stock_card_location(osv.osv_memory):
    _name = "product_stock.card.location"
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location', required=False, domain=[('usage', '=', 'internal')]),
        'from_date': fields.datetime('From Date'),
        'to_date': fields.datetime('To Date'),
        }

    def open_stock_card(self, cr, uid, ids, context=None):
#         view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'product_stock_card', 'view_product_stock_card_tree')
#         view_id = view_ref and view_ref[1] or False,
        ctx = {'search_default_product_id': [context['active_id']],
                'default_product_id': context['active_id'],
                }
        stock_card_location = self.read(cr, uid, ids, ['location_id', 'from_date', 'to_date'], context=context)
        domain = []
        if stock_card_location:
            if stock_card_location[0]['location_id']:
                ctx.update({'location': stock_card_location[0]['location_id'][0]})
                domain += ['|', ('location_id', '=', stock_card_location[0]['location_id'][0]), ('location_dest_id', '=', stock_card_location[0]['location_id'][0])]
            else:
                domain += [('type', 'not in', ('move', False))]

            if stock_card_location[0]['from_date']:
                start = datetime.strptime(stock_card_location[0]['from_date'], "%Y-%m-%d %H:%M:%S")
                domain += [('date', '>=', start.strftime('%Y-%m-%d'))]
            if stock_card_location[0]['to_date']:
                stop = datetime.strptime(stock_card_location[0]['to_date'], "%Y-%m-%d %H:%M:%S")
                stop = stop + relativedelta(days=1)
                domain += [('date', '<=', stop.strftime('%Y-%m-%d'))]
        return {
                'name': _('Stock Card By Location'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'product.stock.card',
                'type': 'ir.actions.act_window',
                'context': ctx,
                'domain': domain,
                }

product_stock_card_location()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
