# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class ExdooRequest(models.Model):
    _name = "exdoo.request"

    name = fields.Char(
        string="Secuencia",
        readonly=True,
        copy=False,
    )
    fecha = fields.Datetime(
        string="Fecha", copy=False, default=lambda self: fields.Datetime.now()
    )
    fecha_confirmación = fields.Date(string="Fecha de confirmación")

    cliente = fields.Many2one(string="Cliente", comodel_name="res.partner")

    termino_pagos = fields.Many2one(
        "account.payment.term",
        string="Termino de pago",
        domain="[('id', 'in', terminos_pagos_id)]",
    )

    terminos_pagos_id = fields.Many2many(
        "account.payment.term",
        string="Términos de pago permitidos",
        compute="_compute_terminos_pago_id",
    )

    @api.depends("cliente")
    def _compute_terminos_pago_id(self):
        self.termino_pagos = False
        terminos_pago = self.cliente.payment_term
        self.terminos_pagos_id = [(6, 0, terminos_pago.ids)]
        self.termino_pagos = self.cliente.property_payment_term_id
        # try:
        #     primer_termino_pago = self.terminos_pagos_id[0]
        # except IndexError:
        #
        #     primer_termino_pago = False

        # self.termino_pagos = primer_termino_pago

    usuario = fields.Many2one(
        "res.users", string="Usuario", default=lambda self: self.env.user, required=True
    )
    company = fields.Many2one(
        "res.company",
        string="Compañía",
        default=lambda self: self.env.company,
        required=True,
    )
    # Company = fields.Many2one("res.company", string="Compañía",
    #                           default = lambda self : self.env["res.company"])

    # ticket_price = fields.Monetary()
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id.id,
    )

    almacen = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Almacén",
    )

    variantes_productos = fields.Many2one(
        comodel_name="product.product", string="variantes_productos"
    )

    qty_available_temp = fields.Float(string="Cantidad a la mano")
    # qty_available_list = []
    qty_available_dict = {}

    @api.depends("variantes_productos.qty_available")
    def qty_available_warehouse(self):
        for record in self:
            for line in record.orderLines_ids:
                warehouse_id = record.almacen.id
                qty_available = line.producto.with_context(
                    warehouse=warehouse_id
                ).qty_available
                record.qty_available_list.append(qty_available)
                record.qty_available_dict[line.producto.id] = qty_available
            record.qty_available_temp = qty_available
        # logger.info(f"****** Se acciono la función qty_available_warehouse {self.qty_available_dict}********")  # {'Monitores': 0.0, 'Teclados': 20.0} or {43: 0.0, 45: 20.0}********

    def confirmar_stock(self):
        self.qty_available_warehouse()
        for line in self.orderLines_ids:
            requested_amount = line.cantidad
            requested_product = line.producto.id
            if requested_product in self.qty_available_dict:
                validacion = (
                    self.qty_available_dict[requested_product] - requested_amount
                )
                if validacion > 0:
                    logger.info(f"******valor de validación {validacion} ********")
                    self.transferir_a_ventas()
                else:
                    logger.info(
                        f"******FALTA valor de validación {validacion} ********"
                    )

    """
    cantidad 
    producto

    en el diccionario esta el id del producto y la cantidad de stock {43: 0.0, 45: 20.0}

    mismo producto y cantidad solicitada 
    """

    def transferir_a_ventas(self):
        
        datos_a_transferir = {
            "partner_id": self.cliente,
            # 'payment_term_id': self.termino_pagos,
            "company_id": self.company
            # ... otros campos del modelo de ventas ...
        }
        ventas_modelo = self.env["sale.order"]
        nuevo_registro_ventas = ventas_modelo.create(datos_a_transferir)
        logger.info(f"****** HECHO ********")

    def confirmar_request(self):
        self.state = "confirmado"
        self.fecha_confirmación = fields.Datetime.now()
        # self.qty_available_warehouse()

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

    ## Funcion lineas de orden relacionado con modulo account.tax.taxes_id
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
            #     quantity=1.0,)
            # record.total_impuestos = taxes["total_included"] - taxes["total_excluded"]
            record.base = sub_total
            record.impuestos = impuestos
            record.total = sub_total + impuestos

    orderLines_ids = fields.One2many(
        comodel_name="request.order.lines",
        inverse_name="exdoo_request_id",
        string="Lineas de orden",
        required=True,
    )

    base = fields.Monetary(string="Subtotal", compute="_compute_total", store=True)
    impuestos = fields.Monetary(
        string="Impuestos", compute="_compute_total", store=True
    )
    total = fields.Monetary(string="Total", compute="_compute_total", store=True)

    @api.model
    def create(self, vals):
        if not vals.get("name"):
            seq_date = None
            vals["name"] = (
                self.env["ir.sequence"].next_by_code(
                    "sale.order", sequence_date=seq_date
                )
                or "/"
            )
        return super(ExdooRequest, self).create(vals)

    def cancelar_request(self):
        self.state = "cancelado"


