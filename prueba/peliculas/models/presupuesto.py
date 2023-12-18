# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime


logger = logging.getLogger(__name__)


class Presupuesto(models.Model):
    _name = "presupuesto"
    _description = "Modulo para el presupuesto de peliculas"
    _inherit = ["mail.thread", "mail.activity.mixin", "image.mixin"]

    @api.depends("detalle_ids")
    def _compute_total(self):
        for record in self:
            subtotal = 0
            for line in record.detalle_ids:
                subtotal += line.importe
            record.base = subtotal
            record.impuestos = subtotal * 0.16
            record.total = subtotal * 1.16

    detalle_ids = fields.One2many(
        comodel_name="presupuesto.detalle",
    inverse_name="presupuesto_id",
        string="Detalles",
    )

    name = fields.Char(string="Película")

    clasificacion = fields.Selection(
        selection=[
            ("G", "G"),
            ("PG", "PG"),
            ("PG-13", "PG-13"),
            ("R", "R"),
            ("NC-17", "NC-17"),
        ],
        string="Clasificación",
    )
    dsc_clasificacion = fields.Char(string="descripcion clasificacion")
    fecha_estreno = fields.Date(string="Fecha de estreno")
    puntuacion = fields.Integer(string="Puntación", related="puntuacion_value")
    puntuacion_value = fields.Integer(String="Puntacion")
    active = fields.Boolean(string="Mostrar", default=True)

    categoria_director_id = fields.Many2one(
        comodel_name="res.partner.category",
        String="Categoria director",
        default=lambda self: self.env.ref("peliculas.category_director")  # External ID
        # default=lambda self: self.env["res.partner.category"].search(
        #     [("name", "=", "Director")]
        # ),
    )
    director_id = fields.Many2one(string="Director", comodel_name="res.partner")

    categoria_actor_id = fields.Many2one(
        comodel_name="res.partner.category",
        String="Categoria actor",
        default=lambda self: self.env.ref("peliculas.category_actor")  # External ID
        # default=lambda self: self.env["res.partner.category"].search(
        #     [("name", "=", "Director")]
        # ),
    )
    actor_id = fields.Many2many(string="Actor", comodel_name="res.partner")

    opinion = fields.Html(string="Opinion")

    genero_ids = fields.Many2many(string="Genero", comodel_name="genero")
    vista_general = fields.Text(string="Descripción")
    link_trailer = fields.Char(string="trailer")
    es_libro = fields.Boolean(string="Version libro")
    libro = fields.Binary(string="Libro")
    libro_filename = fields.Char(string="Nombre del libro")

    fecha_aprobado = fields.Datetime(string="fecha aprobado", copy=False)
    fecha_creacion = fields.Datetime(
        string="fecha creación", copy=False, default=lambda self: datetime.now()
    )

    state = fields.Selection(
        selection=[
            ("borrador", "Borrador"),
            ("aprobado", "Aprobado"),
            ("cancelado", "Cancelado"),
        ],
        default="borrador",
        string="Estados",
        copy=False,
    )

    numero_presupuesto = fields.Char(String="Numero presupuesto", copy=False)

    campos_ocultos = fields.Boolean(string="Campos ocultos")

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id.id,
    )

    terminos = fields.Text(string="Terminos")
    base = fields.Monetary(string="Base imponible", compute="_compute_total")
    impuestos = fields.Monetary(string="Impuestos", compute="_compute_total")
    total = fields.Monetary(string="Total", compute="_compute_total")

    def aprobar_presupuesto(self):
        logger.info("Función aprobar")
        self.state = "aprobado"
        self.fecha_aprobado = datetime.now()

    def cancelar_presupuesto(self):
        logger.info("Función cancelar")
        self.state = "cancelado"

    def unlink(self):
        for record in self:
            logger.info("**** Se acciono la función unlink****")
            if record.state != "cancelado":
                raise UserError(
                    "No se puede eliminar el registro porque se encuentra en un estado de cancelado"
                )
            super(Presupuesto, record).unlink()

    @api.model
    def create(self, dic_variables):
        logger.info(f"**** Se acciono la función create {dic_variables}****")

        secuence_object = self.env["ir.sequence"]
        correlativo = secuence_object.next_by_code("secuencia.presupuesto.pelicula")
        dic_variables["numero_presupuesto"] = correlativo

        return super(Presupuesto, self).create(dic_variables)

    def write(self, variables):
        logger.info(f"**** Se acciono la función create {variables}****")
        if "clasificacion" in variables:
            raise UserError("No se puede modificar el registro clasificación")
        return super(Presupuesto, self).write(variables)

    def copy(self, default=None):
        logger.info(f"**** Se acciono la función copiar {default}****")
        default = dict(default or {})
        logger.info(f"***************** Se accionoooo la función copiar {default}****")
        default["name"] = self.name + " (Copy)"
        default["puntuacion_value"] = 1
        return super(Presupuesto, self).copy(default)

    @api.onchange("clasificacion")
    def _onchange_clasificacion(self):
        if self.clasificacion:
            if self.clasificacion == "G":
                self.dsc_clasificacion = "Publico general"
            if self.clasificacion == "PG":
                self.dsc_clasificacion = "Se recomineda la compania de un adulto"
            if self.clasificacion == "PG-13":
                self.dsc_clasificacion = "Mayores de 13"
            if self.clasificacion == "R":
                self.dsc_clasificacion = "En la compañia de un adulto"
            if self.clasificacion == "NC-17":
                self.dsc_clasificacion = "Mayores de 18"
        else:
            self.dsc_clasificacion = False


class PresupuestoDetalle(models.Model):
    _name = "presupuesto.detalle"

    presupuesto_id = fields.Many2one(comodel_name="presupuesto", string="Presupuesto")

    name = fields.Many2one(
        comodel_name="recurso.cinema",  # model inventario: product.product
        string="Recurso",
    )
    descripcion = fields.Char(string="Descripcion", related="name.descripcion")
    contacto_id = fields.Many2one(
        comodel="res.partner", string="Contacto", related="name.contacto_id"
    )

    imagen = fields.Binary(string="Imagen", related="name.imagen")
    cantidad = fields.Float(
        string="Cantidad", default=1.0, digits=(16, 4)
    )  # Maximo 16 digitos con 4 ceros
    precio = fields.Float(String="Precio", digits="Product Price")
    importe = fields.Monetary(string="Importe")

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        related="presupuesto_id.currency_id",
    )

    @api.onchange("name")
    def _onchange_name(self):
        if self.name:
            self.precio = self.name.precio

    @api.onchange("cantidad", "precio")
    def _onchange_importe(self):
        self.importe = self.cantidad * self.precio
