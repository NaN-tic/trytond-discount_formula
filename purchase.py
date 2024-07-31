from trytond.pool import PoolMeta
from trytond.model import fields
from .discount import DiscountMixin

class PurchaseLine(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'purchase.line'

    @fields.depends('base_price', 'product', 'discount_formula', 'unit_price',
        'discount_rate', 'discount_amount', 'purchase_date',
        methods=['apply_discount_formula', 'on_change_with_discount_rate'])
    def on_change_product(self):
        super().on_change_product()

        if self.product and self.product.product_suppliers:
            supplier = self.product.product_suppliers[0]
            for price in supplier.prices:
                if (self.purchase_date
                        and (not price.start_date
                             or self.purchase_date >= price.start_date)
                        and (not price.end_date
                             or self.purchase_date <= price.end_date)):
                    self.discount_formula = price.discount_formula
                    break
            if self.discount_formula and self.base_price:
                self.unit_price = self.apply_discount_formula(
                    raise_exception=False)
                self.discount_rate = self.on_change_with_discount_rate()
                self.discount_amount = self.on_change_with_discount_amount()
