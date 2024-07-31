from trytond.pool import PoolMeta
from .discount import DiscountMixin

class InvoiceLine(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'account.invoice.line'
