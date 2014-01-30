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

from account.report.account_balance import account_balance
from openerp.report import report_sxw

class account_balance_ext(account_balance):
    
    def set_context(self, objects, data, ids, report_type=None):
        account_ids = data['form'].get('account_ids',False)
        if account_ids:
            res = super(account_balance_ext, self).set_context(objects, data, account_ids, report_type)
        else:
            res = super(account_balance_ext, self).set_context(objects, data, ids, report_type)
        return res
    
    def lines(self, form, ids=None, done=None):
        
        account_ids = form.get('account_ids',False)
        if account_ids: 
            self.result_acc = super(account_balance_ext, self).lines(form, account_ids, done)
        else:
            self.result_acc = super(account_balance_ext, self).lines(form, ids, done)
        
        rec_count= len(self.result_acc)
        i=0
        
        while i<rec_count:
            record = self.result_acc[i]
            if (not record.get('type',False )) or record['type']=='view':
                self.sum_credit -= record.get('credit', 0.0 )
                self.sum_debit -= record.get('debit', 0.0 )
                del self.result_acc[i]
                rec_count= len(self.result_acc)
            else:                   
                i+=1
        self.result_acc.append({'credit': self.sum_credit, 'code': u' ', 'bal_type': '', 'name':'รวม','parent_id': False,
                                     'level': 0, 'balance': self.sum_debit -self.sum_credit ,'debit': self.sum_debit,
                                     'type': u'view', 'id': False}) 

        return self.result_acc

report_sxw.report_sxw('report.account.account_balance_ext', 'account.account', 'addons/account/report/account_balance.rml', parser=account_balance_ext, header="internal")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
