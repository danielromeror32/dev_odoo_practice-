# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Modelo para crear una relacion con solicitudes de exdoo request"

    solicitud_id = fields.Many2one(comodel_name="exdoo.request", string="Solicitud")

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        # for solicitud in self.solicitud_id.sale_order_id:
        invoice_vals["solicitud_id"] = (
            self.solicitud_id.id
            if self.id in self.solicitud_id.sale_order_id.ids
            else False
        )
        return invoice_vals

    def _create_invoices(self, grouped=False, final=False, date=None):
        self._prepare_invoice()
        result = super(SaleOrder, self)._create_invoices(grouped, final, date)
        return result


class AccountMove(models.Model):
    _inherit = "account.move"
    _description = "Modelo para crear una relacion con solicitudes de exdoo request"
    solicitud_id = fields.Many2one(comodel_name="exdoo.request", string="solicitud")
