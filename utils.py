from typing import List

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


STRUCTURE_NAMES = ['chorus', 'verse', 'intro', 'bridge', 'outro']
# TODO: use dynamic word duration
DEFAULT_WORD_TICKS = 170


def split_lyrics(lyrics: str) -> List[str]:
    '''
    Post-process the API responses, splitting them into individual lines.
    The output may include structural labels and non-lyrical content,
    which should be removed to ensure only the desired lyrics are retained.
    '''
    start_index = lyrics.lower().find("[start]")
    end_index = lyrics.lower().find("[end]")
    lyrics = lyrics[start_index + len("[start]"):end_index]

    # Split the lyrics into lines and remove leading/trailing spaces
    lines = [line.strip() for line in lyrics.split("\n") if line.strip()]
    # Remove lines that contain structure names
    lines = [line for line in lines if not any(
        structure in line.lower() for structure in STRUCTURE_NAMES)]

    return lines