class RequestOrderLines(models.Model):
    _name = "request.order.lines"

    exdoo_request_id = fields.Many2one(
        comodel_name="exdoo.request", string="id exdoo request"
    )

    producto = fields.Many2one(string="Producto", comodel_name="product.template")

    unidades_medida = fields.Many2one(
        string="Unidades de medida",
        comodel_name="uom.uom",
        related="producto.uom_id",
        store=True,
    )
    cantidad = fields.Float(string="cantidad", default=1.0)

    list_price = fields.Float(string="Precio unitario", related="producto.list_price")
    taxes_id = fields.Many2many(
        string="Impuestos",
        comodel_name="account.tax",
        related="producto.taxes_id",
    )
    subtotal = fields.Float(string="Subtotal", readonly=True)

    total_impuestos = fields.Float(
        string="Total de Impuestos", compute="_compute_total"
    )

    total = fields.Float(string="Total", readonly=True)

    discount = fields.Float(
        string="Discount (%)",
        digits="Discount",
        default=0.0,
    )

    # Funcion para
    @api.onchange("cantidad", "list_price", "discount")
    def _onchange_cantidad(self):
        self.subtotal = self.cantidad * self.list_price

    ## Funcion lineas de orden con modulo account.tax.taxes_id
    @api.depends(
        "discount",
        "subtotal",
        "taxes_id",
    )
    def _compute_total(self):
        for record in self:
            # Calcular impuestos (tax_obj = self.env['account.tax'])
            taxes = record.taxes_id.compute_all(
                price_unit=record.list_price,
                quantity=record.cantidad,
                product=record.producto,
            )
            discount_factor = 1.0 - record.discount / 100.0
            record.subtotal = record.subtotal * discount_factor
            record.total_impuestos = (
                taxes["total_included"] - taxes["total_excluded"]
            ) * discount_factor
            record.total = taxes["total_included"] * discount_factor

    ## Función sin usar modulo Odoo
    # @api.depends("taxes_id", "subtotal", "impuesto_subtotal", "total")
    # def _compute_total(self):
    #     for record in self:
    #         total_impuestos = sum(impuesto.amount for impuesto in record.taxes_id)
    #         record.total_impuestos = total_impuestos
    #         base = record.total_impuestos / 100
    #         record.impuesto_subtotal = base * record.subtotal
    #         record.total = record.impuesto_subtotal + record.subtotal

    @api.onchange("producto")
    def _onchange_name(self):
        if self.producto and not self.taxes_id:
            default_tax = self.env["account.tax"].search(
                [("name", "=", "IVA 0% VENTAS")]
            )
            if default_tax:
                self.taxes_id = [(6, 0, [default_tax.id])]
        # if self.taxes_id == "":
        #     default = lambda self : self.env["account.tax"].search([('name', '=', "IVA 0% VENTAS")])
