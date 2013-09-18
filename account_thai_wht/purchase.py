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
import types
import netsvc
from osv import osv, fields
from tools.translate import _

class purchase_order(osv.osv):
    
    _inherit="purchase.order"
    
    def _check_tax(self, cr, uid, ids, context=None):
        # loop through each lines, check if tax different.
        if not isinstance(ids, types.ListType): # Make it a list
            ids = [ids]
        orders = self.browse(cr, uid, ids, context=context)
        for order in orders:
            i = 0
            tax_ids = []
            for line in order.order_line:
                next_line_tax_id = [x.id for x in line.taxes_id]
                if i > 0 and set(tax_ids) != set(next_line_tax_id):
                    raise osv.except_osv(
                        _('Error!'),
                        _('You cannot create lines with different taxes!'))
                tax_ids = next_line_tax_id
                i += 1
        return True
        
    def write(self, cr, uid, ids, vals, context=None):
        res = super(purchase_order, self).write(cr, uid, ids, vals, context=context)
        self._check_tax(cr, uid, ids, context=context)
        return res

purchase_order()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
