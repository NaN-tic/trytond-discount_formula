import re

from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from .discount import DiscountMixin
from trytond.modules.product import price_digits


class PurchaseLine(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'purchase.line'

    @fields.depends('amount',methods=['on_change_with_amount'])
    def on_change_discount_formula(self):
        super().on_change_discount_formula()
        self.amount = self.on_change_with_amount()

    @fields.depends('base_price', 'product', 'discount_formula', 'unit_price',
        'discount_rate', 'discount_amount', 'purchase_date', 'product_supplier',
        methods=['on_change_discount_formula'])
    def on_change_product(self):
        super().on_change_product()

        if self.product_supplier and self.product_supplier.prices:
            self.discount_formula = self.product_supplier.prices[0].discount_formula
            self.on_change_discount_formula()

    @fields.depends('purchase', 'discount_formula')
    def on_change_with_discount(self, name=None):
        pool = Pool()
        Lang = pool.get('ir.lang')
        lang = Lang.get()

        if self.discount_formula:
            formula = re.sub(r'([+/])', r' \1', self.discount_formula)
            discounts = formula.split() if formula else None

            if discounts:
                result = [
                    lang.format("%s", discount.replace('+', '')) + '%'
                    if '*' not in discount and '/' not in discount else
                    ("-" + lang.currency(discount.replace(
                                    '+', '').replace('/', ''),
                            self.purchase.currency, digits=price_digits[1])
                        if self.purchase and self.purchase.currency else
                        lang.format_number(discount.replace(
                                    '+', '').replace('/', ''),
                                digits=price_digits[1], monetary=True))
                    if '/' in discount else discount.replace('+', '')
                    for discount in discounts
                    ]
                return ', '.join(result)
        return super().on_change_with_discount(name)


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
    def on_change_product_supplier(self):
        try:
            super().on_change_product_supplier()
        except AttributeError:
            pass

        if self.product and self.product_supplier and self.product_supplier.prices:
            self.discount_formula = self.product_supplier.prices[0].discount_formula
            self.on_change_discount_formula()
