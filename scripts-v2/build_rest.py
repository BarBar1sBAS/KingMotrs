# -*- coding: utf-8 -*-
from pathlib import Path
from bs4 import BeautifulSoup
from html import escape as e
import json

r = Path(__file__).resolve().parents[1]
data = json.loads((r / "docs-v2/site-content.json").read_text(encoding="utf-8"))
s = BeautifulSoup(
    (r / "sources/pages/home.html").read_text(encoding="utf-8"), "html.parser"
)
reviews = [
    (
        x.select_one("strong").get_text(strip=True),
        x.select_one("small").get_text(strip=True),
        x.select_one(".review_text").get_text(" ", strip=True),
    )
    for x in s.select(".review_items .review")
]


# The owner chose the previous site's composition, using the current v2 design.
# Yandex owns the live widget; these seven cards are the preserved site selection.
review_cards = "".join(
    f'<article class="review-card"><header><h3>{e(reviews[i][0])}</h3><p>{e(reviews[i][1])}</p></header><blockquote>{e(reviews[i][2])}</blockquote></article>'
    for i in [2, 5, 4, 3, 1, 6, 0]
)
html = f"""<section class="section" id="reviews"><div class="wrap"><div class="section-head reviews-head"><div><h2>Отзывы об автосервисе КингМоторс</h2><a class="text-link" href="https://yandex.ru/maps/org/kingmotors/13496778418/reviews/" target="_blank" rel="noopener noreferrer">Все отзывы на Яндекс Картах ↗</a></div></div><div class="reviews-showcase"><div class="reviews-widget"><iframe src="https://yandex.ru/maps-reviews-widget/13496778418?comments" title="Отзывы о КингМоторс на Яндекс Картах" width="760" height="600" loading="lazy" referrerpolicy="strict-origin-when-cross-origin"></iframe></div><div class="reviews-selection"><div class="reviews-controls" hidden><span class="reviews-position" aria-hidden="true">1 / 7</span><button type="button" class="reviews-prev" aria-label="Предыдущий отзыв" aria-controls="review-cards" disabled><span aria-hidden="true">←</span></button><button type="button" class="reviews-next" aria-label="Следующий отзыв" aria-controls="review-cards"><span aria-hidden="true">→</span></button></div><div class="reviews-rail" id="review-cards" role="region" aria-label="Подборка из семи отзывов клиентов, прокручивается горизонтально" tabindex="0">{review_cards}</div><p class="reviews-source">Подборка отзывов с сайта КингМоторс</p></div></div></div></section>"""

faqs = data["faqs"]


def faq(items):
    return "".join(
        f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items
    )


