# This file is part discount_formula module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import activate_module

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

del ModuleTestCase
