#-*- coding:utf-8 -*-

from odoo import models, fields,api

class Genre (models.Model):
    _name = "genero"
    name = fields.Char(string="Genero")