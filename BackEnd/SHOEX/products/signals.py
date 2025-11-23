import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_delete,pre_save
from django.dispatch import receiver
from reviews.models import Review
from .models import ProductImage, ProductAttributeOption

@receiver(pre_save, sender=Review)
def update_product_rating_on_save(sender, instance, **kwargs):
    instance.order_item.variant.product.update_rating()

@receiver(post_delete, sender=Review)
def update_product_rating_on_delete(sender, instance, **kwargs):
    instance.order_item.variant.product.update_rating()
@receiver(post_delete, sender=ProductImage)
def delete_product_image_file(sender, instance, **kwargs):
    """
    Xóa file ảnh khi xóa ProductImage
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(post_delete, sender=ProductAttributeOption)
def delete_product_attribute_option_image_file(sender, instance, **kwargs):
    """
    Xóa file ảnh khi xóa ProductAttributeOption
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(pre_save, sender=ProductImage)
def delete_old_product_image_file_on_update(sender, instance, **kwargs):
    """
    Xóa file ảnh cũ khi cập nhật ProductImage
    """
    if not instance.pk:
        return False

    try:
        old_file = ProductImage.objects.get(pk=instance.pk).image
    except ProductImage.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if old_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)


@receiver(pre_save, sender=ProductAttributeOption)
def delete_old_product_attribute_option_image_file_on_update(sender, instance, **kwargs):
    """
    Xóa file ảnh cũ khi cập nhật ProductAttributeOption
    """
    if not instance.pk:
        return False

    try:
        old_file = ProductAttributeOption.objects.get(pk=instance.pk).image
    except ProductAttributeOption.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if old_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)