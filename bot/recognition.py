import cv2
import numpy as np
from PIL import Image
import pytesseract
import os
import json
import langid

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ["TESSDATA_PREFIX"] = r'C:\Program Files\Tesseract-OCR\tessdata'


class ImagePreprocessor:
    def __init__(self, image_path=None, image=None, config=None):
        if image_path:
            self.image = cv2.imread(image_path)
            if self.image is None:
                raise FileNotFoundError(f"Файл изображения {image_path} не найден.")
        elif image is not None:
            self.image = np.array(image)
        else:
            raise ValueError("Необходимо указать image_path или передать изображение в параметре image.")

        self.config = config or {
            "resize_width": 1000,
            "blur_kernel": (3, 3),
            "contrast_alpha": 1.5,
            "brightness_beta": 50,
            "adaptive_block_size": 21,
            "adaptive_C": 5,
        }

    def save_debug_image(self, stage_name):
        """Сохраняет промежуточное изображение для отладки."""
        cv2.imwrite(f"debug_{stage_name}.jpg", self.image)

    def apply_grayscale(self):
        """Преобразует изображение в градации серого."""
        if len(self.image.shape) == 3:  # Если изображение цветное
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self.save_debug_image("grayscale")

    def apply_blur(self):
        """Применяет размытие по Гауссу для уменьшения шума."""
        self.image = cv2.GaussianBlur(self.image, self.config["blur_kernel"], 0)
        self.save_debug_image("blurred")

    def adjust_contrast_and_brightness(self):
        """Регулирует контрастность и яркость изображения."""
        self.image = cv2.convertScaleAbs(
            self.image,
            alpha=self.config["contrast_alpha"],
            beta=self.config["brightness_beta"]
        )
        self.save_debug_image("contrast_brightness")

    def apply_adaptive_threshold(self):
        """Применяет адаптивную бинаризацию для улучшения видимости текста."""
        self.image = cv2.adaptiveThreshold(
            self.image,
            maxValue=255,
            adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            thresholdType=cv2.THRESH_BINARY,
            blockSize=self.config["adaptive_block_size"],
            C=self.config["adaptive_C"]
        )
        self.save_debug_image("adaptive_threshold")

    def resize_image(self):
        """Изменяет размер изображения, если оно шире заданной ширины."""
        height, width = self.image.shape[:2]
        target_width = self.config["resize_width"]
        if width > target_width:
            scaling_factor = target_width / width
            new_dimensions = (target_width, int(height * scaling_factor))
            self.image = cv2.resize(self.image, new_dimensions, interpolation=cv2.INTER_LINEAR)
            self.save_debug_image("resized")

    def perform_ocr(self, lang="rus"):
        """Выполняет распознавание текста с помощью Tesseract OCR."""
        custom_config = r'--psm 4'
        pil_image = Image.fromarray(self.image)
        return pytesseract.image_to_string(pil_image, lang=lang, config=custom_config).strip()

    def process_and_extract_text(self, save_path=None):
        """Полный процесс обработки изображения и распознавания текста."""
        self.apply_grayscale()
        self.apply_blur()
        self.adjust_contrast_and_brightness()
        self.apply_adaptive_threshold()
        self.resize_image()

        if save_path:
            cv2.imwrite(save_path, self.image)

        initial_text = self.perform_ocr(lang="eng+rus")

        detected_language, confidence = langid.classify(initial_text)
        tesseract_lang = "rus" if detected_language == "ru" else "eng"

        final_text = self.perform_ocr(lang=tesseract_lang)
        return final_text


def recognition(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Файл изображения {image_path} не найден.")

    preprocessor = ImagePreprocessor(image_path=image_path)
    output_path = r'C:\Users\aldem\IdeaProjects\PythonDevelop\venv\Scripts\processed_image.jpg'

    recognized_text = preprocessor.process_and_extract_text(save_path=output_path)
    return("Распознанный текст:", recognized_text)
