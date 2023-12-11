# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Carlos Blanco (carlos.blanco@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################

from odoo import api, fields, models, _, tools, SUPERUSER_ID
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_recalculate_margin(self):
        for sale_row in self:
            for line in sale_row.order_line:
                if not line.product_id:
                    line.purchase_price = 0.0
                    continue
                product = line.product_id
                product_cost = product.standard_price
                if not product_cost:
                    # If the standard_price is 0
                    # Avoid unnecessary computations
                    # and currency conversions
                    line.purchase_price = 0.0
                    continue
                fro_cur = product.cost_currency_id
                to_cur = line.currency_id or line.order_id.currency_id
                if line.product_uom and line.product_uom != product.uom_id:
                    product_cost = product.uom_id._compute_price(
                        product_cost,
                        line.product_uom,
                    )
                line.purchase_price = fro_cur._convert(
                    from_amount=product_cost,
                    to_currency=to_cur,
                    company=line.company_id or self.env.company,
                    date=line.order_id.date_order or fields.Date.today(),
                    round=False,
                ) if to_cur and product_cost else product_cost
        return True

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.action_recalculate_margin()
        return res 
