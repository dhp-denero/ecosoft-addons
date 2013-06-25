import decimal_precision as dp
from osv import fields, osv
from common import AdditionalDiscountable
from tools.translate import _

class account_invoice(AdditionalDiscountable, osv.Model):

    _inherit = "account.invoice"
    _description = 'Invoice'

    _line_column = 'invoice_line'
    _tax_column = 'invoice_line_tax_id'

    def record_currency(self, record):
        """Return currency browse record from an invoice record (override)."""
        return record.currency_id

    def _amount_all(self, *args, **kwargs):
        return self._amount_invoice_generic(account_invoice, *args, **kwargs)

    def _get_invoice_line(self, cr, uid, ids, context=None):
        """copy pasted from account_invoice"""
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
  
    def _get_invoice_tax(self, cr, uid, ids, context=None):
        """copy pasted from account_invoice"""
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()

    _columns={
            'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed',
              store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
              },
              multi='all'),
            'add_disc':fields.float('Additional Discount(%)',digits=(4,6),readonly=True, states={'draft':[('readonly',False)]}),
            'add_disc_amt': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Additional Disc Amt',
                                            store =True,multi='sums', help="The additional discount on untaxed amount."),
            'amount_net': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Net Amount',
                                              store = True,multi='sums', help="The amount after additional discount."),
            # Advance 
            'is_advance': fields.boolean('Advance'),
            'amount_advance': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Advance Amt',
                                            store =True,multi='sums', help="The advance amount to be deducted according to original percentage"),
            # Deposit
            'is_deposit': fields.boolean('Advance'),
            'amount_deposit': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Deposit Amt',
                                            store =True,multi='sums', help="The deposit amount to be deducted in the second invoice according to original deposit"),

            'amount_beforetax': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Before Taxes',
                                            store =True,multi='sums', help="Net amount after advance amount deduction"),
            # --
            'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
              store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
              },
              multi='all'),
            'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
              store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
              },
              multi='all'),
    }

    _defaults={
               'add_disc': 0.0,
               'is_advance': False,
               'is_deposit': False
    }
    
account_invoice()

class account_invoice_line(osv.osv):

    _inherit = 'account.invoice.line'
    
    _columns = {
        'is_advance': fields.boolean('Advance'),
        'is_deposit': fields.boolean('Deposit'),
    }
    
    _defaults = {
        'is_advance': False,       
        'is_deposit': False,             
    }
    
    def move_line_get_item(self, cr, uid, line, context=None):
        res = super(account_invoice_line, self).move_line_get_item(cr, uid, line, context=context)
        price = res['price']
        res.update({'price': price * (100.0 - (line.invoice_id.add_disc or 0.0))/100.0})
        return res
    
    # kittiu: also dr/cr advance, force creating new move_line
    def move_line_get(self, cr, uid, invoice_id, context=None):
        
        res = super(account_invoice_line,self).move_line_get(cr, uid, invoice_id, context=context)
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        if inv.amount_advance > 0.0:        
            sign = inv.type in ('out_invoice','out_refund') and -1 or 1
            # account code for advance
            prop = inv.type in ('out_invoice','out_refund') \
                        and self.pool.get('ir.property').get(cr, uid, 'property_account_deposit_customer', 'res.partner', context=context) \
                        or self.pool.get('ir.property').get(cr, uid, 'property_account_deposit_supplier', 'res.partner', context=context)
            prop_id = prop and prop.id or False
            account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, inv.fiscal_position or False, prop_id)
    
            res.append({
                'type':'src',
                'name': _('Advance Amount'),
                'price_unit':sign * inv.amount_advance,
                'quantity': 1,
                'price':sign * inv.amount_advance,
                'account_id':account_id,
                'product_id':False,
                'uos_id':False,
                'account_analytic_id':False,
                'taxes':False,
            })
            
        if inv.amount_deposit > 0.0:        
            sign = inv.type in ('out_invoice','out_refund') and -1 or 1
            # account code for advance
            prop = inv.type in ('out_invoice','out_refund') \
                        and self.pool.get('ir.property').get(cr, uid, 'property_account_deposit_customer', 'res.partner', context=context) \
                        or self.pool.get('ir.property').get(cr, uid, 'property_account_deposit_supplier', 'res.partner', context=context)

                        
            prop_id = prop and prop.id or False
            account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, inv.fiscal_position or False, prop_id)
    
            res.append({
                'type':'src',
                'name': _('Deposit Amount'),
                'price_unit':sign * inv.amount_deposit,
                'quantity': 1,
                'price':sign * inv.amount_deposit,
                'account_id':account_id,
                'product_id':False,
                'uos_id':False,
                'account_analytic_id':False,
                'taxes':False,
            })
            
        return res
    
account_invoice_line()

class account_invoice_tax(osv.Model):

    _inherit = 'account.invoice.tax'

    def compute(self, cr, uid, invoice_id, context=None):
        tax_grouped = super(account_invoice_tax, self).compute(cr, uid, invoice_id, context)
        tax_pool = self.pool.get('account.tax')
        cur_pool = self.pool.get('res.currency')
        tax_ids = set([key[0] for key in tax_grouped])
        taxes = tax_pool.browse(cr, uid, tax_ids)
        if taxes and not all(t.type == 'percent' for t in taxes):
            raise osv.except_osv(_('Discount error'),
                 _('Unable (for now) to compute a global '
                'discount with non percent-type taxes'))
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        add_disc = invoice.add_disc
        cur = invoice.currency_id
        # Getting Order Object (SO/PO)
        order_ids = invoice.sale_order_ids or invoice.purchase_order_ids
        advance_percent = not invoice.is_advance and order_ids and (order_ids[0].advance_percentage / 100) or 0.0
        deposit_amount = not invoice.is_deposit and order_ids and order_ids[0].num_invoice == 2 \
                                and order_ids[0].amount_deposit or 0.0
        for line in tax_grouped:
            # Get new base
            base = tax_grouped[line]['base']
            val_after_disco = base * (1.0 - (add_disc / 100.0))
            advance_amount_tax = val_after_disco * advance_percent
            val_before_tax = val_after_disco - advance_amount_tax - deposit_amount
            new_base = cur_pool.round(cr, uid, cur, val_before_tax)
            tax_grouped[line]['base'] = new_base
            if not base:
                continue
            ratio = new_base / base
            # Adjust others
            tax_grouped[line]['amount'] = tax_grouped[line]['amount'] * ratio
            tax_grouped[line]['base_amount'] = tax_grouped[line]['base_amount'] * ratio
            tax_grouped[line]['tax_amount'] = tax_grouped[line]['tax_amount'] * ratio

        return tax_grouped

