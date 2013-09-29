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
from tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from openerp.tools import float_compare


class account_voucher(osv.osv):
    
    _inherit = 'account.voucher'
    
    def _compute_writeoff_amount(self, cr, uid, line_dr_ids, line_cr_ids, amount, type):
        debit = credit = 0.0
        sign = type == 'payment' and -1 or 1
        for l in line_dr_ids:
            debit += l['amount'] + l.get('amount_wht',0.0) # Add WHT
        for l in line_cr_ids:
            credit += l['amount'] + l.get('amount_wht',0.0) # Add WHT
        return amount - sign * (credit - debit)

    
    # This is a complete overwrite method
    def _get_writeoff_amount(self, cr, uid, ids, name, args, context=None):
        if not ids: return {}
        currency_obj = self.pool.get('res.currency')
        res = {}
        debit = credit = 0.0
        for voucher in self.browse(cr, uid, ids, context=context):
            sign = voucher.type == 'payment' and -1 or 1
            for l in voucher.line_dr_ids:
                debit += l.amount + l.amount_wht # Add WHT
            for l in voucher.line_cr_ids:
                credit += l.amount + l.amount_wht # Add WHT
            currency = voucher.currency_id or voucher.company_id.currency_id
            res[voucher.id] =  currency_obj.round(cr, uid, currency, voucher.amount - sign * (credit - debit))
        return res
            
    # Note: This method is not exactly the same as the line's one.
    def _get_amount_wht_ex(self, cr, uid, partner_id, move_line_id, amount_original, amount, context=None):
        tax_obj = self.pool.get('account.tax')
        partner_obj = self.pool.get('res.partner')
        move_line_obj = self.pool.get('account.move.line')
        partner = partner_obj.browse(cr, uid, partner_id)
        move_line = move_line_obj.browse(cr, uid, move_line_id)
        amount_wht = 0.0
        original_wht_amt = 0.0
        if move_line.invoice:
            for line in move_line.invoice.invoice_line:
                for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, line.product_id, partner, force_excluded=False, context={'is_voucher': True})['taxes']:
                    if tax_obj.browse(cr, uid, tax['id']).is_wht:
                        original_wht_amt += tax['amount']
        # Payment Ratio
        payment_ratio = amount_original == 0.0 and 0.0 or (float(amount) / (float(amount_original-original_wht_amt) or 1))
        amount_wht += original_wht_amt * payment_ratio
        return float(amount), float(amount_wht)
        
    _columns = {
        'writeoff_amount': fields.function(_get_writeoff_amount, string='Difference Amount', type='float', readonly=True, help="Computed as the difference between the amount stated in the voucher and the sum of allocation on the voucher lines."),
        'tax_line': fields.one2many('account.voucher.tax', 'voucher_id', 'Tax Lines', readonly=False),
    }
    
    # The original recompute_voucher_lines() do not aware of withholding.
    # Here we will re-adjust it. As such, the amount allocation will be reduced and carry to the next lines.
    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        res = super(account_voucher, self).recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=context)
        line_cr_ids = res['value']['line_cr_ids']
        line_dr_ids = res['value']['line_dr_ids']
        total_wht = 0.0
        amount_excess = 0.0
        for line in line_cr_ids + line_dr_ids:
            # Find out what is the valid full amount for unreconciled.
            # i.e., amount_unreconciled = 1070000, the valid amount should be 1040000, not 1070000
            if amount_excess > 0.0:
                line['amount'] = line['amount'] + amount_excess
            amount_unreconciled, amount_wht = self.pool.get('account.voucher.line')._get_amount_wht(cr, uid, partner_id, line['move_line_id'], line['amount_original'], line['amount_unreconciled'], context=context)
            amount_to_reconcile = amount_unreconciled - amount_wht
            amount_excess = line['amount'] - amount_to_reconcile
            if amount_excess > 0.0:
                line['amount'] = line['amount'] - amount_excess
            amount, amount_wht = self._get_amount_wht_ex(cr, uid, partner_id, line['move_line_id'], line['amount_original'], line['amount'], context=context)
            line['amount'] = amount + amount_wht
            line['amount_wht'] = -amount_wht
            total_wht += line['amount_wht']
            line['reconcile'] = (round(line['amount']) == round(line['amount_unreconciled']))
        #res['value']['writeoff_amount'] = amount_excess
        return res
    
    def button_reset_taxes(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        avt_obj = self.pool.get('account.voucher.tax')
        for id in ids:
            # Only update if voucher state is not "posted"
            voucher = self.browse(cr, uid, id, context=ctx)
            if voucher.state == 'posted':
                continue
            cr.execute("DELETE FROM account_voucher_tax WHERE voucher_id=%s AND manual is False", (id,))
            partner = voucher.partner_id
            if partner.lang:
                ctx.update({'lang': partner.lang})
            for taxe in avt_obj.compute(cr, uid, id, context=ctx).values():
                avt_obj.create(cr, uid, taxe)
        # Update the stored value (fields.function), so we write to trigger recompute
        #self.pool.get('account.voucher').write(cr, uid, ids, {'line_ids':[]}, context=ctx)
        return True
    
    #automatic compute tax then save 
    def write(self, cr, uid, ids, vals, context=None):
        res = super(account_voucher, self).write(cr, uid, ids, vals, context=context)
        self.button_reset_taxes(cr, uid, ids)
        return res
    
    # A complete overwrite method
    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
            move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, context), context)
            move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
            line_total = move_line_brw.debit - move_line_brw.credit
            rec_list_ids = []
            rec_wht_ids = []
            if voucher.type == 'sale':
                line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            elif voucher.type == 'purchase':
                line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            
            # kittiu - Thai Accounting
            # If voucher.type = receipt or payment, it is possible to have tax.
            elif voucher.type in ('receipt','payment'): # Create dr/cr for taxes, then remove the net amount from line_total
                net_tax, rec_wht_ids = self.voucher_move_line_tax_create(cr, uid, voucher, move_id, company_currency, current_currency, context)
