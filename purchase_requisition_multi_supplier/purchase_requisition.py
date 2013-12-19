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


import openerp.netsvc
from openerp.osv import osv, fields
from openerp.tools.translate import _

class purchase_requisition_line(osv.osv):

    _inherit = "purchase.requisition.line"
    
    _columns = {
        'partner_ids': fields.many2many('res.partner', 'pr_rel_partner', 'pr_line_id', 'partner_id', 'Suppliers', ),
        'seleted_flag':fields.boolean("Select")
    }
#     def onchange_product_id(self, cr, uid, ids, product_id, product_uom_id, context=None):
#         res = super(purchase_requisition_line, self).onchange_product_id(cr, uid, ids, product_id, product_uom_id, context=None)
#         
#         product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
#         partner_ids=[]
#         for partner in product.seller_ids:
#             partner_ids.append(partner.name.id)
#             
#         ttype=set(partner_ids)
#         
#         lv = list(ttype) 
#         if len(lv)>0:
#             res.update({'domain': {'partner_ids': [('id', '=', lv)]}}) 
#         else:
#             res.update({'domain': {'partner_ids': False}})     
#             
#         return res
      
purchase_requisition_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
