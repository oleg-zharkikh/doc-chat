from bs4 import BeautifulSoup
import re


def get_block_by_exec_mask(info, pattern_start, pattern_end):
    """Возвращает блок текста между заданными фрагментами."""
    p_start = info.find(pattern_start)
    if p_start >= 0 :
        p_end = info[p_start+len(pattern_start):].find(pattern_end)
        if p_end >= 0:
            return info[p_start+len(pattern_start):p_start+len(pattern_start)+p_end]
        else:
            return ''
    else:
        return ''


def clean_tags(info):
    """Очищает текст от html тегов."""

    open_tag_char = '<'
    close_tag_char = '>'
    iteration = 0

    open_tag_position = info.find(open_tag_char)
    while open_tag_position >= 0:
        iteration += 1

        close_tag_position = info.find(close_tag_char)

        if close_tag_position > open_tag_position:
            patt = info[open_tag_position:close_tag_position+1]
            info = info.replace(patt, '', 1)
        else:
            break

        open_tag_position = info.find(open_tag_char)

        if iteration > 10_000:
            break

    return info


def extract_clean_text(html_string: str):
    """Возвращает очищенный от html тегов текст документа."""
    if '<html' not in html_string:
        return html_string.strip()

    try:
        soup = BeautifulSoup(html_string, 'html.parser')
        body_content = soup.find('body')
        if not body_content:
            clean_text = ''
        else:
            clean_text = body_content.get_text(separator=' ', strip=True)

    except Exception:
        body_content = get_block_by_exec_mask(html_string, '<body', '</body>')
        clean_text = body_content[body_content.find('>')+1:]

    clean_text = clean_tags(clean_text)

    for char in ('&nbsp;', '\r', '\n', '\t', '\xa0'):
        clean_text = clean_text.replace(char, ' ')

    clean_text = re.sub(r'&#\d{4};', ' ', clean_text)

    while '  ' in clean_text:
        clean_text = clean_text.replace('  ', ' ')

    return clean_text.strip()
