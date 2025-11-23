from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Tên thương hiệu")
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    logo = models.ImageField(upload_to="brands/logos/", blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Quốc gia")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Thương hiệu"
        verbose_name_plural = "Thương hiệu"

    def __str__(self):
        return self.name
