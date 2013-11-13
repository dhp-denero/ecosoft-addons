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

import base64
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
class import_payment_data(osv.osv_memory):

    _name = 'import.payment.data'
    _description = 'Import Payment Data'
    _columns = {
        'name': fields.binary('Excel File'),
    }
    def onchange_name(self, cr, uid, ids, name, context=None):
        x = 1
        file = base64.decodestring(name)
        
        return False
    
    def import_data(self, cr, uid, ids, context=None):

        # Preparation
        res = self.read(cr, uid, ids,['name'])
        res = res and res[0] or {}
        file = base64.decodestring(res['name'])
        file_list = file.split('\n')
        payment_lines = {}
        for line in file_list:
            if line != '':
                data = line.split(',')
                
        partner_id = 1545
        journal_id = 10
        price = 20000.00
        currency_id = 142
        ttype = 'sale'
        date = '2013-11-01'
                
        return self.pool.get('account.voucher').recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=context)

        # Call recompute_voucher_line
        return False
    
import_payment_data()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
