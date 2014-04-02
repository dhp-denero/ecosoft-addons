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

from openerp.osv import osv, fields
from openerp.tools.translate import _
import os
import shutil


class module(osv.osv):
    _inherit = "ir.module.module"
    _columns = {
        'ecosoft_module': fields.one2many('ecosoft.modules', 'name', 'Ecosoft Module', readonly=True),
    }

    def button_immediate_upgrade(self, cr, uid, ids, context=None):
        mods = self.browse(cr, uid, ids, context=context)
        for mod in mods:
            if mod.ecosoft_module:
                result = self.pool.get('ecosoft.modules').compare_version(cr, uid, mod.ecosoft_module[0].addon_id, mod.name, context)
                if result in (1, 2, 3):
                    sourcedir = os.path.join(mod.ecosoft_module[0].addon_id.root_path, mod.name)
                    destdir = mod.ecosoft_module[0].addon_id.production_path
                    shutil.copytree(sourcedir, destdir)
                self.pool.get('ecosoft.modules').unlink(cr, uid, [mod.ecosoft_module[0].id], context)
        return super(module, self).button_immediate_upgrade(cr, uid, ids, context)

module()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
