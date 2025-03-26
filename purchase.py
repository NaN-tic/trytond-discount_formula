from trytond.pool import  PoolMeta
from trytond.model import fields
from .discount import DiscountMixin
from trytond.modules.discount_formula.discount import apply_discount_formula


class PurchaseLine(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'purchase.line'

    @fields.depends('amount',methods=['on_change_with_amount'])
    def on_change_discount_formula(self):
        super().on_change_discount_formula()
        self.amount = self.on_change_with_amount()


class PurchaseDiscountLine(metaclass=PoolMeta):
    __name__ = 'purchase.line'

    def get_invoice_line(self):
        lines = super().get_invoice_line()
        for line in lines:
            line.discount_formula = self.discount_formula
        return lines


class PurchaseLineSupplierDepends(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'purchase.line'

    @fields.depends('base_price', 'product', 'discount_formula', 'unit_price',
        'discount_rate', 'discount_amount', 'purchase_date', 'product_supplier',
        methods=['on_change_discount_formula'])
    def on_change_product(self):
        super().on_change_product()

        if self.product_supplier and self.product_supplier.prices:
            self.discount_formula = self.product_supplier.prices[0].discount_formula
            self.on_change_discount_formula()

    @fields.depends('base_price', 'product', 'discount_formula', 'unit_price',
        'discount_rate', 'discount_amount', 'purchase_date', 'product_supplier',
        methods=['on_change_discount_formula'])
    def on_change_product_supplier(self):
        try:
            super().on_change_product_supplier()
        except AttributeError:
            pass

        if self.product and self.product_supplier and self.product_supplier.prices:
            self.discount_formula = self.product_supplier.prices[0].discount_formula
            self.on_change_discount_formula()
