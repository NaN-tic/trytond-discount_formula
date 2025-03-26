from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Bool, Eval
from trytond.modules.product import round_price
from .discount import apply_discount_formula


class PriceList(metaclass=PoolMeta):
    __name__ = 'product.price_list'

    def compute_discount_formula(self, product, quantity, uom, pattern=None):
        line = self.get_price_line(product, quantity, uom, pattern=pattern)
        if line:
            return line.discount_formula

    def compute(self, product, quantity, uom, pattern=None):
        unit_price = super().compute(product, quantity, uom, pattern)

        line = self.get_price_line(product, quantity, product.default_uom,
            pattern=pattern)
        if line and line.discount_formula is not None:
            unit_price = apply_discount_formula(unit_price,
                line.discount_formula, raise_exception=False)
            if unit_price is not None:
                unit_price = round_price(unit_price)
        return unit_price


class PriceListLine(metaclass=PoolMeta):
    __name__ = 'product.price_list.line'
    discount_formula = fields.Char('Discount Formula',
        states={
            'invisible': Bool(Eval('discount_rate', False)),
        })

    @classmethod
    def __setup__(cls):
        super().__setup__()
        invisible = Bool(Eval('discount_formula', False))
        if cls.discount_rate.states.get('invisible'):
            cls.discount_rate.states['invisible'] |= invisible
        else:
            cls.discount_rate.states['invisible'] = invisible

        readonly = ((Bool(Eval('base_price_formula', False)))
            & (Bool(Eval('discount_formula', False))))
        if cls.formula.states.get('readonly'):
            cls.formula.states['readonly'] |= readonly
        else:
            cls.formula.states['readonly'] = readonly

    @classmethod
    def view_attributes(cls):
        attributes = super().view_attributes() + [
            ('/form//label[@id="discount"]', 'states', {
                'invisible':Bool(Eval('discount_formula', False))}),
            ('/form//group[@id="discounts"]', 'states', {
                'invisible':Bool(Eval('discount_formula', False))}),
            ]
        return attributes

    @fields.depends('discount_formula', 'formula')
    def update_formula(self):
        super().update_formula()
        if (self.base_price_formula and not self.discount_formula
                and not self.discount_rate
                and self.formula == '0'):
            self.formula = self.base_price_formula
        elif self.base_price_formula and self.discount_formula:
            self.formula = '0'

    @fields.depends('discount_formula', 'discount_rate', 'formula')
    def on_change_discount_formula(self):
        self.discount_rate = None
        self.update_formula()

    @fields.depends('discount_formula')
    def on_change_discount_rate(self):
        super().on_change_discount_rate()
        self.discount_formula = None
