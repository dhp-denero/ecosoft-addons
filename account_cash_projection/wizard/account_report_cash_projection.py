# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Ecosoft (<http://www.ecosoft.co.th>)
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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
from .. import format_common

import xlwt
import cStringIO
import base64

from osv import osv, fields


from account_cash_projection.report import account_cash_projection_report

class account_cash_projection_balance(osv.osv_memory):
    _inherit = 'account.common.partner.report'
    _name = 'account.cash.projection'
    _description = 'Account Cash Projection Report'

    _columns = {
        'period_length':fields.integer('Period Length (days)', readonly=True),
        'result_selection': fields.selection([('customer_supplier','Receivable and Payable Accounts')],
                                              "Accounts's", readonly=True),
        'direction_selection': fields.selection([('future','Future')],
                                                 'Analysis Direction', required=True, readonly=True),
        'journal_ids': fields.many2many('account.journal', 'account_cash_projection_balance_journal_rel', 'account_id', 'journal_id', 'Journals', required=True),
    }
    _defaults = {
        'period_length': 1,
        'date_from': lambda *a: time.strftime('%Y-%m-%d'),
        'direction_selection': 'future',
        'result_selection':'customer_supplier',
    }
    def _print_report(self, cr, uid, ids, data, context=None):
        res = {}
        if context is None:
            context = {}

        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['period_length', 'direction_selection'])[0])

        period_length = data['form']['period_length']
        if period_length<=0:
            raise osv.except_osv(_('User Error!'), _('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise osv.except_osv(_('User Error!'), _('You must set a start date.'))

        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
        
        self.start_date = data['form']['date_from']

        if data['form']['direction_selection'] == 'past':
            for i in range(30)[::-1]:
                stop = start - relativedelta(days=period_length)
                res[str(i)] = {
                    'name': (i!=0 and (str((30-(i+1)) * period_length) + '-' + str((30-i) * period_length)) or ('+'+str(29 * period_length))),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop - relativedelta(days=1)
        else:
            for i in range(30):
                stop = start + relativedelta(days=period_length)
                res[str(30-(i+1))] = {
                    'name': (i!=29 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(29 * period_length))),
                    'start': start.strftime('%Y-%m-%d'),
                    'stop': (i!=29 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop + relativedelta(days=1)
        
        self.res = res
        data['form'].update(res)
        if data.get('form',False):
            data['ids']=[data['form'].get('chart_account_id',False)]
            
        obj_gl = account_cash_projection_report.cash_projection_report(cr, uid, 'report.account.cash_projection_balance', context=context)
        a_ids = self.pool.get('account.account').search(cr, uid, [], context=context)
        objects = self.pool.get('account.account').browse(cr, uid, a_ids, context=context)
        obj_gl.set_context(objects, data, data['ids'], report_type='pdf')
        
        res_payable = {}
        res_receivable = {}
        if data['form']['result_selection'] == 'customer':
            res_receivable = obj_gl._get_lines_accounts_inflow(data['form'], account_type=['receivable'])
        elif data['form']['result_selection'] == 'customer': 
            res_payable = obj_gl._get_lines_accounts_inflow(data['form'], account_type=['payable'])
        else:
            res_receivable = obj_gl._get_lines_accounts_inflow(data['form'], account_type=['receivable'])
            res_payable = obj_gl._get_lines_accounts_inflow(data['form'], account_type=['payable'])
             
            
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Cash Projection Report')
        sheet.row(0).height = 256*3
        
        M_header_style = format_common.font_style(position='center', bold=1, border=1, fontos='black', font_height=600)
        D_header_style = format_common.font_style(position='left', bold=1, border=1, fontos='black', font_height=180, color='grey')
        T_header_style = format_common.font_style(position='center', bold=1, border=1, fontos='black', font_height=180, color='grey')
        T1_header_style = format_common.font_style(position='right', bold=1, border=1, fontos='black', font_height=180, color='yellow')
        V_style = format_common.font_style(position='left', bold=1, fontos='black', font_height=180)
        
        self.netcash = dict((x,0) for x in range(0,30))
        self.netcash['netdue'] = 0
        self.netcash['nettotal'] = 0
        sheet.write_merge(0, 0, 3, 6, 'Cash Projection Report', M_header_style)
        sheet.col(0).width = 256*40
        row = self.render_header(sheet, first_row=5, style=D_header_style)
        sheet.write(row, 0, 'Cash Flow From Operations', T_header_style)
        row += 2
        sheet.write(row, 0, 'Cash Inflow Accounts', T_header_style)
        row = self.output_vals(sheet, res_receivable, row=row+1, style=V_style)
        row += 2
        sheet.write(row, 0, 'Cash Outflow Accounts', T_header_style)
        row = self.output_vals(sheet, res_payable, type='out', row = row+1, style=V_style)
        row += 2
        sheet.write(row, 0, 'Net  Cash Flow From Operations', T1_header_style)
        col = 1
        sheet.write(row, col, self.netcash['netdue'], T1_header_style)
        for val in range(30)[::-1]:
            col += 1
            sheet.write(row, col, self.netcash[val], T1_header_style)
        sheet.write(row, col+1, self.netcash['nettotal'], T1_header_style)
        
        stream = cStringIO.StringIO()
        workbook.save(stream)
        cr.execute(""" DELETE FROM output """)
        attach_id = self.pool.get('output').create(cr, uid, {'name':'Cash Projection Report.xls', 'xls_output': base64.encodestring(stream.getvalue())})
        
        return {
                'name': _('Notification'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'output',
                'res_id':attach_id,
                'type': 'ir.actions.act_window',
                'target':'new'
                }
        
    def output_vals(self, ws, output_res, type='in',  row=0, style=False):
        col = 0
        due_total = 0
        daywise_total = dict((x,0) for x in range(0,30))
        final_total = 0
        for main in output_res:
            ws.write(row, col, main['name'], style)
            col += 1
            ws.write(row, col, main['direction'], style)
            due_total += main['direction']
            for val in range(30)[::-1]:
                col += 1
                daywise_total[val] += main[str(val)]
                ws.write(row, col, main[str(val)], style)
            col += 1
            ws.write(row, col, main['total'], style)
            final_total += main['total']
            row += 1
        col = 0
        label = 'Total Cash Inflow'
        if type == 'out':
            label = 'Total Cash Outflow'
        row += 1
        head_style = format_common.font_style(position='center', bold=1, border=1, fontos='black', font_height=180, color='grey')
        ws.write(row, col, label, head_style)
        col += 1
        ws.write(row, col, due_total, head_style)
        self.netcash['netdue'] += due_total
        for val in range(30)[::-1]:
            col += 1
            ws.write(row, col, daywise_total[val], head_style)
            self.netcash[val] += daywise_total[val]
        col += 1
        ws.write(row, col, final_total, style)
        self.netcash['nettotal'] += final_total
        return row
        
    def render_header(self, ws, first_row=0, style=False):
        ws.write(first_row, 0, 'Date/Day Number', style)
        ws.write(first_row, 1, 'Due', style)
        col = 2
        for hdr in range(30)[::-1]:
            hdr_real = self.res[str(hdr)]['start']
            if 'stop' in self.res[str(hdr)] and self.res[str(hdr)]['stop']:
                hdr_real +=  ' To ' + self.res[str(hdr)]['stop']
            ws.write(first_row, col, hdr_real, style)
            ws.col(col).width = len(hdr_real)*300
            col += 1
        ws.write(first_row, col, 'Total', style)
        return first_row + 2
        
account_cash_projection_balance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
