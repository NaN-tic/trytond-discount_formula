import re

from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from trytond.pyson import Eval
from .discount import DiscountMixin
from trytond.modules.product import price_digits


class InvoiceLine(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'account.invoice.line'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.discount_formula.states['readonly'] = (
            Eval('invoice_state') != 'draft')
