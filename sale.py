from trytond.pool import PoolMeta
from .discount import DiscountMixin

class SaleLine(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'sale.line'