#                 move_line_pool.write(cr, uid, [move_line_id], {'debit': move_line_brw.debit and (move_line_brw.debit - net_tax) or 0.0,
#                                                                'credit': move_line_brw.credit and (move_line_brw.credit + net_tax) or 0.0,})
            # -- kittiu
            
            # Create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)

            # kittiu - Thai Accounting, make sure to adjust with tax before making writeoff.
            line_total = line_total + net_tax
            # -- kittiu

            # Create the writeoff line if needed
            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, context)
            # We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    # kittiu, if wht, add it to the list when reconcile
#                     for id in rec_wht_ids:
#                             rec_ids.append(id)
                    # --kittiu
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return True    
    
    # kittiu -- New Method for account.voucher.tax
    def voucher_move_line_tax_create(self, cr, uid, voucher, move_id, company_currency, current_currency, context=None):
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        avt_obj = self.pool.get('account.voucher.tax')
        # one move line per tax line
        vtml = avt_obj.move_line_get(cr, uid, voucher.id)
        # create one move line for the total and possibly adjust the other lines amount
        net_tax_currency, vtml = self.compute_net_tax(cr, uid, voucher, company_currency, vtml, context=context)
        # Create move line,
        rec_ids = []
        for ml in vtml:
            ml.update({'move_id': move_id})
            new_id = move_line_obj.create(cr, uid, ml, context=context)
            rec_ids.append(new_id)
        return net_tax_currency, rec_ids
    
    # kittiu -- New Method to compute the net tax (cr/dr)
    def compute_net_tax(self, cr, uid, voucher, company_currency, voucher_tax_move_lines, context=None):
        if context is None:
            context={}
        total = 0
        total_currency = 0
        cur_obj = self.pool.get('res.currency')
        current_currency = self._get_current_currency(cr, uid, voucher.id, context)
        for i in voucher_tax_move_lines:
            if current_currency != company_currency:
                context.update({'date': voucher.date or time.strftime('%Y-%m-%d')})
                i['currency_id'] = current_currency
                i['amount_currency'] = i['price']
                i['price'] = cur_obj.compute(cr, uid, current_currency,
                        company_currency, i['price'],
                        context=context)
            else:
                i['amount_currency'] = False
                i['currency_id'] = False
                
            debit = credit = 0.0    
                
            if voucher.type == 'payment':
                debit = i['amount_currency'] or i['price']
                total += i['price']
                total_currency += i['amount_currency'] or i['price']
            else:
                credit = i['amount_currency'] or i['price']
                total -= i['price']
                total_currency -= i['amount_currency'] or i['price']
                i['price'] = - i['price']
                
            if debit < 0: credit = -debit; debit = 0.0
            if credit < 0: debit = -credit; credit = 0.0        
            sign = debit - credit < 0 and -1 or 1      
            #'journal_id': voucher_brw.journal_id.id,
            i['period_id'] = voucher.period_id.id
            i['partner_id'] = voucher.partner_id.id
            i['date'] = voucher.date
            i['date_maturity'] = voucher.date_due                
            i['debit'] = debit
            i['credit'] = credit
                
        return total_currency, voucher_tax_move_lines    
    
