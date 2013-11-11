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
from openerp.osv import fields, osv

class account_invoice(osv.osv):

    _inherit = 'account.invoice'
    
    _columns = {
        'invoice_vatinfo': fields.one2many('account.invoice.line', 'invoice_id', 'Invoice Lines', readonly=False),
    }
    
    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(account_invoice, self).line_get_convert(cr, uid, x, part, date, context=context)
        res.update({'vatinfo_supplier_name': x.get('vatinfo_supplier_name', False)})
        return res

account_invoice()

class account_invoice_line(osv.osv):
    
    _inherit = 'account.invoice.line'
    
    _columns = {
        'vatinfo_date': fields.date('Date', required=False, help='This date will be used as Tax Invoice Date in VAT Report'),
        'vatinfo_number': fields.char('Number', required=False, size=64, help='Number Tax Invoice'),
        'vatinfo_supplier_name': fields.char('Supplier', required=False, size=128, help='Name of Organization to pay Tax'),
        'vatinfo_tin': fields.char('Tax ID', required=False, size=64),
        'vatinfo_branch': fields.char('Branch No.', required=False, size=64),
        'vatinfo_base_amount': fields.float('Base', required=False, digits_compute=dp.get_precision('Account')),
        'vatinfo_tax_id': fields.many2one('account.tax', 'Tax', required=False, ),
        'vatinfo_tax_amount': fields.float('VAT', required=False, digits_compute=dp.get_precision('Account')),
    }
    
    def onchange_vat(self, cr, uid, ids, vatinfo_tax_id, vatinfo_tax_amount, context=None):
        res = {}
        if vatinfo_tax_id and vatinfo_tax_amount:
            vatinfo_tax = self.pool.get('account.tax').browse(cr, uid, vatinfo_tax_id)
            tax_percent = vatinfo_tax.amount or 0.0
            if tax_percent > 0.0:
                res['vatinfo_base_amount'] = vatinfo_tax_amount / tax_percent
        return {'value': res}    
    
    def action_add_vatinfo(self, cr, uid, ids, data, context=None):
        for vatinfo in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, vatinfo.id, {'vatinfo_date': data.vatinfo_date,
                                             'vatinfo_number': data.vatinfo_number,
                                             'vatinfo_supplier_name': data.vatinfo_supplier_name,
                                             'vatinfo_tin': data.vatinfo_tin,
                                             'vatinfo_branch': data.vatinfo_branch,
                                             'vatinfo_base_amount': data.vatinfo_base_amount,
                                             'vatinfo_tax_id': data.vatinfo_tax_id.id,
                                             'vatinfo_tax_amount': data.vatinfo_tax_amount,})
        return True  


    def move_line_get(self, cr, uid, invoice_id, context=None):
        
        if context is None:
            context = {}        
        
        res = super(account_invoice_line,self).move_line_get(cr, uid, invoice_id, context=context)
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)

        for line in inv.invoice_line:
            # No additional vat info, continue
            if not line.vatinfo_tax_amount or line.vatinfo_tax_amount == 0:
                continue
            
            sign = 1
            account_id = 0
            if inv.type in ('out_invoice','in_invoice'):
                sign = 1
                account_id = line.vatinfo_tax_id.account_collected_id.id
            else:
                sign = -1
                account_id = line.vatinfo_tax_id.account_paid_id.id

            # Account Post, deduct from the Invoice Line.
            res.append({
                'type': 'src',
                'name': line.name.split('\n')[0][:64],
                'price_unit': -sign * line.vatinfo_tax_amount,
                'quantity': 1.0,
                'price': -sign * line.vatinfo_tax_amount,
                'account_id': line.account_id.id,
                'product_id': line.product_id.id,
                'uos_id': False,
                'account_analytic_id': False,
                'taxes': False,
            })
            
            # Account Post, Tax
            res.append({
                'type': 'tax',
                'name': line.vatinfo_tax_id.name,
                'price_unit' : sign * line.vatinfo_tax_amount,
                'quantity': 1,
                'price': sign * line.vatinfo_tax_amount,
                'account_id': account_id,
                'product_id': False,
                'uos_id': False,
                'account_analytic_id': False,
                'taxes': False,
                'vatinfo_supplier_name': line.vatinfo_supplier_name,
            })
            
        return res


account_invoice_line()  
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
