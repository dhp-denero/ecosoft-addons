from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
import types

class sale_order(osv.osv):

    _inherit = 'sale.order'
    
    def _amount_line_tax_ex(self, cr, uid, line, add_disc=0.0, context=None):
        val = 0.0
        tax_obj = self.pool.get('account.tax')
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, 
                            line.price_unit * (1-(line.discount or 0.0)/100.0) * (1-(add_disc or 0.0)/100.0), 
                            line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
            if not tax_obj.browse(cr, uid, c['id']).is_wht:
                val += c.get('amount', 0.0)
        return val
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax_ex(cr, uid, line, order.add_disc, context=context) # Call new method.
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res    
    