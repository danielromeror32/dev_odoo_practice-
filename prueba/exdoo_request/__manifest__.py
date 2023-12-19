# -*- coding:utf-8 -*-

{
    "name": "modulo de Exdoo Request",
    "version": "1.0",
    "depends": ["contacts", "mail", "sale_management"],
    "author": "Daniel Romero",
    "category": "request",
    "website": "http://www.google.com",
    "summary": "Modulo de Exdoo Request",
    "description": """Este modulo lo que hará es un control de ventas, compras y movimientos de almacén.""",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "./views/menu.xml",
        "./views/exdoo_request_view.xml",
        "./views/res_partner_view.xml",
        "./views/exdoo_request_inh_view.xml",
        "./views/request_order_lines_inh_view.xml",
        "./views/res_config_settings_inh_view.xml",
    ],
}
