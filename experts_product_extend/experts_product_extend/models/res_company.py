# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Carlos Blanco (carlos.blanco@exdoo.mx)
#   Migrated by: Daniel Acosta (daniel.acosta@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################

from odoo import api, fields, models, _, tools

class res_company(models.Model):
    _inherit = 'res.company'

    internal_reference_unique = fields.Boolean(u'Referencia interna única')
    invoice_service_from_sales = fields.Boolean('Facturar servicios desde ventas', default=False)
    product_def_company = fields.Boolean('Compañía del usuario por defecto para producto', default=False)
    client_def_company = fields.Boolean('Compañía del usuario por defecto para cliente', default=False)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Res Config'

    invoice_service_from_sales = fields.Boolean(related='company_id.invoice_service_from_sales',readonly=False)
    product_def_company = fields.Boolean(related='company_id.product_def_company',readonly=False)
    client_def_company = fields.Boolean(related='company_id.client_def_company',readonly=False)