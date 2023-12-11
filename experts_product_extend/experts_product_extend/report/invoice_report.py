# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Carlos Blanco (carlos.blanco@exdoo.mx)
#   Migrated by: Daniel Acosta (daniel.acosta@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################

from odoo import tools
from odoo import models, fields, api


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    brand_id = fields.Many2one('product.brand', 'Marca de producto', readonly=True)

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", brand_id AS brand_id"
