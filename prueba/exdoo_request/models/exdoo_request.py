# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


class ExdooRequest(models.Model):
    _name = "exdoo.request"

    name = fields.Char(string="Secuencia")
    fecha = fields.Datetime(
        string="Fecha", copy=False, default=lambda self: fields.Datetime.now()
    )
    fecha_confirmación = fields.Date(string="Fecha de confirmación")
    cliente = fields.Many2one(string="Cliente", comodel_name="res.partner")
    termino_pago = fields.Many2one("account.payment.term", string="Termino de pago")
    usuario = fields.Many2one("res.users", string="Usuario")
    Company = fields.Many2one("res.company", string="Compañía")
    # ticket_price = fields.Monetary()
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id.id,
    )

    state = fields.Selection(
        selection=[
            ("borrador", "Borrador"),
            ("confirmado", "Confirmado"),
            ("cancelado", "Cancelado"),
        ],
        default="borrador",
        string="Estado",
        copy=False,
    )
    producto = fields.Many2one(string="Producto", comodel_name="product.template")

    ## Funcion lineas de orden con modulo account.tax.taxes_id
    @api.depends("orderLines_ids")
    def _compute_total(self):
        for record in self:
            # sub_total = sum(line.subtotal for line in record.orderLines_ids)
            sub_total = 0
            impuestos = 0
            for line in record.orderLines_ids:
                sub_total += line.subtotal
                impuestos += line.total_impuestos
            # taxes = record.taxes_id.compute_all(
            #     price_unit=sub_total,
            #     quantity=1.0,

            # )
            # record.total_impuestos = taxes["total_included"] - taxes["total_excluded"]
            record.base = sub_total
            record.impuestos = impuestos
            record.total = sub_total + impuestos

    orderLines_ids = fields.One2many(
        comodel_name="request.order.lines",
        inverse_name="exdoo_request_id",
        string="Lineas de orden",
    )

    base = fields.Monetary(string="Subtotal", compute="_compute_total")
    impuestos = fields.Monetary(string="Impuestos", compute="_compute_total")
    # total_impuestos = fields.Float(
    #     string="Total de Impuestos", compute="_compute_total"
    # )
    # taxes_id = fields.Many2many(
    #     string="Impuestos",
    #     comodel_name="account.tax",
    #     # related="producto.taxes_id",
    # )
    total = fields.Monetary(string="Total", compute="_compute_total")

    def confirmar_request(self):
        self.state = "confirmado"

    def cancelar_request(self):
        self.state = "cancelado"


class RequestOrderLines(models.Model):
    _name = "request.order.lines"

    exdoo_request_id = fields.Many2one(
        comodel_name="exdoo.request", string="id exdoo request"
    )

    producto = fields.Many2one(string="Producto", comodel_name="product.template")

    unidades_medida = fields.Many2one(
        string="Unidades de medida", comodel_name="uom.uom", related="producto.uom_id"
    )
    cantidad = fields.Float(string="cantidad", default=1.0)

    list_price = fields.Float(
        string="Precio unitario",
        # related="producto.list_price"
    )
    taxes_id = fields.Many2many(
        string="Impuestos",
        comodel_name="account.tax",
        # related="producto.taxes_id",
    )
    subtotal = fields.Float(
        string="Subtotal",
    )

    total_impuestos = fields.Float(
        string="Total de Impuestos", compute="_compute_total"
    )

    # impuesto_subtotal = fields.Float()
    total = fields.Float(string="total")

    ## Funcion lineas de orden con modulo account.tax.taxes_id
    @api.depends("subtotal", "taxes_id", "subtotal")
    def _compute_total(self):
        for record in self:
            # Calcular impuestos (tax_obj = self.env['account.tax'])
            taxes = record.taxes_id.compute_all(
                record.subtotal,
                quantity=1.0,
                product=record.producto,  # Ajusta si tu modelo tiene un campo product_id
            )
            record.total_impuestos = taxes["total_included"] - taxes["total_excluded"]
            record.total = taxes["total_included"]

    ## Función sin usar modulo Odoo
    # @api.depends("taxes_id", "subtotal", "impuesto_subtotal", "total")
    # def _compute_total(self):
    #     for record in self:
    #         total_impuestos = sum(impuesto.amount for impuesto in record.taxes_id)
    #         record.total_impuestos = total_impuestos
    #         base = record.total_impuestos / 100
    #         record.impuesto_subtotal = base * record.subtotal
    #         record.total = record.impuesto_subtotal + record.subtotal

    @api.onchange("cantidad", "list_price")
    def _onchange_cantidad(self):
        self.subtotal = self.cantidad * self.list_price

    @api.onchange("producto")
    def _onchange_name(self):
        if self.producto:
            self.list_price = self.producto.list_price
            self.taxes_id = self.producto.taxes_id
