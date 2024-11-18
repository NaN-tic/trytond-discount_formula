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

    def test(self):
        activate_modules(['sale_discount', 'discount_formula',
            'account_invoice_discount'])

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
        template.salable = True
        template.save()
        product, = template.products

        # Create a sale
        Sale = Model.get('sale.sale')
        sale = Sale()
        sale.party = party
        sale.invoice_method = 'order'

        line = sale.lines.new()
        line.product = product
        line.quantity = 1

        line.base_price = Decimal('10.0000')
        line.discount_formula = '10*9+10+0.35/'
        self.assertEqual(line.unit_price, Decimal('7.7500'))
        line.unit_price = Decimal('10.0000')
        self.assertEqual(line.discount_formula, None)
        line.discount_formula = '10*9+10'
        self.assertEqual(line.unit_price, Decimal('8.1000'))
        self.assertEqual(line.discount_rate, Decimal('0.1900'))

        sale.click('quote')
        sale.click('confirm')
        self.assertEqual(sale.state, 'processing')

        line, = sale.lines
        self.assertEqual(line.discount, '10*9, -10%')

        self.assertEqual(len(sale.invoices), 1)
        invoice, = sale.invoices
        invoice_line, = invoice.lines
        self.assertEqual(invoice_line.discount_formula, line.discount_formula)
        self.assertEqual(invoice_line.base_price, line.base_price)
        self.assertEqual(invoice_line.discount_rate, line.discount_rate)
        self.assertEqual(invoice_line.discount, '10*9, -10%')

        sale = Sale()
        sale.party = party
        sale.invoice_method = 'order'
        sale.sale_discount_formula = '10'
        line = sale.lines.new()
        line.product = product
        line.quantity = 1
        line.base_price = Decimal('10.0000')
        self.assertEqual(line.discount_formula, None)
        line.unit_price = Decimal('10.0000')
        sale.save()

        line, = sale.lines
        self.assertEqual(line.discount_formula, None)

        sale.click('quote')
        self.assertEqual(sale.sale_discount_formula, '10')

        sale.reload()
        line, = sale.lines
        self.assertEqual(line.discount_formula, '10')
