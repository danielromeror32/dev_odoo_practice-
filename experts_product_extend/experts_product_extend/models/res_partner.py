# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Marco Rodríguez (marco.rodriguez@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################
from odoo import api, fields, models, _, tools

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    
    ###Si def_company es True, asigna por defecto la compañía del usuario
    def _get_company_id(self):
        if self.env.company.client_def_company == True:
            return self.env.company.id
        else:
            return False
    
    company_id = fields.Many2one('res.company', 'Company', index=True, default=_get_company_id)
    