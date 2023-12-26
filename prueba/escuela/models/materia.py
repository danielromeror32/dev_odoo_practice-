# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


logger = logging.getLogger(__name__)


class Materia(models.Model):
    _name = "materia"
    _multi_company = True
    name = fields.Char(string="Materia")

    teacher = fields.Many2one(comodel_name="maestro", string="Maestro")
    no_cedula = fields.Char(string="Numero de Cedula", related="teacher.no_cedula")
    no_room = fields.Integer(string="Numero de Aula")
    state = fields.Selection(
        selection=[("active", "Activa"), ("inactive", "Inactiva")], default="inactive"
    )
    grade = fields.Selection(
        selection=[("1", "Grado 1"), ("2", "Grado 2"), ("3", "Grado 3")],
        string="Grado de los Alumnos",
    )
    alumnos_materia_ids = fields.One2many(
        comodel_name="alumnos.materia",
        inverse_name="materia_id",
        string="Alumnos",
    )

    @api.onchange("grade")
    def _onchange_grade(self):
        self.alumnos_materia_ids = False
        if self.grade:
            # Filtrar los alumnos por el grado seleccionado
            alumnos = self.env["alumno"].search([("grade", "=", self.grade)])
            self.alumnos_materia_ids = [
                (0, 0, {"alumno": alumno.id}) for alumno in alumnos
            ]

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

    def Inactiva_subject(self):
        self.state = "inactive"

    # def get_color_for_final_grade(self):
    #     color = "red" if self.final_grade > 9 else "green"
    #     return color


class AlumnosMateria(models.Model):
    _name = "alumnos.materia"

    materia_id = fields.Many2one(comodel_name="materia", string="Materia")

    alumno = fields.Many2one(
        string="Nombre del alumno",
        comodel_name="alumno",
    )

    age = fields.Integer(string="Edad", related="alumno.age")

    final_grade = fields.Float(string="Calificación")

    @api.onchange("alumno")
    def _onchange_materia_id(self):
        return {
            "domain": {
                "alumno": [("grade", "=", self.materia_id.grade)],
            }
        }
