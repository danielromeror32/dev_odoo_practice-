# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Carlos Blanco (carlos.blanco@exdoo.mx)
#   Migrated by: Daniel Acosta (daniel.acosta@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################

{
    "name": "Mejora a producto",
    "version": "14.0",
    "depends": ["base","product","experts_groups","stock_account","stock","sale","exdoo_stock_change_qty_location"],
    "author": "exdoo.mx",
    "category": "Products Modules",
    "website" : "https://www.exdoo.mx/",
    "description": """ 
        NO se puede instalar si no esta instalado el módulo de compras.\n
        Este módulo agrega acciones para mover lineas de compra desde una compra a otra y fusionar dos compras.\n
            -   Al ejecutar la acción para mover lineas de compra, mediante un asistente se podrán seleccionar las líneas de compra que se
            -   Moverán de una compra a otra.
            -   Al seleccionar dos o mas compras para fusionarlas, en la vista lista y mediante un asistente se especificará el proveedor y se creará una nueva
            -   Orden de compra con los productos de las ordenes de compra elegidas.
            -   Añade un permiso en la configuración de la compañía para permitir o no la confirmación de una compra con precio en alguna de sus líneas en cero.
            -   Agrega el método de facturación por compra, no por producto.
            -   Solo permite agregar una cantidad mas grande a la demanda cuando se cuenta con el permiso "Recibir mas producto del solicitado"
            -   Agrega los siguientes permisos: \n

                *   Actualizar existencias desde el producto
                *   Editar referencia interna
                *   Ver costo de productos
                *   Editar precios de lista de productos
                *   Solicitar abastecimientos desde el producto

        Si tiene dudas, quiere reportar algún error o mejora póngase en contacto con nosotros: info@exdoo.mx
        """,
    "data" : [
        "security/ir.model.access.csv",
        "security/groups.xml",
        "views/res_config.xml",
        "views/res_company_view.xml",
        "views/product_view.xml",
        # "views/sale_view.xml",
        "views/purchase_view.xml",
        "views/account_view.xml",
        "views/product_brand.xml",
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': False,
}