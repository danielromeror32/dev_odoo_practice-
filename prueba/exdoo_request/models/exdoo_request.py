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

    usuario = fields.Many2one(
        "res.users", string="Usuario", default=lambda self: self.env.user, required=True
    )
    company = fields.Many2one(
        "res.company",
        string="Compañía",
        default=lambda self: self.env.company,
        required=True,
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id.id,
    )

    lista_precios = fields.Many2one(
        comodel_name="product.pricelist",
        string="Lista de precios",
        required=True,
    )

    almacen = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Almacén",
    )

    variantes_productos = fields.Many2one(
        comodel_name="product.product", string="variantes_productos"
    )

    qty_available_temp = fields.Float(string="Cantidad a la mano")

    registro_generado = fields.Char(string="Nombre del registro")

    # Funcion para sacar el id del almacen y los productos seleccionados en la linea de orden
    @api.depends("variantes_productos.qty_available")
    def qty_available_warehouse(self):
        self.state_validado = "validado"
        if self.orderLines_ids:
            qty_available_dict = {}
            warehouse_id = self.almacen.id
            for line in self.orderLines_ids:
                cantidad_producto = line.cantidad
                qty_available_cantidad = line.producto.with_context(
                    warehouse=warehouse_id
                ).qty_available  # {'Monitores': (0.0, 1.0), 'Teclados': (20.0, 2.0)}********
                qty_available_dict[line.producto.id] = (
                    qty_available_cantidad,
                    cantidad_producto,
                )
            self.qty_available_temp = (
                qty_available_cantidad  # campo prueba numero de stock
            )
            logger.info(
                f"****** Función qty_available_warehouse {qty_available_dict}********"
            )
            self.confirmar_stock(qty_available_dict)

    producto_compra = fields.Many2one(string="Producto", comodel_name="product.product")
    provedores = fields.Many2many(comodel_name="res.partner")

    def confirmar_stock(self, qty_available_dict):
        verificacion = True
        order_lines = []
        # {'Monitores': (0.0, 1.0), 'Teclados': (20.0, 2.0)}********
        for producto, cantidad in qty_available_dict.items():
            id_producto = producto
            self.producto_compra = id_producto
            cantidad_disponible = cantidad[0] - cantidad[1]
            provedores = self.producto_compra.seller_ids
            if cantidad_disponible > 0:
                datos_producto = self.get_order_line(
                    id_producto, "tax_id", "product_uom_qty", "product_uom"
                )
                order_lines.append((0, 0, datos_producto))
            elif cantidad_disponible <= 0 and provedores:
                verificacion = False
                datos_producto = self.get_order_line(
                    id_producto, "taxes_id", "product_uom_qty", "product_uom"
                )
                order_lines_compra = [(0, 0, datos_producto)]
                self.state_validado = "new_valido"
                for provedor in provedores:
                    self.generar_compra(order_lines_compra, provedor.name)
            else:
                self.state_validado = "new_valido"
                raise UserError(
                    f"Agrega un proveedor al producto: {self.producto_compra.default_code} {self.producto_compra.name}"
                )
        if verificacion is True:
            self.generar_venta(order_lines)

    def get_order_line(self, producto_id, tax, quantity, uom):
        order_line_vals = {}
        for line in self.orderLines_ids:  # orderLines_ids = No.reistros/productos
            if line.producto.id == producto_id:
                order_line_vals = {
                    "product_id": line.producto.id,
                    quantity: line.cantidad,
                    uom: line.unidades_medida.id,
                    "price_unit": line.list_price,
                    tax: line.taxes_id,  # [(6, 0, line.taxes_id.ids)],
                    "price_subtotal": line.subtotal,
                }
                return order_line_vals
                # order_lines.append((0, 0, order_line_vals))

    def create_invoice(self):
        order_lines = []
        if self.orderLines_ids:
            for line in self.orderLines_ids:
                producto = line.producto.id
                order = self.get_order_line(
                    producto, "tax_ids", "quantity", "product_uom_id"
                )
                order_lines.append((0, 0, order))

            self.generar_factura(order_lines)

    invoice_order_id = fields.Many2many(
        comodel_name="account.move",
        string="account Order",
        help="account Order related to this request",
    )
    # invoice_external_order_id = fields.Many2many(
    #     comodel_name="account.move",
    #     string="account Order",
    #     help="account Order related to this request",
    # )

    invoice_count = fields.Integer(
        copy=False, default=0, store=True
    )  # compute="_compute_invoice"

    def generar_factura(self, order_lines):
        datos_a_transferir = {
            "partner_id": self.cliente.id,
            # "date_order": self.fecha,
            "invoice_payment_term_id": self.termino_pagos.id,
            "currency_id": self.currency_id,
            "invoice_user_id": self.usuario.id,
            "company_id": self.company.id,
            "move_type": "out_invoice",
            "invoice_line_ids": order_lines,
        }
        ventas_modelo = self.env["account.move"]
        nuevo_registro = ventas_modelo.create(datos_a_transferir)
        self.invoice_order_id = [(4, nuevo_registro.id, 0)]
        self.invoice_count = len(self.invoice_order_id)
        logger.info(f"****** Factura de venta generada ********")

    # def action_view_invoice(self):
    #     pass

    ventas_count = fields.Integer(
        copy=False, default=0, store=True
    )  # compute="_compute_invoice"

    # @api.depends("sale_order_id")
    # def action_view_invoice(self):
    #     for sale_order in self.sale_order_id:
    #         invoices = self.env["account.move"].search(
    #             [("invoice_origin", "=", sale_order.name)]
    #         )
    #         # self.invoice_order_id = invoices.ids
    #         self.invoice_order_id = invoices.ids
    #         logger.info(f"****** Facturas {self.invoice_order_id.ids}********")

    # a = invoices.ids

    # # logger.info(f"****** Facturas {invoices}********")
    # for invoice in invoices:
    #     # Aquí puedes trabajar con cada factura asociada a la venta actual
    #     # Por ejemplo, imprimir el nombre de la factura
    #     logger.info(f"****** Factura {invoice.name}********")
    #     # print("Nombre de la factura:", invoice.name)

    @api.depends("sale_order_id")
    def action_view_invoice(self):
        logger.info(f"****** Facturas actuales {self.invoice_order_id.ids}********")
        if len(self.invoice_order_id) == 1:
            return {
                "res_model": "account.move",
                "res_id": self.invoice_order_id.id,
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "view_id": self.env.ref("account.view_out_invoice_tree").id,
            }
        else:
            # domain = [("id", "in", self.invoice_order_id.ids)]

            # for sale_order in self.sale_order_id:
            #     invoices = self.env["account.move"].search(
            #         [("invoice_origin", "=", sale_order.name)]
            #     )
            #     # self.invoice_order_id = invoices.ids
            #     self.invoice_order_id = invoices.ids
            #     logger.info(f"****** Facturas {self.invoice_order_id.ids}********")

            # invoice_order_id = self.invoice_external_order_id.ids

            domain = [("id", "in", self.invoice_order_id.ids)]

            return {
                "name": "Ventas",
                "res_model": "account.move",
                "res_id": self.invoice_order_id.id,
                "type": "ir.actions.act_window",
                "view_mode": "tree",
                "view_id": self.env.ref("account.view_out_invoice_tree").id,
                "domain": domain,
            }

    sale_order_id = fields.Many2many(
        comodel_name="sale.order",
        string="Sale Order",
        help="Sale Order related to this request",
    )

    def generar_venta(self, order_lines):
        datos_a_transferir = {
            "partner_id": self.cliente.id,
            "pricelist_id": self.lista_precios.id,
            "date_order": self.fecha,
            "payment_term_id": self.termino_pagos.id,
            "user_id": self.usuario.id,
            "company_id": self.company.id,
            "warehouse_id": self.almacen.id,
            "order_line": order_lines,
        }
        ventas_modelo = self.env["sale.order"]
        nuevo_registro = ventas_modelo.create(datos_a_transferir)
        self.registro_generado = nuevo_registro.id
        self.sale_order_id = [(4, nuevo_registro.id, 0)]
        self.ventas_count = len(self.sale_order_id)
        logger.info(f"****** Cotizacion de venta generada ********")

    # Entrar a nuevo registro de venta
    def action_view_sale(self):
        if len(self.sale_order_id) == 1:
            return {
                "res_model": "sale.order",
                "res_id": self.sale_order_id.id,
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "view_id": self.env.ref("sale.view_order_form").id,
            }
        else:
            domain = [("id", "in", self.sale_order_id.ids)]

            return {
                "name": "Ventas",
                "res_model": "sale.order",
                "res_id": self.sale_order_id.ids,
                "type": "ir.actions.act_window",
                "view_mode": "tree",
                "view_id": self.env.ref("sale.view_quotation_tree_with_onboarding").id,
                "domain": domain,
            }

    purchase_order_id = fields.Many2many(
        comodel_name="purchase.order",
        string="Purchase Orders",
        help="Purchase Orders related to this Exdoo Request",
    )

    purchase_count = fields.Integer(copy=False, default=0, store=True)

    def generar_compra(self, order_lines, provedor):
        datos_a_transferir = {
            "partner_id": provedor.id,
            "currency_id": self.currency_id.id,
            "date_order": self.fecha,
            "user_id": self.usuario.id,
            "company_id": self.company.id,
            "picking_type_id": self.almacen.in_type_id.id,
            "order_line": order_lines,
            "payment_term_id": self.termino_pagos.id,
        }

        compra_modelo = self.env["purchase.order"]
        nuevo_registro = compra_modelo.create(datos_a_transferir)
        # self.registro_generado = nuevo_registro.id
        self.purchase_order_id = [(4, nuevo_registro.id, 0)]
        self.purchase_count = len(self.purchase_order_id)
        logger.info(f"****** Cotizacion de compra generada ********")

    def action_view_purchase(self):
        if len(self.purchase_order_id) == 1:
            return {
                "res_model": "purchase.order",
                "res_id": self.purchase_order_id.id,
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "view_id": self.env.ref("purchase.purchase_order_form").id,
            }
        else:
            domain = [("id", "in", self.purchase_order_id.ids)]
            return {
                "name": "Compras",
                "res_model": "purchase.order",
                "res_id": self.purchase_order_id.ids,
                "type": "ir.actions.act_window",
                "view_mode": "tree",
                "view_id": self.env.ref("purchase.purchase_order_view_tree").id,
                "domain": domain,
            }

    def confirmar_request(self):
        self.state = "confirmado"
        self.fecha_confirmación = fields.Datetime.now()

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

    state_validado = fields.Selection(
        selection=[
            ("validado", "Validado"),
            ("new_valido", "Nueva validacion"),
        ],
        copy=False,
    )

    @api.onchange("orderLines_ids")
    def _onchange_status_validacion(self):
        self.state_validado = "new_valido"

    ## Funcion lineas de orden relacionado con modulo account.tax.taxes_id
    @api.depends("orderLines_ids")
    def _compute_total(self):
        for record in self:
            sub_total = 0
            impuestos = 0
            for line in record.orderLines_ids:
                sub_total += line.subtotal
                impuestos += line.total_impuestos
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

    producto = fields.Many2one(string="Producto", comodel_name="product.product")

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

    @api.onchange("producto")
    def _onchange_name(self):
        if self.producto and not self.taxes_id:
            default_tax = self.env["account.tax"].search(
                [("name", "=", "IVA 0% VENTAS")]
            )
            if default_tax:
                self.taxes_id = [(6, 0, [default_tax.id])]
