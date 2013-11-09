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
from tools.translate import _

class account_voucher_tax(osv.osv):

    _inherit = 'account.voucher.tax'

    def compute(self, cr, uid, voucher_id, context=None):
        
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=context)
        advance_and_discount = {}
        for voucher_line in voucher.line_ids:
            if voucher_line.move_line_id.invoice:
                invoice = voucher_line.move_line_id.invoice
                # Percent Additional Discount
                add_disc = invoice.add_disc
                # Percent Advance
                advance_amount = not invoice.is_advance and invoice.amount_advance or 0.0
                advance = advance_amount / (invoice.amount_net) * 100                
                # Percent Deposit
                deposit_amount = not invoice.is_deposit and invoice.amount_deposit or 0.0
                deposit = deposit_amount / (invoice.amount_net) * 100
                # Add to dict
                advance_and_discount.update({invoice.id: {'add_disc': add_disc, 'advance': advance, 'deposit': deposit}})
        
        tax_grouped = super(account_voucher_tax, self).compute_ex(cr, uid, voucher_id, advance_and_discount, context)

        return tax_grouped
    
account_voucher_tax()
    
class account_voucher(osv.osv):
    
    _inherit = 'account.voucher'
    
    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        # First time, retrieve the voucher lines, this is just to get the invoice ids.
        res = super(account_voucher, self).recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=context)
        line_cr_ids = res['value']['line_cr_ids']
        line_dr_ids = res['value']['line_dr_ids']
        move_line_obj = self.pool.get('account.move.line')
        advance_and_discount = {}
        for line in line_cr_ids + line_dr_ids:
            add_disc = advance = deposit = 0.0
            move_line = move_line_obj.browse(cr, uid, line['move_line_id'])
            if move_line.invoice:
                invoice = move_line.invoice                
                # Percent Additional Discount
                add_disc = invoice.add_disc
                # Percent Advance
                advance_amount = not invoice.is_advance and invoice.amount_advance or 0.0
                advance = advance_amount / (invoice.amount_net) * 100                
                # Percent Deposit
                deposit_amount = not invoice.is_deposit and invoice.amount_deposit or 0.0
                deposit = deposit_amount / (invoice.amount_net) * 100
                # Add to dict
                advance_and_discount.update({invoice.id: {'add_disc': add_disc, 'advance': advance, 'deposit': deposit}})
        res = self.recompute_voucher_lines_ex(cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, advance_and_discount={}, context=context)
        return res
    
    def _get_amount_wht_ex(self, cr, uid, partner_id, move_line_id, amount_original, original_wht_amt, amount, advance_and_discount={}, context=None):
        move_line = self.pool.get('account.move.line').browse(cr, uid, id, move_line_id)
        advance_and_discount = {}
        if move_line.invoice:
            invoice = move_line.invoice
            # Percent Additional Discount
            add_disc = invoice.add_disc
            # Percent Advance
            advance_amount = not invoice.is_advance and invoice.amount_advance or 0.0
            advance = advance_amount / (invoice.amount_net) * 100                
            # Percent Deposit
            deposit_amount = not invoice.is_deposit and invoice.amount_deposit or 0.0
            deposit = deposit_amount / (invoice.amount_net) * 100
            # Add to dict
            advance_and_discount.update({'add_disc': add_disc, 'advance': advance, 'deposit': deposit})
        amount, amount_wht = super(account_voucher, self)._get_amount_wht_ex(cr, uid, partner_id, move_line_id, amount_original, original_wht_amt, amount, advance_and_discount, context=context)
        return float(amount), float(amount_wht)
    
account_voucher()

class account_voucher_line(osv.osv):
    
    _inherit = 'account.voucher.line'
    
    def _get_amount_wht(self, cr, uid, partner_id, move_line_id, amount_original, amount, advance_and_discount={}, context=None):
        move_line = self.pool.get('account.move.line').browse(cr, uid, move_line_id)
        advance_and_discount = {}
        if move_line.invoice:
            invoice = move_line.invoice
            # Percent Additional Discount
            add_disc = invoice.add_disc
            # Percent Advance
            advance_amount = not invoice.is_advance and invoice.amount_advance or 0.0
            advance = advance_amount / (invoice.amount_net) * 100                
            # Percent Deposit
            deposit_amount = not invoice.is_deposit and invoice.amount_deposit or 0.0
            deposit = deposit_amount / (invoice.amount_net) * 100
            # Add to dict
            advance_and_discount.update({'add_disc': add_disc, 'advance': advance, 'deposit': deposit})        
        amount, amount_wht = super(account_voucher_line, self)._get_amount_wht(cr, uid, partner_id, move_line_id, amount_original, amount, advance_and_discount, context=context)
        return float(amount), float(amount_wht)

account_voucher_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: