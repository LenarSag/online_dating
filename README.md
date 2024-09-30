# Онлайн-знакомства

Этот проект представляет собой API для онлайн-знакомств, который позволяет пользователям регистрироваться, оценивать друг друга и находить совместимые матчи на основе заданных критериев. Проект построен с использованием FastAPI и SQLAlchemy.

## Технологии

- **FastAPI**: веб-фреймворк для создания API на Python.
- **SQLAlchemy**: библиотека для работы с базами данных.
- **Pillow**: библиотека для обработки изображений (для наложения водяного знака).


### Запуск проекта

Клонировать репозиторий и перейти в него в командной строке: 
```
https://github.com/LenarSag/file_storage
```
Cоздать и активировать виртуальное окружение: 
```
python3.9 -m venv venv 
```
* Если у вас Linux/macOS 

    ```
    source venv/bin/activate
    ```
* Если у вас windows 
 
    ```
    source venv/Scripts/activate
    ```
```
python3.9 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```

Запуск проекта:
```
python main.py
```


Документация доступна после запуска по адресу:

http://127.0.0.1:8000/docs



### Эндпоинты
Регистрация нового участника
POST /api/v1/auth/clients/create

Тело запроса:

```
{
  "first_name": "Имя",
  "last_name": "Фамилия",
  "email": "email@example.com",
  "password": "пароль",
  "sex": "мужчина/женщина",
  "birth_date": "дата рождения"
}
```

Оценивание участника
POST /api/clients/{id}/match

Ответ:

201_CREATED:

```

{
    'status': 'mutual_match',
    'message': 'You and the user have both matched each other.',
    'matching_user_id': str(matching_user_id),
}
```

GET /clients/list

Параметры фильтрации:

```
gender: пол участника.
first_name: имя участника.
last_name: фамилия участника.
distance_to: расстояние до участника (в км)
```

Ответ:
200 OK: Список участников, соответствующих критериям.

```
{
    "items": [
        {
            "id": "ec1eb2cf-4bb4-4775-ac8a-7049f41a2ca5",
            "first_name": "Anna",
            "last_name": "Annikina",
            "sex": "female",
            "photo": "app\\media\\photos\\ec1eb2cf-4bb4-4775-ac8a-7049f41a2ca5.png",
            "age": 25,
            "distance_to": 61.7,
            "tags": ['dance']
        },
        {
            "id": "207a95dd-94fd-4fc9-8999-563b0328d76a",
            "first_name": "Sveta",
            "last_name": "Svetina",
            "sex": "female",
            "photo": "app\\media\\photos\\207a95dd-94fd-4fc9-8999-563b0328d76a.jpg",
            "age": 79,
            "distance_to": 5.6,
            "tags": ['traveler', 'musiclover']
        }
    ],
    "total": 2,
    "page": 1,
    "size": 50,
    "pages": 1
}
```

Расчет расстояния
Расстояние между участниками рассчитывается с использованием формулы великой окружности (Haversine formula). Участники должны иметь поля latitude и longitude.

### Тестирование

Добавлены асинхронные тесты endpointов, для вызова тестов нужно выолнить команду:

```
pytest
```