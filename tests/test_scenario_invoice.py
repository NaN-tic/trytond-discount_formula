from decimal import Decimal
import unittest
from proteus import Model
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.modules.account.tests.tools import create_chart, get_accounts
from trytond.tests.tools import activate_modules
from trytond.tests.test_tryton import drop_db


class Test(unittest.TestCase):
    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test_account_invoice_discount(self):
        activate_modules(['account_invoice_discount', 'discount_formula'])

        create_company()
        company = get_company()

        create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']

        # Create parties
        Party = Model.get('party.party')
        party = Party(name="Party")
        party.save()

        # Create product
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.save()

        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])

        ProductTemplate = Model.get('product.template')

        template = ProductTemplate()
        template.name = 'product'
        template.default_uom = unit
        template.type = 'goods'
        template.account_category = account_category
        template.save()
        product, = template.products

        # Create a purchase
        Invoice = Model.get('account.invoice')
        invoice = Invoice()
        invoice.party = party
        line = invoice.lines.new()
        line.product = product
        line.quantity = 1
        self.assertEqual(line.base_price, None)
        self.assertEqual(line.unit_price, None)

        # Set a discount formula
        line.base_price = Decimal('10.0000')
        line.discount_formula = '10*9+10+0.35/'
        self.assertEqual(line.unit_price, Decimal('7.7500'))
        self.assertEqual(line.discount, '10*9, 10%, $0.3500')
        line.discount_formula = '10*9+10'
        self.assertEqual(line.unit_price, Decimal('8.1000'))
        self.assertEqual(line.discount, '10*9, 10%')
        line.unit_price = Decimal('10.0000')
        self.assertEqual(line.base_price, line.unit_price)
        self.assertEqual(line.discount_formula, None)
