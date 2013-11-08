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
#         voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=context)
#         # Loop through Tax Lines
#         for line in tax_grouped:
#             new_base = abs(tax_grouped[line]['base'])
#             #Loop through each 1st Invoice line, find whether its tax is matched
#             for voucher_line in voucher.line_ids:
#                 line_sign = 1
#                 if voucher.type in ('sale','receipt'):
#                     line_sign = voucher_line.type == 'cr' and 1 or -1
#                 elif voucher.type in ('purchase','payment'):
#                     line_sign = voucher_line.type == 'dr' and 1 or -1                
#                 invoice = voucher_line.move_line_id.invoice
#                 invoice_lines = invoice.invoice_line
#                 first_invoice_line = invoice_lines and invoice_lines[0]
#                 # As we have protected for all invoice line to have same tax, we can then assume,
#                 if first_invoice_line and tax_grouped[line]['tax_id'] in [x.id for x in first_invoice_line.invoice_line_tax_id]:
#                     payment_ratio = voucher_line.amount_original == 0.0 and 0.0 or (voucher_line.amount / (voucher_line.amount_original or 1.0))
#                     new_base -= (invoice.add_disc_amt + invoice.amount_advance + invoice.amount_deposit) * payment_ratio * line_sign
#             # New base
#             base = abs(tax_grouped[line]['base'])
#             if not base:
#                 continue
#             ratio = new_base / base
#             # Adjust
#             tax_grouped[line]['base'] = tax_grouped[line]['base'] * ratio
#             tax_grouped[line]['amount'] = tax_grouped[line]['amount'] * ratio
#             tax_grouped[line]['base_amount'] = tax_grouped[line]['base_amount'] * ratio
#             tax_grouped[line]['tax_amount'] = tax_grouped[line]['tax_amount'] * ratio

        return tax_grouped
    
account_voucher_tax()
    
class account_voucher(osv.osv):
    
    _inherit = 'account.voucher'
    
    def _get_amount_wht_ex(self, cr, uid, partner_id, move_line_id, amount_original, amount, context=None):
        amount, amount_wht = super(account_voucher, self)._get_amount_wht_ex(cr, uid, partner_id, move_line_id, amount_original, amount, context=context)
        # Calculate Ratio
        move_line_obj = self.pool.get('account.move.line')
        move_line = move_line_obj.browse(cr, uid, move_line_id)
        invoice = move_line.invoice
        if invoice:
            base = invoice.amount_untaxed
            new_base = base - (invoice.add_disc_amt + invoice.amount_advance + invoice.amount_deposit)
            if base:
                ratio = new_base / base
                amount_wht = amount_wht * ratio
        return float(amount), float(amount_wht)
    
account_voucher()

class account_voucher_line(osv.osv):
    
    _inherit = 'account.voucher.line'
    
    def _get_amount_wht(self, cr, uid, partner_id, move_line_id, amount_original, amount, context=None):
        amount, amount_wht = super(account_voucher_line, self)._get_amount_wht(cr, uid, partner_id, move_line_id, amount_original, amount, context=context)
        # Calculate Ratio
        move_line_obj = self.pool.get('account.move.line')
        move_line = move_line_obj.browse(cr, uid, move_line_id)
        invoice = move_line.invoice
        if invoice:
            base = invoice.amount_untaxed
            new_base = base - (invoice.add_disc_amt + invoice.amount_advance + invoice.amount_deposit)
            if base:
                ratio = new_base / base
                amount_wht = amount_wht * ratio
        return float(amount), float(amount_wht)

account_voucher_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: