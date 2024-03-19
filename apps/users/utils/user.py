import base64
import os
import random
import pathlib
import uuid
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont


def preprocess_avatar(path):
    size = settings.AVATAR_SIZE
    try:
        with Image.open(path) as img:
            img = img.resize((size, size))

            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size - 1, size - 1), fill=255, outline=0)

            img_with_alpha = Image.new("RGBA", img.size, (255, 255, 255, 0))
            img_with_alpha.paste(img, (0, 0), mask)

            img_with_alpha.save(path, format="PNG")
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None


def avatar_to_base64(avatar_path):
    with open(avatar_path, "rb") as f:
        base64_encoded = base64.b64encode(f.read()).decode("utf-8")
        mime_type = "image/png"
        data_uri = f"data:{mime_type};base64,{base64_encoded}"
        return data_uri


def generate_avatar(letter):
    folder_path = pathlib.Path(os.path.join(settings.MEDIA_ROOT, 'tmp/'))
    os.makedirs(folder_path, exist_ok=True)
    size = settings.AVATAR_SIZE

    # Generate a random color
    color = (
        random.randint(0, 200),
        random.randint(0, 200),
        random.randint(0, 200)
    )

    # Create a blank image with the specified size and background color
    image = Image.new('RGB', (size, size), color)

    # Get a font and calculate text size
    font_size = int(size * 0.5)
    font = ImageFont.truetype(settings.AVATAR_FONT, font_size)
    (width, height), (offset_x, offset_y) = font.font.getsize(letter)

    # Calculate text position to center it in the image
    text_position = ((size - width) // 2, (size - height) // 2 - offset_y)

    # Draw text on the image
    draw = ImageDraw.Draw(image)
    draw.text(text_position, letter, font=font, fill=(255, 255, 255))

    # Save or return the image
    save_path = folder_path / (uuid.uuid4().hex + '.png')
    image.save(save_path)
    return str(save_path)
