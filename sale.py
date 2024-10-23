from trytond.pool import PoolMeta
from .discount import DiscountMixin


class SaleLine(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'sale.line'


class SaleDiscountLine(metaclass=PoolMeta):
    __name__ = 'sale.line'

    def get_invoice_line(self):
        lines = super().get_invoice_line()
        for line in lines:
            line.discount_formula = self.discount_formula
        return lines
