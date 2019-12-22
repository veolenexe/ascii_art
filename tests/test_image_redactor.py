from unittest import TestCase
from image_redactor import ImageRedactor
from PIL import Image
import os


class TestImageRedactor(TestCase):
    def setUp(self):
        tmp_folder_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'temp')
        if not os.path.exists(tmp_folder_dir):
            os.mkdir(tmp_folder_dir)
        self.ir = ImageRedactor()
        self.image = Image.new('RGB', (400, 400), color=100)

    def tearDown(self):
        pass

    def test_change_size(self):
        result_image = self.ir.change_size(self.image, 100, 150)
        result_width, result_height = result_image.size
        assert result_width == 100 and result_height == 150

    def test_change_size_wrong_parameters(self):
        result_image = self.ir.change_size(self.image, -1, 0)
        result_width, result_height = result_image.size
        assert result_width == 400 and result_height == 400

    def test_change_contrast(self):
        pixel_color = self.image.getpixel((0, 0))[0]
        result_image = self.ir.change_contrast(self.image, 100)
        result_pixel_color = result_image.getpixel((0, 0))[0]
        assert pixel_color == 100 and result_pixel_color == 64

    def test_to_greyscale(self):
        pixel_color = self.image.getpixel((0, 0))[1]
        result_image = self.ir.to_greyscale(self.image)
        result_pixel_color = result_image.getpixel((0, 0))[1]
        assert pixel_color == 0 and result_pixel_color == 255

    def test_convert_to_ascii_negative_values(self):
        result_image = self.ir.convert_to_ascii(self.image, -10, 100)
        assert not result_image

    def test_convert_to_ascii_larger_than_original(self):
        result_image = self.ir.convert_to_ascii(self.image, 1000, 1000)
        assert not result_image

    def test_convert_to_ascii(self):
        result_image = self.ir.convert_to_ascii(self.image, 100, 100)
        width, height = result_image.size
        for y in range(height):
            for x in range(width):
                pixel = result_image.getpixel((x, y))
                if pixel[0] != pixel[1] != pixel[2]:
                    assert False
        assert True

    def test_to_ascii_txt(self):
        self.ir.to_ascii_txt(self.image, 10, 10, 'test')
        result = True
        with open('test.txt', 'r', encoding='ascii')as f:
            symbol = f.read(1)
            if symbol != '?':
                result = False
        os.unlink('test.txt')
        assert result

    def test_to_ascii_txt_negative_values(self):
        self.ir.to_ascii_txt(self.image, 10, -10, 'test')
        result = not os.path.exists('test.txt')
        assert result

    def test_to_ascii_txt_wrong_values(self):
        self.ir.to_ascii_txt(self.image, 1000, 100, 'test')
        result = not os.path.exists('test.txt')
        assert result
