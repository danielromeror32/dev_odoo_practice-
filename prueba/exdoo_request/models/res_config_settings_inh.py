# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    _description = (
        "Modelo para añadir configuraciones a ventas para permitir realizar compras"
    )
    is_purchase = fields.Boolean(string="Permitir compra")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            is_purchase=self.env["ir.config_parameter"]
            .sudo()
            .get_param("my_module.is_purchase", default=False),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "my_module.is_purchase", self.is_purchase
        )

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     res.update(
    #         is_purchase=self.env["ir.config_parameter"]
    #         .sudo()
    #         .get_param("my_module.is_purchase", default=False),
    #     )
    #     return res

    # def set_values(self):
    #     super(ResConfigSettings, self).set_values()
    #     self.env["ir.config_parameter"].sudo().set_param(
    #         "my_module.is_purchase", self.is_purchase
    #     )
