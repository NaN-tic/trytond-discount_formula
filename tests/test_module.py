# This file is part discount_formula module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.tests.test_tryton import activate_module
from trytond.modules.currency.tests import create_currency
from trytond.modules.company.tests import create_company, set_company
from trytond.transaction import Transaction
from trytond.pool import Pool


class DiscountFormulaTestCase(ModuleTestCase):
    'Test Discount Formula module'
    module = 'discount_formula'
    extras = ['sale_discount_price_list']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        activate_module('account_invoice_discount')
        activate_module('purchase_discount')
        activate_module('purchase_supplier_discount')
        activate_module('sale_discount')

    @with_transaction()
    def test_product_price_list(self):
        'Test price_list'
        pool = Pool()
        Template = pool.get('product.template')
        Product = pool.get('product.product')
        Uom = pool.get('product.uom')
        PriceList = pool.get('product.price_list')
        Category = pool.get('product.category')

        company = create_company()
        with set_company(company):
            kilogram, = Uom.search([
                    ('name', '=', 'Kilogram'),
                    ])

            account_category = Category(
                name='Account Category',
                accounting=True,
                )
            account_category.save()

            template = Template(
                name='product',
                list_price=Decimal(10),
                default_uom=kilogram,
                account_category=account_category,
                salable=True,
                sale_uom=kilogram,
                )
            template.save()
            variant1 = Product(template=template)
            variant1.save()
            variant2 = Product(template=template)
            variant2.save()
            variant3 = Product(template=template)
            variant3.save()
            variant4 = Product(template=template)
            variant4.save()

            price_list, = PriceList.create([{
                        'name': 'Default Price List',
                        'price': 'list_price',
                        'lines': [('create', [{
                                        'quantity': None,
                                        'product': variant1.id,
                                        'formula': 'unit_price',
                                        }, {
                                        'quantity': None,
                                        'product': variant2.id,
                                        'formula': 'unit_price',
                                        'base_price_formula': 'unit_price + 1',
                                        }, {
                                        'quantity': None,
                                        'product': variant3.id,
                                        'formula': '0',
                                        'base_price_formula': 'unit_price',
                                        'discount_formula': '50',
                                        }, {
                                        'quantity': None,
                                        'product': variant4.id,
                                        'formula': '0',
                                        'base_price_formula': 'unit_price',
                                        'discount_formula': '30+5',
                                        }, {
                                        'formula': 'unit_price',
                                        }])],
                        }])

            tests = [
                (variant1, Decimal('10.0000')),
                (variant2, Decimal('10.0000')),
                (variant3, Decimal('5.0000')),
                (variant4, Decimal('6.6500')),
                ]
            with Transaction().set_context(price_list=price_list.id):
                for product, unit_price in tests:
                    product = Product(product.id)
                    self.assertEqual(product.sale_price_uom, unit_price)

    @with_transaction()
    def test_discount_formula(self):
        'Test discount formula'

        pool = Pool()

        currency = create_currency('USD')

        for model_name in ('sale.line', 'purchase.line', 'account.invoice.line',
                'purchase.product_supplier.price'):
            Model = pool.get(model_name)
            line = Model()
            line.base_price = Decimal(6.5)

            if model_name.endswith('line'):
                # set currency in parent model
                if model_name == 'sale.line':
                    ModelParent = pool.get('sale.sale')
                    parent = ModelParent()
                    parent.currency = currency
                    setattr(line, 'sale', parent)
                elif model_name == 'purchase.line':
                    ModelParent = pool.get('purchase.purchase')
                    parent = ModelParent()
                    parent.currency = currency
                    setattr(line, 'purchase', parent)
                else:
                    ModelParent = pool.get('account.invoice')
                    parent = ModelParent()
                    parent.currency = currency
                    setattr(line, 'invoice', parent)

            line.discount_formula = '30'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('4.5500'))
            self.assertEqual(line.discount_amount, Decimal('1.9500'))
            self.assertEqual(line.discount_rate, Decimal('0.3000'))
            self.assertEqual(line.on_change_with_discount(), '30%')
            self.assertEqual(line.discount, '30%')

            line.discount_formula = '30+5'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('4.3225'))
            self.assertEqual(line.discount_amount, Decimal('2.1775'))
            self.assertEqual(line.discount_rate, Decimal('0.3350'))
            self.assertEqual(line.on_change_with_discount(), '30%, 5%')
            self.assertEqual(line.discount, '30%, 5%')

            # #Case absolut value discount
            line.discount_formula = '0.35/'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('6.1500'))
            self.assertEqual(line.discount_amount, Decimal('0.3500'))
            self.assertEqual(line.discount_rate, Decimal('0.0538'))
            if hasattr(line, 'currency') and line.currency:
                self.assertEqual(line.on_change_with_discount(), 'USD0.3500')
            else:
                self.assertEqual(line.on_change_with_discount(), '0.35')

            line.discount_formula = '-0.35/'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('6.8500'))
            self.assertEqual(line.discount_amount, Decimal('-0.3500'))
            self.assertEqual(line.discount_rate, Decimal('-0.0538'))
            if hasattr(line, 'currency') and line.currency:
                self.assertEqual(line.on_change_with_discount(), '-USD0.3500')
            else:
                self.assertEqual(line.on_change_with_discount(), '-0.35')

            #Case buy x pay y discount
            line.discount_formula = '3*2'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('4.3333'))
            self.assertEqual(line.discount_amount, Decimal('2.1667'))
            self.assertEqual(line.discount_rate, Decimal('0.3333'))
            self.assertEqual(line.on_change_with_discount(), '3*2')

            # The amounts for the products in "buy x pay y" discount "2*3" are not valid
            line.discount_formula = '2*3'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, None)
            self.assertEqual(line.discount_amount, None)
            self.assertEqual(line.discount_rate, None)
            self.assertEqual(line.on_change_with_discount(), '')

            #Case percent discount
            line.discount_formula = '22'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('5.0700'))
            self.assertEqual(line.discount_amount, Decimal('1.4300'))
            self.assertEqual(line.discount_rate, Decimal('0.2200'))
            self.assertEqual(line.on_change_with_discount(), "22%")

            line.discount_formula = '22.5'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('5.0375'))
            self.assertEqual(line.discount_amount, Decimal('1.4625'))
            self.assertEqual(line.discount_rate, Decimal('0.2250'))
            self.assertEqual(line.on_change_with_discount(), '22.5%')

            # The format for the discount formula provided "22,5" is incorrect. It can only contain numeric values, and the symbols "+" "*" "/" "."
            line.discount_formula = '22,5'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, None)
            self.assertEqual(line.discount_amount, None)
            self.assertEqual(line.discount_rate, None)

            line.discount_formula = '-22.5'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('7.9625'))
            self.assertEqual(line.discount_amount, Decimal('-1.4625'))
            self.assertEqual(line.discount_rate, Decimal('-0.2250'))
            self.assertEqual(line.on_change_with_discount(), '-22.5%')

            #Check complex formulas
            line.discount_formula = '30+-4/'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('8.5500'))
            self.assertEqual(line.discount_amount, Decimal('-2.0500'))
            self.assertEqual(line.discount_rate, Decimal('-0.3154'))
            if hasattr(line, 'currency') and line.currency:
                self.assertEqual(line.on_change_with_discount(), '30%, -USD4.0000')
            else:
                self.assertEqual(line.on_change_with_discount(), '30%, -4')

            line.discount_formula = '30+3*2+-4/'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('7.0333'))
            self.assertEqual(line.discount_amount, Decimal('-0.5333'))
            self.assertEqual(line.discount_rate, Decimal('-0.0820'))
            if hasattr(line, 'currency') and line.currency:
                self.assertEqual(line.on_change_with_discount(), '30%, 3*2, -USD4.0000')
            else:
                self.assertEqual(line.on_change_with_discount(), '30%, 3*2, -4')

            line.discount_formula = '30+3*2+1/'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('2.0333'))
            self.assertEqual(line.discount_amount, Decimal('4.4667'))
            self.assertEqual(line.discount_rate, Decimal('0.6872'))
            if hasattr(line, 'currency') and line.currency:
                self.assertEqual(line.on_change_with_discount(), '30%, 3*2, USD1.0000')
            else:
                self.assertEqual(line.on_change_with_discount(), '30%, 3*2, 1')

del ModuleTestCase
