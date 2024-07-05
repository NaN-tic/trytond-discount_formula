from trytond.pool import PoolMeta
from trytond.model import fields
from .discount import DiscountMixin

class ProductSupplierPrice(DiscountMixin, metaclass=PoolMeta):
    __name__ = 'purchase.product_supplier.price'
