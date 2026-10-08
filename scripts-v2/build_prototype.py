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
inv = json.loads((root / "sources/inventory.json").read_text(encoding="utf-8"))
groups = [
    ("maintenance", "Обслуживание", "Плановые работы и забота о ресурсе", 16, 32),
    ("repair", "Ремонт", "Вернём уверенность за рулём", 32, 38),
    ("diagnostics", "Диагностика", "Найдём причину, а не только ошибку", 38, 49),
    ("parts", "Подбор запчастей", "Под автомобиль и ваш бюджет", 0, 0),
    ("tires", "Шиномонтаж", "Уверенное сцепление с дорогой", 0, 0),
    ("wash", "Мойка", "Чистота снаружи и внутри", 0, 0),
]
slugs = [x["slug"] for x in inv]


# Inventory positions are zero-based; first child is index 15.
def content(slug):
    c = chunks.get(slug, "")
    title = re.search(r"\*\*Название блока:\*\* (.+)", c)
    title = (
        title.group(1) if title else next(x["h1"][0] for x in inv if x["slug"] == slug)
    )
    intro = re.search(r"\*\*Название блока:\*\*[^\n]+\n\n([^#\n][^\n]+)", c)
    intro = intro.group(1) if intro else ""
    parts = re.search(r"### Что обсуждаем перед работой\n([^#]+)", c)
    return title, intro, parts.group(1).strip() if parts else ""


card = ""
for gid, title, desc, a, b in groups:
    if a:
        children = slugs[a - 1 : b - 1]
    else:
        children = []
    intro = {
        "parts": "Подбираем оригинальные комплектующие и подходящие аналоги. Для подбора подготовьте VIN, марку и модель автомобиля.",
        "tires": "Снятие и установка колёс, балансировка и ремонт проколов. Состав работ уточним при записи.",
        "wash": "Мойка кузова и уход за салоном. Уточните нужные работы при записи.",
    }.get(gid, "Выберите работу. Состав и стоимость согласуем до начала.")
    card += f'<details class="service-card" id="service-{gid}"><summary><span class="service-media"><img class="service-photo" src="assets/{gid}.webp" alt="Иллюстрация направления: {title}" width="700" height="396" loading="lazy"></span><div class="service-info"><div><h3>{title}</h3><p>{desc}</p></div><span class="plus" aria-hidden="true">+</span></div></summary><div class="service-content"><p class="service-intro">{intro}</p>'
    for slug in children:
        t, lead, parts = content(slug)
        card += f'<details class="job" id="detail-{slug}"><summary>{escape(t)}</summary><div class="job-body"><p>{escape(lead)}</p><h4>Что входит в работу</h4><p>{escape(parts)}</p><p class="price-note">Стоимость зависит от автомобиля, деталей и объёма работ. Согласуем её до ремонта.</p><a class="btn" href="#booking" data-service="{escape(t)}">Записаться <span class="arrow" aria-hidden="true">↗</span></a></div></details>'
    card += f'<a class="text-link" href="#booking" data-service="{title}">Записаться на {title.lower()} <span aria-hidden="true">↗</span></a></div></details>'
