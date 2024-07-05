from trytond.pool import PoolMeta
from trytond.model import fields
from .discount import DiscountMixin

class PurchaseLine(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'purchase.line'

    @fields.depends('product', 'discount_formula', 'unit_price', 
        methods=['apply_discount_formula'])
    def on_change_product(self):
        super().on_change_product()

        if self.product and self.product.product_suppliers:
            supplier = self.product.product_suppliers[0]
            if supplier.prices and supplier.prices[0].discount_formula:
                self.discount_formula = supplier.prices[0].discount_formula
                self.unit_price = self.apply_discount_formula(
                    raise_exception=False)
