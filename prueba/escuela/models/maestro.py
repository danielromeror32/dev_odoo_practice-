# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


logger = logging.getLogger(__name__)


class Maestro(models.Model):
    _name = "maestro"
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    name = fields.Char(string="Nombre del maestro")
    no_cedula = fields.Char(string="No. cedula", readonly=1)

    # materia_ids = fields.one2many()

    materia_ids = fields.One2many(
        comodel_name="materia",
        inverse_name="teacher",
        string="Materias",
    )
    

    @api.model
    def create(self, vals):
        seq_date = None
        vals["no_cedula"] = (
            self.env["ir.sequence"].next_by_code(
                "maestro.cedula.secuence", sequence_date=seq_date
            )
            or "/"
        )
        vals["name"] = vals["name"].title()
        return super(Maestro, self).create(vals)