head = """<!doctype html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>КингМоторс · дизайн-концепция</title><link rel="preload" href="assets/Manrope-Variable.ttf" as="font" type="font/ttf" crossorigin><link rel="stylesheet" href="style.css"><link rel="stylesheet" href="motion.css"><script src="app.js" defer></script></head><body><a class="skip" href="#main">К содержанию</a>
<header class="site-header"><div class="wrap header-inner"><a class="brand" href="#top" aria-label="КингМоторс, на главную"><img src="assets/logo.svg" width="186" height="54" alt="КингМоторс"></a><nav class="desktop-nav" aria-label="Главная навигация"><a href="#services">Услуги</a><a href="#about">О сервисе</a><a href="#team">Команда</a><a href="#reviews">Отзывы</a><a href="#contacts">Контакты</a></nav><a class="top-phone" href="tel:+79063664911">8 906 366 49 11</a><a class="btn header-book" href="#booking">Записаться <span class="arrow" aria-hidden="true">↗</span></a><button class="menu-toggle" aria-expanded="false" aria-controls="mobile-nav">Меню</button></div><nav id="mobile-nav" class="mobile-nav wrap" hidden aria-label="Мобильная навигация"><a href="#services">Услуги</a><a href="#about">О сервисе</a><a href="#team">Команда</a><a href="#reviews">Отзывы</a><a href="#business">Корпоративным клиентам</a><a href="#careers">Вакансии</a><a href="#contacts">Контакты</a><a class="btn" href="#booking">Записаться ↗</a></nav></header>
<main id="main"><section class="hero" id="top"><img class="hero-photo" src="assets/hero.webp" alt="Иллюстрация: автомобиль с открытым капотом в процессе обслуживания" width="1672" height="941" fetchpriority="high"><div class="wrap hero-content"><p class="hero-location"><span class="hero-rule" aria-hidden="true"></span>КингМоторс / Нижний Новгород</p><h1><span class="hero-title-part">Ремонт и обслуживание</span><br><span class="second hero-title-part">без несогласованных работ</span></h1><p class="hero-lead">Разберёмся в задаче, объясним решение и согласуем стоимость до начала ремонта.</p><div class="hero-actions"><a href="#booking" class="btn">Записаться в сервис <span class="arrow" aria-hidden="true">↗</span></a><a class="phone" href="tel:+79063664911">8 906 366 49 11</a></div></div><span class="hero-caption">Иллюстрация дизайн-концепции</span></section>
<div class="arrival"><div class="wrap arrival-inner"><div><small>Ждём вас по адресу</small><strong>Московское шоссе, 12А</strong></div><div><small>Режим работы</small><strong>Ежедневно, 9:00–19:00</strong></div><a class="text-link route" href="https://yandex.ru/maps/?text=КингМоторс%20Московское%20шоссе%2012А" target="_blank" rel="noopener">Построить маршрут <span aria-hidden="true">↗</span></a></div></div>
<section id="services" class="section services"><div class="wrap"><div class="section-head services-head"><h2>Что нужно<br>вашему автомобилю?</h2><p class="help">Не знаете причину неисправности? <a href="#booking">Просто опишите, что случилось ↗</a></p></div><div class="service-grid">"""
about = """</div></div></section><section class="section about" id="about"><div class="wrap about-grid"><div class="about-image"><img src="assets/process.webp" width="667" height="1000" alt="Иллюстрация обслуживания автомобиля" loading="lazy"><small>Иллюстрация дизайн-концепции</small></div><div class="about-copy"><h2>Сначала согласуем.<br>Затем ремонтируем.</h2><ol class="service-steps"><li><h3>Обсудим вашу задачу</h3><p>Расскажите об автомобиле и о том, что беспокоит. Определим, какие проверки нужны.</p></li><li><h3>Согласуем работы и стоимость</h3><p>Объясним, что нужно сделать, и обсудим стоимость до начала ремонта.</p></li><li><h3>Выполним согласованные работы</h3><p>Приступим к ремонту после согласования с вами.</p></li></ol><div class="service-assurances"><p><strong>Запчасти под вашу задачу.</strong> Подбираем оригиналы и подходящие аналоги.</p><p><strong>Гарантия на работы и запчасти.</strong> Условия уточняем для конкретной работы.</p></div><a href="#booking" class="text-link">Обсудить ремонт <span aria-hidden="true">↗</span></a></div></div></section>"""
about = about.replace("<li>", '<li><span class="step-line" aria-hidden="true"></span>')
# Demo staff live in the generator so rebuilds preserve the section.
team_members = [
    ("smirnov", "Алексей Смирнов", "Мастер-приёмщик"),
    ("volkov", "Дмитрий Волков", "Автодиагност"),
    ("morozov", "Сергей Морозов", "Автомеханик"),
    ("sokolov", "Андрей Соколов", "Автоэлектрик"),
    ("orlov", "Максим Орлов", "Специалист по подбору запчастей"),
]
team = '<section class="section team-section" id="team" aria-labelledby="team-title"><div class="wrap"><div class="team-heading"><h2 id="team-title">Наша команда</h2><p class="team-notice">Демо-состав команды. Имена, должности и портреты вымышлены.</p></div><ul class="team-list" role="list">'
for slug, name, role in team_members:
    team += f'<li class="team-member"><img src="assets/team-{slug}.webp" alt="Демо-портрет вымышленного сотрудника: {escape(name)}" width="640" height="800" loading="lazy" decoding="async"><h3>{escape(name)}</h3><p>{escape(role)}</p></li>'
team += '</ul></div></section>'
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
    enrich(head + card + about + team + rest + "</main></body></html>"), encoding="utf-8"
)
print("built", sum(1 for x in re.finditer('class="job"', card)), "jobs")
