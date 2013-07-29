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

class report_xml(osv.osv):

    _inherit = 'ir.actions.report.xml'
    _columns = {
        'views_id': fields.many2many('ir.ui.view', 'res_views_report_rel', 'uid', 'view_id', 'Views', domain="[('model','=',model),('inherit_id','=',False),('type','in',('tree','form'))]"),
    }

report_xml()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
