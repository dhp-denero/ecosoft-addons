import decimal_precision as dp
from osv import fields, osv
from tools.translate import _

class account_voucher_tax(osv.osv):

    _inherit = 'account.voucher.tax'

    def compute(self, cr, uid, voucher_id, context=None):
        tax_grouped = super(account_voucher_tax, self).compute(cr, uid, voucher_id, context)
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=context)
        # Loop through Tax Lines
        for line in tax_grouped:
            new_base = abs(tax_grouped[line]['base'])
            #Loop through each 1st Invoice line, find whether its tax is matched
            for voucher_line in voucher.line_ids:
                invoice = voucher_line.move_line_id.invoice
                invoice_lines = invoice.invoice_line
                first_invoice_line = invoice_lines and invoice_lines[0]
                # As we have protected for all invoice line to have same tax, we can then assume,
                if first_invoice_line and tax_grouped[line]['tax_id'] in [x.id for x in first_invoice_line.invoice_line_tax_id]:
                    new_base -= (invoice.add_disc_amt + invoice.amount_advance + invoice.amount_deposit)
            # New base
            base = abs(tax_grouped[line]['base'])
            if not base:
                continue
            ratio = new_base / base
            # Adjust
            tax_grouped[line]['base'] = tax_grouped[line]['base'] * ratio
            tax_grouped[line]['amount'] = tax_grouped[line]['amount'] * ratio
            tax_grouped[line]['base_amount'] = tax_grouped[line]['base_amount'] * ratio
            tax_grouped[line]['tax_amount'] = tax_grouped[line]['tax_amount'] * ratio

        return tax_grouped

