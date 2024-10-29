# This file is part discount_formula module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.tests.test_tryton import activate_module
from trytond.pool import Pool


class DiscountFormulaTestCase(ModuleTestCase):
    'Test Discount Formula module'
    module = 'discount_formula'

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
        for model_name in ('sale.line', 'purchase.line',
                'purchase.product_supplier.price'):
            Model = pool.get(model_name)
            line = Model()
            line.base_price = Decimal(6.5)

            #Case absolut value discount
            line.discount_formula = '0.35/'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('6.1500'))
            self.assertEqual(line.discount_amount, Decimal('0.3500'))
            self.assertEqual(line.discount_rate, Decimal('0.0538'))

            line.discount_formula = '-0.35/'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('6.8500'))
            self.assertEqual(line.discount_amount, Decimal('-0.3500'))
            self.assertEqual(line.discount_rate, Decimal('-0.0538'))

            #Case buy x pay y discount
            line.discount_formula = '2*3'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, None)
            self.assertEqual(line.discount_amount, None)
            self.assertEqual(line.discount_rate, None)

            line.discount_formula = '3*2'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('4.3333'))
            self.assertEqual(line.discount_amount, Decimal('2.1667'))
            self.assertEqual(line.discount_rate, Decimal('0.3333'))

            #Case percent discount
            line.discount_formula = '22'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('5.0700'))
            self.assertEqual(line.discount_amount, Decimal('1.4300'))
            self.assertEqual(line.discount_rate, Decimal('0.2200'))

            line.discount_formula = '22.5'
            line.on_change_discount_formula()
            self.assertEqual(line.unit_price, Decimal('5.0375'))
            self.assertEqual(line.discount_amount, Decimal('1.4625'))
            self.assertEqual(line.discount_rate, Decimal('0.2250'))

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

del ModuleTestCase
