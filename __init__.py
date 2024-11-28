# This file is part discount_formula module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import invoice
from . import purchase
from . import product_supplier
from . import sale
from . import price_list

def register():
    Pool.register(
        invoice.InvoiceLine,
        module='discount_formula', type_='model',
        depends=['account_invoice_discount'])
    Pool.register(
        purchase.PurchaseLine,
        module='discount_formula', type_='model',
        depends=['purchase_discount'])
    Pool.register(
        purchase.PurchaseDiscountLine,
        module='discount_formula', type_='model',
        depends=['purchase_discount', 'account_invoice_discount'])
    Pool.register(
        product_supplier.ProductSupplierPrice,
        purchase.PurchaseLineSupplierDepends,
        module='discount_formula', type_='model',
        depends=['purchase_supplier_discount'])
    Pool.register(
        sale.SaleLine,
        sale.Sale,
        module='discount_formula', type_='model',
        depends=['sale_discount'])
    Pool.register(
        sale.SaleDiscountLine,
        module='discount_formula', type_='model',
        depends=['sale_discount', 'account_invoice_discount'])
    Pool.register(
        price_list.PriceList,
        price_list.PriceListLine,
        sale.SaleDiscountPriceListLine,
        module='discount_formula', type_='model',
        depends=['sale_discount_price_list'])
