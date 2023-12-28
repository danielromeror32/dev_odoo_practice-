# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError


logger = logging.getLogger(__name__)


class Alumno(models.Model):
    _name = "alumno"
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    full_name = fields.Char(
        string="Nombre Completo",
        compute="_compute_full_name",
        store=True,
    )
    name = fields.Char(string="Nombre")
    last_name = fields.Char(string="Apellidos", default="")

    grade = fields.Selection(
        [("1", "Grado 1"), ("2", "Grado 2"), ("3", "Grado 3")],
        string="Grado del alumno",
    )
    age = fields.Integer(string="Edad")
    no_student = fields.Char(string="Numero de alumno")

    # materia_id = fields.Many2one(comodel_name="materia", string="Materia")

    @api.depends("name", "last_name")
    def _compute_full_name(self):
        for name in self:
            name.full_name = f"{name.name} {name.last_name}"

    @api.constrains("age")
    def _check_age_range(self):
        for record in self:
            if record.age > 120 or record.age < 0:
                raise ValidationError(
                    "Edad no válida. Por favor, introduzca una edad válida."
                )

    @api.model
    def create(self, vals):
        seq_date = None
        vals["no_student"] = (
            self.env["ir.sequence"].next_by_code(
                "alumno.secuence", sequence_date=seq_date
            )
            or "/"
        )
        vals["name"] = vals["name"].title()
        vals["last_name"] = vals["last_name"].title()

        return super(Alumno, self).create(vals)

    @api.model
    def name_get(self):
        result = []
        for alumno in self:
            name = alumno.full_name or alumno.name
            result.append((alumno.id, name))
        return result
