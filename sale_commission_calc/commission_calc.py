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

import time
import netsvc
from osv import osv, fields
from openerp.tools.translate import _

LAST_PAY_DATE_RULE = [('invoice_duedate', 'Invoice Due Date (default)'),
                      ('invoice_date_plus_cust_payterm', 'Invoice Date + Customer Payment Term'),
                      ('1st_billing_date_plus_cust_payterm', '1st Billing Date + Customer')]


class commission_rule(osv.osv):

    _name = "commission.rule"
    _description = "Commission Rule"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'type': fields.selection((('percent_fixed', 'Fixed Commission Rate'),
                                  ('percent_product_category', 'Product Category Commission Rate'),
                                  ('percent_product', 'Product Commission Rate'),
                                  ('percent_amount', 'Commission Rate By Amount'),
                                  ('percent_accumulate', 'Commission Rate By Monthly Accumulated Amount')),
                                 'Type', required=True),
        'fix_percent': fields.float('Fix Percentage'),
        'rule_rates': fields.one2many('commission.rule.rate', 'commission_rule_id', 'Rates'),
        'rule_conditions': fields.one2many('commission.rule.condition', 'commission_rule_id', 'Conditions'),
        'active': fields.boolean('Active'),
        'sale_team_ids': fields.one2many('sale.team', 'commission_rule_id', 'Teams'),
        'salesperson_ids': fields.one2many('res.users', 'commission_rule_id', 'Salesperson'),
    }
    _defaults = {
        'active': True
    }

commission_rule()


class commission_rule_rate(osv.osv):

    _name = "commission.rule.rate"
    _description = "Commission Rule Rate"
    _columns = {
        'commission_rule_id': fields.many2one('commission.rule', 'Commission Rule'),
        'amount_over': fields.float('Amount Over', required=True),
        'amount_upto': fields.float('Amount Up-To', required=True),
        'percent_commission': fields.float('Commission (%)', required=True),
    }
    _order = 'id'

commission_rule_rate()


class commission_rule_condition(osv.osv):

    _name = "commission.rule.condition"
    _description = "Commission Rule Lines"
    _columns = {
        'sequence': fields.integer('Sequence', required=True),
        'commission_rule_id': fields.many2one('commission.rule', 'Commission Rule'),
        'sale_margin_over': fields.float('Margin Over (%)', required=True),
        'sale_margin_upto': fields.float('Margin Up-To (%)', required=True),
        'commission_coeff': fields.float('Commission Coeff', required=True),
        'accumulate_coeff': fields.float('Accumulate Coeff', required=True),
    }
    _defaults = {
        'commission_coeff': 1.0,
        'accumulate_coeff': 1.0
    }
    _order = 'sequence'

commission_rule_condition()


class sale_team(osv.osv):

    _name = "sale.team"
    _description = "Sales Team"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'commission_rule_id': fields.many2one('commission.rule', 'Commission Rule', required=False),
        'users': fields.many2many('res.users', 'sale_team_users_rel', 'tid', 'uid', 'Users'),
        'implied_ids': fields.many2many('sale.team', 'sale_team_implied_rel', 'tid', 'hid',
            string='Inherits', help='Users of this group automatically inherit those groups'),
        'comm_unpaid': fields.boolean('Allow unpaid invoice', help='Allow paying commission without invoice being paid.'),
        'comm_overdue': fields.boolean('Allow overdue payment', help='Allow paying commission with overdue payment.'),
        'last_pay_date_rule': fields.selection(LAST_PAY_DATE_RULE, 'Last Pay Date Rule'),
        'buffer_days': fields.integer('Buffer Days')
    }
    _defaults = {
        'comm_unpaid': False,
        'comm_overdue': False,
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the team must be unique !')
    ]

sale_team()


