"""SEO from the rendered HTML. The local concept always remains noindex."""

import csv
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://kingmotors52.ru/"
TITLE = "Автосервис в Нижнем Новгороде — ремонт и ТО | КингМоторс"
DESCRIPTION = "КингМоторс: ремонт, диагностика и обслуживание автомобилей в Нижнем Новгороде. Согласуем работы и стоимость до ремонта. Московское шоссе, 12А. Запись по телефону."


def enrich(html):
    soup = BeautifulSoup(html, "html.parser")
    business_id = SITE + "#organization"
    services = []
    for node in soup.select(".service-card, .job"):
        job = "job" in node.get("class", [])
        services.append(
            {
                "@type": "Service",
                "@id": SITE + "#" + node["id"],
                "url": SITE + "#" + node["id"],
                "name": node.select_one(":scope > summary" if job else "h3").get_text(
                    " ", strip=True
                ),
                "description": node.select_one(
                    ".job-body > p" if job else ".service-intro"
                ).get_text(" ", strip=True),
                "provider": {"@id": business_id},
                "areaServed": {"@type": "City", "name": "Нижний Новгород"},
            }
        )
    questions = []
    for node in soup.select(".faq-list details"):
        answer = node.select_one(":scope > p")
        if answer:
            questions.append(
                {
                    "@type": "Question",
                    "name": node.select_one(":scope > summary").get_text(
                        " ", strip=True
                    ),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": answer.get_text(" ", strip=True),
                    },
                }
            )
    graph = [
        {
            "@type": "AutoRepair",
            "@id": business_id,
            "name": "КингМоторс",
            "url": SITE,
            "telephone": soup.select_one(".contact-phone")["href"].removeprefix("tel:"),
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Московское шоссе, 12А",
                "addressLocality": "Нижний Новгород",
                "addressCountry": "RU",
            },
            "logo": SITE + "assets/logo.svg",
        },
        {
            "@type": "WebSite",
            "@id": SITE + "#website",
            "url": SITE,
            "name": "КингМоторс",
            "inLanguage": "ru-RU",
            "publisher": {"@id": business_id},
        },
        {
            "@type": ["WebPage", "FAQPage"],
            "@id": SITE + "#webpage",
            "url": SITE,
            "name": TITLE,
            "description": DESCRIPTION,
            "inLanguage": "ru-RU",
            "isPartOf": {"@id": SITE + "#website"},
            "about": {"@id": business_id},
            "mainEntity": questions,
        },
        *services,
    ]
    metadata = "\n".join(
        [
            f'<meta name="description" content="{escape(DESCRIPTION, quote=True)}">',
            f'<link rel="canonical" href="{SITE}">',
            '<meta property="og:type" content="website">',
            '<meta property="og:locale" content="ru_RU">',
            '<meta property="og:site_name" content="КингМоторс">',
            f'<meta property="og:title" content="{escape(TITLE, quote=True)}">',
            f'<meta property="og:description" content="{escape(DESCRIPTION, quote=True)}">',
            f'<meta property="og:url" content="{SITE}">',
            '<meta name="twitter:card" content="summary">',
            '<script type="application/ld+json">'
            + json.dumps(
                {"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False
            ).replace("<", "\\u003c")
            + "</script>",
        ]
    )
    html = re.sub(
        r"<title>.*?</title>", "<title>" + escape(TITLE) + "</title>", html, count=1
    )
    html = html.replace("</head>", metadata + "\n</head>", 1)
    build_launch_files(soup, services)
    return html


def build_launch_files(soup, services):
    # These are reviewable launch candidates, deliberately outside the served prototype.
    out = ROOT / "docs-v2/seo-launch"
    out.mkdir(exist_ok=True)
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{SITE}</loc></url>\n</urlset>\n",
        encoding="utf-8",
    )
    (out / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + SITE + "sitemap.xml\n",
        encoding="utf-8",
    )
    links = "\n".join(
        f'- [{x["name"]}]({x["url"]}): {x["description"]}' for x in services
    )
    (out / "llms.txt").write_text(
        "# КингМоторс\n\n"
        "> Автосервис в Нижнем Новгороде, Московское шоссе, 12А.\n\n"
        "## Сведения\n\nИсточник: содержание официального сайта. Стоимость и состав работ "
        "согласуются индивидуально. Исторические цены не являются действующим прайсом. "
        "Иллюстрации концепции не документируют реальное помещение или сотрудников.\n\n"
        "## Услуги и работы\n\n" + links + "\n\n## Контакты\n\n"
        f"- [Контакты и телефон]({SITE}#contacts)\n- [Вопросы перед визитом]({SITE}#faq)\n",
        encoding="utf-8",
    )
    rows = re.findall(
        r"\| (https://kingmotors52\.ru/[^ ]*) \| ([^ |]+) \|",
        (ROOT / "docs-v2/content-map.md").read_text(encoding="utf-8"),
    )
    assert len(rows) == 48
    with (out / "redirects.csv").open("w") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target", "status", "note"])
        for url, target in rows:
            path = urlsplit(url).path
            dest = "/" + target
            if target.startswith("#"):
                assert soup.find(id=target[1:]), target
            writer.writerow(
                [
                    path,
                    "/" if path == "/" else dest,
                    200 if path == "/" else 301,
                    (
                        "keep root"
                        if path == "/"
                        else (
                            "legal document approval required"
                            if target == "legal.html"
                            else "launch candidate"
                        )
                    ),
                ]
            )
    with (ROOT / "docs-v2/seo-content-inventory.csv").open("w") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "url",
                "topic",
                "answer_from_html",
                "status",
                "search_impressions",
                "search_clicks",
            ]
        )
        for item in services:
            writer.writerow(
                [
                    item["url"],
                    item["name"],
                    item["description"],
                    "local draft",
                    "unavailable",
                    "unavailable",
                ]
            )
