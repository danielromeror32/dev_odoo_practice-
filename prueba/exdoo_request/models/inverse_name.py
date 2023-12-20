# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Modelo para crear una relacion con solicitudes de exdoo request"

    solicitud_id = fields.Many2one(comodel_name="exdoo.request", string="solicitud")


class AccountMove(models.Model):
    _inherit = "account.move"
    _description = "Modelo para crear una relacion con solicitudes de exdoo request"

    solicitud_id = fields.Many2one(comodel_name="exdoo.request", string="solicitud")