class commission_worksheet(osv.osv):

    _name = 'commission.worksheet'
    _description = 'Commission Worksheet'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _search_wait_pay(self, cr, uid, obj, name, args, domain=None, context=None):
        if not len(args):
            return []
        worksheet_line_obj = self.pool.get('commission.worksheet.line')
        for arg in args:
            if arg[1] == '=':
                if arg[2]:
                    lines = worksheet_line_obj.search(cr, uid, [('invoice_state', '=', 'paid'), ('commission_state', '!=', 'done')], context=context)
        ids = self.search(cr, uid, [('worksheet_lines', 'in', lines), ('state', '=', 'confirmed')], context=context)
        return [('id', 'in', [x for x in ids])]

    def _invoice_wait_pay(self, cr, uid, ids, name, arg, context=None):
        worksheet_line_obj = self.pool.get('commission.worksheet.line')
        res = {}.fromkeys(ids, False)
        for worksheet in self.browse(cr, uid, ids):
            if worksheet.state == 'confirmed':
                # Checking at least invoice was paid, and not commission paid
                lines = worksheet_line_obj.search(cr, uid, [('commission_worksheet_id', '=', worksheet.id), ('invoice_state', '=', 'paid'), ('commission_state', '!=', 'done')], limit=1)
                if len(lines) > 0:
                    res[worksheet.id] = True
        return res

    def _get_period(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        ctx = dict(context, account_period_prefer_normal=True)
        periods = self.pool.get('account.period').find(cr, uid, context=ctx)
        return periods and periods[0] or False

    _columns = {
        'name': fields.char('Name', size=64, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'sale_team_id': fields.many2one('sale.team', 'Team', required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'salesperson_id': fields.many2one('res.users', 'Salesperson', required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'worksheet_lines': fields.one2many('commission.worksheet.line', 'commission_worksheet_id', 'Calculation Lines', ondelete='cascade', readonly=True, states={'draft': [('readonly', False)]}),
        'wait_pay': fields.function(_invoice_wait_pay, type='boolean', string='Ready to pay', fnct_search=_search_wait_pay, store=False),
        'state': fields.selection([('draft', 'Draft'),
                                   ('confirmed', 'Confirmed'),
                                   ('done', 'Done'),
                                   ('cancel', 'Cancelled')], 'Status', required=True, readonly=True,
                help='* The \'Draft\' status is set when the work sheet in draft status. \
                    \n* The \'Confirmed\' status is set when the work sheet is confirmed by related parties. \
                    \n* The \'Done\' status is set when the work sheet is ready to pay for commission. This state can not be undone. \
                    \n* The \'Cancelled\' status is set when a user cancel the work sheet.'),
        'invoice_ids': fields.one2many('account.invoice', 'commission_worksheet_id', 'Invoices', readonly=True),
    }
    _defaults = {
        'state': 'draft',
        'period_id': _get_period,
        'name': '/'
    }
    _sql_constraints = [
        ('unique_sale_team_period', 'unique(sale_team_id, period_id)', 'Duplicate Sale Team / Period'),
        ('unique_salesperson_period', 'unique(salesperson_id, period_id)', 'Duplicate Salesperson / Period')
    ]

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'commission.worksheet') or '/'
        return super(commission_worksheet, self).create(cr, uid, vals, context=context)

    def _get_match_rule_condition(self, cr, uid, rule, order, context=None):
        if context is None:
            context = {}
        rule_condition_obj = self.pool.get('commission.rule.condition')
        percent_margin = order.amount_untaxed and (order.margin / order.amount_untaxed) * 100 or 0.0
        rule_condition_ids = rule_condition_obj.search(cr, uid, [('commission_rule_id', '=', rule.id),
                                            ('sale_margin_over', '<', percent_margin),
                                            ('sale_margin_upto', '>=', percent_margin)
                                            ])
        if not rule_condition_ids:
            return False
        elif len(rule_condition_ids) > 1:
            raise osv.except_osv(_('Error!'),
                                _('More than 1 Rule Condition match %s! There seems to be problem with Rule %s.') % (order.name, rule.name))
        elif len(rule_condition_ids) == 1:
            return rule_condition_ids[0]

    def _calculate_commission(self, cr, uid, rule, worksheet, invoices, context=None):
        if rule.type == 'percent_fixed':
            self._calculate_percent_fixed(cr, uid, rule, worksheet, invoices, context=context)
        if rule.type == 'percent_product_category':
            self._calculate_percent_product_category(cr, uid, rule, worksheet, invoices, context=context)
        if rule.type == 'percent_product':
            self._calculate_percent_product(cr, uid, rule, worksheet, invoices, context=context)
        if rule.type == 'percent_amount':
            self._calculate_percent_amount(cr, uid, rule, worksheet, invoices, context=context)
        if rule.type == 'percent_accumulate':
            self._calculate_percent_accumulate(cr, uid, rule, worksheet, invoices, context=context)
        return True

    def _prepare_worksheet_line(self, worksheet, invoice, accumulated_amt, commission_amt):
        res = {
            'commission_worksheet_id': worksheet.id,
            'invoice_id': invoice.id,
            'date_invoice': invoice.date_invoice,
            'invoice_amt': invoice.amount_total - invoice.amount_tax,
            'accumulated_amt': accumulated_amt,
            'commission_amt': commission_amt,
        }
        return res

    def _calculate_percent_fixed(self, cr, uid, rule, worksheet, invoices, context=None):
        if context is None:
            context = {}
        commission_rate = rule.fix_percent / 100
        accumulated_amt = 0.0
        worksheet_line_obj = self.pool.get('commission.worksheet.line')
        for invoice in invoices:
            amount_untaxed = (invoice.amount_total - invoice.amount_tax)
            accumulated_amt += amount_untaxed
            # For each order, find its match rule line
            commission_amt = 0.0
            if commission_rate:
                commission_amt = amount_untaxed * commission_rate
            res = self._prepare_worksheet_line(worksheet, invoice, accumulated_amt, commission_amt)
            worksheet_line_obj.create(cr, uid, res)
        return True

    def _calculate_percent_product_category(self, cr, uid, rule, worksheet, invoices, context=None):
        if context is None:
            context = {}
        commission_rate = 0.0
        accumulated_amt = 0.0
        worksheet_line_obj = self.pool.get('commission.worksheet.line')
        for invoice in invoices:
            amount_untaxed = (invoice.amount_total - invoice.amount_tax)
            accumulated_amt += amount_untaxed
            # For each product line
            commission_amt = 0.0
            for line in invoice.invoice_line:
                percent_commission = line.product_id.categ_id.percent_commission
                commission_rate = percent_commission and percent_commission / 100 or 0.0
                if commission_rate:
                    commission_amt += line.price_subtotal * commission_rate
            res = self._prepare_worksheet_line(worksheet, invoice, accumulated_amt, commission_amt)
            worksheet_line_obj.create(cr, uid, res)
        return True

    def _calculate_percent_product(self, cr, uid, rule, worksheet, invoices, context=None):
        if context is None:
            context = {}
        commission_rate = 0.0
        accumulated_amt = 0.0
        worksheet_line_obj = self.pool.get('commission.worksheet.line')
        for invoice in invoices:
            amount_untaxed = (invoice.amount_total - invoice.amount_tax)
            accumulated_amt += amount_untaxed
            # For each product line
            commission_amt = 0.0
            for line in invoice.invoice_line:
                percent_commission = line.product_id.percent_commission
                commission_rate = percent_commission and percent_commission / 100 or 0.0
                if commission_rate:
                    commission_amt += line.price_subtotal * commission_rate
            res = self._prepare_worksheet_line(worksheet, invoice, accumulated_amt, commission_amt)
            worksheet_line_obj.create(cr, uid, res)
        return True

    def _calculate_percent_amount(self, cr, uid, rule, worksheet, invoices, context=None):
        if context is None:
            context = {}
        worksheet_line_obj = self.pool.get('commission.worksheet.line')
        accumulated_amt = 0.0
        for invoice in invoices:
            amount_untaxed = (invoice.amount_total - invoice.amount_tax)
            accumulated_amt += amount_untaxed
            # For each order, find its match rule line
            commission_amt = 0.0
            ranges = rule.rule_rates
            for range in ranges:
                commission_rate = range.percent_commission / 100
                if amount_untaxed <= range.amount_upto:
                    commission_amt = amount_untaxed * commission_rate
                    break
            res = self._prepare_worksheet_line(worksheet, invoice, accumulated_amt, commission_amt)
            worksheet_line_obj.create(cr, uid, res)
        return True

    def _calculate_percent_accumulate(self, cr, uid, rule, worksheet, invoices, context=None):
        if context is None:
            context = {}
        rule_condition_obj = self.pool.get('commission.rule.condition')
        worksheet_line_obj = self.pool.get('commission.worksheet.line')
        accumulated_amt = 0.0
        for invoice in invoices:
            amount_untaxed = (invoice.amount_total - invoice.amount_tax)
            # For each order, find its match rule line
            amount_to_accumulate = 0.0
            commission_amt = 0.0
            rule_condition_id = self._get_match_rule_condition(cr, uid, rule, invoice, context=context)
            if rule_condition_id:
                rule_condition = rule_condition_obj.browse(cr, uid, rule_condition_id)
                amount_to_accumulate = amount_untaxed * rule_condition.accumulate_coeff
                accumulated_amt += amount_untaxed
                amount_from = accumulated_amt - amount_to_accumulate
                ranges = rule.rule_rates
                for range in ranges:
                    commission_rate = range.percent_commission / 100
                    # Case 1: In Range, get commission and quit.
                    if amount_from <= range.amount_upto and accumulated_amt <= range.amount_upto:
                        commission_amt = amount_to_accumulate * commission_rate
                        break
                    # Case 2: Over Range, only get commission for this range first and postpone to next range.
                    elif amount_from <= range.amount_upto and accumulated_amt > range.amount_upto:
                        commission_amt += (range.amount_upto - amount_from) * commission_rate
                        amount_from = range.amount_upto
            res = self._prepare_worksheet_line(worksheet, invoice, accumulated_amt, commission_amt)
            worksheet_line_obj.create(cr, uid, res)
        return True

    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def action_confirm(self, cr, uid, ids, context=None):
        # Only if today has passed the period, allow to confirm
        period_obj = self.pool.get('account.period')
        for worksheet in self.browse(cr, uid, ids):
            period = period_obj.browse(cr, uid, worksheet.period_id.id)
            if time.strftime('%Y-%m-%d') <= period.date_stop:
                raise osv.except_osv(_('Warning!'), _("You cannot confirm this worksheet. Period not yet over!"))
            self.action_calculate(cr, uid, ids, context=context)
        # Confirm all worksheet
        self.write(cr, uid, ids, {'state': 'confirmed'})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        # Only allow cancel if no commission has been paid yet.
        worksheet_line_obj = self.pool.get('commission.worksheet.line')
        for worksheet in self.browse(cr, uid, ids):
            line_ids = worksheet_line_obj.search(cr, uid, [('commission_worksheet_id', '=', worksheet.id), ('commission_state', '=', 'done')])
            if line_ids:
                raise osv.except_osv(_('Warning!'), _("Worksheet(s) has been commission paid and can not be cancelled!"))
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    def _get_product_commission(self, cr, uid):
        ir_model_data = self.pool.get('ir.model.data')
        product = ir_model_data.get_object(cr, uid, 'sale_commission_calc', 'product_product_commission')
        return product.id

    def action_create_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context.update({'type': 'in_invoice'})
        worksheet_line_obj = self.pool.get('commission.worksheet.line')
        inv_obj = self.pool.get('account.invoice')
        invline_obj = self.pool.get('account.invoice.line')
        invoice_ids = []
        worksheets = self.browse(cr, uid, ids, context=context)
        product_id = self._get_product_commission(cr, uid)
        for worksheet in  worksheets:
            comm_unpaid = False
            users = []
            if worksheet.salesperson_id:
                comm_unpaid = worksheet.salesperson_id.comm_unpaid
                users = [worksheet.salesperson_id]
            elif worksheet.sale_team_id:
                comm_unpaid = worksheet.sale_team_id.comm_unpaid
                users = worksheet.sale_team_id.users
            else:
                continue

            if comm_unpaid:
                line_ids = worksheet_line_obj.search(cr, uid, [('commission_worksheet_id', '=', worksheet.id), ('commission_state', '!=', 'done')])
            else:
                line_ids = worksheet_line_obj.search(cr, uid, [('commission_worksheet_id', '=', worksheet.id), ('commission_state', '!=', 'done'), ('invoice_state', '=', 'paid')])
            if not line_ids:
                raise osv.except_osv(_('Warning!'), _("No Commission Invoice(s) can be created for Worksheet %s" % (worksheet.name)))

            #Create invoice for each sale person in team
            for user in users:
                #initial value of invoice
                inv_rec = inv_obj.default_get(cr, uid,
                                              ['type', 'state', 'journal_id', 'currency_id', 'company_id', 'reference_type', 'check_total',
                                               'internal_number', 'user_id', 'sent'], context=context)
                inv_rec.update(inv_obj.onchange_partner_id(cr, uid, [], 'in_invoice', user.partner_id.id, company_id=inv_rec['company_id'])['value'])
                inv_rec.update({'origin': worksheet.name,
                                'commission_worksheet_id': worksheet.id,
                                'type': 'in_invoice',
                                'partner_id': user.partner_id.id,
                                'date_invoice': time.strftime('%Y-%m-%d')})
                invoice_id = inv_obj.create(cr, uid, inv_rec, context=context)
                invoice_ids.append(invoice_id)
                wlines = worksheet_line_obj.browse(cr, uid, line_ids, context=context)
                for wline in wlines:
#                   #initial value of invoice lines
                    inv_line_rec = (invline_obj.product_id_change(cr, uid, [], product_id, False, 1, name=False, type='in_invoice',
                                    partner_id=user.partner_id.id, fposition_id=False,
                                    price_unit=0, currency_id=inv_rec['currency_id'],
                                    context=None, company_id=inv_rec['company_id'])['value'])
                    inv_line_rec.update({
                                         'name': _('Period: ') + worksheet.period_id.name + \
                                                _(', Invoice: ') + wline.invoice_id.number,
                                         'origin': worksheet.name,
                                         'invoice_id': invoice_id,
                                         'product_id': product_id,
                                         'partner_id': user.partner_id.id,
                                         'company_id': inv_rec['company_id'],
                                         'currency_id': inv_rec['currency_id'],
                                         'price_unit': wline.commission_amt,
                                         'price_subtotal': wline.commission_amt,
                                         })
                    invline_obj.create(cr, uid, inv_line_rec, context=context)
                    #Update worksheet line was paid commission
                    worksheet_line_obj.write(cr, uid, [wline.id], {'commission_state': 'done'}, context)
                if worksheet_line_obj.search_count(cr, uid, [('commission_worksheet_id', '=', worksheet.id), ('commission_state', '!=', 'done')]) <= 0:
                    #All worksheet lines has been paid will update state of worksheet is done.
                    self.write(cr, uid, [worksheet.id], {'state': 'done'})
        #Show new Invoice
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree2')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['domain'] = "[('id','in', [" + ','.join(map(str, invoice_ids)) + "])]"
        result['name'] = 'Commission invoice(s)'
        return result

    def action_calculate(self, cr, uid, ids, context=None):

        if context is None:
            context = {}

        period_obj = self.pool.get('account.period')
        worksheet_line_obj = self.pool.get('commission.worksheet.line')
        invoice_obj = self.pool.get('account.invoice')

        # For each work sheet, reset the calculation
        for worksheet in self.browse(cr, uid, ids):
            salesperson_id = worksheet.salesperson_id and worksheet.salesperson_id.id or False
            sale_team_id = worksheet.sale_team_id and worksheet.sale_team_id.id or False
            period = period_obj.browse(cr, uid, worksheet.period_id.id)
            if not (salesperson_id or sale_team_id) or not period:
                continue

            rule = (worksheet.salesperson_id and worksheet.salesperson_id.commission_rule_id) \
                    or (worksheet.sale_team_id and worksheet.sale_team_id.commission_rule_id)
            if not rule:
                raise osv.except_osv(_('Error!'), _('No commission rule specified for this salesperson/team!'))
            # Delete old lines
            line_ids = worksheet_line_obj.search(cr, uid, [('commission_worksheet_id', '=', worksheet.id)])
            worksheet_line_obj.unlink(cr, uid, line_ids)
            # Search for matched Completed Invoice for this work sheet (either salesperson or sales team)
            res_id = salesperson_id or sale_team_id
            condition = salesperson_id and 't.salesperson_id = %s' or 't.sale_team_id = %s'
            cr.execute("select ai.id from account_invoice ai \
                                join account_invoice_team t on ai.id = t.invoice_id \
                                where ai.state in ('open','paid') \
                                and date_invoice >= %s and date_invoice <= %s \
                                and " + condition + " order by ai.id", \
                                (period.date_start, period.date_stop, res_id))
            invoice_ids = map(lambda x: x[0], cr.fetchall())
            invoices = invoice_obj.browse(cr, uid, invoice_ids)
            self._calculate_commission(cr, uid, rule, worksheet, invoices, context=context)

        return True

commission_worksheet()


class commission_worksheet_line(osv.osv):

    _name = "commission.worksheet.line"
    _description = "Commission Worksheet Lines"

    def _get_paid_date(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for id in ids:
            res[id] = False
        return res

    def _calculate_last_pay_date(self, cr, uid, rule, invoice, context=None):
        if rule == 'invoice_duedate':
            return invoice.date_due
        else:
            return False

    def _get_last_pay_date(self, cr, uid, ids, name, arg, context=None):
        res = {}
        last_pay_date_rule = False
        buffer_days = 0
        if ids:
            worksheet = self.browse(cr, uid, ids[0], context=context).commission_worksheet_id
            if worksheet.salesperson_id:
                last_pay_date_rule = worksheet.salesperson_id.last_pay_date_rule
                buffer_days = worksheet.salesperson_id.buffer_days
            elif worksheet.sale_team_id:
                last_pay_date_rule = worksheet.sale_team_id.last_pay_date_rule
                buffer_days = worksheet.sale_team_id.buffer_days

        for worksheet_line in self.browse(cr, uid, ids, context=context):
            invoice = worksheet_line.invoice_id
            res[worksheet_line.id] = self._calculate_last_pay_date(cr, uid, last_pay_date_rule, invoice, context=context) \
                                        or invoice.date_due  # Default fall back date
        return res

    def _get_overdue(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for id in ids:
            res[id] = False
        return res

    _columns = {
        'commission_worksheet_id': fields.many2one('commission.worksheet', 'Commission Worksheet'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'date_invoice': fields.date('Invoice Date'),
        'invoice_amt': fields.float('Amount', readonly=True),
        'accumulated_amt': fields.float('Accumulated', readonly=True),
        'commission_amt': fields.float('Commission', readonly=True),
        'invoice_state': fields.related('invoice_id', 'state', type='selection', readonly=True, string="Status",
                                        selection=[('open', 'Open'),
                                                    ('paid', 'Paid'),
                                                    ('cancel', 'Cancelled')]),
        'paid_date': fields.function(_get_paid_date, type='date', string='Paid Date',
            help="The date of payment that make this invoice marked as paid"),
        'last_pay_date': fields.function(_get_last_pay_date, type='date', string='Due Payment Date',
            help="Last payment date that will make commission valid. This date is calculated by the due date condition"),
        'overdue': fields.function(_get_overdue, type='boolean', string='Overdue',
            help="For the paid invoice, is it over due?"),
        'commission_state': fields.selection([('draft', 'Not Ready'),
                                              ('valid', 'Ready'),
                                              ('invalid', 'Invalid'),
                                              ('done', 'Done')], 'State', required=True, readonly=True),
    }
    _defaults = {
        'commission_state': 'draft',
    }
    _order = 'id'

    def unlink(self, cr, uid, ids, context=None):
        line_ids = self.search(cr, uid, [('id', 'in', ids), ('commission_state', '=', 'done')], context=context)
        if line_ids and len(line_ids) > 0:
            wlines = self.browse(cr, uid, line_ids)
            invoice_numbers = [wline.invoice_id.number for wline in wlines]
            raise osv.except_osv(_('Error!'), _("You can't delete this Commission Worksheet, \
                                                because commission has been issued for Invoice No. %s" % (",".join(invoice_numbers))))
        else:
            return super(commission_worksheet_line, self).unlink(cr, uid, ids, context=context)

commission_worksheet_line()


class res_users(osv.osv):

    _inherit = "res.users"
    _columns = {
        'commission_rule_id': fields.many2one('commission.rule', 'Applied Commission', required=False, readonly=False),
        'comm_unpaid': fields.boolean('Allow Unpaid Invoice', help='Allow paying commission without invoice being paid.'),
        'comm_overdue': fields.boolean('Allow Overdue Payment', help='Allow paying commission with overdue payment.'),
        'last_pay_date_rule': fields.selection(LAST_PAY_DATE_RULE, 'Last Pay Date Rule'),
        'buffer_days': fields.integer('Buffer Days')
    }
    _defaults = {
        'comm_unpaid': False,
        'comm_overdue': False,
    }

res_users()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
