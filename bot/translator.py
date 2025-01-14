from googletrans import Translator
from langdetect import detect, LangDetectException

class TranslationResult:
    def __init__(self, original_text, translated_text, source_language, target_language): # исправлено: __init__
        self.original_text = original_text
        self.translated_text = translated_text
        self.source_language = source_language
        self.target_language = target_language

    def __str__(self):
        return f"Оригинал ({self.source_language}): {self.original_text}\nПеревод ({self.target_language}): {self.translated_text}"

translator = Translator()

def translate_text(text, source_language):
    """
    Переводит текст и возвращает результат в виде объекта класса TranslationResult.
    Проверяет указанный язык с обнаруженным языком.
    """
    try:
        detected_language = detect(text[1] if isinstance(text, tuple) else text) # определяем язык с помощью langdetect

        target_language = 'ru' if source_language == 'en' else 'en'

        #Проверка на соответствие языков
        if detected_language.lower() != source_language.lower():
            if source_language == 'ru':
                return "Текст, который вы отправили написан не на русском языке. Выберите нужное действие снова и отправьте корректный текст."
            else:
                return "Текст, который вы отправили написан не на английском языке. Выберите нужное действие снова и отправьте корректный текст."

        translation = translator.translate(text[1] if isinstance(text, tuple) else text, src=source_language, dest=target_language)
        result = TranslationResult(text[1] if isinstance(text, tuple) else text, translation.text, source_language, target_language)
        return result
    except LangDetectException as e:
        print(f"Ошибка определения языка: {e}")
        return TranslationResult(text[1] if isinstance(text, tuple) else text, None, source_language, target_language, "Не удалось определить язык") #Возвращаем сообщение об ошибке
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return None



