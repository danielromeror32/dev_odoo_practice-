# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class Materia(models.Model):
    _name = "materia"
    _description = "Registros de materia"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Materia")

    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    teacher_id = fields.Many2one(comodel_name="maestro", string="Maestro")
    no_cedula = fields.Char(string="No. Cedula maestro", related="teacher_id.no_cedula")
    no_room = fields.Integer(string="Numero de Aula")
    state = fields.Selection(
        selection=[
            ("borrador", "Borrador"),
            ("active", "Activa"),
            ("inactive", "Inactiva"),
        ],
        default="borrador",
        string="Estado",
    )
    grade = fields.Selection(
        selection=[("1", "Grado 1"), ("2", "Grado 2"), ("3", "Grado 3")],
        string="Grado",
    )

    alumnos_materia_ids = fields.One2many(
        comodel_name="alumnos.materia",
        inverse_name="materia_id",
        string="Alumnos",
        domain="[('alumno_id.grade', '=', grade)]",
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

    @api.constrains("no_room")
    def _check_age_range(self):
        for room in self:
            if room.no_room > 500 or room.no_room < 0:
                raise ValidationError(
                    "Número de aula no válida. Por favor, introduzca un número de aula válido."
                )

    def active_subject(self):
        self.state = "active"
        self.start_date = fields.Datetime.now()
        body = f"Materia activada"
        subtype_id = (
            self.env["mail.message.subtype"]
            .search([("name", "=", "Discusión")], limit=1)
            .id
        )
        self.message_post(body=body, subtype_id=subtype_id)

    def Inactiva_subject(self):
        self.state = "inactive"
        self.end_date = fields.Datetime.now()
        body = f"Materia inactiva"
        subtype_id = (
            self.env["mail.message.subtype"]
            .search([("name", "=", "Discusión")], limit=1)
            .id
        )
        self.message_post(body=body, subtype_id=subtype_id)


class AlumnosMateria(models.Model):
    _description = "Seguimiento de lista de los alumnos"
    _name = "alumnos.materia"

    materia_id = fields.Many2one(comodel_name="materia", string="Materia")

    alumno_id = fields.Many2one(comodel_name="alumno")
    full_name = fields.Char(string="Nombre del alumno", related="alumno_id.full_name")

    age = fields.Integer(string="Edad", related="alumno_id.age")

    final_grade = fields.Float(string="Calificación")

    @api.onchange("alumno_id")
    def _onchange_materia_id(self):
        return {
            "domain": {
                "alumno_id": [("grade", "=", self.materia_id.grade)],
            }
        }

    @api.constrains("final_grade")
    def _check_age_range(self):
        for score in self:
            if score.final_grade > 10 or score.final_grade < 0:
                raise ValidationError(
                    "Calificación no válida. Por favor, introduzca una calificación en el rango de 0 a 10."
                )
