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

class account_account(osv.osv):
    
    _inherit = 'account.account'
    
    def get_total_account_balance(self, cr, uid, ids, context=None):
        total_balance = 0.0
        res = self.__compute(cr, uid, ids, ['balance'])
        for id in res:
            total_balance += res[id]['balance']
        return total_balance
    
account_account()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
