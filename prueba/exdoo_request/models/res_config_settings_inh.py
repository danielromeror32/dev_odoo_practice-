# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"
    _description = "Modelo para crear una relacion con nuevas configuraciones"

    is_purchase = fields.Boolean(string="Permitir compra")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    _description = (
        "Modelo para añadir configuraciones a ventas para permitir realizar compras"
    )
    company_id = fields.Many2one("res.company")

    is_purchase = fields.Boolean(
        string="Permitir compra",
        readonly=False,
        related="company_id.is_purchase",
    )

    @api.depends("company_id")
    def _compute_has_purchase(self):
        self.has_purchase = bool(self.company_id.is_purchase)

    def set_values(self):
        super(ResConfigSettings, self).set_values()

        # compañía actual desde el usuario actual
        company = self.env.context.get("company_id") or self.env.company

        if company == self.company_id:
            self.company_id.write({"is_purchase": self.is_purchase})











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
