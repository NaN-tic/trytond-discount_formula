# This file is part discount_formula module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import invoice
from . import purchase
from . import product_supplier
from . import sale

def register():
    Pool.register(
        invoice.InvoiceLine,
        module='discount_formula', type_='model', depends=['account_invoice_discount'])
    Pool.register(
        purchase.PurchaseLine,
        module='discount_formula', type_='model', depends=['purchase_discount'])
    Pool.register(
        product_supplier.ProductSupplierPrice,
        module='discount_formula', type_='model', depends=['purchase_supplier_discount'])
    Pool.register(
        sale.SaleLine,
        module='discount_formula', type_='model', depends=['sale_discount'])
