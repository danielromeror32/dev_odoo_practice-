# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


logger = logging.getLogger(__name__)


class Alumno(models.Model):
    _name = "alumno"

    name = fields.Char(string="Nombre del alumno")
    grade = fields.Integer(string="Grado")
    edad = fields.Integer(string="Grado")
    # no_student = ## relacion con estudiante 