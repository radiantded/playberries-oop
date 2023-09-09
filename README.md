# Playberries
* Асинхронный эмулятор поведения пользователя на сайте Wildberries  
* Скрипт имитирует поиск по сайту, перелистывание страниц, прокручивание страницы, добавление товара в корзину  
* Позволяет накручивать просмотры у выбранного товара, что повышает его место в поисковой выдаче  
* Накрутка может выполняться одновременно у нескольких товаров
* Поддерживается работа через прокси  
* Управление и настройка скрипта осуществляется через телеграм-бот, поддерживается использование несколькими пользователями одновременно  

## Настройка
Переменные окружения  
```
AUTH_USERS - список telegram id пользователей, имеющих доступ к боту
TOKEN - telegram токен бота
PROXY_SITE - URL прокси
PROXY_LOGIN - логин прокси
PROXY_PASS - пароль прокси
```

## Запуск
```
poetry shell
poetry install
python bot.py
```
