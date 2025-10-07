import os
import uuid
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from io import BytesIO


def generate_unique_filename(instance, filename):
    """
    Tạo tên file unique để tránh trùng lặp
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return filename


def resize_image(image, max_width=800, max_height=600, quality=85):
    """
    Resize ảnh về kích thước phù hợp và nén
    
    Args:
        image: Django ImageField file
        max_width: Chiều rộng tối đa
        max_height: Chiều cao tối đa  
        quality: Chất lượng nén (1-100)
    
    Returns:
        ContentFile: File ảnh đã được resize
    """
    # Mở ảnh bằng PIL
    img = Image.open(image)
    
    # Convert sang RGB nếu cần (cho JPEG)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # Tính toán kích thước mới giữ nguyên tỉ lệ
    original_width, original_height = img.size
    
    # Tính tỉ lệ scale
    width_ratio = max_width / original_width
    height_ratio = max_height / original_height
    scale_ratio = min(width_ratio, height_ratio, 1.0)  # Không scale up
    
    # Kích thước mới
    new_width = int(original_width * scale_ratio)
    new_height = int(original_height * scale_ratio)
    
    # Resize ảnh
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Lưu vào BytesIO
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    
    # Tạo ContentFile
    content_file = ContentFile(output.read())
    
    return content_file


def create_thumbnail(image, size=(150, 150)):
    """
    Tạo thumbnail từ ảnh gốc
    
    Args:
        image: Django ImageField file
        size: Tuple (width, height) cho thumbnail
    
    Returns:
        ContentFile: File thumbnail
    """
    img = Image.open(image)
    
    # Convert sang RGB nếu cần
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # Tạo thumbnail (crop to fit)
    img.thumbnail(size, Image.Resampling.LANCZOS)
    
    # Tạo background trắng để đảm bảo kích thước chính xác
    background = Image.new('RGB', size, (255, 255, 255))
    
    # Paste ảnh vào giữa background
    offset = ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2)
    background.paste(img, offset)
    
    # Lưu vào BytesIO
    output = BytesIO()
    background.save(output, format='JPEG', quality=90, optimize=True)
    output.seek(0)
    
    return ContentFile(output.read())


def validate_image(image):
    """
    Validate file upload là ảnh hợp lệ
    
    Args:
        image: Django UploadedFile
    
    Returns:
        dict: {'valid': bool, 'error': str}
    """
    # Kiểm tra kích thước file (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        return {
            'valid': False,
            'error': f'File quá lớn. Kích thước tối đa: {max_size // (1024*1024)}MB'
        }
    
    # Kiểm tra định dạng file
    allowed_formats = ['JPEG', 'JPG', 'PNG', 'WEBP']
    try:
        img = Image.open(image)
        if img.format not in allowed_formats:
            return {
                'valid': False,
                'error': f'Định dạng không hỗ trợ. Chỉ chấp nhận: {", ".join(allowed_formats)}'
            }
    except Exception as e:
        return {
            'valid': False,
            'error': 'File không phải là ảnh hợp lệ'
        }
    
    # Kiểm tra kích thước ảnh
    max_dimensions = (2000, 2000)  # 2000x2000px
    if img.size[0] > max_dimensions[0] or img.size[1] > max_dimensions[1]:
        return {
            'valid': False,
            'error': f'Kích thước ảnh quá lớn. Tối đa: {max_dimensions[0]}x{max_dimensions[1]}px'
        }
    
    return {'valid': True, 'error': None}


# Upload path functions
def product_image_upload_path(instance, filename):
    """Upload path cho ProductImage"""
    filename = generate_unique_filename(instance, filename)
    return f'products/gallery/{instance.product.product_id}/{filename}'


def product_attribute_option_upload_path(instance, filename):
    """Upload path cho ProductAttributeOption"""
    filename = generate_unique_filename(instance, filename)
    return f'products/attributes/{instance.product.product_id}/{instance.attribute.name}/{filename}'