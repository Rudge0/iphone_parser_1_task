from django.contrib import admin
from .models import Product, ProductPhoto, ProductCharacteristic


admin.site.register(Product)
admin.site.register(ProductPhoto)
admin.site.register(ProductCharacteristic)
