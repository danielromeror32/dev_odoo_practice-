    # -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SAS (www.experts.com.mx)
#   Coded by: Marco Hernández (marco.hernandez@experts.com.mx), Daniel Acosta (daniel.acosta@experts.com.mx)
#   Migrated by: Giovany Villarreal (giovany.villarreal@exdoo.mx)
#   License: https://blog.experts.com.mx/licencia-de-uso-de-software/
#
##################################################################################################
from odoo import api, fields, models, _ ,SUPERUSER_ID

class AccountMove(models.Model):
    _inherit = "account.move"

    margin_percent = fields.Float(
        string = 'Porcentaje',
        compute = '_get_margin_percent',
        readonly=True,
        default=0
    )

    def _get_margin_percent(self):
        for record in self:
            if record.margin_in_invoice != 0 and record.amount_untaxed != 0:
                record.margin_percent = record.margin_in_invoice * 100 / record.amount_untaxed
            else:
                record.margin_percent = 0

    def _get_cost_total(self):
        for invoice_row in self:
            cost_total = 0
            for line in invoice_row.invoice_line_ids:
                cost_line = 0
                cost_line = line.standard_price * line.quantity
                cost_total += cost_line
            invoice_row.cost_in_invoice = cost_total
        return {}

    def _get_margin(self):
        for invoice_row in self:
            margin = 0
            margin = sum(line.margin_line for line in invoice_row.invoice_line_ids)
            invoice_row.margin_in_invoice = margin
        return {}

    cost_in_invoice = fields.Float('Costo Total', compute="_get_cost_total", store=False)
    margin_in_invoice = fields.Float('Margen', compute="_get_margin", store=False)

    # @api.multi
    def action_invoice_open(self):
        for invoice_row in self:
            for line_row in invoice_row.invoice_line_ids:
                line_row.product_id_change_margin()
        return super(AccountMove, self).action_invoice_open()

    # @api.multi
    def recompute_margin_invoice(self):
        for inv_row in self:
            for line_row in inv_row.invoice_line_ids:
                line_row.product_id_change_margin()
        return True

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends('product_id','quantity')
    def _product_standard_price(self):
        for line in self:
            standard_price = 0
            if line.product_id.standard_price:
                standard_price = line.product_id.standard_price * line.quantity
            line.standard_price = standard_price

    @api.depends('product_id', 'standard_price', 'quantity', 'price_unit', 'price_subtotal')
    def _product_margin(self):
        for line in self:
            currency = line.move_id.currency_id
            price = line.standard_price
            if not price:
                from_cur = line.env.user.company_id.currency_id
                if line.product_id._fields.get('is_kit',False):
                    if line.product_id.is_kit:
                        purchase_price = self.get_cost_kit(line.product_id)
                    else:
                        purchase_price = line.product_id.standard_price
                else:
                    purchase_price = line.product_id.standard_price
                if line.product_id and line.product_uom_id != line.product_id.uom_id:
                    purchase_price = line.product_id.uom_id._compute_price(purchase_price, line.product_uom_id)
                price = from_cur.compute(purchase_price, currency, round=False)
                line.standard_price = price
            line.margin_line = currency.round(line.price_subtotal - (price * line.quantity))

    margin_line = fields.Float(string='Margen de producto',compute='_product_margin', digits='Product Price')
    standard_price = fields.Float(string='Costo de producto', digits='Product Price', compute='_product_standard_price', store=True)

    def get_cost_kit(self,product_id):
        cost = 0
        for product_kit in product_id.product_kit_ids:
            cost += product_kit.product_kit_id.standard_price * product_kit.qty
        return cost

    def _compute_margin(self, invoice_id, product_id, uom_id):
        frm_cur = self.env.user.company_id.currency_id
        to_cur = invoice_id.currency_id
        if product_id._fields.get('is_kit',False):
            if product_id.is_kit:
                purchase_price = self.get_cost_kit(product_id)
            else:
                purchase_price = product_id.standard_price
        else:
            purchase_price = product_id.standard_price
        if uom_id != product_id.uom_id:
            purchase_price = product_id.uom_id._compute_price(purchase_price, uom_id)
        ctx = self.env.context.copy()
        price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
        return price

    @api.onchange('product_id', 'uom_id')
    def product_id_change_margin(self):
        if not self.product_id or not self.product_uom_id:
            return
        self.standard_price = self._compute_margin(self.move_id, self.product_id, self.product_uom_id)
