from osv import fields, osv

class stock_picking(osv.osv):
    
    _inherit = 'stock.picking'
    
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        """ Adding Additional Discount % from SO/PO into INV when created from DO """
        
        assert type in ('out_invoice', 'in_invoice')
        
        res = super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id,
                                                                group, type, context=context)
        # Loop through each id (DO), getting its SO/PO's Additional Discount, Write it to Invoice
        order_obj = type == 'out_invoice' and self.pool.get('sale.order') or self.pool.get('purchase.order')
        inv_obj = self.pool.get('account.invoice')
        pickings = self.browse(cr, uid, ids)
        for picking in pickings:
            add_disc = 0.0
            invoice_id = res[picking.id]
            order_ids = order_obj.search(cr, uid, [('name','=',picking.origin or '')])
            if order_ids:
                results = order_obj.read(cr, uid, order_ids, ['add_disc'])
                add_disc = results and results[0] and results[0]['add_disc'] or 0.0
                inv_obj.write(cr, uid, [invoice_id], {'add_disc': add_disc}, context)
                inv_obj.button_compute(cr, uid, [invoice_id])
        return res

