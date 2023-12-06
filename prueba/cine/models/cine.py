# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class Cine(models.Model):
    _name = "cine"
    _description = "Modulo para el registro de cine"
    name = fields.Char(string="Nombre de la sala")
    cinema_owner = fields.Many2one(string="Responsable", comodel_name="res.partner")
    room_number = fields.Integer(string="Numero de sala")
    ticket_price = fields.Monetary(string="Costo del boleto")

    currency_id = fields.Many2one(
    comodel_name="res.currency",
    string="Moneda",
    default=lambda self: self.env.company.currency_id.id,
    )

    list_available_pelicula = fields.Many2many(
        comodel_name="presupuesto",
        string="Peliculas disponibles",
        domain="[('state', '=', 'aprobado')]",
    )
    # status_pelicula = fields.Many2many(
    #     comodel_name="presupuesto",
    #     string="categoria pelicula",
    #     # default=lambda self: self.env.ref("peliculas.category_actor")
    #     default=lambda self: self.env["presupuesto"].search(
    #         [("state", "=" , "Aprobado")]
    #     )
    #     # default=lambda self: self.env.presupuesto.state,
    # )
