# Диаграмма структуры данных (ER-модель)

## Описание

Ниже представлена ER-диаграмма основной структуры данных системы. Спроектирована для гибридного хранилища: реляционная PostgreSQL — для транзакционных данных, ClickHouse — для аналитики, S3-совместимое хранилище — для моделей и артефактов.

## ER-диаграмма

```mermaid
erDiagram
    Comment {
        uuid comment_id PK
        uuid post_id FK
        uuid author_id FK
        text content
        timestamp created_at
        timestamp updated_at
        boolean is_deleted
        uuid moderated_by FK
    }

    User {
        uuid user_id PK
        string username
        string email
        enum user_status
        timestamp registered_at
        int trust_score
    }

    Post {
        uuid post_id PK
        uuid author_id FK
        string title
        text body
        enum post_type
        timestamp published_at
    }

    SentimentReport {
        uuid report_id PK
        uuid comment_id FK
        float negativity_score
        float toxicity_score
        enum sentiment_label
        float confidence
        string model_version
        timestamp analysed_at
    }

    ModerationAction {
        uuid action_id PK
        uuid comment_id FK
        uuid moderator_id FK
        enum action_type
        text moderator_note
        boolean followed_ai_recommendation
        timestamp action_at
    }

    FeedbackSignal {
        uuid signal_id PK
        uuid comment_id FK
        enum signal_type
        uuid source_user_id FK
        text reason
        timestamp created_at
    }

    ModelMetadata {
        uuid model_id PK
        string model_name
        string model_version
        string framework
        string s3_path
        float val_f1
        float val_negativity_recall
        timestamp trained_at
        boolean is_active
    }

    ContentTopic {
        uuid topic_id PK
        string topic_name
        string description
    }

    PostTopic {
        uuid post_id FK
        uuid topic_id FK
        float relevance_score
    }

    User ||--o{ Comment : "пишет"
    User ||--o{ Post : "автор"
    User ||--o{ ModerationAction : "выполняет как модератор"
    Post ||--o{ Comment : "содержит"
    Comment ||--o| SentimentReport : "анализируется"
    Comment ||--o{ ModerationAction : "подвергается"
    Comment ||--o{ FeedbackSignal : "получает сигнал"
    Post }o--o{ ContentTopic : "связан через PostTopic"
```

## Распределённый характер хранения данных

| Сущность | Хранилище | Причина |
|---|---|---|
| User, Post, Comment | PostgreSQL (OLTP) | Транзакционные данные, ACID, целостность ссылок |
| SentimentReport | ClickHouse (OLAP) | Аналитические запросы, агрегация по времени, фильтрация миллионов строк |
| ModelMetadata | PostgreSQL + S3 | Метаданные в PostgreSQL, артефакты модели (веса) в S3 |
| FeedbackSignal | ClickHouse | Потоковые сигналы для дообучения, агрегация |