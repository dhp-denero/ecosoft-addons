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
            'add_disc':fields.float('Additional Discount(%)', digits_compute= dp.get_precision('Additional Discount'),readonly=True, states={'draft':[('readonly',False)]}),
            'add_disc_amt': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Additional Disc Amt',
              store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
                  }, multi='all', help="The additional discount on untaxed amount."),
            'amount_net': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Net Amount',
              store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
                  }, multi='all', help="The amount after additional discount."),
            # Advance 
            'is_advance': fields.boolean('Advance'),
            'amount_advance': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Advance Amt',
              store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
                  }, multi='all', help="The advance amount to be deducted according to original percentage"),
            # Deposit
            'is_deposit': fields.boolean('Advance'),
            'amount_deposit': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Deposit Amt',
              store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
                  },multi='all', help="The deposit amount to be deducted in the second invoice according to original deposit"),

            'amount_beforetax': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Before Taxes',
              store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
                  },multi='all', help="Net amount after advance amount deduction"),
            # --
            'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
              store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
              },
              multi='all'),
            # Retention
            'is_retention': fields.boolean('Retention'),
            'amount_retention': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Retention Amt',
                store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
                  }, multi='all', help="The amount to be retained according to retention percentage"),
            'amount_beforeretention': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Before Retention',
                store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
                  }, multi='all', help="Net amount after retention deduction"),

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
               'is_deposit': False,
               'is_retention': False
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
    
#     def move_line_get_item(self, cr, uid, line, context=None):
#         cur_pool = self.pool.get('res.currency')
#         res = super(account_invoice_line, self).move_line_get_item(cr, uid, line, context=context)
#         price = res['price']
#         new_price = cur_pool.round(cr, uid, line.invoice_id.currency_id, (price * (100.0 - (line.invoice_id.add_disc or 0.0))/100.0))
#         res.update({'price': new_price})
#         return res
    
    # kittiu: also dr/cr advance, force creating new move_line
    def move_line_get(self, cr, uid, invoice_id, context=None):
        
        res = super(account_invoice_line,self).move_line_get(cr, uid, invoice_id, context=context)
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        
        if inv.add_disc_amt > 0.0:        
            sign = inv.type in ('out_invoice','out_refund') and -1 or 1
            # account code for advance
            prop = inv.type in ('out_invoice','out_refund') \
                        and self.pool.get('ir.property').get(cr, uid, 'property_account_add_disc_customer', 'res.partner', context=context) \
                        or self.pool.get('ir.property').get(cr, uid, 'property_account_add_disc_supplier', 'res.partner', context=context)
            prop_id = prop and prop.id or False
            account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, inv.fiscal_position or False, prop_id)
    
            res.append({
                'type':'src',
                'name': _('Additional Discount'),
                'price_unit':sign * inv.add_disc_amt,
                'quantity': 1,
                'price':sign * inv.add_disc_amt,
                'account_id':account_id,
                'product_id':False,
                'uos_id':False,
                'account_analytic_id':False,
                'taxes':False,
            })
            
        if inv.amount_advance > 0.0:        
            sign = inv.type in ('out_invoice','out_refund') and -1 or 1
            # account code for advance
            prop = inv.type in ('out_invoice','out_refund') \
                        and self.pool.get('ir.property').get(cr, uid, 'property_account_advance_customer', 'res.partner', context=context) \
                        or self.pool.get('ir.property').get(cr, uid, 'property_account_advance_supplier', 'res.partner', context=context)
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
            
        if inv.amount_retention > 0.0:        
            sign = inv.type in ('out_invoice','out_refund') and -1 or 1
            # account code for advance
            prop = inv.type in ('out_invoice','out_refund') \
                        and self.pool.get('ir.property').get(cr, uid, 'property_account_retention_customer', 'res.partner', context=context) \
                        or self.pool.get('ir.property').get(cr, uid, 'property_account_retention_supplier', 'res.partner', context=context)
            prop_id = prop and prop.id or False
            account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, inv.fiscal_position or False, prop_id)
    
            res.append({
                'type':'src',
                'name': _('Retention Amount'),
                'price_unit':sign * inv.amount_retention,
                'quantity': 1,
                'price':sign * inv.amount_retention,
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
            val_after_disco = cur_pool.round(cr, uid, cur, base * (1.0 - (add_disc / 100.0)))
            advance_amount_tax = cur_pool.round(cr, uid, cur, val_after_disco * advance_percent)
            new_base = val_after_disco - advance_amount_tax - deposit_amount
            tax_grouped[line]['base'] = new_base
            if not base:
                continue
            ratio = new_base / base
            # Adjust others
            tax_grouped[line]['amount'] = cur_pool.round(cr, uid, cur, tax_grouped[line]['amount'] * ratio)
            tax_grouped[line]['base_amount'] = cur_pool.round(cr, uid, cur, tax_grouped[line]['base_amount'] * ratio)
            tax_grouped[line]['tax_amount'] = cur_pool.round(cr, uid, cur, tax_grouped[line]['tax_amount'] * ratio)

        return tax_grouped

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
