# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


logger = logging.getLogger(__name__)


class Maestro(models.Model):
    _name = "maestro"

    name = fields.Char(string="Nombre del maestro")
    no_cedula = fields.Integer(string="No. cedula")
    