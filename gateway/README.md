# API Gateway Service

## Зоны ответственности

* Принимает запросы от UI
* Определяет, к какому внутреннему сервису должен быть направлен запрос 
* Маршрутизирует запросы к нужным сервисам
* Отправляет события о лайках, просмотрах, комментариях в брокер сообщений

## Границы ответственности

*   API Gateway отвечает только за предоставление API для взаимодействия с UI
*   не отвечает за хранение данных пользователей, постов или статистики