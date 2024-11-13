from trytond.pool import Pool, PoolMeta
from .discount import DiscountMixin
from trytond.model import fields
from trytond.transaction import Transaction


class SaleLine(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'sale.line'


class SaleDiscountLine(metaclass=PoolMeta):
    __name__ = 'sale.line'

    def get_invoice_line(self):
        lines = super().get_invoice_line()
        for line in lines:
            line.discount_formula = self.discount_formula
        return lines


class SaleDiscountPriceListLine(metaclass=PoolMeta):
    __name__ = 'sale.line'

    @fields.depends('product', 'quantity', 'unit', 'sale',
        '_parent_sale.price_list')
    def update_discount(self):
        pool = Pool()
        PriceList = pool.get('product.price_list')

        super().update_discount()

        price_list = None
        context = Transaction().context

        if self.sale:
            price_list = self.sale.price_list
        if context.get('price_list'):
            price_list = PriceList(context.get('price_list'))
        if price_list and self.unit:
            discount_formula = price_list.compute_discount_formula(self.product,
                self.quantity, self.unit)
            if not (discount_formula is None or discount_formula == ''):
                self.discount_formula = discount_formula
                self.on_change_discount_formula()
