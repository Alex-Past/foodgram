### Проект "Foodgram"

«Фудграм» — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Основной стек технологий проекта:

Python 3.9, Django, PostgreSQL, Django Rest Framework, Nginx, Docker

### Как запустить проект ЛОКАЛЬНО* (*временное описание):


Находясь в папке backend запустите команду:

```
sudo docker compose up
```
В отдельном окне терминала последовательно выполните команды:

```
sudo docker compose exec backend python manage.py migrate
```

```
sudo docker compose exec backend python manage.py collectstatic
```

```
sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/
```

### ЛОКАЛЬНО проект доступен по адресу:

```
http://localhost:8000/
```

### Документация к API Foodgram:

```
http://localhost:8000/api/docs/
```

### Авторы:

Alexandr Pastukh

https://github.com/Alex-Past