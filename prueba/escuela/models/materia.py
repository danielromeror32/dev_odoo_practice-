# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class Materia(models.Model):
    _name = "materia"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Materia")

    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    teacher = fields.Many2one(comodel_name="maestro", string="Maestro")
    no_cedula = fields.Char(string="No. Cedula maestro", related="teacher.no_cedula")
    no_room = fields.Integer(string="Numero de Aula")
    state = fields.Selection(
        selection=[
            ("borrador", "Borrador"),
            ("active", "Activa"),
            ("inactive", "Inactiva"),
        ],
        default="borrador",
    )
    grade = fields.Selection(
        selection=[("1", "Grado 1"), ("2", "Grado 2"), ("3", "Grado 3")],
        string="Grado",
    )
    alumno = fields.Many2one("alumno")

    alumnos_materia_ids = fields.One2many(
        comodel_name="alumnos.materia",
        inverse_name="materia_id",
        string="Alumnos",
        domain="[('alumno.grade', '=', grade)]",
    )

    # @api.onchange("grade")
    # def _onchange_grade(self):
    #     self.alumnos_materia_ids = False
    #     if self.grade:
    #         # Filtrar los alumnos por el grado seleccionado
    #         alumnos = self.env["alumno"].search([("grade", "=", self.grade)])
    #         if not self.alumnos_materia_ids in alumnos:
    #             self.alumnos_materia_ids = [
    #                 (0, 0, {"alumno": alumno.id}) for alumno in alumnos
    #             ]

    start_date = fields.Date(string="Inicio de la materia")
    end_date = fields.Date(string="Fin de la materia")

    schedule = fields.Selection(
        selection=[
            ("7 - 8", "7:00 - 8:00"),
            ("8 - 9", "8:00 - 9:00"),
            ("10 - 11", "10:00 - 11:00"),
        ],
        string="Horario",
        default="7 - 8",
    )

    def active_subject(self):
        self.state = "active"
        self.start_date = fields.Datetime.now()
        body = "El estado ha cambiado a {}".format(self.state)
        subtype_id = (
            self.env["mail.message.subtype"]
            .search([("name", "=", "Discusión")], limit=1)
            .id
        )
        self.message_post(body=body, subtype_id=subtype_id)

    def Inactiva_subject(self):
        self.state = "inactive"
        self.end_date = fields.Datetime.now()
        body = "El estado ha cambiado a {}".format(self.state)
        subtype_id = (
            self.env["mail.message.subtype"]
            .search([("name", "=", "Discusión")], limit=1)
            .id
        )
        self.message_post(body=body, subtype_id=subtype_id)


class AlumnosMateria(models.Model):
    _name = "alumnos.materia"

    materia_id = fields.Many2one(comodel_name="materia", string="Materia")

    alumno = fields.Many2one(string="Nombre del alumno", comodel_name="alumno")
    full_name = fields.Char(string="Nombre del alumno", related="alumno.full_name")

    age = fields.Integer(string="Edad", related="alumno.age")

    # grade = fields.Integer(string="Grado", related="alumno.grade")

    final_grade = fields.Float(string="Calificación")

    @api.onchange("alumno")
    def _onchange_materia_id(self):
        return {
            "domain": {
                "alumno": [("grade", "=", self.materia_id.grade)],
            }
        }

    @api.constrains("final_grade")
    def _check_age_range(self):
        for record in self:
            if record.final_grade > 10 or record.final_grade < 0:
                raise ValidationError(
                    "Edad no válida. Por favor, introduzca una edad en el rango de 1 a 10."
                )
