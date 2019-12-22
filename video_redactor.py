from image_redactor import ImageRedactor
import cv2
from PIL import Image
import os


class VideoRedactor:
    TMP_IMG = r'temp\temp.png'
    VIDEO_FORMATS = ('.mp4', '.avi', '.webm')

    def __init__(self):
        self.ir = ImageRedactor()
        self.__cap = None
        self.__fps = 0
        self.__length = 0
        self.__converted_to_ascii = False

    def set_video(self, video: str):
        """
        загружает видео
        :param video: путь к файлу
        :return: boolean удачно ли загружен
        """
        if os.path.exists(video) and video.endswith(
                VideoRedactor.VIDEO_FORMATS):
            self.__cap = cv2.VideoCapture(video)
            self.__fps = self.__cap.get(cv2.CAP_PROP_FPS)
            self.__length = int(self.__cap.get(cv2.CAP_PROP_FRAME_COUNT))
            return True
        else:
            return False

    def get_frame(self, time: int, save_image=TMP_IMG):
        """
        :param time: время видео
        :param save_image:
        :return: кадр, взятый с time времени
        """
        self.__cap.set(cv2.CAP_PROP_POS_FRAMES, time)
        ret, frame = self.__cap.read()
        cv2.imwrite(save_image, frame)

    def get_length(self):
        return self.__length

    def convert_to_ascii(self, width: int, height: int, contrast: int):
        """
        преобразует кадры видео в ascii-art
        """
        if self.__cap:
            self.__cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.__cap.read()
            i = 0
            while ret:
                if i % 5 == 0:
                    cv2.imwrite(f'temp\\tmpframe{i // 5}.png', frame)
                i += 1
                ret, frame = self.__cap.read()
            i = 0
            filename = f'temp\\tmpframe{i}.png'
            while os.path.exists(filename):
                with Image.open(filename) as img:
                    img = self.ir.change_contrast(img, contrast)
                    img = self.ir.to_greyscale(img)
                    img = self.ir.convert_to_ascii(img, width, height)
                    img.save(filename)
                i += 1
                filename = f'temp\\tmpframe{i}.png'
            self.__converted_to_ascii = True
        return self.__converted_to_ascii

    def make_video(self, filename='out'):
        """
        склеивает кадры в видео
        """
        if self.__converted_to_ascii:
            i = 0
            frame = f'temp\\tmpframe{i}.png'
            if not os.path.exists(frame):
                return
            with Image.open(frame) as first_frame:
                width, height = first_frame.size
            writer = cv2.VideoWriter(
                f'{filename}_ascii.avi',
                cv2.VideoWriter_fourcc(*'DIVX'),
                self.__fps // 5,
                (width, height))
            while os.path.exists(frame):
                writer.write(cv2.imread(frame))
                i += 1
                os.unlink(frame)
                frame = f'temp\\tmpframe{i}.png'
            writer.release()
            cv2.destroyAllWindows()
            return True
        return False
