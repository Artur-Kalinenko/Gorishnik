from django.core.exceptions import ValidationError
from PIL import Image
import os

def validate_image(image):
    # Размер файла (в байтах)
    max_size = 2 * 1024 * 1024  # 2 MB
    if image.size > max_size:
        raise ValidationError("Зображення не повинно перевищувати 2MB.")

    # Тип файла
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError("Дозволені формати зображень: JPG, PNG, WEBP.")

    # Размеры изображения
    img = Image.open(image)
    width, height = img.size
    if width < 400 or height < 400:
        raise ValidationError("Зображення повинно бути щонайменше 400x400 пікселів.")
