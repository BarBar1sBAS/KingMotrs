"""Verify the actual local HTTP responses, content preservation and launch map."""

import csv
import json
import subprocess
import os
from pathlib import Path
from xml.etree import ElementTree
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8765")
SITE = "https://kingmotors52.ru/"


def fetch(path):
    from urllib.request import urlopen
    from urllib.error import HTTPError

    try:
        response = urlopen(BASE + path, timeout=15)
    except HTTPError as error:
        response = error
    with response:
        body = response.read()
        if response.headers.get_content_type().startswith("text/"):
            body = body.decode("utf-8")
        return body, response.status


html, status = fetch("/")
assert status == 200
soup = BeautifulSoup(html, "html.parser")
assert len(soup.select("h1")) == 1
assert len(soup.select(".service-card")) == 6
assert len(soup.select(".job")) == 32
assert soup.select_one('meta[name="robots"]')["content"] == "noindex,nofollow"
assert soup.select_one('link[rel="canonical"]')["href"] == SITE
assert 100 <= len(soup.select_one('meta[name="description"]')["content"]) <= 180
ids = [x["id"] for x in soup.select("[id]")]
assert len(ids) == len(set(ids))
for a in soup.select('a[href^="#"]'):
    assert a["href"][1:] in ids, a["href"]
for img in soup.select("img"):
    assert all(img.has_attr(a) for a in ["alt", "width", "height"])
graph = json.loads(soup.select_one('script[type="application/ld+json"]').string)[
    "@graph"
]
services = [x for x in graph if x["@type"] == "Service"]
assert len(services) == 38
for service in services:
    target = soup.find(id=service["url"].split("#")[1])
    assert service["name"] in target.get_text(" ", strip=True)
    assert service["description"] in target.get_text(" ", strip=True)
questions = next(x["mainEntity"] for x in graph if isinstance(x["@type"], list))
assert len(questions) == 17
for q in questions:
    assert q["name"] in soup.select_one(".faq-list").get_text(" ", strip=True)
    assert q["acceptedAnswer"]["text"] in soup.select_one(".faq-list").get_text(
        " ", strip=True
    )
assert not any(
    key in html for key in ['"aggregateRating"', '"priceRange"', '"openingHours"']
)
# Owner-approved editorial contract, distinct from archived source counts.
content = json.loads((ROOT / "docs-v2/site-content.json").read_text(encoding="utf-8"))
assert len(json.loads((ROOT / "sources/inventory.json").read_text())) == 48
assert len(content["jobs"]) == len({j["slug"] for j in content["jobs"]}) == 32
assert [card["id"] for card in soup.select(".service-card")] == [
    "service-repair", "service-suspension", "service-transmission",
    "service-diagnostics", "service-maintenance", "service-other",
]
assert [len(card.select(".job")) for card in soup.select(".service-card")] == [4, 9, 4, 4, 6, 5]
for job in content["jobs"]:
    node = soup.find(id="detail-" + job["slug"])
    assert node.find_parent(class_="service-card")["id"] == "service-" + job["group"]
    assert node.select_one(".price-note").get_text() == job["price_note"]
    assert node.select_one(".job-body > p").get_text() == job["intro"]
assert [q["name"] for q in questions] == [q for q, _ in content["faqs"]]
assert [q["acceptedAnswer"]["text"] for q in questions] == [a for _, a in content["faqs"]]
assert len(soup.select(".service-steps > li")) == 4
for selector in [".arrival", ".contact-hours", ".location-hours"]:
    assert content["hours"] in soup.select_one(selector).get_text()
assert content["offer"] == soup.select_one(".hero-offer").get_text()
assert not soup.select('.job#detail-besplatnaya-diagnostika-avtomobilya')
assert not soup.select('.service-card#service-wash')
assert not soup.select('img[src*="wash.webp"]')
assert not soup.select('.sitemap-links a[href="#detail-besplatnaya-diagnostika-avtomobilya"]')
assert not any(x in soup.body.get_text() for x in ['[уточнить', 'На сайте сервиса заявлена', 'На действующем сайте', 'Ежедневно'])
assert soup.select_one('.booking-form [type="submit"]').has_attr("disabled")
assert 'Данные никуда не отправляются' in soup.select_one('.demo-notice').get_text()
assert len(soup.select('.hero-caption, .about-image small')) == 2
hours = next(x for x in graph if x['@type'] == 'AutoRepair')['openingHoursSpecification']
assert hours == [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "09:00", "closes": "19:00"}]
assert [x.h3.get_text() for x in soup.select('.review-card')[:3]] == ['Артем П.', 'Евгений', 'Дмитрий Заграй']

original = BeautifulSoup(
    (ROOT / "sources/pages/home.html").read_text(encoding="utf-8"), "html.parser"
)
reviews = original.select(".review_items .review")
assert len(reviews) == len(soup.select(".review-card")) == 7
for review in reviews:
    author = review.select_one("strong").get_text(strip=True)
    card = next(card for card in soup.select(".review-card") if card.h3.get_text(strip=True) == author)
    assert card.blockquote.get_text(" ", strip=True) == review.select_one(".review_text").get_text(" ", strip=True)
    assert card.select_one("header p").get_text(strip=True) == review.select_one("small").get_text(strip=True)
