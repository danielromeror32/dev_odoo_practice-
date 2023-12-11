# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SAS (www.experts.com.mx)
#   Coded by: Mauricio Ruiz (mauricio.ruiz@experts.com.mx), Daniel Acosta (daniel.acosta@experts.com.mx)
#   Migrated by: Giovany Villarreal (giovany.villarreal@exdoo.mx)
#   License: https://blog.experts.com.mx/licencia-de-uso-de-software/
#
##################################################################################################

from odoo import api, fields, models, SUPERUSER_ID, release, _

class res_company(models.Model):

    _inherit = 'res.company'
    _description = "Res Company"

    prevent_sale_margin = fields.Boolean(u'Impedir venta')
    margin_percentage  = fields.Float(u'% Margen permitido')
    margin_options = fields.Selection([('sale_line','Por línea de venta'),('sale_total','Por total de venta')],"Criterio")