html += f"""<section class="section faq-section" id="faq"><div class="wrap"><div class="faq-layout"><div class="faq-intro"><h2>Частые вопросы о ремонте</h2><p>Цена, сроки, запись</p></div><div class="faq-list">{faq(faqs[:7])}<details class="extra-topics"><summary>Вопросы об автомобиле</summary><div>{faq(faqs[7:])}</div></details></div></div><div class="business-careers"><details class="secondary-panel" id="business"><summary><div><h3>Для вашего автопарка</h3><p class="teaser">Обслуживание корпоративных автомобилей</p></div></summary><div class="body"><p>Обсудим состав автопарка, необходимые работы, документооборот и порядок оплаты. Условия сотрудничества согласовываются индивидуально.</p><p>Контакт для корпоративных клиентов: <a href="tel:+79696029835">+7 969 602 98 35</a>.</p><a class="text-link" href="#booking" data-service="Корпоративное обслуживание">Обсудить сотрудничество ↗</a></div></details><details class="secondary-panel" id="careers"><summary><div><h3>Работа в КингМоторс</h3><p class="teaser">Мастер-приёмщик</p></div></summary><div class="body"><p>Вакансия мастера-приёмщика: общение с клиентами, оформление заказов и организация обслуживания. Актуальность вакансии и условия уточните у сервиса.</p><a class="text-link" href="mailto:kingmotors152@yandex.ru">Отправить резюме ↗</a></div></details></div></div></section>
<section class="booking dark" id="booking"><div class="wrap booking-grid"><div><h2>Обсудим ваш автомобиль.</h2><p class="booking-lead">Позвоните: обсудим задачу и согласуем время визита.</p><div id="contacts" class="contact-list"><a class="contact-phone" href="tel:+79063664911">8 906 366 49 11</a><p class="contact-address">Нижний Новгород,<br>Московское шоссе, 12А</p><p class="contact-hours">Пн–Пт 9:00–19:00. Сб–Вс — выходные</p><a class="text-link contact-route" href="#location">Посмотреть на карте ↓</a></div></div><form class="booking-form" id="booking-form" novalidate><h3>Записаться в сервис</h3><p class="demo-notice">Демонстрация формы. Данные никуда не отправляются. Для записи позвоните в сервис.</p><div class="form-context" hidden><span></span><button type="button" id="clear-service">Убрать</button></div><label class="field" for="phone"><span>Телефон *</span><input id="phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 999 123 45 67" required aria-describedby="phone-error"><small class="error" id="phone-error" hidden>Введите номер: 11 цифр, начинается с 7 или 8.</small></label><label class="field" for="name"><span>Имя · необязательно</span><input id="name" name="name" autocomplete="given-name" maxlength="80"></label><label class="field" for="request"><span>Что нужно сделать? · необязательно</span><textarea id="request" name="request" rows="3" maxlength="1500" placeholder="Марка, модель и что беспокоит"></textarea></label><label class="consent"><input type="checkbox" id="consent" required aria-describedby="consent-error"><span>Согласен на обработку персональных данных. <a href="legal.html">Политика и согласие</a></span></label><small id="consent-error" class="error" hidden>Для демонстрации отправки отметьте согласие.</small><button type="submit" class="btn" disabled>Проверить форму <span class="arrow" aria-hidden="true">↗</span></button><div class="form-message" role="status" aria-live="polite" hidden></div><noscript><p>Демонстрация формы работает с JavaScript. Для записи: 8 906 366 49 11.</p></noscript><details class="demo-states"><summary>Посмотреть состояния формы</summary><div class="demo-buttons"><button type="button" data-demo="sending">Отправка</button><button type="button" data-demo="success">Успех</button><button type="button" data-demo="error">Ошибка</button><button type="button" data-demo="idle">Сброс</button></div></details></form></div></section>
<section class="location-section" id="location" aria-labelledby="location-title"><div class="wrap"><div class="location-layout"><div class="location-copy"><h2 id="location-title">Как добраться</h2><p class="location-address">Нижний Новгород,<br><strong>Московское шоссе, 12А</strong></p><p class="location-hours"><span class="location-dot" aria-hidden="true"></span>Пн–Пт 9:00–19:00. Сб–Вс — выходные</p><a class="btn" href="https://yandex.ru/maps/?rtext=~56.317015,43.927428" target="_blank" rel="noopener noreferrer">Построить маршрут <span class="arrow" aria-hidden="true">↗</span></a><a class="location-phone" href="tel:+79063664911">8 906 366 49 11</a><p class="location-help">Позвоните, если нужна помощь с&nbsp;дорогой.</p></div><div class="location-map"><iframe src="https://yandex.ru/map-widget/v1/?ll=43.927428%2C56.317015&amp;z=16&amp;pt=43.927428%2C56.317015%2Cpm2rdm" title="КингМоторс на Яндекс Картах — Московское шоссе, 12А" width="900" height="480" loading="lazy" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe><div class="location-map-caption"><span>КингМоторс · Московское шоссе, 12А</span><a href="https://yandex.ru/maps/org/kingmotors/13496778418/" target="_blank" rel="noopener noreferrer">Открыть в Яндекс Картах ↗</a></div></div></div></div></section>
<footer class="footer"><div class="wrap"><div class="footer-top"><a href="#top"><img class="footer-logo" src="assets/logo.svg" alt="КингМоторс" width="168" height="48"></a><div class="footer-links"><a href="#services">Услуги</a><a href="#business">Бизнесу</a><a href="#careers">Вакансии</a><a href="legal.html">Правовая информация</a></div></div><div class="footer-bottom"><p>КингМоторс · Нижний Новгород</p><p>Локальная дизайн-концепция. Не принимает заявки.</p></div></div></footer>"""
links = "".join(
    f'<a href="#detail-{x["slug"]}">{e(x["title"])}</a>' for x in data["jobs"]
)
html = html.replace(
    '<div class="footer-bottom">',
    f'<details class="sitemap" id="sitemap"><summary>Все работы сервиса</summary><div class="sitemap-links">{links}</div></details><div class="footer-bottom">',
)
(r / "output-v2/build").mkdir(parents=True, exist_ok=True)
(r / "output-v2/build/rest.html").write_text(html, encoding="utf-8")
print("reviews", len(reviews))
