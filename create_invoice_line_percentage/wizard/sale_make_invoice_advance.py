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
import openerp.addons.decimal_precision as dp

class sale_advance_payment_inv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"

    _columns = {
        'line_percent':fields.float('Installment', digits_compute= dp.get_precision('Account'),
            help="The % of installment to be used to calculate the quantity to invoice"),
        'advance_payment_method':fields.selection(
            [('all', 'Invoice the whole sales order'), ('percentage','Percentage'),
             ('line_percentage','Line Percentage'),
             ('fixed','Fixed price (deposit)'),
                ('lines', 'Some order lines')],
            'What do you want to invoice?', required=True,
            help="""Use All to create the final invoice.
                Use Percentage to invoice a percentage of the total amount.
                Use Line Percentage to invoice a percentage of lines from Sales Order.
                Use Fixed Price to invoice a specific amount in advance.
                Use Some Order Lines to invoice a selection of the sales order lines."""),
    }
    
    def create_invoices(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context)
        # Additional case, Line Percentage
        if wizard.advance_payment_method == 'line_percentage':
            # Getting Sale Order Line IDs of this SO
            sale_obj = self.pool.get('sale.order')
            sale_ids = context.get('active_ids', [])
            orders = sale_obj.browse(cr, uid, sale_ids)
            order_line_ids = []
            for order in orders:
                for order_line in order.order_line:
                    order_line_ids.append(order_line.id)
            # Assign them into active_ids
            context.update({'active_ids': order_line_ids})
            context.update({'line_percent': wizard.line_percent})
            sale_order_line_make_invoice_obj = self.pool.get('sale.order.line.make.invoice')
            res = sale_order_line_make_invoice_obj.make_invoices(cr, uid, ids, context=context)
            # Update invoice
            self.pool.get('account.invoice').button_compute(cr, uid, [res.get('res_id')], context=context)
            return res
        
        return super(sale_advance_payment_inv, self).create_invoices(cr, uid, ids, context=context)
    
    
sale_advance_payment_inv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
