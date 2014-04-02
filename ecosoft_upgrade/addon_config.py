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
from openerp import modules, pooler, tools, addons
from openerp.tools.translate import _
import os


class addon_config(osv.osv):

    _name = "addon.config"

    def _get_addons_path(self):
        return tools.config['addons_path'].split(',')

    def _get_addon_name(self, cursor, user_id, context=None):
        addons_path = self._get_addons_path()
        res = []
        for path in addons_path:
            addon_name = os.path.basename(os.path.abspath(path + '/..')) + '-' + os.path.basename(path)
            res.append((addon_name, addon_name))
        return res

    _columns = {
        'name': fields.selection(_get_addon_name, 'Add-on Name', required=True,),
        'note': fields.text('Description'),
        'root_path': fields.char('Local Path', required=True,),
        'bzr_source': fields.char('Bazaar Source',),
        'production_path': fields.char('Production Path', required=True,),
    }

    def onchange_name(self, cr, uid, ids, name, context=None):
        res = {}
        addons = []
        addons_path = self._get_addons_path()
        for path in addons_path:
            addon_name = os.path.basename(os.path.abspath(path + '/..')) + '-' + os.path.basename(path)
            addons.append((addon_name, path))
        sel_path = next((v[1] for i, v in enumerate(addons) if v[0] == name), None)
        res.update({'value': {'production_path': sel_path}})
        return res

    def create_addon_folder(self, path, context=None):
        addon_dir = tools.config['root_path'] + 'ecosoft_upgrade'
        if  not os.path.exists(addon_dir):
            os.makedirs(addon_dir)
        return True

addon_config()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
