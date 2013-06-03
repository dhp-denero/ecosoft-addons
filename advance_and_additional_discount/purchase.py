from osv import osv, fields
import decimal_precision as dp
from tools.translate import _
from common import AdditionalDiscountable

class purchase_order(AdditionalDiscountable, osv.osv):

    _inherit = "purchase.order"
    _description = "Purchase Order"

    _tax_column = 'taxes_id'
    _line_column = 'order_line'


    def _amount_all(self, *args, **kwargs):
        return self._amount_all_generic(purchase_order, *args, **kwargs)

    _columns={
            'add_disc': fields.float('Additional Discount(%)', digits=(4,6),
                                     states={'confirmed': [('readonly',True)],
                                             'approved': [('readonly',True)],
                                             'done': [('readonly',True)]}),
            'add_disc_amt': fields.function(_amount_all, method=True, store=True, multi='sums',
                                            digits_compute= dp.get_precision('Sale Price'),
                                            string='Additional Disc Amt',
                                            help="The additional discount on untaxed amount."),
            'amount_net': fields.function(_amount_all, method=True, store=True, multi='sums',
                                          digits_compute= dp.get_precision('Sale Price'),
                                          string='Net Amount',
                                          help="The amount after additional discount."),
            'amount_untaxed': fields.function(_amount_all, method=True, store=True, multi="sums",
                                              digits_compute= dp.get_precision('Purchase Price'),
                                              string='Untaxed Amount',
                                              help="The amount without tax"),
            'amount_tax': fields.function(_amount_all, method=True, store=True, multi="sums",
                                          digits_compute= dp.get_precision('Purchase Price'),
                                          string='Taxes',
                                          help="The tax amount"),
            'amount_total': fields.function(_amount_all, method=True, store=True, multi="sums",
                                         digits_compute= dp.get_precision('Purchase Price'),
                                         string='Total',
                                         help="The total amount"),
            }

    _defaults={
               'add_disc': 0.0,
               }

    def action_invoice_create(self, cr, uid, ids, context=None):
        """Add a discount in the invoice after creation, and recompute the total
        """
        inv_obj = self.pool.get('account.invoice')
        for order in self.browse(cr, uid, ids, context):
            # create the invoice
            inv_id = super(purchase_order, self).action_invoice_create(cr, uid, ids, context)
            # modify the invoice
            inv_obj.write(cr, uid, [inv_id], {'add_disc': order.add_disc or 0.0}, context)
            inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)
            res = inv_id
        return res

