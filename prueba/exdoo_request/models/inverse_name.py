# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Modelo para crear una relacion con solicitudes de exdoo request"

    solicitud_id = fields.Many2one(comodel_name="exdoo.request", string="solicitud")

    def _create_invoices(self, grouped=False, final=False, date=None):
        # Lógica adicional antes de llamar al método original
        self._get_invoiced()
        logger.info(f"****** invoice_vals1******** {self.id}")
        logger.info(f"****** invoice_vals0******** {moves}")
        value = self._prepare_invoice()
        name = value["invoice_origin"]
        for solicitudes in self.solicitud_id:
            # invoice_vals = self._prepare_invoice()

            for solicitud in solicitudes.sale_order_id.ids:
                logger.info(f"****** invoice_vals2{solicitud}  ********")
                if solicitud.id == self.id:
                    solicitudes.invoice_order_id |= self.moves
                    logger.info(
                        f"****** invoice_vals3 { solicitudes.invoice_order_id }********"
                    )

                else:
                    logger.info(f"****** invoice_vals4********")

        result = super(SaleOrder, self)._create_invoices(grouped, final, date)
        return result


# cines = self.env['cine'].search([('list_available_pelicula', 'in', pelicula.id)])


class AccountMove(models.Model):
    _inherit = "account.move"
    _description = "Modelo para crear una relacion con solicitudes de exdoo request"
    solicitud_id = fields.Many2one(comodel_name="exdoo.request", string="solicitud")


# funcion donde le asigna los valores de venta a factura
