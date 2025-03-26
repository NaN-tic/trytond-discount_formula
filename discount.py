import re
from decimal import Decimal

from trytond.pool import Pool
from trytond.model import fields, Model
from trytond.i18n import gettext
from trytond.exceptions import UserError
from trytond.modules.product import price_digits, round_price

__all__ = ['apply_discount_formula']

def apply_discount_formula(unit_price, formula, raise_exception=True):
    def is_number(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    m = re.compile(r'[0-9+\-*./]*$')
    if not m.match(formula):
        if raise_exception:
            raise UserError(gettext(
                'discount_formula.msg_invalid_discount_formula',
                formula=formula))
        else:
            return

    elements = formula.split('+')
    for element in elements:
        if element.count('/') == 1: #Case absolut value discount
            negative = False
            value = element.split('/')[0]
            if '-' in value:
                negative = True
                value = value.replace('-', '', 1)
            if (value and is_number(value) and element.split('/')[1] == ''):
                value = Decimal(value)
                if negative:
                    value *= -1
                unit_price = unit_price - value
            elif raise_exception:
                raise UserError(gettext(
                    'discount_formula.msg_invalid_amount_discount',
                    element=element))
            else:
                return

        elif element.count('*') == 1: #Case buy x pay y discount
            value1, value2 = element.split('*')
            if (value1 and value2
                    and value1.isdigit() and value2.isdigit()
                    and Decimal(value2) < Decimal(value1)):

                value1, value2 = Decimal(value1), Decimal(value2)
                unit_price = (value2 / value1 * unit_price)
            elif raise_exception:
                raise UserError(gettext(
                    'discount_formula.msg_invalid_multiproduct_discount',
                    element=element))
            else:
                return

        else: #Case percent discount
            negative = False
            if '-' in element:
                negative = True
                element = element.replace('-', '', 1)
            if (element and is_number(element) and float(element) <= 100):
                element = float(element)
                if negative:
                    element *= -1
                unit_price = unit_price * (1 -
                    Decimal(element * 0.01))
            elif raise_exception:
                raise UserError(gettext(
                    'discount_formula.msg_invalid_percent_discount',
                    element=element))
            else:
                return

    unit_price = round_price(unit_price)
    return unit_price if unit_price >= 0 else 0


class DiscountMixin(Model):
    discount_formula = fields.Char('Discount Formula')

    def apply_discount_formula(self):
        return apply_discount_formula(self.base_price, self.discount_formula, raise_exception=False)

    @fields.depends('base_price', 'discount_formula', 'unit_price',
        'discount_rate', 'discount_amount',
        methods=['apply_discount_formula', 'on_change_with_discount_rate',
                 'on_change_with_discount_amount' ])
    def on_change_discount_formula(self):
        if self.discount_formula is not None and self.base_price is not None:
            self.unit_price = self.apply_discount_formula()
            self.discount_rate = self.on_change_with_discount_rate()
            self.discount_amount = self.on_change_with_discount_amount()
            self.discount = self.on_change_with_discount()

    @fields.depends('base_price', 'discount_formula', 'unit_price',
        methods=['apply_discount_formula'])
    def on_change_base_price(self):
        try:
            super().on_change_base_price()
        except AttributeError:
            pass
        if self.discount_formula and self.base_price is not None:
            self.unit_price = self.apply_discount_formula()

    @fields.depends('base_price', 'discount_formula', 'unit_price',
        methods=['apply_discount_formula'])
    def on_change_unit_price(self):
        try:
            super().on_change_unit_price()
        except AttributeError:
            pass
        if self.discount_formula and self.base_price is not None:
            unit_price = self.apply_discount_formula()
            if unit_price != self.unit_price:
                self.discount_formula = None

    @fields.depends('base_price', 'discount_formula', 'unit_price',
        methods=['apply_discount_formula'])
    def on_change_discount_rate(self):
        super().on_change_discount_rate()
        if self.discount_formula and self.base_price is not None:
            unit_price = self.apply_discount_formula()
            if unit_price != self.unit_price:
                self.discount_formula = None

    @fields.depends('base_price', 'discount_formula', 'unit_price',
        methods=['apply_discount_formula'])
    def on_change_discount_amount(self):
        super().on_change_discount_amount()
        if self.discount_formula and self.base_price is not None:
            unit_price = self.apply_discount_formula()
            if unit_price != self.unit_price:
                self.discount_formula = None

    @property
    def discount_currency(self):
        if hasattr(self, 'currency'):
            return self.currency

    @fields.depends('discount_formula', methods=['discount_currency'])
    def on_change_with_discount(self, name=None):
        pool = Pool()
        Lang = pool.get('ir.lang')
        lang = Lang.get()

        currency = self.discount_currency

        def is_number(value):
            try:
                float(value)
                return True
            except ValueError:
                return False

        if self.discount_formula:
            formula = self.discount_formula
            elements = formula.split('+')

            result = []
            for element in elements:
                if element.count('/') == 1: #Case absolut value discount
                    negative = False
                    value = element.split('/')[0]
                    if '-' in value:
                        negative = True
                        value = value.replace('-', '', 1)
                    if (value and is_number(value) and element.split('/')[1] == ''):
                        if currency:
                            value = lang.currency(Decimal(value), currency,
                                    symbol=True, digits=price_digits[1])
                        result.append('-'+value if negative else value)

                elif element.count('*') == 1: #Case buy x pay y discount
                    value1, value2 = element.split('*')
                    if (value1 and value2
                            and value1.isdigit() and value2.isdigit()
                            and Decimal(value2) < Decimal(value1)):
                        result.append(element)

                else: #Case percent discount
                    negative = False
                    if '-' in element:
                        negative = True
                        element = element.replace('-', '', 1)
                    if (element and is_number(element) and float(element) <= 100):
                        # value = lang.format_number(Decimal(element),
                        #             digits=price_digits[1], monetary=True)
                        result.append('-'+element+'%' if negative else element+'%')

            return ', '.join(result)
        return super().on_change_with_discount(name)
