# -*- coding:utf-8 -*-

{
    "name": "modulo de peliculas",
    "version": "1.0",
    "depends": ["contacts", "mail"],
    "author": "Daniel Romero",
    "category": "peliculas",
    "website": "http://www.google.com",
    "summary": "Modulo de presupuestos para peliculas",
    "description": """Modulos para hacer presupuestos de peliculas""",
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "./data/categoria.xml",
        "./data/secuencia.xml",
        "./wizard/update_wizard_views.xml",
        "./report/reporte_pelicula.xml",
        "views/menu.xml",
        "./views/presupuesto_views.xml",
    ],
}
