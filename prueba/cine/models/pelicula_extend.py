# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api


class PresupuestoExtend(models.Model):
    _inherit = "presupuesto"
    _description = "Modelo para añadir salas de ciene a peliculas"

    cines_ids = fields.Many2many(comodel_name='cine', string='Sala de cine disponible', compute='_compute_cines_ids', store=True)

    @api.depends('cines_ids')
    def _compute_cines_ids(self):
        for pelicula in self:
            cines = self.env['cine'].search([('list_available_pelicula', 'in', pelicula.id)])
            pelicula.cines_ids = cines.ids

    movie_price = fields.Monetary(string="Precio")
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id.id,
        )   