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
from tools.translate import _

class purchase_requisition(osv.osv):

    _inherit = "purchase.requisition"
    
    _columns = {
        'state': fields.selection([('draft','New'),
                                   ('in_purchase','Sent to Purchase'), # Additional Step
                                   ('in_progress','Sent to Suppliers'),('cancel','Cancelled'),('done','Purchase Done')],
            'Status', track_visibility='onchange', required=True)
    }
    
    def tender_in_purchase(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'in_purchase'} ,context=context)   
      
purchase_requisition()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
