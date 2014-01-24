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
import decimal_precision as dp

class purchase_requisition_line(osv.osv):

    _inherit = "purchase.requisition.line"
    
    _columns = {
        'partner_ids': fields.many2many('res.partner', 'pr_rel_partner', 'pr_line_id', 'partner_id', 'Suppliers', ),
        'selected_flag':fields.boolean("Select"),
#         'po_line_ids': fields.many2many('purchase.order.line', 'pr_rel_po', 'pr_id', 'po_id', 'Purchase Line Orders', ondelete='cascade'),
    }
    
    _default ={
               'selected_flag':True,
               }
    def write(self, cr, uid, ids, vals, context=None):           
        res = super(purchase_requisition_line, self).write(cr, uid, ids, vals, context=context)
        return res
    
    def create(self, cr, uid, vals, context=None):
        res_id = super(purchase_requisition_line, self).create(cr, uid, vals, context=context)
        return res_id 
    
    def selected_flag_onchange(self, cr, uid, ids, selected_flag,  context=None):
        res ={'value':{'all_selected':True}}
        if not selected_flag:
            res['value'].update({'all_selected':False})   
        return res
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

class purchase_requisition(osv.osv):
    _inherit = 'purchase.requisition'
    _columns = {
        'all_selected': fields.boolean("All Select(s)"),
    }
    
    def all_selected_onchange(self, cr, uid, ids, all_selected, line_ids, context=None):
        res = {'value':{'line_ids': False}}
 
        for index in range(len(line_ids)):
            if line_ids[index][0] in (0, 1, 4):
                if line_ids[index][2]: 
                    line_ids[index][2].update({'selected_flag':all_selected})
                else:
                    if line_ids[index][0] == 4:
                        line_ids[index][0] = 1 
                    line_ids[index][2] = {'selected_flag':all_selected}
        
        res['value']['line_ids'] =  line_ids
        
        return res
purchase_requisition()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
