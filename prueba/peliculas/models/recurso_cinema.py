# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


class RecursoCinema(models.Model):
    _name = "recurso.cinema"

    name = fields.Char(string="Recurso")
    descripcion = fields.Char(sting="Descripción")
    precio = fields.Float(string="Precio")

    contacto_id = fields.Many2one(
        comodel_name="res.partner", domain="[('is_company', '=',False)]"
    )
    imagen = fields.Binary(string="Imagen")
