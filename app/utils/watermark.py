import io

from PIL import Image, ImageDraw, ImageFont

from config import WATERMARK


def add_watermark_to_photo(file, file_name=None):
    # Convert bytes to an image
    original_image = Image.open(io.BytesIO(file))
    draw = ImageDraw.Draw(original_image)

    watermark_text = WATERMARK

    image_width, image_height = original_image.size
    font_size = int(image_width * 0.05)
    font = ImageFont.truetype('arial.ttf', font_size)
    text_color = (255, 255, 255)
    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    margin = 10
    position = (image_width - text_width - margin, image_height - text_height - margin)
    draw.text(position, watermark_text, font=font, fill=text_color)

    output = io.BytesIO()
    original_image.save(
        output, format=original_image.format if original_image.format else 'PNG'
    )
    output.seek(0)

    return output.getvalue()
