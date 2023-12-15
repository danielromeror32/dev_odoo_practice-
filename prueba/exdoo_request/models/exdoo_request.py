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
        # relacion ventas con solicitud
        # Generar solicitud
        self.state_validado = "validado"
        # self.state_validado = "no_validado"
        if not self.registro_generado and self.orderLines_ids:
            # self.state_validado = "validado"
            qty_available_dict = {}
            # logger.info(f"****** CONTADOR ********")
            warehouse_id = self.almacen.id
            for line in self.orderLines_ids:
                # logger.info(f"****** CONTADOR ********")  # {'Monitores': 0.0, 'Teclados': 20.0} or {43: 0.0, 45: 20.0}********
                cantidad_producto = line.cantidad
                qty_available_cantidad = line.producto.with_context(
                    warehouse=warehouse_id
                ).qty_available
                # record.qty_available_list.append(qty_available)
                qty_available_dict[line.producto.id] = (
                    qty_available_cantidad,
                    cantidad_producto,
                )  # {'Monitores': (0.0, 1.0), 'Teclados': (20.0, 2.0)}********
            self.qty_available_temp = qty_available_cantidad  # prueba
            logger.info(
                f"****** Se acciono la función qty_available_warehouse {qty_available_dict}********"
            )  # {'Monitores': 0.0, 'Teclados': 20.0} or {43: 0.0, 45: 20.0}********
            self.confirmar_stock(qty_available_dict)

    producto_compra = fields.Many2one(string="Producto", comodel_name="product.product")
    provedores = fields.Many2many(comodel_name="res.partner")

    def confirmar_stock(self, qty_available_dict):
        verificacion = True
        order_lines = []
        # order_lines_compra = []
        # {'Monitores': (0.0, 1.0), 'Teclados': (20.0, 2.0)}********
        for producto, cantidad in qty_available_dict.items():
            id_producto = producto
            self.producto_compra = id_producto
            cantidad_disponible = cantidad[0] - cantidad[1]
            logger.info(
                f"****** Resultado de la resta para '{id_producto}': {cantidad_disponible}********"
            )
            provedores = self.producto_compra.seller_ids

            # datos_producto = self.get_order_line(id_producto)

            if cantidad_disponible > 0:
                datos_producto = self.get_order_line(id_producto, "tax_id")
                order_lines.append((0, 0, datos_producto))
            elif cantidad_disponible <= 0 and provedores:
                datos_producto = self.get_order_line(id_producto, "taxes_id")
                verificacion = False
                # order_lines_compra = ((0, 0, datos_producto))
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
        logger.info(f"******DATOS  {self.producto_compra} ********")
        # else:
        #     self.state_validado = "new_valido"  # Seguir validando
        #     for provedor in provedores:
        #         # logger.info(f"******DATOS Provedores {provedor.name} ********")
        #         self.generar_compra(order_lines_compra, provedor.name)
        #         break

    def get_order_line(self, producto_id, tax):
        order_line_vals = {}
        for line in self.orderLines_ids:  # orderLines_ids = No.reistros/productos
            # logger.info(f"****** Valor de producto {producto_id} ********")
            if (
                line.producto.id == producto_id
            ):  # Verifica si el producto_id coincide con el producto de la línea actual
                order_line_vals = {
                    "product_id": line.producto.id,
                    "product_uom_qty": line.cantidad,
                    "product_uom": line.unidades_medida.id,
                    "price_unit": line.list_price,
                    tax: line.taxes_id,  # [(6, 0, line.taxes_id.ids)],
                    # "discount": line.discount,
                    "price_subtotal": line.subtotal,
                }
                return order_line_vals
                # order_lines.append((0, 0, order_line_vals))

    ventas_count = fields.Integer(
        copy=False, default=0, store=True
    )  # compute="_compute_invoice"

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

    def action_view_sale(self):
        return {
            "res_model": "sale.order",
            "res_id": self.sale_order_id.id,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": self.env.ref("sale.view_order_form").id,
        }

    purchase_order_id = fields.Many2many(
        comodel_name="purchase.order",
        string="Compra order",
        help="purchase Order related to this request",
    )

    purchase_count = fields.Integer(
        copy=False, default=0, store=True
    )  

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
        return {
            "res_model": "purchase.order",
            "res_id": self.purchase_order_id.id,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": self.env.ref("purchase.purchase_order_form").id,
        }

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
