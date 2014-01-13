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


import openerp.netsvc
from openerp.osv import osv, fields
from openerp.tools.translate import _
import decimal_precision as dp

class purchase_order(osv.osv):

    _inherit = "purchase.order"

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context)
        orders = self.browse(cr, uid, ids, context=context)
        for order in orders:
            if order.requisition_id:
                self.pool.get('purchase.requisition').tender_done(cr, uid, [order.requisition_id.id], context)
        return True
    