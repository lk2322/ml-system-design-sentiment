# Архитектура системы

## 1. Общая схема архитектуры

Система построена на микросервисной архитектуре с использованием очередей сообщений для асинхронной обработки.

```mermaid
graph LR
    UserApp[User App / Frontend] --> API[API Gateway]
    API --> Kafka{Kafka Topic: comments}
    Kafka --> MLWorker[ML Sentiment Worker]
    MLWorker --> DB[(Distributed DB)]
    MLWorker --> ActionService[Moderation Action Service]
    ActionService --> Notify[Notification Service]
    MLWorker --> Monitoring[Prometheus/Grafana]
```

## 2. UML-диаграмма компонентов

```mermaid
flowchart TB
    subgraph ModerationSystem [Moderation System]
        API[API Service]
        ML[ML Inference Service]
        Ingest[Data Ingestion Service]
        Action[Action Service]
        Registry[Model Registry]
        
        API --> Ingest
        Ingest --> ML
        ML --> Action
        ML -.->|loads model| Registry
    end
```

## 3. UML-диаграмма последовательности (Sequence Diagram)

Процесс обработки нового комментария:

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant A as API Gateway
    participant K as Kafka
    participant W as ML Worker
    participant DB as Database
    participant M as Модератор

    U->>A: Опубликовать комментарий
    A->>K: Отправить событие (comment_created)
    A-->>U: Успешно (202 Accepted)
    K->>W: Получить комментарий
    W->>W: Анализ тональности (BERT/RoBERTa)
    alt Высокая уверенность (Токсично)
        W->>DB: Сохранить результат и скрыть
        W->>A: Команда на скрытие контента
    else Низкая уверенность
        W->>DB: Сохранить (status: pending)
        W->>M: Создать задачу в очереди модерации
        M->>DB: Обновить решение (approve/reject)
    end
```

## 4. Обоснование выбора технологий
- **Kafka:** Необходима для обработки пиковых нагрузок (500k/день) и обеспечения гарантии доставки сообщений.
- **ML Worker:** Отдельный сервис позволяет масштабировать GPU-ресурсы независимо от API.
- **Model Registry (MLflow):** Для версионирования моделей и быстрого отката в случае деградации метрик.
