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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class sale_advance_payment_inv(osv.osv_memory):
    
    _inherit = "sale.advance.payment.inv"
    
    def _get_advance_payment_method(self, cr, uid, context=None):
        
        res = [('all', 'Invoice the whole sales order'), ('lines', 'Some order lines')]
        
        sale_id = context.get('active_id', False)
        if sale_id:
            sale = self.pool.get('sale.order').browse(cr, uid, context.get('active_id', False))
            if not len(sale.invoice_ids):
                res.append(('percentage','Percentage'))
                res.append(('fixed','Fixed price (deposit)'))
        
        return res
    
    _columns = {
        'advance_payment_method':fields.selection(_get_advance_payment_method,
            'What do you want to invoice?', required=True,
            help="""Use All to create the final invoice.
                Use Percentage to invoice a percentage of the total amount.
                Use Fixed Price to invoice a specific amound in advance.
                Use Some Order Lines to invoice a selection of the sales order lines."""),
    }
               
    def create_invoices(self, cr, uid, ids, context=None):
        res = super(sale_advance_payment_inv, self).create_invoices(cr, uid, ids, context=context)
        wizard = self.browse(cr, uid, ids[0], context)
        sale_obj= self.pool.get('sale.order')
        advance_percent = 0.0
        sale_id = context.get('active_id', False)
        if sale_id:
            # calculate the percentage of advancement
            if wizard.advance_payment_method == 'percentage':
                advance_percent = wizard.amount
            elif wizard.advance_payment_method == 'fixed':
                sale = sale_obj.browse(cr, uid, context.get('active_id', False))            
                advance_percent = (wizard.amount / sale.amount_net) * 100
            
            # write back to sale_order
            sale_obj.write(cr, uid, [sale_id], {'advance_percentage': advance_percent})
        
        return res               
               
    # This is a complete overwrite method of sale/wizard/sale_make_invoice_advance (rev8852)
    # How ever we might not need to double check it, as it only relate to type = percentage and fixed amount.
    # Which is completely changed.
    def _prepare_advance_invoice_vals(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sale_obj = self.pool.get('sale.order')
        ir_property_obj = self.pool.get('ir.property')
        fiscal_obj = self.pool.get('account.fiscal.position')
        inv_line_obj = self.pool.get('account.invoice.line')
        wizard = self.browse(cr, uid, ids[0], context)
        sale_ids = context.get('active_ids', [])

        result = []
        for sale in sale_obj.browse(cr, uid, sale_ids, context=context):
            val = inv_line_obj.product_id_change(cr, uid, [], wizard.product_id.id,
                    False, partner_id=sale.partner_id.id, fposition_id=sale.fiscal_position.id)
            res = val['value']

            # kittiu: determine and check advance customer account
            # TODO: please do also for supplier side for Purchase Order
            if not wizard.product_id.id :
                prop = ir_property_obj.get(cr, uid,
                            'property_account_advance_customer', 'res.partner', context=context)
                prop_id = prop and prop.id or False
                account_id = fiscal_obj.map_account(cr, uid, sale.fiscal_position or False, prop_id)
                if not account_id:
                    raise osv.except_osv(_('Configuration Error!'),
                            _('There is no advance customer account defined as global property.'))
                res['account_id'] = account_id
            # -- kittiu
            if not res.get('account_id'):
                raise osv.except_osv(_('Configuration Error!'),
                        _('There is no income account defined for this product: "%s" (id:%d).') % \
                            (wizard.product_id.name, wizard.product_id.id,))

            # determine invoice amount
            if wizard.amount <= 0.00:
                raise osv.except_osv(_('Incorrect Data'),
                    _('The value of Advance Amount must be positive.'))
            if wizard.advance_payment_method == 'percentage':
                # kittiu: Use net amount before Tax!!! Then, it should have tax
                inv_amount = sale.amount_net * wizard.amount / 100
                if not res.get('name'):
                    res['name'] = _("Advance of %s %%") % (wizard.amount)
                    # Get default sales tax
                    ir_values = self.pool.get('ir.values')
                    taxes_id = ir_values.get_default(cr, uid, 'product.product', 'taxes_id', company_id=sale.company_id.id)
                    #supplier_taxes_id = ir_values.get_default(cr, uid, 'product.product', 'supplier_taxes_id', company_id=sale.company_id.id)
                    res['invoice_line_tax_id'] = taxes_id  
                # -- kittiu
            else:
                inv_amount = wizard.amount
                if not res.get('name'):
                    #TODO: should find a way to call formatLang() from rml_parse
                    symbol = sale.pricelist_id.currency_id.symbol
                    if sale.pricelist_id.currency_id.position == 'after':
                        res['name'] = _("Advance of %s %s") % (inv_amount, symbol)
                    else:
                        res['name'] = _("Advance of %s %s") % (symbol, inv_amount)
                    # kittiu, Get default sales tax
                    ir_values = self.pool.get('ir.values')
                    taxes_id = ir_values.get_default(cr, uid, 'product.product', 'taxes_id', company_id=sale.company_id.id)
                    #supplier_taxes_id = ir_values.get_default(cr, uid, 'product.product', 'supplier_taxes_id', company_id=sale.company_id.id)
                    res['invoice_line_tax_id'] = taxes_id
                    # --kittiu
                    
            # determine taxes
            if res.get('invoice_line_tax_id'):
                res['invoice_line_tax_id'] = [(6, 0, res.get('invoice_line_tax_id'))]
            else:
                res['invoice_line_tax_id'] = False

            # create the invoice
            inv_line_values = {
                'name': res.get('name'),
                'origin': sale.name,
                'account_id': res['account_id'],
                'price_unit': inv_amount,
                'quantity': wizard.qtty or 1.0,
                'discount': False,
                'uos_id': res.get('uos_id', False),
                'product_id': wizard.product_id.id,
                'invoice_line_tax_id': res.get('invoice_line_tax_id'),
                'account_analytic_id': sale.project_id.id or False,
                # kittiu
                'is_advance': True
                # -- kittiu            
            }
            inv_values = {
                'name': sale.client_order_ref or sale.name,
                'origin': sale.name,
                'type': 'out_invoice',
                'reference': False,
                'account_id': sale.partner_id.property_account_receivable.id,
                'partner_id': sale.partner_invoice_id.id,
                'invoice_line': [(0, 0, inv_line_values)],
                'currency_id': sale.pricelist_id.currency_id.id,
                'comment': '',
                'payment_term': sale.payment_term.id,
                'fiscal_position': sale.fiscal_position.id or sale.partner_id.property_account_position.id,
                # kittiu
                'is_advance': True
                # -- kittiu
            }
            result.append((sale.id, inv_values))
        return result

sale_advance_payment_inv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
