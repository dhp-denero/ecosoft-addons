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
# TODO
# - Only create Payment Register, if Type = Receipt


import time
from lxml import etree

from openerp import netsvc
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class account_voucher(osv.osv):

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for account_voucher in self.browse(cr, uid, ids, context=context):
            res[account_voucher.id] = {
                'amount_total': 0.0,
            }
            val = 0.0
            for line in account_voucher.payment_details:
                val += line.amount
            res[account_voucher.id]['amount_total'] = val
        return res

    
    def _get_account_voucher(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.voucher.pay.detail').browse(cr, uid, ids, context=context):
            result[line.voucher_id.id] = True
        return result.keys()
    
    _inherit = 'account.voucher'
    #_rec_name = 'number'
    _columns = {
        'payment_details': fields.one2many('account.voucher.pay.detail', 'voucher_id', 'Payment Details', readonly=True, states={'draft':[('readonly',False)]}),
        'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Total',
            store = {
                'account.voucher.pay.detail': (_get_account_voucher, None, 10),
            },
            multi='sums', help="The total amount."),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if context is None: context = {}
        return [(r['id'], r['number'] or '') for r in self.read(cr, uid, ids, ['number'], context, load='_classic_write')]

    
    def proforma_voucher(self, cr, uid, ids, context=None):
        
        # Validate Payment and Payment Register Amount
        this = self.browse(cr, uid, ids[0], context=context)
        if this.type == 'receipt':
            if (this.amount_total or 0.0) <> (this.amount or 0.0):
                raise osv.except_osv(_('Unable to save!'), _('Total Amount in Payment Details must equal to Paid Amount'))

        self.create_payment_register(cr, uid, ids, context=context)
        super(account_voucher, self).action_move_line_create(cr, uid, ids, context=context)
        return True

    def create_payment_register(self, cr, uid, ids, context=None):
        
        if context is None:
            context = {}
        payment_register_pool = self.pool.get('payment.register')
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.type <> 'receipt': # Only on receipt case.
                continue
            # For each of the Payment Detail, create a new payment register.
            period_pool = self.pool.get('account.period')
            ctx = context.copy()
            ctx.update({'company_id': voucher.company_id.id})
            for payment_detail in voucher.payment_details:
                pids = period_pool.find(cr, uid, payment_detail.date_due, context=ctx)
                res = { 'voucher_id':voucher.id,
                        'pay_detail_id':payment_detail.id,
                        'original_pay_currency_id':voucher.currency_id and voucher.currency_id.id or voucher.company_id.currency_id.id,
                        'original_pay_amount':payment_detail.amount,
                        'amount':payment_detail.amount,
                        'date':payment_detail.date_due,
                        'period_id':pids and pids[0] or False,
                }
                payment_register_pool.create(cr, uid, res, context)

        return True
    
account_voucher()

class account_voucher_pay_detail(osv.osv):
    
    _name = "account.voucher.pay.detail"
    _description = "Payment Details"

    _columns = {
        'name': fields.char('Bank/Branch', size=128, required=False),
        'voucher_id': fields.many2one('account.voucher', 'Voucher Reference', ondelete='cascade', select=True),
        'type': fields.selection([
            ('check','Check'),
            ('cash','Cash'),
            ('transfer','Transfer'),
            ],'Type', required=True, select=True, change_default=True),
        'check_no': fields.char('Check No.', size=64),   
        'date_due': fields.date('Check Date'),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account')),        
        #'date_payin': fields.date('Pay-in Date'),
    }

account_voucher_pay_detail()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
