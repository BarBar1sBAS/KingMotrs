# -*- coding: utf-8 -*-
from pathlib import Path
from bs4 import BeautifulSoup
from html import escape

r = Path(__file__).resolve().parents[1]
text = BeautifulSoup(
    (r / "sources/pages/privacypolicy.html").read_text(encoding="utf-8"), "html.parser"
).select_one("main")
body = "<h1>Правовая информация</h1><p>Архив исходного сайта от 6 октября 2026. Реквизиты оператора расходятся между страницами; согласие не содержит полноценного текста. Перед запуском необходимо согласовать документы. Прототип не собирает и не отправляет данные.</p><h2>Политика конфиденциальности · исходный текст</h2>"
body += "".join(
    "<p>" + escape(x) + "</p>" for x in text.get_text("\n", strip=True).splitlines()
)
body += '<h2>Согласие на обработку данных</h2><p>В источнике не найден полноценный текст согласия. Не использовать этот экран как утверждённый юридический документ.</p><a class="text-link" href="index.html#booking">Вернуться к форме</a>'
(r / "prototype/legal.html").write_text(
    '<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="description" content="Архив правовой информации КингМоторс. Документы требуют согласования перед запуском сайта."><title>Правовая информация · архив</title><link rel="stylesheet" href="style.css"><main class="wrap section legal">'
    + body
    + "</main></html>",
    encoding="utf-8",
)
