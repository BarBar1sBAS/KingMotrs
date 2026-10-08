# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import json, math

r = Path(__file__).resolve().parents[1]
out = r / "output-v2/pdf/KingMotors-v2.pdf"
out.parent.mkdir(parents=True, exist_ok=True)
for n, w in [("Body", 400), ("Medium", 500), ("Bold", 700)]:
    pdfmetrics.registerFont(TTFont(n, str(r / f"assets/fonts/GolosText-{w}.ttf")))
W, H = 1200, 900
c = canvas.Canvas(str(out), pagesize=(W, H))
c.setTitle("КингМоторс · дизайн-система v2")
c.setAuthor("KingMotors design concept")
page = 0
ink = "#191c1e"
paper = "#f4f4f0"
red = "#ce1616"


def start(title, sub=""):
    global page
    page += 1
    c.setFillColor(HexColor(paper))
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(HexColor(red))
    c.rect(50, H - 49, 32, 3, fill=1, stroke=0)
    c.setFillColor(HexColor(ink))
    c.setFont("Bold", 30)
    c.drawString(50, H - 95, title)
    c.setFont("Body", 13)
    c.setFillColor(HexColor("#626865"))
    c.drawString(50, H - 122, sub)
    c.setFont("Body", 11)
    c.drawString(50, 28, "КИНГМОТОРС / КОНЦЕПЦИЯ V2 / 08.10.2026")
    c.drawRightString(W - 50, 28, f"{page:02d}")


def para(txt, x, y, w=1050, size=19, color=ink):
    st = ParagraphStyle(
        "p",
        fontName="Body",
        fontSize=size,
        leading=size * 1.48,
        textColor=HexColor(color),
        spaceAfter=16,
    )
    p = Paragraph(txt, st)
    pw, ph = p.wrap(w, H)
    p.drawOn(c, x, y - ph)
    return y - ph - 22


def textpage(title, blocks, sub=""):
    start(title, sub)
    y = H - 175
    for h, t in blocks:
        c.setFillColor(HexColor(ink))
        c.setFont("Bold", 23)
        c.drawString(50, y, h)
        y -= 16
        y = para(t, 50, y, size=18)
    assert y > 45, (title, y)
    c.showPage()


def imgfit(im, x, y, w, h):
    iw, ih = im.size
    sc = min(w / iw, h / ih)
    dw, dh = iw * sc, ih * sc
    c.drawImage(ImageReader(im), x, y + h - dh, width=dw, height=dh)


def safe_parts(im, limit):
    from PIL import ImageChops

    if im.height <= limit * 1.15:
        return [im]
    count = math.ceil(im.height / limit)
    step = im.height / count
    cuts = [0]
    for n in range(1, count):
        target = int(step * n)
        best = None
        for delta in range(0, 181):
            for y in [target + delta, target - delta]:
                if y <= cuts[-1] + 150 or y >= im.height - 100:
                    continue
                dif = ImageChops.difference(
                    im.crop((0, y - 2, im.width, y - 1)),
                    im.crop((0, y + 2, im.width, y + 3)),
                )
                changed = sum(1 for pix in dif.getdata() if max(pix) > 12)
                # A flat row inside a red CTA is not whitespace between blocks.
                red = sum(
                    r > 100 and r > g * 1.3 and r > b * 1.3
                    for r, g, b in im.crop((0, y, im.width, y + 1)).getdata()
                )
                if changed < im.width * 0.005 and red < im.width * 0.02:
                    best = y
                    break
            if best is not None:
                break
        cuts.append(best or target)
    cuts.append(im.height)
    return [im.crop((0, a, im.width, b)) for a, b in zip(cuts, cuts[1:])]


def screenshot(title, file, sub="Браузерный экспорт Chromium · фактическая компоновка"):
    global H
    im = Image.open(r / "output-v2/mockups" / file).convert("RGB")
    parts = safe_parts(im, 1250)
    for idx, crop in enumerate(parts):
        H = max(900, math.ceil(crop.height * 1100 / crop.width + 225))
        c.setPageSize((W, H))
        start(title + (f" · фрагмент {idx+1}" if len(parts) > 1 else ""), sub)
        imgfit(crop, 50, 65, 1100, H - 215)
        c.showPage()
    H = 900
    c.setPageSize((W, H))


