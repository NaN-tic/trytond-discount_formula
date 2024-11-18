# This file is part discount_formula module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.tests.test_tryton import activate_module
from trytond.modules.currency.tests import create_currency
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
    def test_discount_formula(self):
        'Test discount formula'

        pool = Pool()
        Sale = pool.get('sale.sale')

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

            line.discount_formula = '30+5'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('4.3225'))
            self.assertEqual(line.discount_amount, Decimal('2.1775'))
            self.assertEqual(line.discount_rate, Decimal('0.3350'))
            self.assertEqual(line.on_change_with_discount(), '30%, 5%')

            # #Case absolut value discount
            line.discount_formula = '0.35/'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('6.1500'))
            self.assertEqual(line.discount_amount, Decimal('0.3500'))
            self.assertEqual(line.discount_rate, Decimal('0.0538'))
            # self.assertEqual(line.on_change_with_discount(), '30%, 5%')

            line.discount_formula = '-0.35/'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('6.8500'))
            self.assertEqual(line.discount_amount, Decimal('-0.3500'))
            self.assertEqual(line.discount_rate, Decimal('-0.0538'))
            # self.assertEqual(line.on_change_with_discount(), '30%, 5%')

            #Case buy x pay y discount
            line.discount_formula = '3*2'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('4.3333'))
            self.assertEqual(line.discount_amount, Decimal('2.1667'))
            self.assertEqual(line.discount_rate, Decimal('0.3333'))
            # self.assertEqual(line.on_change_with_discount(), '30%, 5%')

            # The amounts for the products in "buy x pay y" discount "2*3" are not valid
            line.discount_formula = '2*3'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, None)
            self.assertEqual(line.discount_amount, None)
            self.assertEqual(line.discount_rate, None)

            #Case percent discount
            line.discount_formula = '22'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('5.0700'))
            self.assertEqual(line.discount_amount, Decimal('1.4300'))
            self.assertEqual(line.discount_rate, Decimal('0.2200'))
            # self.assertEqual(line.on_change_with_discount(), '30%, 5%')

            line.discount_formula = '22.5'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('5.0375'))
            self.assertEqual(line.discount_amount, Decimal('1.4625'))
            self.assertEqual(line.discount_rate, Decimal('0.2250'))
            # self.assertEqual(line.on_change_with_discount(), '30%, 5%')

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
            # self.assertEqual(line.on_change_with_discount(), '30%, 5%')

del ModuleTestCase
