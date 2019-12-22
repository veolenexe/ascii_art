from PIL import Image, ImageDraw, ImageFont, ImageOps
import os


class ImageRedactor:
    ASCII_CHARS = ['@', '#', '%', 'S', '?', '/', '!', '+', '*', ':', ',',
                   '.', ' ']

    @staticmethod
    def change_contrast(img: Image, level: int):
        """
        меняет контрастность изображения
        """
        factor = (259 * (level + 255)) / (255 * (259 - level))

        def contrast(c):
            return 128 + factor * (c - 128)

        return img.point(contrast)

    @staticmethod
    def to_greyscale(image: Image):
        """
        преобразует изображение в черно-беылй
        """
        return image.convert('LA')

    @staticmethod
    def change_size(image: Image, width: int, height: int):
        if width > 0 and height > 0:
            return image.resize((width, height))
        else:
            return image

    @staticmethod
    def convert_to_ascii(image: Image, ascii_width: int, ascii_height: int):
        """
        возвращает преобразованое изображение в ascii-art
        """
        width, height = image.size
        larger_than_original = ascii_width > width or ascii_height > height
        less_than_zero = ascii_width < 0 or ascii_height < 0
        if larger_than_original or less_than_zero:
            return ''
        width_offset = width // ascii_width
        height_offset = height // ascii_height
        offset = max(width_offset, height_offset, 6)
        font = ImageRedactor.__find_font(offset)
        image = image.resize((ascii_width, ascii_height))
        result_img = Image.new('RGB',
                               (ascii_width * offset, ascii_height * offset))
        d = ImageDraw.Draw(result_img)
        for y in range(ascii_height):
            for x in range(ascii_width):
                pixel_color = image.getpixel((x, y))[0]
                character = ImageRedactor.ASCII_CHARS[pixel_color // 20]
                d.text((x * offset, y * offset), character,
                       fill=(255, 255, 255),
                       font=font)

        return ImageOps.invert(result_img)

    @staticmethod
    def __find_font(offset=6):
        try:
            path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(path, 'arial.ttf')
            font_size = (offset * 2) // 3
            loaded_font = ImageFont.load(path)
            font = ImageFont.truetype(font=loaded_font, size=font_size)
        except OSError:
            font = ImageFont.load_default()
        return font

    @staticmethod
    def to_ascii_txt(image: Image, ascii_width: int, ascii_height: int,
                     image_name='result'):
        """
        преображает изображение в ascii-art.txt
        """
        width, height = image.size
        larger_than_original = ascii_width > width or ascii_height > height
        less_than_zero = ascii_width < 0 or ascii_height < 0
        if larger_than_original or less_than_zero:
            return
        image = image.resize((ascii_width, ascii_height))
        image_name += '.txt'
        f = open(image_name, 'w')
        f.close()
        with open(image_name, 'a+', encoding='ascii') as result:
            result.truncate()
            for y in range(ascii_height):
                for x in range(ascii_width):
                    pixel_color = image.getpixel((x, y))[0]
                    character = ImageRedactor.ASCII_CHARS[pixel_color // 23]
                    result.write(character)
                result.write('\n')