start("КингМоторс · статическая v2", "Финальное ревью и упрощение кода · 08.10.2026")
im = Image.open(r / "output-v2/mockups/top-1440.png")
imgfit(im, 50, 130, 1100, 600)
para("Ремонт и обслуживание без несогласованных работ", 50, 110, size=23)
c.showPage()
textpage(
    "Что изменилось",
    [
        (
            "Код и сборка",
            "Исправлены возврат из услуг и сохранение URL при уходе со страницы. Удалены перекрытые CSS-объявления, неиспользуемые стили и повторные обработчики. Кнопка повторного интро убрана; основная анимация сохранена. Новых зависимостей нет.",
        ),
        (
            "Содержание и ритм",
            "Шесть направлений и три шага согласования ремонта. После описания сервиса добавлена команда из пяти демо-сотрудников. Имена, должности и портреты явно обозначены как вымышленные. Семь отзывов сохранены дословно.",
        ),
        (
            "Рамки",
            "Демонстрационный сайт: noindex, без отправки данных. Публикация не выполнена. Сохранены SVG, фирменный красный, Manrope/Golos, 48 источников и 33 работы. Сгенерированные изображения не являются фотографиями реальных сотрудников или помещения.",
        ),
    ],
)
textpage(
    "Система и адаптация",
    [
        (
            "Фирменная основа",
            "Графит #191C1E, светлая поверхность #F4F4F0, исходный красный #E51313. Кнопки #CE1616. Общие цвета, интервалы и длительности находятся в prototype/tokens.css.",
        ),
        (
            "Компоновка",
            "Контейнер до 1328 px. Desktop: две крупные услуги 7/5 и четыре компактные. Tablet: сетка услуг 2×3; до 1024 px основной отзыв над двумя дополнительными. Mobile: крупные услуги по одной, остальные по две, содержательные секции в одну колонку.",
        ),
        (
            "Типографика",
            "Hero 44–60 px на desktop и 30–50 px на mobile. Длинный согласованный заголовок переносится свободно, без обрезки. Поля 18–24 px на мобильном. Высота текстовых блоков определяется содержимым.",
        ),
    ],
)
for title, name in [
    ("Первый экран · 1440", "top-1440.png"),
    ("Услуги · 1440", "services-1440.png"),
    ("Порядок работы · 1440", "about-1440.png"),
    ("Наша команда · 1440", "team-1440.png"),
    ("Отзывы · 1440", "reviews-1440.png"),
    ("Запись · 1440", "booking-1440.png"),
    ("Яндекс Карта · 1440", "location-1440.png"),
    ("Модальное окно · 1440", "service-expanded-1440.png"),
]:
    screenshot(title, name)
for size in [390, 768]:
    im = Image.open(r / f"output-v2/mockups/home-{size}.png").convert("RGB")
    chunk = 1000 if size == 390 else 950
    cols = 3 if size == 390 else 2
    tilew = 340 if size == 390 else 535
    parts = safe_parts(im, chunk)
    for i in range(0, len(parts), cols):
        H = 1100
        c.setPageSize((W, H))
        start(
            f"Главная · {size}px · {i//cols+1}",
            "Браузерные фрагменты сверху вниз, слева направо. Полный PNG в комплекте.",
        )
        for j, part in enumerate(parts[i : i + cols]):
            imgfit(part, 50 + j * (tilew + 25), 65, tilew, 890)
        c.showPage()
for size in [390, 768]:
    screenshot(f"Модальное окно · {size}", f"service-expanded-{size}.png")
screenshot("Компоненты и состояния", "components-1440.png")
textpage(
    "Animate · постановка движения",
    [
        (
            "Первый экран",
            "Общая сцена 820 мс: фотография приближается к конечному масштабу, заголовок появляется смысловыми группами, затем пояснение. Красная линия раскрывается слева направо. Телефон и запись доступны сразу. SVG сохранён.",
        ),
        (
            "Прокрутка и интерфейс",
            "Маски фотографий 600 мс, шаги и отзывы 420 мс; интервалы 60/80 мс. Модалка 280/240 мс, меню 220/180 мс, высота аккордеонов 240 мс. Переходы по меню используют плавную нативную прокрутку. CSS transitions и WAAPI без новых библиотек. Тонкие красные линии соединяют номера шагов.",
        ),
        (
            "Доступность и отмена",
            "Сцены однократные, содержимое видно без JavaScript. Клавиатура, Escape, hash и запись работают сразу. Reduced motion отменяет движение; повторное действие разворачивает переход. Существующие записи движения сохранены как материалы предыдущего этапа.",
        ),
    ],
)
textpage(
    "Проверка и ограничения",
    [
        (
            "Браузерная проверка",
            "12 ширин от 320 до 1920 px, в том числе промежуточные. Закрытая страница, модальное окно, text200%. Все 33 работы, прямые ссылки, клавиатура, возврат фокуса, no-JS, storage denial, reduced motion и состояния формы.",
        ),
        (
            "Визуальное ревью",
            "84 контрольных браузерных кадра основных разделов и модалки на 12 ширинах совпали пиксель в пиксель до и после очистки. Из футера удалена кнопка повторного интро. Это контроль регрессий, а не доказательство художественного качества. Ревью выполнено автором доработки.",
        ),
        (
            "Граница проверки",
            "Проверен локальный Chromium. Safari/Firefox, реальные устройства, screen reader и Core Web Vitals отдельно не проверялись. Форма ничего не отправляет. Юридические сведения, условия, часы и права на изображения требуют подтверждения перед публикацией.",
        ),
    ],
)
c.save()
print(out, "pages", page)
