# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


logger = logging.getLogger(__name__)


class Materia(models.Model):
    _name = "materia"

    name = fields.Char(string="Nombre del alumno")

    teacher = fields.Char(string="Maestro")  ## relacion con el modulo maestro
    no_cedula = fields.Integer(strring="No. Cedula")
    grade = fields.Integer(string="Grado")
    no_room = fields.Integer(string="No. Aula")
    state = fields.Selection(selection=[("active", "Activa"), ("inactive", "Inactiva")])
    # alumn_list ## relacion entre alumnos 
    


