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

from openerp.osv import fields, osv

class accounting_report(osv.osv_memory):  
    _inherit = ["account.common.report",'accounting.report']
    _name = "accounting.report"
    _description = "Accounting Report"
    
    _columns = {
        'account_type': fields.selection([
            ('view', 'View'),
            ('other', 'Regular'),
            ('receivable', 'Receivable'),
            ('payable', 'Payable'),
            ('liquidity','Liquidity'),
            ('consolidation', 'Consolidation'),
            ('closed', 'Closed'),
        ], 'Account Type', help="The 'Internal Type' is used for features available on "\
            "different types of accounts: view can not have journal items, consolidation are accounts that "\
            "can have children accounts for multi-company consolidations, payable/receivable are for "\
            "partners accounts (for debit/credit computations), closed for depreciated accounts."),
    }
    
    def _print_report(self, cr, uid, ids, data, context=None):
        data = super(accounting_report,self)._print_report( cr, uid, ids, data, context)
        data['datas']['form'].update(self.read(cr, uid, ids, ['account_type'], context=context)[0])
        data.update({'report_name':'account.financial.report_ext'})
        return data
    
accounting_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
