# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Carlos Blanco (carlos.blanco@exdoo.mx)
#   Migrated by: Daniel Acosta (daniel.acosta@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.addons.stock.models.product import OPERATORS
from odoo.tools.float_utils import float_round
from odoo.tools import float_compare

class ProductCategory(models.Model):
    _inherit = "product.category"
    _description = "Product Category"

    ref = fields.Char('Referencia', size=64)

class ProductBrand(models.Model):
    _name = "product.brand"
    _description = 'Marca de producto'

    name = fields.Char('Nombre', size=64, required=True)
    description = fields.Text('Descripción')

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    def validate_default_code(self,default_code):
        # Si especifican default_code
        if default_code:
            # Si se debe validar la referencia interna única
            if self.env.user.company_id.internal_reference_unique:
                # Validamos que no exista
                product_ids = self.search([('default_code','=',default_code.strip())])
                if product_ids:
                    raise UserError (_('Ya existe un producto con esta referencia interna.'))
        return True
    
    ###Si def_company es True, asigna por defecto la compañía del usuario
    def _get_company_id(self):
        if self.env.company.product_def_company == True:
            return self.env.company.id
        else:
            return False
    
    company_id = fields.Many2one('res.company', 'Company', index=True, default=_get_company_id)
        
    @api.model
    def create(self, vals):
        default_code = vals.get('default_code')
        self.validate_default_code(default_code)
        rec = super(ProductTemplate, self).create(vals)
        return rec

    def write(self, vals):
        default_code = vals.get('default_code')
        if default_code:
            self.validate_default_code(default_code)
        res = super(ProductTemplate, self).write(vals)
        return res

    def _get_stock_value(self):
        for product_row in self:
            product_row.stock_value = product_row.standard_price * product_row.qty_available

    sale_guarantee = fields.Float(u'Garantía de venta',default='0.0')
    brand_id = fields.Many2one( 'product.brand', 'Marca')
    model = fields.Char('Modelo', size=64)
    stock_value =fields.Float(compute=_get_stock_value, string="Valor de stock")
    volume = fields.Float('Volume',digits='Volume', compute='_compute_volume', inverse='_set_volume',help="Volumen en m3.", store=True)
    qty_available_not_res = fields.Float(
        string='Disponible',
        digits='Product Unit of Measure',
        compute='_compute_product_available_not_res',
        search='_search_quantity_unreserved',
    )
    shelf = fields.Char('Estante')
    row = fields.Char('Fila')
    box = fields.Char('Caja')

    @api.depends('product_variant_ids.qty_available_not_res')
    def _compute_product_available_not_res(self):
        for tmpl in self:
            if isinstance(tmpl.id, models.NewId):
                continue
            tmpl.qty_available_not_res = sum(
                tmpl.mapped('product_variant_ids.qty_available_not_res')
            )

    def _search_quantity_unreserved(self, operator, value):
        domain = [('qty_available_not_res', operator, value)]
        product_variant_ids = self.env['product.product'].search(domain)
        return [('product_variant_ids', 'in', product_variant_ids.ids)]

class Product(models.Model):
    _inherit = "product.product"

    def _get_stock_value_variant(self):
        for product_row in self:
            product_row.stock_value_varian = product_row.standard_price * product_row.qty_available

    stock_value_varian = fields.Float(compute=_get_stock_value_variant, string="Valor de stock")

    qty_available_not_res = fields.Float(
        string='Disponible',
        digits='Product Unit of Measure',
        compute='_compute_qty_available_not_reserved',
        search="_search_quantity_unreserved",
    )

    def _prepare_domain_available_not_reserved(self):
        domain_quant = [
            ('product_id', 'in', self.ids),
        ]
        domain_quant_locations = self._get_domain_locations()[0]
        domain_quant.extend(domain_quant_locations)
        return domain_quant

    def _compute_product_available_not_res_dict(self):

        res = {}

        domain_quant = self._prepare_domain_available_not_reserved()
        quants = self.env['stock.quant'].with_context(lang=False).read_group(
            domain_quant,
            ['product_id', 'location_id', 'quantity', 'reserved_quantity'],
            ['product_id', 'location_id'],
            lazy=False)
        product_sums = {}
        for quant in quants:
            # create a dictionary with the total value per products
            product_sums.setdefault(quant['product_id'][0], 0.)
            product_sums[quant['product_id'][0]] += (
                quant['quantity'] - quant['reserved_quantity']
            )
        for product in self.with_context(prefetch_fields=False, lang=''):
            available_not_res = float_round(
                product_sums.get(product.id, 0.0),
                precision_rounding=product.uom_id.rounding
            )
            res[product.id] = {
                'qty_available_not_res': available_not_res,
            }
        return res

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    def _compute_qty_available_not_reserved(self):
        res = self._compute_product_available_not_res_dict()
        for prod in self:
            qty = res[prod.id]['qty_available_not_res']
            prod.qty_available_not_res = qty
        return res

    def _search_quantity_unreserved(self, operator, value):
        if operator not in OPERATORS:
            raise UserError(_('Invalid domain operator %s') % operator)
        if not isinstance(value, (float, int)):
            raise UserError(_('Invalid domain right operand %s') % value)

        ids = []
        for product in self.search([]):
            if OPERATORS[operator](product.qty_available_not_res, value):
                ids.append(product.id)
        return [('id', 'in', ids)]

    def _select_seller(self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False):
        ##############################################################################################
        # Se sobrescribe la original para agregar todos los proveedores y luego ordenarlos por costo
        # ya que solo estaba tomando el primero
        ##############################################################################################
        self.ensure_one()
        if date is None:
            date = fields.Date.context_today(self)
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        res = self.env['product.supplierinfo']
        sellers = self._prepare_sellers(params)
        sellers = sellers.filtered(lambda s: not s.company_id or s.company_id.id == self.env.company.id)
        for seller in sellers:
            # Set quantity in UoM of seller
            quantity_uom_seller = quantity
            if quantity_uom_seller and uom_id and uom_id != seller.product_uom:
                quantity_uom_seller = uom_id._compute_quantity(quantity_uom_seller, seller.product_uom)

            if seller.date_start and seller.date_start > date:
                continue
            if seller.date_end and seller.date_end < date:
                continue
            if partner_id and seller.name not in [partner_id, partner_id.parent_id]:
                continue
            if quantity is not None and float_compare(quantity_uom_seller, seller.min_qty, precision_digits=precision) == -1:
                continue
            if seller.product_id and seller.product_id != self:
                continue
            # Solo comentamos esta linea para que tome todos los proveedores que sean permitidos
            # if not res or res.name == seller.name:
            res |= seller
        return res.sorted('price')[:1]


class ProductChangeQuantity(models.TransientModel):
    _inherit = "stock.change.product.qty"
    _description = "Change Product Quantity"

    @api.constrains('new_quantity')
    def check_new_quantity(self):
        # Se elimina la validacion para poder actualizar cantidades negativas en productos
        pass