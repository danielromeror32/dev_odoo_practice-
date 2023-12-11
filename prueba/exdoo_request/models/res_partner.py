# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


class PresupuestoExtend(models.Model):
    _inherit = "res.partner"
    _description = "Adicionar campo Términos de pago permitidos al modulo contactos"

    saludo = fields.Char(string="saludo")

    payment_term = fields.Many2many(
        string="Términos de pago permitidos",
        comodel_name="account.payment.term",
    )

    @api.onchange("payment_term", "property_payment_term_id")
    def _onchange_cantidad(self):
        return {
            "domain": {
                "property_payment_term_id": [("id", "in", self.payment_term.ids)]
            }
        }

    payment_term_test = fields.Many2one(
        "account.payment.term",
        string="Termino de pago prueba",
        domain="[('id', 'in', payment_term)]",
    )
