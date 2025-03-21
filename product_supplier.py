from trytond.pool import PoolMeta
from .discount import DiscountMixin, ApplyDiscountMixin


class ProductSupplierPrice(DiscountMixin, ApplyDiscountMixin, metaclass=PoolMeta):
    __name__ = 'purchase.product_supplier.price'
