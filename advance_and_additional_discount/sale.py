from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
from common import AdditionalDiscountable

class sale_order(AdditionalDiscountable, osv.osv):

    _inherit = 'sale.order'

    _tax_column = 'tax_id'
    _line_column = 'order_line'
    
    def _num_invoice(self, cursor, user, ids, name, args, context=None):
        '''Return the amount still to pay regarding all the payment orders'''
        if not ids:
            return {}
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            res[sale.id] = len(sale.invoice_ids)
        return res
    
    def _amount_all(self, *args, **kwargs):
        return self._amount_all_generic(sale_order, *args, **kwargs)



    def _get_amount_retained(self, cr, uid, ids, field_names, arg, context=None):
        if context is None:
            context = {}  
            
        res = {}     
        currency_obj = self.pool.get('res.currency')
        sale_obj = self.pool.get('sale.order')

        # Account Retention
        prop = self.pool.get('ir.property').get(cr, uid, 'property_account_retention_customer', 'res.partner', context=context)
        prop_id = prop and prop.id or False
        account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, False, prop_id)
        if not account_id:
            for id in ids:
                res[id] = 0.0
        else:
            for id in ids:
                order = sale_obj.browse(cr, uid, id)
                cr.execute("""select sum(l.debit-l.credit) as amount_debit
                                from account_move_line l
                                inner join
                                (select order_id, move_id from account_invoice inv
                                inner join sale_order_invoice_rel rel 
                                on inv.id = rel.invoice_id and order_id = %s) inv
                                on inv.move_id = l.move_id
                                where state = 'valid'
                                and account_id = %s
                                group by order_id
                              """, (order.id,account_id))
                amount_debit = cr.fetchone() and cr.fetchone()[0] or 0.0
                amount = currency_obj.compute(cr, uid, order.company_id.currency_id.id, order.pricelist_id.currency_id.id, amount_debit)
                res[order.id] = amount
                
        return res

    _columns = {
            # Additional Discount Feature
            'add_disc':fields.float('Additional Discount(%)',digits=(4,6), readonly=True, states={'draft': [('readonly', False)]}),
            'add_disc_amt': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Additional Disc Amt',
                                            store =True,multi='sums', help="The additional discount on untaxed amount."),
            'amount_untaxed': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Untaxed Amount',
                                              store = True,multi='sums', help="The amount without tax."),
            'amount_net': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Net Amount',
                                              store = True,multi='sums', help="The amount after additional discount."),
            'amount_tax': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Taxes',
                                          store = True,multi='sums', help="The tax amount."),
            'amount_total': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Total',
                                            store = True,multi='sums', help="The total amount."),
            # Advance Feature
            'num_invoice': fields.function(_num_invoice, string="Number invoices created", store=True),
            'advance_type': fields.selection([('advance','Advance on 1st Invoice'), ('deposit','Deposit on 1st Invoice')], 'Advance Type', 
                                             required=False, help="Deposit: Deducted full amount on the next invoice. Advance: Deducted in percentage on all following invoices."),
            'advance_percentage': fields.float('Advance (%)', digits=(16,2), required=False, readonly=True),
            'amount_deposit': fields.float('Deposit Amount', readonly=True, digits_compute=dp.get_precision('Account')),
            # Retention Feature
            'retention_percentage': fields.float('Retention (%)', digits=(16,2), required=False, readonly=True),
            'amount_retained': fields.function(_get_amount_retained, string='Retained Amount', type='float', readonly=True, digits_compute=dp.get_precision('Account'))
            #'amount_retained': fields.float('Retained Amount',readonly=True, digits_compute=dp.get_precision('Account'))
        
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
    

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        invoice_line_obj = self.pool.get('account.invoice.line')
        results = invoice_line_obj.read(cr, uid, lines, ['id', 'is_advance', 'is_deposit'])
        for result in results:
            if result['is_advance']: # If created for advance, remove it.
                lines.remove(result['id'])
            if result['is_deposit']: # If created for deposit, remove it.
                lines.remove(result['id'])                
                
        res = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context=context)
        return res