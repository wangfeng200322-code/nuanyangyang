from langdetect import detect, LangDetectException

class LanguageRouter:
    LANGUAGE_MAP = {
        'zh-cn': 'zh',
        'nl': 'nl',
        'en': 'en'
    }
    
    @staticmethod
    def detect_language(text: str, default: str = "zh") -> str:
        """检测文本语言"""
        try:
            detected = detect(text)
            return LanguageRouter.LANGUAGE_MAP.get(detected, default)
        except LangDetectException:
            return default
    
    @staticmethod
    def get_language_code(language: str) -> str:
        """获取语言代码（用于ASR/TTS）"""
        mapping = {
            "zh": "zh-CN",
            "nl": "nl-NL",
            "en": "en-US"
        }
        return mapping.get(language, "zh-CN")
