# Statistics Service

## Зоны ответственности

* Получает события из брокера сообщений
* Предоставляет API для запроса статистики
* Хранит данные для статистики о постах и комментариях
* Подсчитывает статистику по постам: лайки, просмотры, комментарии

## Границы ответственности

*   взаимодействует с API Gateway для обработки запросов и получает события через брокер сообщений
*   сервис статистики ответственен только за получение и обработку событий о лайках, комментариях и просмотрах пользователя
*   не отвечает за управление пользователями
*   не отвечает за создание, редактирование или удаление постов и комментариев