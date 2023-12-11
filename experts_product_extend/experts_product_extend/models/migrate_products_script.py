# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SAS (www.exdoo.mx)
#   Coded by: Daniel Acosta (daniel.acosta@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################
from odoo import api, fields, models, _, tools, SUPERUSER_ID
from odoo.exceptions import UserError
#
# Este archivo solo es usando cuando se migran los productos
#
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product Template'

    def create_from_script(self, values):
        new_ids = []
        res = False
        default_code = values.get('default_code')
        values['responsible_id'] = self._uid
        name = values.get('name')
        if not self.search([('name','=',name), ('default_code','=',default_code)]):
            res = self.create(values)
        return res.id if res else False

class ProductCategory(models.Model):
    _inherit = 'product.category'
    _description = 'Categories'

    def create_from_script(self,vals):
        res = self.sudo().create(vals)
        return res.id

class UomUom(models.Model):
    _inherit = 'uom.uom'

    def create_uom_from_script(self, vals):
        res = self.sudo().with_context(from_script=True).create(vals)
        return res.id if res else False

    @api.model
    def create(self, vals):
        res = super(UomUom, self).create(vals)
        return res

    @api.constrains('category_id', 'uom_type', 'active')
    def _check_category_reference_uniqueness(self):
        if self._context.get('from_script',False):
            return True
        
        return super(UomUom, self)._check_category_reference_uniqueness()
    
    @api.constrains('category_id')
    def _validate_uom_category(self):
        if self._context.get('from_script',False):
            return True
        return super(UomUom, self)._validate_uom_category()

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def write_from_script(self,vals):
        self.sudo().write(vals)
        return True

    def create_from_script(self,vals):
        try:
            res = self.sudo().create(vals)
            return res.ids
        except Exception as error:
            print('error: ',error)
            return False

    
class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    def write_from_script(self,vals):
        self.sudo().write(vals)
        return True

    def create_from_script(self,vals):
        try:
            res = self.sudo().create(vals)
            return res.ids
        except Exception as error:
            print('error: ',error)
            return False