#!/usr/bin/env python3
"""Generate personalized wedding invitation pages from template + guest list."""

import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "index.html")
GUESTS_PATH = os.path.join(SCRIPT_DIR, "guests.json")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "guests")

# Transliteration map
TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
}

# Known single female names (for "Дорогая" instead of "Дорогой")
FEMALE_NAMES = {"Наташенька", "Мамочка Лена", "Машенька", "Кристиночка"}


def transliterate(text):
    """Transliterate Russian text to Latin."""
    result = []
    for ch in text:
        if ch in TRANSLIT:
            result.append(TRANSLIT[ch])
        elif ch.isascii():
            result.append(ch)
        else:
            result.append('')
    return ''.join(result)


def make_filename(guest_id, names):
    """Create a safe filename from guest id and names."""
    slug = transliterate(names).lower()
    # Replace separators
    slug = slug.replace(', ', '-').replace(' и ', '-i-').replace(' ', '-')
    # Remove non-alphanumeric except hyphens
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return f"{guest_id:02d}-{slug}.html"


def make_greeting(names):
    """Generate personalized greeting based on names."""
    is_group = (' и ' in names) or (',' in names)
    if is_group:
        return f"Дорогие {names}!"
    elif names in FEMALE_NAMES:
        return f"Дорогая {names}!"
    else:
        return f"Дорогой {names}!"


def generate():
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    with open(GUESTS_PATH, 'r', encoding='utf-8') as f:
        guests = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Fix image paths: images/ -> ../images/
    html_base = template.replace('src="images/', 'src="../images/')

    created = []
    for guest in guests:
        gid = guest['id']
        names = guest['names']
        greeting = make_greeting(names)
        if 'slug' in guest:
            filename = f"{gid:02d}-{guest['slug']}.html"
        else:
            filename = make_filename(gid, names)

        html = html_base
        # Replace guest name in hidden form field
        html = html.replace('value="{{GUEST_NAME}}"', f'value="{names}"')
        # Replace greeting heading
        html = html.replace(
            'id="heading-friends">Дорогие Друзья!</h1>',
            f'id="heading-friends">{greeting}</h1>'
        )

        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        created.append((gid, names, filename))
        print(f"  ✅ {filename}")

    print(f"\n🎉 Создано {len(created)} персональных приглашений в папке guests/")
    return created


if __name__ == '__main__':
    generate()
