# -*- coding:utf-8 -*-       # "./views/cine_view.xml",
import logging
from odoo import models, fields, api


class UpdateWizard(models.TransientModel):
    _name = "update.wizard"
    name = fields.Text(string="Nueva descripcion")

    def update_vista_general(self): 
        presupuesto_obj = self.env["presupuesto"]
        # presupuesto_id = presupuesto_obj.search([('id', '=', self._context['active_id'])])
        presupuesto_id = presupuesto_obj.browse(self._context["active_id"])
        presupuesto_id.vista_general = self.name
