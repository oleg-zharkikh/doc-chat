import os
from typing import List, Dict, Any
from bs4 import BeautifulSoup


def clean_tags(info) -> str:
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


def read_html_files(directory: str) -> List[Dict[str, Any]]:
    """Считывает все HTML файлы из указанной папки.

    Возвращает список словарей: {'filename': str, 'content': str}
    """
    files_data = []
    if not os.path.isdir(directory):
        raise FileNotFoundError(f'Каталог не найден: {directory}')
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.html', '.htm')):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                files_data.append({
                    'filename': filename,
                    'content': content,
                    'filepath': filepath
                })
                print(f'Загружен файл: {filename}')
            except Exception as e:
                print(f'Ошибка чтения {filename}: {e}')
    return files_data


def extract_text_from_html(html_content: str) -> str:
    """Извлекает чистый текст из HTML."""
    soup = BeautifulSoup(html_content, 'lxml')
    for tag in soup(['script', 'style', 'head', 'meta']):
        tag.decompose()
    text = soup.get_text(separator=' ', strip=True)
    text = ' '.join(text.split())
    text = clean_tags(text)
    return text
