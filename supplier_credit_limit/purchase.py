#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from osv import fields, osv
from tools.translate import _


class purchase_order(osv.osv):

    _inherit = "purchase.order"

    def check_limit(self, cr, uid, ids, context=None):
        for order_id in ids:
            processed_order = self.browse(cr, uid, order_id, context=context)
            # Purchase has no invoice type "Before Delivery"
#             if processed_order.order_policy == 'prepaid':
#                 continue
            partner = processed_order.partner_id
            debit = partner.debit
            # We sum from all the purchase orders that are aproved, the purchase order lines that are not yet invoiced
            order_obj = self.pool.get('purchase.order')
            filters = [('partner_id', '=', partner.id), ('state', '<>', 'draft'), ('state', '<>', 'cancel')]
            approved_invoices_ids = order_obj.search(cr, uid, filters, context=context)
            approved_invoices_amount = 0.0
            for order in order_obj.browse(cr, uid, approved_invoices_ids, context=context):
                for order_line in order.order_line:
                    if not order_line.invoiced:
                        approved_invoices_amount += order_line.price_subtotal
            # We sum from all the invoices that are in draft the total amount
            invoice_obj = self.pool.get('account.invoice')
            filters = [('partner_id', '=', partner.id), ('state', '=', 'draft')]
            draft_invoices_ids = invoice_obj.search(cr, uid, filters, context=context)
            draft_invoices_amount = 0.0
            for invoice in invoice_obj.browse(cr, uid, draft_invoices_ids, context=context):
                draft_invoices_amount += invoice.amount_total
            available_credit = partner.credit_limit - debit - approved_invoices_amount - draft_invoices_amount
            if processed_order.amount_total > available_credit:
                title = 'Credit Over Limits!'
                msg = 'Can not confirm Purchase Order, the client does not have enough credit.'
                title = 'Credit Limit Exceed!'
                msg = u'Can not confirm the order since there is no sufficient credit left with supplier'
                raise osv.except_osv(_(title), _(msg))
                return False
        return True

purchase_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

