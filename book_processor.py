import os
import json
import time
from ebooklib import epub
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import nltk

from google.genai import Client
from google.genai.types import Content, GenerateContentConfig

nltk.download("punkt", quiet=True)
from nltk.tokenize import sent_tokenize

# Загрузка API ключа
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
client = Client(api_key=API_KEY)


def extract_metadata(epub_path):
    book = epub.read_epub(epub_path)
    title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else "Untitled"
    author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else "Unknown"
    return book, title, author


def extract_document_structure(book):
    structured_bodies = []
    for item in book.get_items():
        if item.media_type == 'application/xhtml+xml':
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            body = soup.find('body')
            if body:
                structured_bodies.append(body)
    return structured_bodies


def annotate_sentence(sentence, target_lang, native_lang, level):
    prompt = f"""
Переведи и грамматически проанализируй следующее предложение на языке {target_lang}:

"{sentence}"

Выдели подлежащее, сказуемое и устойчивые выражения. Если полезно обратить внимание на какие-то элементы на уровне изучения языка {level}, добавь краткую сноску, но не перебарщивай. Верни строго JSON в следующем формате:

{{
  "translation": "перевод предложения на {native_lang}",
  "grammar": {{
    "subject": "подлежащее",
    "predicate": "сказуемое",
    "phrases": ["устойчивые выражения"]
  }},
  "notes": ["короткие языковые комментарии, от нуля до трех"]
}}
"""
    try:
        contents = [Content(role="user", parts=[{"text": prompt}])]
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=contents,
            config=GenerateContentConfig(candidate_count=1, temperature=0.6)
        )
        raw_text = response.candidates[0].content.parts[0].text.strip("` \n")
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()
        return json.loads(raw_text)

    except Exception as e:
        print(f"[Gemini error] {e}")
        if 'RESOURCE_EXHAUSTED' in str(e):
            print("⏸️ Превышен лимит. Пауза 60 секунд...")
            time.sleep(60)
        return None


def mark(text, word, tag):
    if not word or word not in text:
        return text
    return text.replace(word, f"<{tag}>{word}</{tag}>", 1)


def annotate_html_tree(soup_body, lang='english', target_lang='en', native_lang='ru', level='B1', note_counter_start=1):
    note_counter = note_counter_start
    notes_html = ""

    for tag in soup_body.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'blockquote']):
        if not tag.string and not tag.get_text(strip=True):
            continue

        segments = sent_tokenize(tag.get_text(" ", strip=True), language=lang)
        annotated_fragments = []

        for sentence in segments:
            ann = annotate_sentence(sentence, target_lang, native_lang, level)
            if not ann:
                print(f"⚠️ Пропущено предложение из-за ошибки: {sentence}")
                continue

            s = sentence
            grammar = ann.get('grammar', {})
            s = mark(s, grammar.get('subject'), 'b')
            s = mark(s, grammar.get('predicate'), 'i')
            for phrase in grammar.get('phrases', []):
                s = mark(s, phrase, 'u')

            for note in ann.get('notes', []):
                anchor = f"note{note_counter}"
                sup = f'<sup><a href="#{anchor}" id="ref{anchor}">[{note_counter}]</a></sup>'
                notes_html += f'<p id="{anchor}"><small>[{note_counter}] {note} <a href="#ref{anchor}">↩</a></small></p>'
                s += sup
                note_counter += 1

            s += f"<br><em>{ann.get('translation')}</em>"
            annotated_fragments.append(s)

        if annotated_fragments:
            tag.clear()
            tag.append(BeautifulSoup("<br/><br/>".join(annotated_fragments), "html.parser"))

    if notes_html:
        soup_body.append(BeautifulSoup("<hr/>" + notes_html, "html.parser"))

    return soup_body, note_counter


def build_structured_epub(soups, title="Annotated Book", author="Unknown", user_lang ='ru', max_chapters=5):
    book = epub.EpubBook()
    book.set_title(title)
    book.add_author(author)

    chapters = []
    note_counter = 1

    for i, body in enumerate(soups[:max_chapters]):
        annotated_body, note_counter = annotate_html_tree(body, note_counter_start=note_counter)

        chapter = epub.EpubHtml(title=f'Chapter {i+1}', file_name=f'chap_{i+1}.xhtml', lang=user_lang)
        chapter.content = f"<html><body>{annotated_body}</body></html>"
        book.add_item(chapter)
        chapters.append(chapter)

    book.toc = tuple(chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    for c in chapters:
        book.add_item(c)

    file_name = f"{title.replace(' ', '_')}_annotated.epub"
    epub.write_epub(file_name, book)
    print(f"✅ EPUB saved as {file_name}")

def process_book(input_path, output_dir, target_lang='en', level='B1'):
    import os
    original_book, title, author = extract_metadata(input_path)
    structured_bodies = extract_document_structure(original_book)
    build_structured_epub(structured_bodies, title=title, author=author, max_chapters=5,
                          user_lang=target_lang)
    output_path = os.path.join(output_dir, f"{title.replace(' ', '_')}_annotated.epub")
    return title, output_path


if __name__ == '__main__':
    input_path = "examples/pg1342.epub"
    original_book, title, author = extract_metadata(input_path)
    structured_bodies = extract_document_structure(original_book)
    build_structured_epub(structured_bodies, title=title, author=author, max_chapters=2)
