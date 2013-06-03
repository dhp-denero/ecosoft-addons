from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
from common import AdditionalDiscountable

class sale_order(AdditionalDiscountable, osv.osv):

    _inherit = 'sale.order'

    _tax_column = 'tax_id'
    _line_column = 'order_line'

    def _amount_all(self, *args, **kwargs):
        return self._amount_all_generic(sale_order, *args, **kwargs)

    _columns = {
            # Additional Discount Feature
            'add_disc':fields.float('Additional Discount(%)',digits=(4,6), readonly=True, states={'draft': [('readonly', False)]}),
            'add_disc_amt': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Additional Disc Amt',
                                            store =True,multi='sums', help="The additional discount on untaxed amount."),
            'amount_untaxed': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Untaxed Amount',
                                              store = True,multi='sums', help="The amount without tax."),
            'amount_net': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Net Amount',
                                              store = True,multi='sums', help="The amount after additional discount."),
            'amount_tax': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Taxes',
                                          store = True,multi='sums', help="The tax amount."),
            'amount_total': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Total',
                                            store = True,multi='sums', help="The total amount."),
            # Advance Feature
            'advance_percentage': fields.float('Advance (%)', digits=(16,2), required=False, readonly=False),
        }

    _defaults = {
            'add_disc': 0.0,
        }

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
        """Add a discount in the invoice after creation, and recompute the total
        """
        order = self.browse(cr, uid, ids[0], context=context)
        inv_obj = self.pool.get('account.invoice')
        # create the invoice
        inv_id = super(sale_order, self).action_invoice_create(cr, uid, ids, grouped, states, date_invoice, context=context)
        # modify the invoice
        inv_obj.write(cr, uid, [inv_id], {'add_disc': order.add_disc or 0.0,
                                          'name': order.client_order_ref or ''}, 
                                          context)
        inv_obj.button_compute(cr, uid, [inv_id])
        return inv_id

