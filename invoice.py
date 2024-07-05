from trytond.pool import PoolMeta
from trytond.model import fields
from .discount import DiscountMixin

class InvoiceLine(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'account.invoice.line'
