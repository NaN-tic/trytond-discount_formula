from decimal import Decimal

from trytond.pool import Pool, PoolMeta
from trytond.model import fields, ModelView
from trytond.pyson import Eval
from trytond.transaction import Transaction
from .discount import DiscountMixin, ApplyDiscountMixin


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    sale_discount_formula = fields.Char('Sale Discount Formula',
        states={
            'readonly': Eval('state') != 'draft',
            }, depends=['state'],
        help='This discount will be applied in all lines after their own '
        'discount.')

    @classmethod
    @ModelView.button
    def draft(cls, sales):
        Line = Pool().get('sale.line')

        to_save = []
        for sale in sales:
            if not sale.sale_discount_formula:
                continue

            formula = sale.sale_discount_formula
            for line in sale.lines:
                if (line.discount_formula and
                        line.discount_formula.endswith(formula)):
                    line.discount_formula = (
                        line.discount_formula[:-len(formula)-1])
                    line.on_change_discount_formula()
                    to_save.append(line)

        if to_save:
            Line.save(to_save)

        super().draft(sales)

    @classmethod
    @ModelView.button
    def quote(cls, sales):
        Line = Pool().get('sale.line')

        def trim_decimals(value):
            # Convert to string without scientific notation
            return format(Decimal(value).normalize(), 'f') if value else value

        to_save = []
        for sale in sales:
            if not sale.sale_discount_formula:
                continue
            for line in sale.lines:
                if not line.base_price:
                    continue

                discount = trim_decimals(line.discount_rate * 100
                    if not line.discount_formula and line.discount_rate
                    else line.discount_amount if not line.discount_formula
                    and line.discount_amount else '')
                formula = ""
                if not line.discount_rate and line.discount_amount:
                    formula = "/"
                formula += (discount + ("+" if discount
                        or line.discount_formula else "")
                    + sale.sale_discount_formula)
                if formula:
                    if line.discount_formula:
                        line.discount_formula += formula
                    else:
                        line.discount_formula = formula
                    line.on_change_discount_formula()
                    to_save.append(line)

        if to_save:
            Line.save(to_save)

        super().quote(sales)


class SaleLine(DiscountMixin, ApplyDiscountMixin, metaclass=PoolMeta):
    __name__ = 'sale.line'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.discount_formula.states['readonly'] = Eval('sale_state') != 'draft'

    @fields.depends('discount_formula', 'discount_rate',
        methods=['on_change_discount_rate'])
    def on_change_discount_formula(self):
        super().on_change_discount_formula()
        if not self.discount_formula:
            self.discount_rate = 0.0
            self.on_change_discount_rate()


class SaleDiscountLine(metaclass=PoolMeta):
    __name__ = 'sale.line'

    def get_invoice_line(self):
        lines = super().get_invoice_line()
        for line in lines:
            line.discount_formula = self.discount_formula
        return lines


class SaleDiscountPriceListLine(metaclass=PoolMeta):
    __name__ = 'sale.line'

    @fields.depends('product', 'quantity', 'unit', 'sale',
        '_parent_sale.price_list')
    def update_discount(self):
        pool = Pool()
        PriceList = pool.get('product.price_list')

        super().update_discount()

        price_list = None
        context = Transaction().context

        if self.sale:
            price_list = self.sale.price_list
        if context.get('price_list'):
            price_list = PriceList(context.get('price_list'))
        if price_list and self.unit:
            discount_formula = price_list.compute_discount_formula(self.product,
                self.quantity, self.unit)
            if discount_formula:
                self.discount_formula = discount_formula
                self.on_change_discount_formula()
