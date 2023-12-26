# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


logger = logging.getLogger(__name__)


class Maestro(models.Model):
    _name = "maestro"

    name = fields.Char(string="Nombre del maestro")
    no_cedula = fields.Char(string="No. cedula", readonly=1)

    @api.model
    def create(self, vals):
        seq_date = None
        vals["no_cedula"] = (
            self.env["ir.sequence"].next_by_code(
                "maestro.cedula.secuence", sequence_date=seq_date
            )
            or "/"
        )
        return super(Maestro, self).create(vals)
