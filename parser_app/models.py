from django.db import models


class Product(models.Model):
    url = models.URLField()
    full_name = models.CharField(max_length=255)
    color = models.CharField(max_length=120, blank=True, null=True)
    memory = models.CharField(max_length=110, blank=True, null=True)
    manufacturer = models.CharField(max_length=1000, blank=True, null=True)

    price_regular = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    price_discount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    product_code = models.CharField(max_length=50, blank=True, null=True)
    reviews_count = models.PositiveIntegerField(default=0)

    screen_diagonal = models.CharField(max_length=50, blank=True, null=True)
    screen_resolution = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class ProductPhoto(models.Model):
    product = models.ForeignKey(Product, related_name="photos", on_delete=models.CASCADE)
    url = models.URLField()

    def __str__(self):
        return f"Photo of {self.product_id}"


class ProductCharacteristic(models.Model):
    product = models.ForeignKey(Product, related_name="characteristics", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_index=True)
    value = models.TextField()

    def __str__(self):
        return f"{self.name}: {self.value[:30]}..."
