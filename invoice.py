from trytond.pool import PoolMeta
from trytond.pyson import Eval
from .discount import DiscountMixin
from trytond.modules.discount_formula.discount import apply_discount_formula


class InvoiceLine(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'account.invoice.line'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.discount_formula.states['readonly'] = (
            Eval('invoice_state') != 'draft')
