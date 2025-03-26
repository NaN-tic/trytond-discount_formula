from trytond.pool import PoolMeta
from .discount import DiscountMixin
from trytond.modules.discount_formula.discount import apply_discount_formula


class ProductSupplierPrice(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'purchase.product_supplier.price'
