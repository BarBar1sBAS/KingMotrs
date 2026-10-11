# -*- coding: utf-8 -*-
from pathlib import Path
from html import escape
import json, re
from seo import enrich

root = Path(__file__).resolve().parents[1]
copy = (root / "docs/page-copy.md").read_text(encoding="utf-8")
chunks = {
    m.group(1): m.group(2)
    for m in re.finditer(
        r"## \d+\. https://kingmotors52.ru/([^\n]*)\n(.*?)(?=\n## \d+\.|\Z)", copy, re.S
    )
}
data = json.loads((root / "docs-v2/site-content.json").read_text(encoding="utf-8"))
groups = data["groups"]


def work_scope(slug):
    section = chunks[slug]
    scope = re.search(r"### Что обсуждаем перед работой\n([^#]+)", section)
    assert scope, slug
    return scope.group(1).strip()


card = ""
for group in groups:
    gid, title, desc = group["id"], group["title"], group["description"]
    children = [job for job in data["jobs"] if job["group"] == gid]
    intro = desc + " Выберите работу. Цена «от» — за работу без запчастей; итог согласуем до начала."
    card += f'<details class="service-card" id="service-{gid}"><summary><span class="service-media"><img class="service-photo" src="assets/{group["image"]}" alt="Иллюстрация направления: {escape(title)}" width="{group.get("image_width", 700)}" height="{group.get("image_height", 396)}" loading="lazy"></span><div class="service-info"><div><h3>{escape(title)}</h3><p>{escape(group["teaser"])}</p></div><span class="plus" aria-hidden="true">+</span></div></summary><div class="service-content"><p class="service-intro">{escape(intro)}</p>'
    if gid == "diagnostics":
        card += f'<p id="detail-besplatnaya-diagnostika-avtomobilya">{escape(data["offer"])}</p>'
    if gid == "other":
        card += '<p id="service-parts"><strong>Подбор запчастей.</strong> Подбираем по VIN оригиналы и подходящие аналоги. Объясняем разницу в цене и ресурсе.</p><p id="service-tires"><strong>Шиномонтаж.</strong> Снятие и установка колёс, балансировка и ремонт проколов. Состав и стоимость уточним при записи.</p>'
    for job in children:
        slug, t, lead = job["slug"], job["title"], job["intro"]
        parts = work_scope(slug)
        card += f'<details class="job" id="detail-{slug}"><summary>{escape(t)}</summary><div class="job-body"><p>{escape(lead)}</p><h4>Что входит в работу</h4><p>{escape(parts)}</p><p class="price-note">{escape(job["price_note"])}</p><a class="btn" href="#booking" data-service="{escape(t)}">Записаться <span class="arrow" aria-hidden="true">↗</span></a></div></details>'
    card += f'<a class="text-link" href="#booking" data-service="{escape(title)}">Обсудить работы <span aria-hidden="true">↗</span></a></div></details>'
