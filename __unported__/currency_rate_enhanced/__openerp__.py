# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2008 Camtocamp SA
#    @author JB Aubort, Nicolas Bessi, Joel Grand-Guillaume
#    European Central Bank and Polish National Bank invented by Grzegorz Grzelak
#    Ported to OpenERP 7.0 by Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#    Banxico implemented by Agustin Cruz openpyme.mx
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
{
    "name": "Currency Rate Enhanced",
    "version": "1.0",
    "author": "ECOSOFT",
    "website": "http://www.ecosoft.co.th",
    "category": "Financial Management/Configuration",
    "description": """
Features:
=========

* Enhance Currency Rate for Sales / Purchase
* Use Bigger/Smaller reference to Base Currency, so that we can always use rate > 1, instead of 0.0001 which can lead to digit inaccuracy

""",
    "depends": [
        "base", "product","account"
        ],
    "data": [
        "res_currency_view.xml",
        ],
    "demo": [],
    "active": False,
    'installable': True
}
