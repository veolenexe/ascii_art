from unittest import TestCase
from video_redactor import VideoRedactor
import os


class TestVideoRedactor(TestCase):
    def setUp(self):
        self.vr = VideoRedactor()
        self.folder = os.path.dirname(os.path.abspath(__file__))
        if not self.folder.endswith('tests'):
            self.folder = os.path.join(self.folder, 'tests')

    def tearDown(self):
        folder = os.path.join(os.getcwd(), 'temp')
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            os.unlink(file_path)

    def test_set_video(self):
        file_path = os.path.join(self.folder, 'test.avi')
        result = self.vr.set_video(file_path)
        length = self.vr.get_length()
        assert result and length == 11

    def test_set_video_wrong_file(self):
        result = not self.vr.set_video('something.wrong')
        length = self.vr.get_length()
        assert result and length == 0

    def test_set_video_nonexistent_file(self):
        result = not self.vr.set_video('nonexist_file.mp4')
        length = self.vr.get_length()
        assert result and length == 0

    def test_convert_to_ascii(self):
        file_path = os.path.join(self.folder, 'test.avi')
        self.vr.set_video(file_path)
        result = self.vr.convert_to_ascii(10, 10, 40)
        assert result

    def test_convert_to_ascii_without_video(self):
        self.vr.set_video(f'wrong file')
        result = not self.vr.convert_to_ascii(10, 10, 40)
        assert result

    def test_make_video_before_to_ascii(self):
        file_path = os.path.join(self.folder, 'test.avi')
        self.vr.set_video(file_path)
        result = not self.vr.make_video()
        assert result
