# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Daniel Romero ()
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################
{
    "name": "Escuela",
    "version": "1.0",
    "depends": ["mail"],
    "author": "exdoo.mx",
    "category": "Modulo extra",
    "website": "https://www.exdoo.mx/",
    "description": """
        Módulo de escuela diseñado para recopilar información relacionada con materias, docentes y estudiantes.
    """,
    "data": [
        "./views/menu.xml",
        "./security/escuela_security.xml",
        "./security/ir.model.access.csv",
        "./views/materia_view.xml",
        "./views/alumnos_views.xml",
        "./views/maestro_view.xml",
        "./data/seceuences.xml",
    ],
}
