import hashlib
import pathlib

import lxml.html
import lxml.html.clean
import requests
import templater


INLINE_ELEMENTS = {
    'a',
    'abbr',
    'acronym',
    'b',
    'big',
    'dfn',
    'em',
    'i',
    'img',
    'kbd',
    'label',
    'map',
    'q',
    'small',
    'span',
    'strong',
    'sub',
    'sup',
    'time',
    'tt',
    'var',
}


def get_html_content(url):
    cache_file = pathlib.Path('cache') / hashlib.sha1(url.encode()).hexdigest()
    if cache_file.exists():
        return cache_file.read_text()
    else:
        resp = requests.get(url)
        cache_file.write_text(resp.text)
        return resp.text


def get_text_content(url):
    html = get_html_content(url)
    html = lxml.html.fromstring(html)
    cleaner = lxml.html.clean.Cleaner(
        scripts=True,
        javascript=True,
        comments=True,
        style=True,
        inline_style=True,
        links=False,
        embedded=True,
        frames=True,
        forms=True,
        page_structure=False,
        processing_instructions=True,
    )
    html = cleaner.clean_html(html)
    text = extract_text([html])
    text = ' '.join(filter(None, text))
    text = clean_text(text)
    return text


def extract_text(nodes, tail=False):
    texts = []
    for node in nodes:
        if isinstance(node, str):
            texts.append(node)
            continue
        texts.append(node.text)
        texts.extend(extract_text(node.getchildren(), tail=True))
        if node.tag not in INLINE_ELEMENTS:
            texts.append('\n')
        if tail:
            texts.append(node.tail)
    return texts


def clean_text(text):
    lines = []
    for line in text.splitlines():
        words = [w.strip() for w in line.split()]
        lines.append(' '.join(filter(None, words)))
    return '\n'.join(filter(None, lines))


texts = [
    'https://www.delfi.lt/news/ringas/lit/rita-miliute-nunykus-zurnalistikai-nelieka-demokratijos.d?id=79370859',
    'https://www.delfi.lt/news/daily/lithuania/liberalu-krize-apima-visa-lietuva-pagegiuose-spaudziama-ranka-komskiui-klaipedoje-bresta-skilimas.d?id=79351279',
]
texts = map(get_text_content, texts)

template = templater.Templater()
for text in texts:
    template.learn(text)

for x in template._template:
    print(x)
