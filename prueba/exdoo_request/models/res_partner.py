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
        # groups="exdoo_request.group_exdoo_administrador",
        # groups="exdoo_request.group_exdoo_administrador,exdoo_request.group_exdoo_usuario",
    )
