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

import openerp.addons.decimal_precision as dp
from osv import osv, fields

class account_move_line(osv.osv):
    
    def _is_payment_schedule(self, cr, uid, ids, fieldnames, args, context=None):
        result = dict.fromkeys(ids, 0)
        for record in self.browse(cr, uid, ids, context=context):
            if record.journal_id.type in ['sale','sale_refund','purchase','purchase_refund']:
                result[record.id] = True
            else:
                result[record.id] = False
        return result
    
    def _amount_residual2(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        cr.execute("select id from account_account where type = 'liquidity'")
        cash_ids = map(lambda x: x[0], cr.fetchall())
        begin_balance = self.pool.get('account.account').get_total_account_balance(cr, uid, cash_ids, ['balance'])
        if context is None:
            context = {}
        cur_obj = self.pool.get('res.currency')
        for move_line in self.browse(cr, uid, ids, context=context):
            res[move_line.id] = {
                'amount_begin_balance': 0.0,
                'amount_residual2': 0.0,
                'amount_residual_currency2': 0.0,
                'amount_end_balance': 0.0,
            }

            if move_line.reconcile_id:
                continue
            if not move_line.account_id.type in ('payable', 'receivable'):
                continue

            if move_line.currency_id:
                move_line_total = move_line.amount_currency
            else:
                move_line_total = move_line.debit - move_line.credit
            line_total_in_company_currency =  move_line.debit - move_line.credit
            context_unreconciled = context.copy()
            if move_line.reconcile_partial_id:
                for payment_line in move_line.reconcile_partial_id.line_partial_ids:
                    if payment_line.id == move_line.id:
                        continue
                    if payment_line.currency_id and move_line.currency_id and payment_line.currency_id.id == move_line.currency_id.id:
                        move_line_total += payment_line.amount_currency
                    else:
                        if move_line.currency_id:
                            context_unreconciled.update({'date': payment_line.date})
                            amount_in_foreign_currency = cur_obj.compute(cr, uid, move_line.company_id.currency_id.id, move_line.currency_id.id, (payment_line.debit - payment_line.credit), round=False, context=context_unreconciled)
                            move_line_total += amount_in_foreign_currency
                        else:
                            move_line_total += (payment_line.debit - payment_line.credit)
                    line_total_in_company_currency += (payment_line.debit - payment_line.credit)

            result = move_line_total
            res[move_line.id]['amount_begin_balance'] = begin_balance
            res[move_line.id]['amount_residual_currency2'] =  move_line.currency_id and self.pool.get('res.currency').round(cr, uid, move_line.currency_id, result) or result
            res[move_line.id]['amount_residual2'] = line_total_in_company_currency
            ending_balance = begin_balance + line_total_in_company_currency
            res[move_line.id]['amount_end_balance'] = ending_balance
            begin_balance = ending_balance
        return res

    _inherit = 'account.move.line'
    _order = 'date_maturity, id'
    _columns = {
        'is_payment_schedule': fields.function(_is_payment_schedule, type='boolean', string='Is Payment Schedule', store=True),
        'amount_begin_balance': fields.function(_amount_residual2, type='float', digits_compute=dp.get_precision('Account'), string='Begin Balance', multi="residual"),
        'amount_residual_currency2': fields.function(_amount_residual2, type='float', digits_compute=dp.get_precision('Account'), string='Residual Amount Currency', multi="residual"),
        'amount_residual2': fields.function(_amount_residual2, type='float', digits_compute=dp.get_precision('Account'), string='Residual Amount', multi="residual"),
        'amount_end_balance': fields.function(_amount_residual2, type='float', digits_compute=dp.get_precision('Account'), string='End Balance', multi="residual"),
    }

    def init(self, cr):
        cr.execute("update account_move_line ml set is_payment_schedule = \
                    (select case when type in ('sale','sale_refund','purchase','purchase_refund') \
                    then true else false end \
                    from account_move m \
                    left outer join account_journal j on m.journal_id = j.id \
                    where m.id = ml.move_id) where is_payment_schedule is null")

account_move_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: