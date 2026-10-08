# -*- coding: utf-8 -*-
from pathlib import Path
from bs4 import BeautifulSoup
from html import escape as e
import json

r = Path(__file__).resolve().parents[1]
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


def author(x):
    return f'<div class="attribution"><span class="avatar" aria-hidden="true">{e(x[0][0])}</span><div><strong>{e(x[0])}</strong><small>{e(x[1])} · с сайта КингМоторс</small></div></div>'


def review(x):
    return f'<article class="review-item"><p>{e(x[2])}</p>{author(x)}</article>'


featured = reviews[4]
html = f"""<section class="section" id="reviews"><div class="wrap"><div class="section-head reviews-head"><h2>Клиенты о КингМоторс.</h2><a class="text-link" href="https://yandex.ru/maps/org/kingmotors/13496778418/reviews/" target="_blank" rel="noopener">Отзывы на Яндекс Картах ↗</a></div><div class="reviews-layout"><article class="featured-quote"><div class="quote-mark" aria-hidden="true">“</div><blockquote>{e(featured[2])}</blockquote>{author(featured)}</article><div class="review-stack">{review(reviews[3])}{review(reviews[2])}</div></div><details class="review-more"><summary>Ещё 4 отзыва</summary><div class="all-reviews">{''.join(review(reviews[i]) for i in [0,1,5,6])}</div></details></div></section>"""
faqs = [
    (
        "Сколько стоит диагностика?",
        "Стоимость зависит от нужных проверок и автомобиля. Объём и условия уточнит сотрудник при записи.",
    ),
    (
        "Как проходит запись?",
        "Оставьте телефон и опишите задачу. Сотрудник свяжется с вами, уточнит автомобиль и согласует время. Заявка сама по себе не подтверждает запись.",
    ),
    (
        "Можно подобрать запчасти в сервисе?",
        "Да, подбираем оригинальные комплектующие и подходящие аналоги. Подготовьте VIN, марку и модель автомобиля.",
    ),
    (
        "Есть ли гарантия на ремонт?",
        "На сайте сервиса заявлена гарантия на работы и запчасти. Условия для конкретной работы уточните при согласовании ремонта.",
    ),
    (
        "Когда нужна компьютерная диагностика?",
        "Если появились ошибки на панели или изменилось поведение двигателя, расскажите об этом при записи. Специалист определит подходящие проверки.",
    ),
    (
        "Почему стучит подвеска?",
        "Причин может быть несколько. Проверка ходовой части помогает определить источник стука.",
    ),
    (
        "Как проверить тормоза?",
        "При скрипе, вибрации или изменениях торможения нужна проверка состояния системы.",
    ),
    (
        "Когда менять масло?",
        "Ориентируйтесь на регламент производителя и условия эксплуатации. Сообщите модель, пробег и дату последнего обслуживания.",
    ),
    (
        "Почему кондиционер плохо охлаждает?",
        "Причина определяется после диагностики. Перечень работ и стоимость зависят от результата проверки.",
    ),
]


def faq(items):
    return "".join(
        f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items
    )


html += f"""<section class="section faq-section" id="faq"><div class="wrap"><div class="faq-layout"><div class="faq-intro"><h2>Перед визитом.</h2><p>Стоимость, запись, запчасти и гарантия.</p></div><div class="faq-list">{faq(faqs[:4])}<details class="extra-topics"><summary>Вопросы об автомобиле</summary><div>{faq(faqs[4:])}</div></details></div></div><div class="business-careers"><details class="secondary-panel" id="business"><summary><div><h3>Для вашего автопарка</h3><p class="teaser">Обслуживание корпоративных автомобилей</p></div></summary><div class="body"><p>Обсудим состав автопарка, необходимые работы, документооборот и порядок оплаты. Условия сотрудничества согласовываются индивидуально.</p><p>Контакт для корпоративных клиентов: <a href="tel:+79696029835">+7 969 602 98 35</a>.</p><a class="text-link" href="#booking" data-service="Корпоративное обслуживание">Обсудить сотрудничество ↗</a></div></details><details class="secondary-panel" id="careers"><summary><div><h3>Работа в КингМоторс</h3><p class="teaser">Мастер-приёмщик</p></div></summary><div class="body"><p>На действующем сайте открыта вакансия мастера-приёмщика: общение с клиентами, оформление заказов и организация обслуживания. Актуальность вакансии и условия уточните у сервиса.</p><a class="text-link" href="mailto:kingmotors152@yandex.ru">Отправить резюме ↗</a></div></details></div></div></section>
<section class="booking dark" id="booking"><div class="wrap booking-grid"><div><h2>Обсудим ваш автомобиль.</h2><p class="booking-lead">Позвоните: обсудим задачу и согласуем время визита.</p><div id="contacts" class="contact-list"><a class="contact-phone" href="tel:+79063664911">8 906 366 49 11</a><p class="contact-address">Нижний Новгород,<br>Московское шоссе, 12А</p><p class="contact-hours">Ежедневно, 9:00–19:00</p><a class="text-link contact-route" href="#location">Посмотреть на карте ↓</a></div></div><form class="booking-form" id="booking-form" novalidate><h3>Записаться в сервис</h3><p class="demo-notice">Демонстрация формы. Данные никуда не отправляются. Для записи позвоните в сервис.</p><div class="form-context" hidden><span></span><button type="button" id="clear-service">Убрать</button></div><label class="field" for="phone"><span>Телефон *</span><input id="phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 999 123 45 67" required aria-describedby="phone-error"><small class="error" id="phone-error" hidden>Введите номер: 11 цифр, начинается с 7 или 8.</small></label><label class="field" for="name"><span>Имя · необязательно</span><input id="name" name="name" autocomplete="given-name" maxlength="80"></label><label class="field" for="request"><span>Что нужно сделать? · необязательно</span><textarea id="request" name="request" rows="3" maxlength="1500" placeholder="Марка, модель и что беспокоит"></textarea></label><label class="consent"><input type="checkbox" id="consent" required aria-describedby="consent-error"><span>Согласен на обработку персональных данных. <a href="legal.html">Политика и согласие</a></span></label><small id="consent-error" class="error" hidden>Для демонстрации отправки отметьте согласие.</small><button type="submit" class="btn" disabled>Проверить форму <span class="arrow" aria-hidden="true">↗</span></button><div class="form-message" role="status" aria-live="polite" hidden></div><noscript><p>Демонстрация формы работает с JavaScript. Для записи: 8 906 366 49 11.</p></noscript><details class="demo-states"><summary>Посмотреть состояния формы</summary><div class="demo-buttons"><button type="button" data-demo="sending">Отправка</button><button type="button" data-demo="success">Успех</button><button type="button" data-demo="error">Ошибка</button><button type="button" data-demo="idle">Сброс</button></div></details></form></div></section>
<section class="location-section" id="location" aria-labelledby="location-title"><div class="wrap"><div class="location-layout"><div class="location-copy"><h2 id="location-title">Как добраться</h2><p class="location-address">Нижний Новгород,<br><strong>Московское шоссе, 12А</strong></p><p class="location-hours"><span class="location-dot" aria-hidden="true"></span>Ежедневно, 9:00–19:00</p><a class="btn" href="https://yandex.ru/maps/?rtext=~56.317015,43.927428" target="_blank" rel="noopener noreferrer">Построить маршрут <span class="arrow" aria-hidden="true">↗</span></a><a class="location-phone" href="tel:+79063664911">8 906 366 49 11</a><p class="location-help">Позвоните, если нужна помощь с&nbsp;дорогой.</p></div><div class="location-map"><iframe src="https://yandex.ru/map-widget/v1/?ll=43.927428%2C56.317015&amp;z=16&amp;pt=43.927428%2C56.317015%2Cpm2rdm" title="КингМоторс на Яндекс Картах — Московское шоссе, 12А" width="900" height="480" loading="lazy" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe><div class="location-map-caption"><span>КингМоторс · Московское шоссе, 12А</span><a href="https://yandex.ru/maps/org/kingmotors/13496778418/" target="_blank" rel="noopener noreferrer">Открыть в Яндекс Картах ↗</a></div></div></div></div></section>
<footer class="footer"><div class="wrap"><div class="footer-top"><a href="#top"><img class="footer-logo" src="assets/logo.svg" alt="КингМоторс" width="168" height="48"></a><div class="footer-links"><a href="#services">Услуги</a><a href="#business">Бизнесу</a><a href="#careers">Вакансии</a><a href="legal.html">Правовая информация</a></div></div><div class="footer-bottom"><p>КингМоторс · Нижний Новгород</p><p>Локальная дизайн-концепция. Не принимает заявки.</p></div></div></footer>"""
inventory = json.loads((r / "sources/inventory.json").read_text(encoding="utf-8"))
links = "".join(
    f'<a href="#detail-{x["slug"]}">{e(x["h1"][0])}</a>' for x in inventory[15:]
)
html = html.replace(
    '<div class="footer-bottom">',
    f'<details class="sitemap" id="sitemap"><summary>Все работы сервиса</summary><div class="sitemap-links">{links}</div></details><div class="footer-bottom">',
)
(r / "output-v2/build").mkdir(parents=True, exist_ok=True)
(r / "output-v2/build/rest.html").write_text(html, encoding="utf-8")
print("reviews", len(reviews))
