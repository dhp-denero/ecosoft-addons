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
from openerp.tools.translate import _

class stock_picking(osv.osv):

    _inherit = "stock.picking"

    _columns = {
        'create_uid':  fields.many2one('res.users', 'Creator', readonly=True),
    }
    
stock_picking()


class stock_move(osv.osv):

    _inherit = "stock.move"

    def _default_location_destination(self, cr, uid, context=None):
        if context is None: 
            context = {}
        if context.get('location_dest_id', False):
            location_dest_id = context.get('location_dest_id')
            return location_dest_id
        return super(stock_move, self)._default_location_destination(cr, uid, context=context)

    def _default_location_source(self, cr, uid, context=None):
        if context is None: 
            context = {}
        if context.get('location_id', False):
            location_id = context.get('location_id')
            return location_id
        return super(stock_move, self)._default_location_source(cr, uid, context=context)

    _defaults = {
        'location_id': _default_location_source,
        'location_dest_id': _default_location_destination,
    }
    
    def onchange_move_type(self, cr, uid, ids, type, context=None):
        if context.get('simplified_move', False):
            return True
        return super(stock_move, self).onchange_move_type(cr, uid, ids, type, context=context)
    
stock_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