account_voucher()

class account_voucher_line(osv.osv):
    
    _inherit = 'account.voucher.line'
    
    _columns = {
        'amount_wht': fields.float('WHT', digits_compute=dp.get_precision('Account')),
    }
    
    def _get_amount_wht(self, cr, uid, partner_id, move_line_id, amount_original, amount, context=None):
        tax_obj = self.pool.get('account.tax')
        partner_obj = self.pool.get('res.partner')
        move_line_obj = self.pool.get('account.move.line')
        partner = partner_obj.browse(cr, uid, partner_id)
        move_line = move_line_obj.browse(cr, uid, move_line_id)
        amount_wht = 0.0
        original_wht_amt = 0.0
        if move_line.invoice:
            for line in move_line.invoice.invoice_line:
                for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, line.product_id, partner, force_excluded=False, context={'is_voucher': True})['taxes']:
                    if tax_obj.browse(cr, uid, tax['id']).is_wht:
                        original_wht_amt += tax['amount']
        # Payment Ratio
        payment_ratio = amount_original == 0.0 and 0.0 or (float(amount) / (float(amount_original) or 1))
        amount_wht += original_wht_amt * payment_ratio
        return float(amount), float(amount_wht)

#     def _get_original_amount_wht(self, cr, uid, partner_id, move_line_id, amount_original, context=None):
#         tax_obj = self.pool.get('account.tax')
#         partner_obj = self.pool.get('res.partner')
#         move_line_obj = self.pool.get('account.move.line')
#         partner = partner_obj.browse(cr, uid, partner_id)
#         move_line = move_line_obj.browse(cr, uid, move_line_id)
#         original_wht_amt = 0.0
#         for line in move_line.invoice.invoice_line:
#             for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, line.product_id, partner, force_excluded=False, context={'is_voucher': True})['taxes']:
#                 if tax_obj.browse(cr, uid, tax['id']).is_wht:
#                     original_wht_amt += tax['amount']
#         return float(amount_original), float(original_wht_amt)
 
    def onchange_amount(self, cr, uid, ids, partner_id, move_line_id, amount_original, amount, amount_unreconciled, context=None):
        #return super(account_voucher_line, self).onchange_amount(cr, uid, ids, amount, amount_unreconciled, context=context)
        vals = {}
        amount, amount_wht = self._get_amount_wht(cr, uid, partner_id, move_line_id, amount_original, amount, context=context)
        vals['amount_wht'] = -amount_wht
        vals['reconcile'] = (round(amount) == round(amount_unreconciled))
        return {'value': vals}
     
    def onchange_reconcile(self, cr, uid, ids, partner_id, move_line_id, amount_original, reconcile, amount, amount_unreconciled, context=None):
        vals = {}
        if reconcile:
            amount = amount_unreconciled
            amount, amount_wht = self._get_amount_wht(cr, uid, partner_id, move_line_id, amount_original, amount, context=context)
            vals['amount_wht'] = -amount_wht
            vals['amount'] = amount
        return {'value': vals}
        
