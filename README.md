# api_posts_ai
## Tools used:
- The main framework: Django Ninja, Pydantic
- DATABASE: Sqlite 
- User authorisation: JWT
- API client: Gemini API 
  - Does not support Ukrainian localisation. To work from the territory of Ukraine, use a VPN
- Autotesting: Pytest
- Documentation: Swagger

## Project launch. 
- git clone https://github.com/kolesnikdi/Starnavi.git
- cd .\Starnavi\api_posts_ai
- Create .env file у \Starnavi\api_posts_ai
  - SECRET_KEY='django-insecure-' + token with a length of 50 characters
  - HOST_NAME= hostname
  - GEMINI_API_KEY= gemini api key
- `pip install -r requirements.txt`
- `python manage.py migrate`
- `python manage.py runserver`
- Run end-to-end tests -> `pytest`

## Explanation
- Implemented as an API.
- The API is divided into 2 branches 'api/users/' and 'api/post/'. This will ensure the correct route hierarchy and
  separate processes.
- 'api/users/' [registration](http://127.0.0.1:8000/api/users/register), [login](http://127.0.0.1:8000/api/users/login),
[renew token](http://127.0.0.1:8000/api/users/renew_token)
  - The authorisation is implemented as a request for issuing a JWT token and a request for token renewal. 
    The token is issued for 15 minutes (TTL can be configured in settings).
- 'api/post/' [create post](http://127.0.0.1:8000/api/post), 
[create comment / get or update or delete (post / comment)](http://127.0.0.1:8000/api/post/1),
[update post settings](http://127.0.0.1:8000/api/post/1/settings), 
[daily breakdown](http://127.0.0.1:8000/api/post/daily-breakdown?date_from=2020-02-02&date_to=2022-02-15)
  - To implement posts and comments, we used MP_Node from treebeard. It provides convenient interfaces for managing 
    and reduces the amount of code. But it is only suitable for projects with a small number of posts and comments. 
    For large projects, it's better to use conventional models.
  - The automatic reply to a comment is implemented as a Django Signal. The process starts when a comment is created and 
    the reply is added after a time interval specified by the user (a 2 hour waiting time limit has been added). To 
    configure automatic responses to comments, the PostSettings model has been added. This will allow you to configure 
    an automatic response personally for each post. Basic settings for a post are created automatically with
    the creation of the post itself (auto-reply is disabled by default). Added a "basic reply" field that is filled in 
    by the user. This will ensure continuous operation of the system even if the Gemini API is not available. 
    The waiting time before the auto response is configured here. The logic has also been extended: 1. Added the ability
    to conduct a dialogue (Gemini will engage in a dialogue with each user who has commented on the post); 2. The user 
    can customise the creativity of their auto-messages. All exceptions have been handled so that Gemini does not start 
    talking to itself.
  - Changes to auto-response settings are sent to a separate url. Does not support changing individual settings, only 
    all at once.
  - Checking posts or comments for foul language is implemented both for creating new posts and for 
    editing existing ones. The post or comment will be saved in the database but will not be displayed to customers.
  - The display of posts/comments is implemented as a return of the object itself and all comments to it. 
    The display is cascading. Data processing in 2 requests to the database.
  - Analytics on the number of comments is implemented as statistics for each individual day in the period provided.
    Each day includes the total number of blocked comments, the total number of allowed comments, as well as the number 
    of blocked and allowed comments related to each individual post. Data processing in 1 database requests.
- The Gemini API is implemented as a class that has 2 separate interfaces. is_swearing and reply. This will allow you to
  customise each interface to suit your needs, as well as separately handle exceptions from the Gemini API

### Інші посилання 
[swagger](http://127.0.0.1:8000/api/docs).


# api_posts_ai
## Використані інструменти:
- Oсновний фреймвок: Django Ninja, Pydantic
- БД: Sqlite 
- Авторизації користувачів: JWT
- API клієнт: Gemini API 
- - не підтримує Українську Локалізацію. Для роботи з території України використовуйте VPN
- Автотестування: Pytest
- Документація: Swagger

## Запуск проекту 
- git clone https://github.com/kolesnikdi/Starnavi.git
- cd .\Starnavi\api_posts_ai
- Створи .env файл у \Starnavi\api_posts_ai
  - SECRET_KEY='django-insecure-' + токен довжиною 50 символів
  - HOST_NAME= ім'я хоста
  - GEMINI_API_KEY= ключ gemini api
- `pip install -r requirements.txt`
- `python manage.py migrate`
- `python manage.py runserver`
- Run end-to-end tests -> `pytest`

## Додаткові пояснення
- Реалізовано як API.
- API розділено на 2 гілки 'api/users/' та 'api/post/'. Це забезпечить правильну ієрархію маршрутів і розділить процеси.
- 'api/users/' [registration](http://127.0.0.1:8000/api/users/register), [login](http://127.0.0.1:8000/api/users/login),
[renew token](http://127.0.0.1:8000/api/users/renew_token)
  - Авторизації реалізована як запит на видачу токена JWT і запит на поновлення токена. 
    Токен видається на 15 хв (TTL можна налаштувати в settings).
- 'api/post/' [create post](http://127.0.0.1:8000/api/post), 
[create comment / get or update or delete (post / comment)](http://127.0.0.1:8000/api/post/1),
[update post settings](http://127.0.0.1:8000/api/post/1/settings), 
[daily breakdown](http://127.0.0.1:8000/api/post/daily-breakdown?date_from=2020-02-02&date_to=2022-02-15)
  - Для реалізації постів та коментарів була використана MP_Node з treebeard. Вона надає зручні інтерфейси для управління 
  та зменшує кількість коду. Але вона підходить тільки для проєктів з малою кількістю постів та коментарів. 
  Для великих проєктів краще використовувати звичайні моделі.
  - Автоматична відповідь на коментар реалізована як Django Signal. Процес запускається під час створення коментаря і 
    відповідь додається через проміжок часу вказаний користувачем (додано обмеження на очікування в 2 години). Для 
    налаштування автоматичних відповідей на коментарі була додана модель PostSettings. Це дозволить налаштовувати 
    автоматичну відповідь персонально для кожного поста. Базові налаштування для поста створюються автоматично зі
    створенням самого поста (авто відповідь базово вимкнена). Додано поле "базова відповідь" яке заповнює користувач. 
    Це забезпечить безперервну роботу системи навіть якщо Gemini API буде не доступний. Час очікування перед авто 
    відповіддю налаштовується тут. Також була розширена логіка: 1. Додана можливість ведення діалогу 
    (Gemini буде вести діалог з кожним користувачем, що прокоментував пост); 2. Користувач може налаштовувати 
    креативність своїх автоповідомлень. Оброблені всі винятки, щоб Gemini не почала спілкуватися сама з собою.
  - Зміна налаштувань авто відповіді відправляється на окремий url. Не підтримує зміни окремих налаштувань, виключно 
    всіх одразу.
  - Перевірка поста чи коментарів на наявність нецензурної лексики реалізована як для створення нових так і для 
    редагування існуючих. Пост чи коментар буде збережено в БД але не буде відображатись для клієнтів.
  - Відображення постів / коментарів реалізовано як повернення самого обєкта і всіх коментарів до нього. 
    Відображення каскадне. Обробка даних в 2 запити до БД.
  - Аналітика щодо кількості коментарів реалізована як статистика за кожен окремий день в періоді що надається.
    Кожен день включає в себе загальну кількість заблокованих коментарів, загальну кількість дозволених коментарів, 
    а також кількість заблокованих та дозволенних коментарів які належать до кожного окремого поста. Обробка даних в 1 
    запити до БД.
- Gemini API реалізований як клас, що має 2 окремі інтерфейси. is_swearing та reply. Це дозволить налаштовувати кожен 
  інтерфейс під потреби, а також окремо оброблювати винятки від Gemini API

### Інші посилання 
[swagger](http://127.0.0.1:8000/api/docs).

