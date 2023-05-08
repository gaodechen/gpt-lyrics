def contains_chinese(text):
    '''
    Determine whether the given text contains Chinese characters.
    Detects both simplified and traditional Chinese characters.
    '''
    for char in text:
        if '\u4e00' <= char <= '\u9fff' or '\u3400' <= char <= '\u4dbf':
            return True
    return False

SUPPORTED_LANGUAGES = ['en', 'zh']

def get_writing_language(selected_lang: str, user_lang: str):
    # extract the first part of the locale if it's divided by a dash, other wise keep it as is
    if selected_lang == 'auto':
        user_lang = user_lang.split(
            '-')[0] if '-' in user_lang else user_lang
        if user_lang not in SUPPORTED_LANGUAGES:
            user_lang = "en"
        return user_lang
    return selected_lang