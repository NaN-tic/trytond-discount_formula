from trytond.pool import PoolMeta
from trytond.model import fields
from .discount import DiscountMixin

class SaleLine(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'sale.line'
