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
        
        "security/security.xml",
          "security/ir.model.access.csv",
        "views/menu.xml",
        "./wizard/update_wizard_views.xml",
        "./report/reporte_pelicula.xml",
        "./data/categoria.xml",
        "./data/secuencia.xml",
         "./views/presupuesto_views.xml",
    ],
}
