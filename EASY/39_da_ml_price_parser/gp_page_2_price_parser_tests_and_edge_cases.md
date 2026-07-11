# DA/ML: PRICE PARSER — страница 2

# Тесты, граничные случаи и проверка решения

## 1. Пример из задания

```python
from solution import parse_product_info

html = '''
<html>
<body>
    <div class="product">
        <h1 class="product-title"><b>Телевизор</b> Ultra HD</h1>
        <div class="product-category">Электроника / Телевизоры</div>
        <div class="product-price">
            <span class="price-old"><strike>55 000 ₽</strike></span>
            <span class="price-new">50 000 ₽</span>
        </div>
    </div>
</body>
</html>
'''

assert parse_product_info(html) == {
    "title": "Телевизор Ultra HD",
    "category": "Электроника / Телевизоры",
    "old_price": "55 000 ₽",
    "new_price": "50 000 ₽",
}
```

---

## 2. Пустая старая цена

```python
html = '''
<h1 class="product-title">Смартфон</h1>
<div class="product-category">Электроника</div>
<span class="price-old"></span>
<span class="price-new">79 990 ₽</span>
'''

assert parse_product_info(html) == {
    "title": "Смартфон",
    "category": "Электроника",
    "old_price": "",
    "new_price": "79 990 ₽",
}
```

Это обязательный тест из условий задачи.

---

## 3. Вложенные теги

```python
html = '''
<h1 class="product-title"><b>Ноутбук</b> <i>Pro</i></h1>
<div class="product-category"><strong>Компьютеры</strong></div>
<span class="price-old"><strike><b>120 000 ₽</b></strike></span>
<span class="price-new"><strong>99 000 ₽</strong></span>
'''

assert parse_product_info(html) == {
    "title": "Ноутбук Pro",
    "category": "Компьютеры",
    "old_price": "120 000 ₽",
    "new_price": "99 000 ₽",
}
```

---

## 4. Переносы строк

```python
html = '''
<h1 class="product-title">
    Телевизор

    Ultra HD
</h1>
<div class="product-category">
    Электроника   /   Телевизоры
</div>
<span class="price-old">
    55 000 ₽
</span>
<span class="price-new">
    50 000 ₽
</span>
'''

assert parse_product_info(html) == {
    "title": "Телевизор Ultra HD",
    "category": "Электроника / Телевизоры",
    "old_price": "55 000 ₽",
    "new_price": "50 000 ₽",
}
```

---

## 5. Одинарные кавычки

```python
html = """
<h1 class='product-title'>Кофемашина</h1>
<div class='product-category'>Бытовая техника</div>
<span class='price-old'>60 000 ₽</span>
<span class='price-new'>54 000 ₽</span>
"""

assert parse_product_info(html)["title"] == "Кофемашина"
```

---

## 6. Дополнительные HTML-атрибуты

```python
html = '''
<h1 id="main-title" class="product-title" data-id="12">
    Пылесос
</h1>
<div data-level="2" class="product-category">
    Бытовая техника
</div>
<span aria-hidden="true" class="price-old">
    20 000 ₽
</span>
<span class="price-new" data-currency="RUB">
    17 990 ₽
</span>
'''

assert parse_product_info(html)["new_price"] == "17 990 ₽"
```

---

## 7. Несколько CSS-классов

```python
html = '''
<h1 class="headline product-title active">Монитор</h1>
<div class="section product-category">Компьютеры</div>
<span class="muted price-old hidden">40 000 ₽</span>
<span class="highlight price-new">35 000 ₽</span>
'''

assert parse_product_info(html)["title"] == "Монитор"
```

---

## 8. HTML-сущности

```python
html = '''
<h1 class="product-title">TV &amp; Sound</h1>
<div class="product-category">Audio &amp; Video</div>
<span class="price-old">55&nbsp;000 ₽</span>
<span class="price-new">50&nbsp;000 ₽</span>
'''

assert parse_product_info(html) == {
    "title": "TV & Sound",
    "category": "Audio & Video",
    "old_price": "55 000 ₽",
    "new_price": "50 000 ₽",
}
```

---

## 9. Теги в верхнем регистре

```python
html = '''
<H1 CLASS="product-title">Телевизор</H1>
<DIV CLASS="product-category">Электроника</DIV>
<SPAN CLASS="price-old">55 000 ₽</SPAN>
<SPAN CLASS="price-new">50 000 ₽</SPAN>
'''

assert parse_product_info(html)["title"] == "Телевизор"
```

---

## 10. Что не нужно добавлять

Не нужно преобразовывать цену в число:

```python
50000
```

потому что ожидается:

```python
"50 000 ₽"
```

Не нужно использовать:

```python
BeautifulSoup
lxml
pandas
requests
```

Функция уже получает готовый HTML и должна вернуть только словарь.

Не нужно печатать:

```python
print(product_info)
```

Нужно вернуть:

```python
return product_info
```

---

## 11. Как запустить локальную проверку

Создайте временный тестовый файл рядом с `solution.py`:

```python
from solution import parse_product_info


def test_example():
    html = '''
    <h1 class="product-title"><b>Телевизор</b> Ultra HD</h1>
    <div class="product-category">Электроника / Телевизоры</div>
    <span class="price-old"><strike>55 000 ₽</strike></span>
    <span class="price-new">50 000 ₽</span>
    '''

    expected = {
        "title": "Телевизор Ultra HD",
        "category": "Электроника / Телевизоры",
        "old_price": "55 000 ₽",
        "new_price": "50 000 ₽",
    }

    assert parse_product_info(html) == expected
```

Запуск:

```bash
pytest -q
```

В Karpov Simulator загружайте только файл, который требует форма задания: `solution.py`.
