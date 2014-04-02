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
import zipfile
from os.path import join as opj
from bzrlib.branch import Branch
import bzrlib.directory_service
import bzrlib.plugin
from openerp.tools import float_compare

bzrlib.plugin.load_plugins()


class ecosoft_modules(osv.osv):

    _name = "ecosoft.modules"
    _columns = {
        'name': fields.many2one('ir.module.module', 'Module Name', readonly=True, select=True),
        'addon_id': fields.many2one('addon.config', 'Add-on Name', readonly=True, select=True),
        'state': fields.related('name', 'state', type="many2one", relation="ir.module.module", string="Status",
                store=False),
    }

    def get_modules(self, cr, uid, path):
        """Returns the list of module names
        """
        def listdir(dir):
            def clean(name):
                name = os.path.basename(name)
                if name[-4:] == '.zip':
                    name = name[:-4]
                return name

            def is_really_module(name):
                manifest_name = opj(dir, name, '__openerp__.py')
                zipfile_name = opj(dir, name)
                return os.path.isfile(manifest_name) or zipfile.is_zipfile(zipfile_name)
            return map(clean, filter(is_really_module, os.listdir(dir)))

        plist = []
        plist.extend(listdir(path))
        return list(set(plist))

    def unlink_all(self, cr, uid, context):
        ids = self.search(cr, uid, [('state', '!=', 'uninstalled')])
        self.unlink(cr, uid, ids, context)
        return True

    def update_from_bzr(self, cr, uid, addon_id, context=None):
        addon_obj = self.pool.get('addon.config')
        addon_config = addon_obj.browse(cr, uid, addon_id, context)
        if addon_config:
            if addon_config.bzr_source:
                if not os.path.exists(addon_config.root_path):
                    # this helps us determine the full address of the remote branch
                    branchname = bzrlib.directory_service.directories.dereference(addon_config.bzr_source)
                    # let's now connect to the remote branch
                    remote_branch = Branch.open(branchname)
                    # download the branch
                    remote_branch.bzrdir.sprout(addon_config.root_path).open_branch()
                else:
                    b1 = Branch.open(addon_config.root_path)
                    b2 = Branch.open(addon_config.bzr_source)
                    b1.pull(b2)

        return True

    def compare_version(self, cr, uid, addon_config, module_name, context):
        """
        """
        sourcedir = os.path.join(addon_config.root_path, module_name)
        destdir = os.path.join(addon_config.production_path, module_name)

        if not os.path.isdir(sourcedir):
            return False

        if not os.path.isdir(destdir):
            return 1
        #Compare with DateTime
        source_date = os.path.getmtime(sourcedir)
        destination_date = os.path.getmtime(destdir)

        if float_compare(source_date, destination_date, 2) == 0:
            return False
        else:
            if float_compare(source_date, destination_date, 2) == -1:
                return 2
            else:
                return 3
ecosoft_modules()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
