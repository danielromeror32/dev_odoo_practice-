# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


logger = logging.getLogger(__name__)


class Alumno(models.Model):
    _name = "alumno"

    name = fields.Char(string="Nombre del alumno")
    grade = fields.Selection(
        [("1", "Grado 1"), ("2", "Grado 2"), ("3", "Grado 3")],
        string="Grado del alumno",
    )
    age = fields.Integer(string="Edad")
    no_student = fields.Char(string="Numero de alumno")

    @api.model
    def create(self, vals):
        seq_date = None
        vals["no_student"] = (
            self.env["ir.sequence"].next_by_code(
                "alumno.secuence", sequence_date=seq_date
            )
            or "/"
        )
        return super(Alumno, self).create(vals)