assert soup.select_one("#reviews iframe")["src"] == "https://yandex.ru/maps-reviews-widget/13496778418?comments"
legal, legal_status = fetch("/legal.html")
assert legal_status == 200
assert (
    "noindex"
    in BeautifulSoup(legal, "html.parser").select_one('meta[name="robots"]')["content"]
)
components, components_status = fetch("/components.html")
assert components_status == 404
assert fetch("/rest.html")[1] == 404
assert fetch("/seo-not-found-check")[1] == 404
assert fetch("/sitemap.xml")[1] == 404  # No public launch artifacts on the concept.
assert fetch("/llms.txt")[1] == 404
assert fetch("/robots.txt")[1] == 200
rows = list(csv.DictReader((ROOT / "docs-v2/seo-launch/redirects.csv").open()))
assert len(rows) == 48
assert rows[0]["source"] == rows[0]["target"] == "/" and rows[0]["status"] == "200"
for row in rows[1:]:
    assert row["source"] != row["target"] and row["status"] == "301"
    if "#" in row["target"]:
        assert row["target"].split("#")[1] in ids
xml = ElementTree.parse(ROOT / "docs-v2/seo-launch/sitemap.xml")
assert [n.text for n in xml.findall(".//{*}loc")] == [SITE]
result = {
    "checked_at": __import__("datetime")
    .datetime.now(__import__("datetime").timezone.utc)
    .isoformat(),
    "transport": "urllib; no JavaScript",
    "root_status": status,
    "h1": 1,
    "groups": 6,
    "jobs": 32,
    "reviews_exact": 7,
    "official_reviews_widget": True,
    "faq_matches_html": 17,
    "services_match_html": 38,
    "source_routes": 48,
    "launch_redirect_candidates": 47,
    "prototype_noindex": True,
    "legal_noindex": True,
    "removed_fragment_status": 404,
    "unknown_url_status": 404,
    "launch_sitemap_urls": 1,
    "broken_anchors": 0,
    "live_rankings_measured": False,
}
(ROOT / "docs-v2/seo-checks.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps(result, ensure_ascii=False))

# Validate only public resources; no sources, reviews or original PNGs escape into dist.
from package import PUBLIC_FILES
from hashlib import sha256
from tempfile import TemporaryDirectory
import shutil
import sys
import re
import zipfile
from fontTools.ttLib import TTFont

actual = sorted(
    p.relative_to(ROOT / "dist").as_posix()
    for p in (ROOT / "dist").rglob("*")
    if p.is_file()
)
assert actual == sorted(PUBLIC_FILES)
for name in PUBLIC_FILES:
    assert fetch("/" + name)[1] == 200, name
for path in [
    "/sources/inventory.json",
    "/review/text200-320.png",
    "/assets/hero.png",
    "/assets/brakes.webp",
    "/app.js.map",
]:
    assert fetch(path)[1] == 404, path
for filename in ["index.html", "legal.html"]:
    document = BeautifulSoup(
        (ROOT / "dist" / filename).read_text(encoding="utf-8"), "html.parser"
    )
    for element in document.select("[src], link[href]"):
        url = element.get("src") or element.get("href")
        if not url.startswith(("http:", "https:", "data:", "#")):
            assert url in PUBLIC_FILES, (filename, url)
logo = (ROOT / "dist/assets/logo.svg").read_text(encoding="utf-8")
original_logo = (ROOT / "prototype/assets/logo-original.svg").read_text(
    encoding="utf-8"
)
assert re.findall(r'<path\b[^>]*\bd="([^"]+)"', logo) == re.findall(
    r'<path\b[^>]*\bd="([^"]+)"', original_logo
)
for name in ["Manrope-Variable.ttf", "GolosText-Variable.ttf"]:
    with TTFont(ROOT / "dist/assets" / name) as font:
        cmap = font.getBestCmap()
        assert all(
            ord(c) in cmap
            for c in "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        )


def hashes(folder):
    return {
        p.relative_to(folder).as_posix(): sha256(p.read_bytes()).hexdigest()
        for p in folder.rglob("*")
        if p.is_file()
    }


source_hashes = hashes(ROOT / "sources")
expected = hashes(ROOT / "dist")
zip_path = ROOT / "output-v2/KingMotors-static.zip"
with zipfile.ZipFile(zip_path) as archive:
    assert sorted(archive.namelist()) == sorted(PUBLIC_FILES)
    for name in PUBLIC_FILES:
        assert archive.read(name) == (ROOT / "dist" / name).read_bytes()
with TemporaryDirectory(prefix="kingmotors-build-") as directory:
    clean = Path(directory)
    for folder in ["sources", "scripts-v2", "prototype"]:
        shutil.copytree(
            ROOT / folder, clean / folder, ignore=shutil.ignore_patterns("__pycache__")
        )
    for name in ["index.html", "legal.html"]:
        (clean / "prototype" / name).unlink()
    (clean / "docs").mkdir()
    (clean / "docs-v2").mkdir()
    shutil.copyfile(ROOT / "docs/page-copy.md", clean / "docs/page-copy.md")
    shutil.copyfile(ROOT / "docs-v2/content-map.md", clean / "docs-v2/content-map.md")
    shutil.copyfile(ROOT / "docs-v2/site-content.json", clean / "docs-v2/site-content.json")
    for repeat in range(2):
        for script in ["build_rest", "build_prototype", "build_legal", "package"]:
            subprocess.run(
                [sys.executable, str(clean / "scripts-v2" / (script + ".py"))],
                check=True,
                capture_output=True,
            )
        assert hashes(clean / "dist") == expected, "Clean build changed public content"
        assert (
            clean / "output-v2/KingMotors-static.zip"
        ).read_bytes() == zip_path.read_bytes(), "ZIP is not reproducible"
    assert hashes(clean / "sources") == source_hashes
assert hashes(ROOT / "sources") == source_hashes
result.update(
    {
        "public_files": len(PUBLIC_FILES),
        "clean_build_repeats": 2,
        "reproducible_zip": True,
        "sources_unchanged": True,
        "svg_paths_unchanged": True,
        "fonts_cyrillic": True,
    }
)
(ROOT / "docs-v2/seo-checks.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(
    "Static package: allowlist, HTTP, sources, logo, fonts and reproducible clean build passed."
)
