from trytond.pool import PoolMeta
from .discount import DiscountMixin


class ProductSupplierPrice(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'purchase.product_supplier.price'
