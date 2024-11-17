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

    @fields.depends('invoice', 'discount_formula')
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
                            self.invoice.currency, digits=price_digits[1])
                        if self.invoice and self.invoice.currency else
                        lang.format_number(discount.replace(
                                    '+', '').replace('/', ''),
                                digits=price_digits[1], monetary=True))
                    if '/' in discount else discount.replace('+', '')
                    for discount in discounts
                    ]
                return ', '.join(result)
        return super().on_change_with_discount(name)
