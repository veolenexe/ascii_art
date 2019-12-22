from PIL import Image
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from threading import Thread
from image_redactor import ImageRedactor
from video_redactor import VideoRedactor

TMP_IMG = r'temp\temp.png'
TMP_CONTRAST = r'temp\temp_contr.png'
TMP_GREYSCALE = r'temp\temp_greyscale.png'
TMP_ASCII = r'temp\temp_ascii.png'
IMAGE_FORMATS = ('.jpg', '.png', '.jpeg')
VIDEO_FORMATS = ('.mp4', '.avi', '.webm')

class UserInterface(QWidget):  # pragma: no cover

    def __init__(self):
        super().__init__()
        self.image = None
        self.gs_image = None
        self.ascii_image = None
        self.convert_thread = Thread()
        self.preview_thread = Thread()
        self.file_name = ''
        self.image_redactor = ImageRedactor()
        self.video_redactor = VideoRedactor()
        self.initUI()
        self.is_video = False

    def initUI(self):

        # contrast slider
        self.contrast_slider = QSlider(Qt.Horizontal, self)
        self.contrast_slider.setFocusPolicy(Qt.NoFocus)
        self.contrast_slider.setGeometry(30, 40, 100, 30)
        self.contrast_slider.setMinimum(0)
        self.contrast_slider.setMaximum(200)

        # frame slider
        self.frame_slider = QSlider(Qt.Horizontal, self)
        self.frame_slider.setFocusPolicy(Qt.NoFocus)
        self.frame_slider.setGeometry(30, 40, 100, 30)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(200)

        # width
        width = QLabel('width:')
        self.width_edit = QLineEdit()
        self.width_edit.setInputMask('999')
        # height
        height = QLabel('height:')
        self.height_edit = QLineEdit()
        self.height_edit.setInputMask('999')

        # buttons
        convert = QPushButton('convert')
        choose = QPushButton('choose')
        preview = QPushButton('preview')

        # image labels
        self.main_img_label = QLabel()
        self.gs_img_label = QLabel()
        self.ascii_img_label = QLabel()

        q_img = QImage(TMP_IMG).scaled(500, 400)
        self.main_img_label.setPixmap(QPixmap.fromImage(q_img))

        # grid
        self.grid = QGridLayout()
        self.grid.addWidget(self.main_img_label, 0, 0)
        self.grid.addWidget(self.gs_img_label, 0, 1)
        self.grid.addWidget(self.ascii_img_label, 0, 2, 1, 5)

        self.grid.addWidget(self.contrast_slider, 1, 0)
        self.grid.addWidget(self.frame_slider, 1, 1)
        self.grid.addWidget(width, 1, 2)
        self.grid.addWidget(self.width_edit, 1, 3)
        self.grid.addWidget(height, 1, 4)
        self.grid.addWidget(self.height_edit, 1, 5)

        self.grid.addWidget(choose, 2, 0)
        self.grid.addWidget(preview, 2, 1)
        self.grid.addWidget(convert, 2, 2, 1, 5)
        self.setLayout(self.grid)

        # events
        choose.clicked.connect(self.choose_file)
        preview.clicked.connect(self.create_preview_thread)
        self.contrast_slider.sliderReleased.connect(self.change_slide_value)
        self.frame_slider.sliderReleased.connect(self.change_frame)
        convert.clicked.connect(self.create_thread)

        # final
        self.setGeometry(50, 50, 320, 200)
        self.setWindowTitle("PyQT show image")
        self.show()

    def create_thread(self):
        """
        создает поток для метода конвертирования
        """
        if self.convert_thread.is_alive():
            self.convert_thread.join()
        self.convert_thread = Thread(target=self.convert, daemon=True)
        self.convert_thread.start()

    def convert(self):
        """
        если файл видео - делает ascii-видео.avi
        если изображение - ascii-art.txt
        """
        if self.__is_input_correct():
            width = int(self.width_edit.text())
            height = int(self.height_edit.text())
            if self.is_video:
                contrast = self.contrast_slider.value()
                self.video_redactor.convert_to_ascii(width, height, contrast)
                self.video_redactor.make_video(self.file_name)
            else:
                with Image.open(TMP_GREYSCALE) as img:
                    self.image_redactor.to_ascii_txt(img, width, height,
                                                     self.file_name)

    def to_greyscale(self):
        """
        выводит превью изображения, преобразованного в черно-белый цвет
        """
        img = TMP_CONTRAST if os.path.exists(TMP_CONTRAST) else TMP_IMG
        with Image.open(img) as img:
            self.image = self.image_redactor.to_greyscale(img)
            self.image.save(TMP_GREYSCALE)
            self.gs_image = QImage(TMP_GREYSCALE).scaled(500, 400)
            self.gs_img_label.setPixmap(QPixmap.fromImage(self.gs_image))

    def choose_file(self):

        fname = QFileDialog.getOpenFileName(self, 'Open file')[0]
        if fname and fname.endswith(IMAGE_FORMATS):
            self.__clear_tmp_folder()
            self.file_name = fname.rsplit(".", 1)[0]
            self.__change_tmp_file(fname)
            self.__change_tmp_file(fname, TMP_CONTRAST)
            self.is_video = False
        if fname and fname.endswith(VIDEO_FORMATS):
            self.__clear_tmp_folder()
            self.video_redactor.set_video(fname)
            self.file_name = fname.rsplit(".", 1)[0]
            self.video_redactor.get_frame(0)
            self.__change_tmp_file()
            self.__change_tmp_file(TMP_IMG, TMP_CONTRAST)
            length = self.video_redactor.get_length()
            self.frame_slider.setMaximum(length)
            self.is_video = True

    def __is_input_correct(self):
        """
        проверяет, корректно ли заполнены поля width, height
        должны быть заполнены, больше 0 и файл загружен
        """
        try:
            width = int(self.width_edit.text())
            height = int(self.height_edit.text())
            input_correct = width and height and self.gs_image
            return input_correct and width * height > 0
        except ValueError:
            return False

    def create_preview_thread(self):

        if self.__is_input_correct():
            if self.convert_thread.is_alive():
                self.convert_thread.join()
            self.preview_thread = Thread(target=self.preview_ascii_format,
                                         daemon=True)
            self.preview_thread.start()

    def preview_ascii_format(self):
        """
        выводит превью изображения, преобразованного в ascii-art
        """
        if self.__is_input_correct():
            width = int(self.width_edit.text())
            heigth = int(self.height_edit.text())
            with Image.open(TMP_GREYSCALE) as img:
                img = self.image_redactor.change_size(img, 400, 400)
                ascii_image = self.image_redactor.convert_to_ascii(img, width,
                                                                   heigth)
                if ascii_image:
                    ascii_image.save(TMP_ASCII)
                    ascii_image = QImage(TMP_ASCII).scaled(500, 400)
                    self.ascii_img_label.setPixmap(
                        QPixmap.fromImage(ascii_image))

    def __change_tmp_file(self, image=TMP_IMG, save_img=TMP_IMG):
        """
        создает, меняет временные файлы, необходимые для вывода в превью
        :param image: какой файл открываем
        :param save_img: в какой файл сохраняем
        """
        with Image.open(image) as img:
            img.save(save_img)
            self.image = QImage(save_img).scaled(500, 400)
            self.main_img_label.setPixmap(QPixmap.fromImage(self.image))
            self.to_greyscale()

    def change_slide_value(self):
        if self.image:
            value = self.contrast_slider.value()
            with Image.open(TMP_IMG) as img:
                self.image = self.image_redactor.change_contrast(img, value)
                self.image.save(TMP_CONTRAST)
            self.__change_tmp_file(TMP_CONTRAST, TMP_CONTRAST)

    def change_frame(self):
        if self.is_video:
            value = self.frame_slider.value()
            self.video_redactor.get_frame(value)
            self.__change_tmp_file()
            self.__change_tmp_file(TMP_IMG, TMP_CONTRAST)
            self.change_slide_value()

    @staticmethod
    def __clear_tmp_folder():
        """
        отчищает папку с времеными файлами
        """
        folder = os.getcwd() + r'\temp'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            os.unlink(file_path)

    def closeEvent(self, event):
        self.__clear_tmp_folder()
        event.accept()
