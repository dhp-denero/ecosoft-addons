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

class account_invoice(osv.osv):
    
    _inherit="account.invoice"
    
    def _check_tax(self, cr, uid, ids, context=None):
        # loop through each lines, check if tax different.
        if not isinstance(ids, list) :
            ids = [ids]        
        invoices = self.browse(cr, uid, ids, context=context)
        for invoice in invoices:
            i = 0
            tax_ids = []
            for line in invoice.invoice_line:
                next_line_tax_id = [x.id for x in line.invoice_line_tax_id]
                if i > 0 and set(tax_ids) != set(next_line_tax_id):
                    raise osv.except_osv(
                        _('Error!'),
                        _('You cannot create lines with different taxes!'))
                tax_ids = next_line_tax_id
                i += 1
        return True
        
    def write(self, cr, uid, ids, vals, context=None):
        res = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
        self._check_tax(cr, uid, ids, context=context)
        return res
    
account_invoice()


class account_invoice_tax(osv.osv):
    
    _inherit = 'account.invoice.tax'

    # This is a complete overwrite method.
    def compute(self, cr, uid, invoice_id, context=None):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        cur = inv.currency_id
        company_currency = inv.company_id.currency_id.id

        for line in inv.invoice_line:

            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, line.product_id, inv.partner_id)['taxes']:
                val={}
                val['invoice_id'] = inv.id
                val['name'] = tax['name']
                val['amount'] = tax['amount']
                val['manual'] = False
                val['sequence'] = tax['sequence']
                val['base'] = cur_obj.round(cr, uid, cur, tax['price_unit'] * line['quantity'])
                
                # start kittiu for Thai Accounting, 
                # Check the product are services (which need suspend account)
                use_suspend_acct = line.product_id.id in tax_obj.read(cr, uid, [tax['id']], ['product_ids'])[0]['product_ids']
                # end kittiu
                
                if inv.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    
                    # start kittiu for Thai Accounting
                    #val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_id'] = use_suspend_acct and tax['account_suspend_collected_id'] or tax['account_collected_id'] or line.account_id.id
                    # end kittiu
                    
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    # start kittiu
                    #val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_id'] = use_suspend_acct and tax['account_suspend_paid_id'] or tax['account_collected_id'] or line.account_id.id
                    # end kittiu                    
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'], val['account_analytic_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        return tax_grouped  
account_invoice_tax()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
