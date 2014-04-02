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

from openerp.osv import osv
import os
import shutil


class base_module_update(osv.osv_memory):
    """ Update Module """

    _inherit = "base.module.update"

    def update_module(self, cr, uid, ids, context=None):
        addon_obj = self.pool.get('addon.config')
        addon_ids = self.pool.get('addon.config').search(cr, uid, [])
        addons_config = addon_obj.browse(cr, uid, addon_ids, context)

        self.pool.get('ecosoft.modules').unlink_all(cr, uid, context)
        for addon in addons_config:
            self.pool.get('ecosoft.modules').update_from_bzr(cr, uid, addon.id, context)
            mod_names = self.pool.get('ecosoft.modules').get_modules(cr, uid, addon.root_path)
            for mod_name in mod_names:
                result = self.pool.get('ecosoft.modules').compare_version(cr, uid, addon, mod_name, context)
                module_ids = self.pool.get('ir.module.module').search(cr, uid, [('name', '=', mod_name)])
                if result in (2, 3):
                    if module_ids:
                        vals = {'name': module_ids[0], 'addon_id': addon.id}
                        self._create_list_upgrade(cr, uid, vals, context)
                else:
                    if result == 1:
                        sourcedir = os.path.join(addon.root_path, mod_name)
                        destdir = os.path.join(addon.production_path, mod_name)
                        shutil.copytree(sourcedir, destdir)
                        if module_ids:
                            vals = {'name': module_ids[0], 'addon_id': addon.id}
                            self._create_list_upgrade(cr, uid, vals, context)

        super(base_module_update, self).update_module(cr, uid, ids, context)
        return False

    def _create_list_upgrade(self, cr, uid, vals, context):
        module_id = vals.get('name', False)
        if module_id:
            found = self.pool.get('ecosoft.modules').search(cr, uid, [('name', '=', module_id)])
            if not found:
                self.pool.get('ecosoft.modules').create(cr, uid, vals, context)

        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