account_voucher_line()

# kittiu -- New class    
class account_voucher_tax(osv.osv):
    
    _name = "account.voucher.tax"
    _description = "Voucher Tax"

    def _count_factor(self, cr, uid, ids, name, args, context=None):
        res = {}
        for voucher_tax in self.browse(cr, uid, ids, context=context):
            res[voucher_tax.id] = {
                'factor_base': 1.0,
                'factor_tax': 1.0,
            }
            if voucher_tax.amount <> 0.0:
                factor_tax = voucher_tax.tax_amount / voucher_tax.amount
                res[voucher_tax.id]['factor_tax'] = factor_tax

            if voucher_tax.base <> 0.0:
                factor_base = voucher_tax.base_amount / voucher_tax.base
                res[voucher_tax.id]['factor_base'] = factor_base

        return res

    _columns = {
        'voucher_id': fields.many2one('account.voucher', 'Voucher Line', ondelete='cascade', select=True),
        'tax_id': fields.many2one('account.tax', 'Tax'),
        'name': fields.char('Tax Description', size=64, required=True),
        'name2': fields.char('Tax Description 2', size=64, required=False),
        'account_id': fields.many2one('account.account', 'Tax Account', required=True, domain=[('type','<>','view'),('type','<>','income'), ('type', '<>', 'closed')]),
        'account_analytic_id': fields.many2one('account.analytic.account', 'Analytic account'),
        'base': fields.float('Base', digits_compute=dp.get_precision('Account')),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'manual': fields.boolean('Manual'),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of voucher tax."),
        'base_code_id': fields.many2one('account.tax.code', 'Base Code', help="The account basis of the tax declaration."),
        'base_amount': fields.float('Base Code Amount', digits_compute=dp.get_precision('Account')),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Code', help="The tax basis of the tax declaration."),
        'tax_amount': fields.float('Tax Code Amount', digits_compute=dp.get_precision('Account')),
        'company_id': fields.related('account_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
        'factor_base': fields.function(_count_factor, string='Multipication factor for Base code', type='float', multi="all"),
        'factor_tax': fields.function(_count_factor, string='Multipication factor Tax code', type='float', multi="all")
    }

    _order = 'sequence'
    _defaults = {
        'manual': 1,
        'base_amount': 0.0,
        'tax_amount': 0.0,
    }
    def compute(self, cr, uid, voucher_id, context=None):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=context)
        cur = voucher.currency_id or voucher.journal_id.company_id.currency_id
        company_currency = voucher.company_id.currency_id.id

        for voucher_line in voucher.line_ids:
            line_sign = 1
            if voucher.type in ('sale','receipt'):
                line_sign = voucher_line.type == 'cr' and 1 or -1
            elif voucher.type in ('purchase','payment'):
                line_sign = voucher_line.type == 'dr' and 1 or -1
            # Each voucher line is equal to an invoice, we will need to go through all of them.
            if voucher_line.move_line_id.invoice:
                
                payment_ratio = voucher_line.amount_original == 0.0 and 0.0 or (voucher_line.amount / (voucher_line.amount_original or 1))
                                
                for line in voucher_line.move_line_id.invoice.invoice_line:
                    # Each invoice line, calculate tax
                    for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, line.product_id, voucher.partner_id, force_excluded=False, context={'is_voucher': True})['taxes']:
                        # For Normal
                        val={}
                        val['voucher_id'] = voucher.id
                        val['tax_id'] = tax['id']
                        val['name'] = tax['name']
                        val['amount'] = tax['amount'] * payment_ratio * line_sign
                        val['manual'] = False
                        val['sequence'] = tax['sequence']
                        val['base'] = cur_obj.round(cr, uid, cur, tax['price_unit'] * line.quantity) * payment_ratio * line_sign
                        # For Suspend
                        vals={}
                        vals['voucher_id'] = voucher.id
                        vals['tax_id'] = tax['id']
                        vals['name'] = tax['name']
                        vals['amount'] = - tax['amount'] * payment_ratio * line_sign # Reverse Sign
                        vals['manual'] = False
                        vals['sequence'] = tax['sequence']
                        vals['base'] = - cur_obj.round(cr, uid, cur, tax['price_unit'] * line.quantity) * payment_ratio * line_sign # Reverse Sign
                        # Check the product are services, which has been using suspend account. This time, it needs to cr: non-suspend acct and dr: suspend acct
                        use_suspend_acct = line.product_id.id in tax_obj.read(cr, uid, [tax['id']], ['product_ids'])[0]['product_ids']
                        is_wht = tax_obj.browse(cr, uid, tax['id']).is_wht
                        # -------------------> Adding Tax for Posting
                        if is_wht: 
                            # Check Threshold first
                            if abs(val['base']) and abs(val['base']) < tax_obj.read(cr, uid, val['tax_id'], ['threshold_wht'])['threshold_wht']:
                                continue
                            # Case Withholding Tax Dr.
                            if voucher.type in ('receipt','payment'):
                                val['base_code_id'] = tax['base_code_id']
                                val['tax_code_id'] = tax['tax_code_id']
                                val['base_amount'] = cur_obj.compute(cr, uid, voucher.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': voucher.date or time.strftime('%Y-%m-%d')}, round=False) * payment_ratio
                                val['tax_amount'] = cur_obj.compute(cr, uid, voucher.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': voucher.date or time.strftime('%Y-%m-%d')}, round=False) * payment_ratio
                                val['account_id'] = tax['account_collected_id'] or line.account_id.id
                                val['account_analytic_id'] = tax['account_analytic_collected_id']
                            else:
                                val['base_code_id'] = tax['ref_base_code_id']
                                val['tax_code_id'] = tax['ref_tax_code_id']
                                val['base_amount'] = cur_obj.compute(cr, uid, voucher.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': voucher.date or time.strftime('%Y-%m-%d')}, round=False) * payment_ratio
                                val['tax_amount'] = cur_obj.compute(cr, uid, voucher.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': voucher.date or time.strftime('%Y-%m-%d')}, round=False) * payment_ratio
                                val['account_id'] = tax['account_paid_id'] or line.account_id.id
                                val['account_analytic_id'] = tax['account_analytic_paid_id']
                            
                            key = (val['tax_code_id'], val['base_code_id'], val['account_id'], val['account_analytic_id'])
                            if not key in tax_grouped:
                                tax_grouped[key] = val       # REVERSE SIGN for WHT
                                tax_grouped[key]['amount'] = -tax_grouped[key]['amount']     # REVERSE SIGN for WHT
                                tax_grouped[key]['base'] = -tax_grouped[key]['base']
                                tax_grouped[key]['base_amount'] = -tax_grouped[key]['base_amount']
                                tax_grouped[key]['tax_amount'] = -tax_grouped[key]['tax_amount']                              
                            else:
                                tax_grouped[key]['amount'] -= val['amount'] # REVERSE SIGN for WHT
                                tax_grouped[key]['base'] -= val['base']
                                tax_grouped[key]['base_amount'] -= val['base_amount']
                                tax_grouped[key]['tax_amount'] -= val['tax_amount']    
                        
                        # -------------------> Adding Tax for Posting 1) Contra-Suspend 2) Non-Suspend               
                        elif use_suspend_acct: 
                            # First: Do the Cr: with Non-Suspend Account
                            if voucher.type in ('receipt','payment'):
                                val['base_code_id'] = tax['base_code_id']
                                val['tax_code_id'] = tax['tax_code_id']
                                val['base_amount'] = cur_obj.compute(cr, uid, voucher.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': voucher.date or time.strftime('%Y-%m-%d')}, round=False) * payment_ratio
                                val['tax_amount'] = cur_obj.compute(cr, uid, voucher.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': voucher.date or time.strftime('%Y-%m-%d')}, round=False) * payment_ratio
                                val['account_id'] = tax['account_collected_id'] or line.account_id.id
                                val['account_analytic_id'] = tax['account_analytic_collected_id']
                            else:
                                val['base_code_id'] = tax['ref_base_code_id']
                                val['tax_code_id'] = tax['ref_tax_code_id']
                                val['base_amount'] = cur_obj.compute(cr, uid, voucher.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': voucher.date or time.strftime('%Y-%m-%d')}, round=False) * payment_ratio
                                val['tax_amount'] = cur_obj.compute(cr, uid, voucher.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': voucher.date or time.strftime('%Y-%m-%d')}, round=False) * payment_ratio
                                val['account_id'] = tax['account_paid_id'] or line.account_id.id
                                val['account_analytic_id'] = tax['account_analytic_paid_id']
                            
                            key = (val['tax_code_id'], val['base_code_id'], val['account_id'], val['account_analytic_id'])
                            if not key in tax_grouped:
                                tax_grouped[key] = val
                            else:
                                tax_grouped[key]['amount'] += val['amount']
                                tax_grouped[key]['base'] += val['base']
                                tax_grouped[key]['base_amount'] += val['base_amount']
                                tax_grouped[key]['tax_amount'] += val['tax_amount']
                                
                            # Second: Do the Dr: with Suspend Account
                            if voucher.type in ('receipt','payment'):
                                vals['base_code_id'] = tax['base_code_id']
                                vals['tax_code_id'] = tax['tax_code_id']
                                vals['base_amount'] = - cur_obj.compute(cr, uid, voucher.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': voucher.date or time.strftime('%Y-%m-%d')}, round=False) * payment_ratio
                                vals['tax_amount'] = - cur_obj.compute(cr, uid, voucher.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': voucher.date or time.strftime('%Y-%m-%d')}, round=False) * payment_ratio
                                # USE SUSPEND ACCOUNT HERE
                                vals['account_id'] = tax['account_suspend_collected_id'] or line.account_id.id
                                vals['account_analytic_id'] = tax['account_analytic_collected_id']
                            else:
                                vals['base_code_id'] = tax['ref_base_code_id']
                                vals['tax_code_id'] = tax['ref_tax_code_id']
                                vals['base_amount'] = - cur_obj.compute(cr, uid, voucher.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': voucher.date or time.strftime('%Y-%m-%d')}, round=False) * payment_ratio
                                vals['tax_amount'] = - cur_obj.compute(cr, uid, voucher.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': voucher.date or time.strftime('%Y-%m-%d')}, round=False) * payment_ratio
                                # USE SUSPEND ACCOUNT HERE
                                vals['account_id'] = tax['account_suspend_paid_id'] or line.account_id.id
                                vals['account_analytic_id'] = tax['account_analytic_paid_id']
                            
                            key = (vals['tax_code_id'], vals['base_code_id'], vals['account_id'], vals['account_analytic_id'])
                            if not key in tax_grouped:
                                tax_grouped[key] = vals
                            else:
                                tax_grouped[key]['amount'] += vals['amount']
                                tax_grouped[key]['base'] += vals['base']
                                tax_grouped[key]['base_amount'] += vals['base_amount']
                                tax_grouped[key]['tax_amount'] += vals['tax_amount'] # REVERSE SIGN                   
                        # --------------------------------------------------------------------------
        for t in tax_grouped.values():
            t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        return tax_grouped

    def move_line_get(self, cr, uid, voucher_id):
        res = []
        cr.execute('SELECT * FROM account_voucher_tax WHERE voucher_id=%s', (voucher_id,))
        for t in cr.dictfetchall():
            if not t['amount'] \
                    and not t['tax_code_id'] \
                    and not t['tax_amount']:
                continue
            res.append({
                'type':'tax',
                'name':t['name'],
                'price_unit': t['amount'],
                'quantity': 1,
                'price': t['amount'] or 0.0,
                'account_id': t['account_id'],
                'tax_code_id': t['tax_code_id'],
                'tax_amount': t['tax_amount'],
                'account_analytic_id': t['account_analytic_id'],
            })
        return res



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
