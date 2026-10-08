# Реестр материалов v2

## Демо-команда · 8 октября 2026

Пять отдельных портретов созданы встроенным imagegen. Все персонажи вымышлены, не являются сотрудниками сервиса. На странице видна общая подпись о демо-данных, alt каждого изображения также обозначает демо-портрет. Перед рабочим запуском заменить реальными согласованными фотографиями. Промпты и пути исходников сохранены в `docs-v2/team-image-prompts.json`.

| Локальный WebP | Демо-персонаж |
|---|---|
| prototype/assets/team-smirnov.webp | Алексей Смирнов |
| prototype/assets/team-volkov.webp | Дмитрий Волков |
| prototype/assets/team-morozov.webp | Сергей Морозов |
| prototype/assets/team-sokolov.webp | Андрей Соколов |
| prototype/assets/team-orlov.webp | Максим Орлов |

Единое направление: портрет 4:5, мягкий дневной свет слева, графитовая рабочая одежда без логотипов, нейтральный размытый фон мастерской. Для сайта исходники уменьшены до 640×800 и сохранены в WebP, quality86. Пять локальных файлов включены в dist и ZIP.

V1 с тормозным диском отклонена. В текущем hero автомобиль в процессе обслуживания. Все фотографии — иллюстрации; факт изображённого места и права исходного сайта не подтверждены.

| Файл прототипа | Происхождение | Назначение / замена |
|---|---|---|
| assets/logo.svg | Пользовательский SVG, обрезан только viewBox | Шапка/футер/интро; сохранить path |
| assets/hero.webp | Imagegen, G02 | Автомобиль с открытым капотом; заменить реальным процессом1600×900, текст слева, авто справа |
| assets/process.webp | Imagegen, G03 | Руки с динамометрическим ключом; заменить реальным процессом4:5 без графических оверлеев |
| assets/maintenance.webp | [Исходный сайт](https://kingmotors52.ru/assets/cache_image/img/upload/41/41-177399359147-1773982316xxl1-600x340-38d1_700x396_791.webp) | Иллюстрация направления; согласовать права/заменить съёмкой |
| assets/repair.webp | [Исходный сайт](https://kingmotors52.ru/assets/cache_image/img/upload/42/42-177399356667-1773987778032300181-600x340-38d1_700x396_791.webp) | Иллюстрация направления; согласовать права/заменить съёмкой |
| assets/diagnostics.webp | [Исходный сайт](https://kingmotors52.ru/assets/cache_image/img/upload/43/43-177399353669-177398800426-x3tm7qmaxresdefault67981-600x340-38d1_700x396_791.webp) | Иллюстрация направления; согласовать права/заменить съёмкой |
| assets/parts.webp | [Исходный сайт](https://kingmotors52.ru/assets/cache_image/img/upload/44/44-177399017927-1jwn3s91_700x396_791.webp) | Иллюстрация направления; согласовать права/заменить съёмкой |
| assets/tires.webp | [Исходный сайт](https://kingmotors52.ru/assets/cache_image/img/upload/45/45-177399022127-nyhrv2-qaaage1aua-9601_700x396_791.webp) | Иллюстрация направления; согласовать права/заменить съёмкой |
| assets/wash.webp | [Исходный сайт](https://kingmotors52.ru/assets/cache_image/img/upload/46/46-177399143027-sif8qesrc1_700x396_791.webp) | Иллюстрация направления; согласовать права/заменить съёмкой |

## Генерации
G02: graphite modern unbranded sedan right two-thirds, hood open, cropped mechanic, red lift/tool cabinet, left quiet dark negative space, realistic workshop daylight. Без текста, номеров, неона, дыма и узнаваемого бизнеса. Исходник hero.png сохранён в prototype/assets.

G03: vertical4:5, gloved mechanic hands torque wrench on graphite sedan engine, no visible face, graphite workwear, red tool cabinet blurred, soft daylight. Без иконок/коллажа/надписей. Исходный PNG: Codex generated_images/01a110aa-cf1c-7662-a719-4fbf24973448/exec-bd449427-2cd2-4e5c-970e-9b070f4ac20a.png; оптимизированная копия локально. Обе генерации помечены на макете «Иллюстрация дизайн-концепции».

## Шрифты
Manrope: https://github.com/google/fonts/tree/main/ofl/manrope. Golos Text: https://github.com/google/fonts/tree/main/ofl/golostext. Variable TTF + OFL локально. Полный русский алфавит включая Ё/ё проверен по cmap.

## Архив
185 ссылок ресурсов в sources/assets.json,80 крупных вариантов в sources/photo-index.json. Снимок контента48 URL от6октября2026 сохранён без пересъёмки. Перекодирование исходных сервисных фото только в WebP; композиционные изменения не вносились. Неиспользованный brakes.webp удалён при очистке.

## Интерактивная карта
Яндекс map-widget/v1, штатная метка pt; внешняя ссылка на организацию13496778418; центр43.927428,56.317015. Это внешний интерактивный виджет, требует сети. Ресурсы/подписи карты принадлежат Яндексу и не маскируются. Изображения location-390/768/1440.png — браузерные экспорты этого виджета, не замена работающему iframe. Пользователь прямо запросил подключение Яндекс Карт; аналитика и передача заявок не добавлены.