head = """<!doctype html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>КингМоторс · дизайн-концепция</title><link rel="preload" href="assets/Manrope-Variable.ttf" as="font" type="font/ttf" crossorigin><link rel="stylesheet" href="style.css"><link rel="stylesheet" href="motion.css"><script src="app.js" defer></script></head><body><a class="skip" href="#main">К содержанию</a>
<header class="site-header"><div class="wrap header-inner"><a class="brand" href="#top" aria-label="КингМоторс, на главную"><img src="assets/logo.svg" width="186" height="54" alt="КингМоторс"></a><nav class="desktop-nav" aria-label="Главная навигация"><a href="#services">Услуги и цены</a><a href="#about">Как работаем</a><a href="#reviews">Отзывы</a><a href="#faq">Вопросы</a><a href="#contacts">Контакты</a></nav><a class="top-phone" href="tel:+79063664911">8 906 366 49 11</a><a class="btn header-book" href="#booking">Записаться <span class="arrow" aria-hidden="true">↗</span></a><button class="menu-toggle" aria-expanded="false" aria-controls="mobile-nav">Меню</button></div><nav id="mobile-nav" class="mobile-nav wrap" hidden aria-label="Мобильная навигация"><a href="#services">Услуги и цены</a><a href="#about">Как работаем</a><a href="#reviews">Отзывы</a><a href="#faq">Вопросы</a><a href="#business">Корпоративным клиентам</a><a href="#careers">Вакансии</a><a href="#contacts">Контакты</a><a class="btn" href="#booking">Записаться ↗</a></nav></header>
<main id="main"><section class="hero" id="top"><img class="hero-photo" src="assets/hero.webp" alt="Иллюстрация: автомобиль с открытым капотом в процессе обслуживания" width="1672" height="941" fetchpriority="high"><div class="wrap hero-content"><p class="hero-location"><span class="hero-rule" aria-hidden="true"></span>КингМоторс · Московское шоссе, 12А</p><h1><span class="hero-title-part">Автосервис в Нижнем Новгороде</span><span class="second hero-title-part">Ремонтируем только то, что согласовали</span></h1><p class="hero-lead">Капитальный ремонт двигателя, ходовая, АКПП, DSG и вариаторы, диагностика и ТО. Все марки, кроме ВАЗ.</p><p class="hero-offer">Стоимость диагностики полностью вычитаем из стоимости ремонта выявленной неисправности, если ремонтируете её у нас.</p><div class="hero-actions"><a href="#booking" class="btn">Записаться на диагностику <span class="arrow" aria-hidden="true">↗</span></a><a class="phone" href="tel:+79063664911">8 906 366 49 11</a></div></div><span class="hero-caption">Иллюстрация дизайн-концепции</span></section>
<div class="arrival"><div class="wrap arrival-inner"><div><small>Ждём вас по адресу</small><strong>Московское шоссе, 12А</strong></div><div><small>Режим работы</small><strong>Пн–Пт 9:00–19:00. Сб–Вс — выходные</strong></div><a class="text-link route" href="https://yandex.ru/maps/?text=КингМоторс%20Московское%20шоссе%2012А" target="_blank" rel="noopener">Построить маршрут <span aria-hidden="true">↗</span></a></div></div>
<section id="services" class="section services"><div class="wrap" id="service-wash"><div class="section-head services-head"><h2>Ремонт и обслуживание автомобилей</h2><p class="help">Кузовной ремонт не выполняем. Не знаете причину неисправности? <a href="#booking">Опишите, что чувствуете за рулём ↗</a></p></div><div class="service-grid">"""
about = """</div></div></section><section class="section about" id="about"><div class="wrap about-grid"><div class="about-image"><img src="assets/process.webp" width="667" height="1000" alt="Иллюстрация обслуживания автомобиля" loading="lazy"><small>Иллюстрация дизайн-концепции</small></div><div class="about-copy"><h2>Сначала согласуем.<br>Затем ремонтируем.</h2><ol class="service-steps"><li><h3>Находим причину</h3><p>Диагностика помогает определить неисправность. Стоимость диагностики полностью вычитаем из стоимости ремонта выявленной неисправности, если ремонтируете её у нас.</p></li><li><h3>Называем цену</h3><p>Мастер-приёмщик составляет смету: работы и запчасти. Что срочно, а что может подождать, говорим прямо.</p></li><li><h3>Подбираем запчасти</h3><p>Оригинал или аналог — выбираете вы. Объясняем разницу в цене и ресурсе.</p></li><li><h3>Ремонтируем согласованное</h3><p>Нашли по ходу что-то ещё — сначала звоним вам. Без вашего согласия сумма не меняется.</p></li></ol><div class="service-assurances"><p><strong>Гарантия на работы и запчасти.</strong> Условия для каждого ремонта указываем в смете.</p></div><a href="#booking" class="text-link">Записаться на диагностику <span aria-hidden="true">↗</span></a></div></div></section>"""
about = about.replace("<li>", '<li><span class="step-line" aria-hidden="true"></span>')
svg = (root / "prototype/assets/logo.svg").read_text(encoding="utf-8")
paths = re.findall(r"<path[^>]+/?>", svg)
intro = re.sub(r"<path[^>]+/?>", "", svg).replace(
    "</svg>",
    '<g class="intro-mark">'
    + paths[0]
    + '</g><g class="intro-name">'
    + "".join(paths[1:])
    + "</g></svg>",
)
head = head.replace(
    '<span class="hero-caption">',
    '<div class="brand-intro" aria-hidden="true" hidden>'
    + intro
    + '</div><span class="hero-caption">',
)
rest = (root / "output-v2/build/rest.html").read_text(encoding="utf-8")
(root / "prototype/index.html").write_text(
    enrich(head + card + about + rest + "</main></body></html>"), encoding="utf-8"
)
print("built", sum(1 for x in re.finditer('class="job"', card)), "jobs")
