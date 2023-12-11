# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Carlos Blanco (carlos.blanco@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################
{
    "name": "Actualizar Margen al confirmar venta",
    "version": "14.0",
    "depends": ["base","sale_margin","experts_groups"],
    "author": "exdoo.mx",
    "category": "Sales Modules",
    "website" : "https://www.exdoo.mx/",
    "description": """ 
        Este módulo actualiza el costo del producto para el calculo dle margen al confirmar la venta.
        
        Si tiene dudas, quiere reportar algún error o mejora póngase en contacto con nosotros: info@exdoo.mx
        """,
    "data" : [
        "security/groups.xml",
        "views/res_company_view.xml",
        "views/account_move_view.xml",
        "views/sale_order_view.xml",
        ],
    "demo": [],
    "images": [],
    "test": [],
    "installable": True,
    "active": False,
    "certificate": False,
}