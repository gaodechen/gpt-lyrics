def contains_chinese(text):
    '''
    Determine whether the given text contains Chinese characters.
    Detects both simplified and traditional Chinese characters.
    '''
    for char in text:
        if '\u4e00' <= char <= '\u9fff' or '\u3400' <= char <= '\u4dbf':
            return True
    return False