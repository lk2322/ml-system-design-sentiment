# Диаграмма структуры данных — ER-модель

## Обоснование выбора БД

Система использует **гибридную архитектуру данных** — распределённое хранение, оптимальное для разных типов нагрузки:

| Хранилище | Тип | Назначение |
|---|---|---|
| **PostgreSQL** | Реляционная | Основные сущности (пользователи, посты, комментарии, решения модерации) — транзакционная целостность |
| **MongoDB** | Документная | Сырые входящие комментарии в оригинальном формате (JSON) — гибкая схема, высокий Writes/sec |
| **ClickHouse** | Колонковая | Аналитика, агрегация тональности по временным срезам — быстрые OLAP-запросы |
| **Redis** | Ключ-значение (in-memory) | Кэш моделей, сессии, rate limiting — суб-миллисекундный доступ |
| **S3-совместимое** | Объектное | Хранение артефактов ML-моделей, логов предсказаний — долговременное хранение |

## ER-диаграмма (основная реляционная модель — PostgreSQL)

```mermaid
erDiagram
    USER ||--o{ COMMENT : writes
    USER ||--o{ POST : creates
    USER ||--o{ USER_BAN : receives
    POST ||--o{ COMMENT : contains
    COMMENT ||--o| SENTIMENT_RESULT : analysed_by
    COMMENT ||--o| MODERATION_DECISION : subject_of
    SENTIMENT_RESULT ||--o| MODERATION_DECISION : informs
    MODERATION_DECISION ||--o| DECISION_REVIEW : reviewed_in
    MODERATION_DECISION }o--|| MODERATOR : made_by
    ML_MODEL ||--o{ SENTIMENT_RESULT : produces
    MODERATOR ||--o{ DECISION_REVIEW : performs
    CONTENT_TYPE ||--o{ POST : categorizes
    
    USER {
        uuid user_id PK
        string username
        string email
        int reputation_score
        timestamp registration_date
        boolean is_banned
        int violation_count
    }
    
    POST {
        uuid post_id PK
        uuid author_id FK
        string title
        text content
        timestamp created_at
        uuid content_type_id FK
    }
    
    COMMENT {
        uuid comment_id PK
        uuid post_id FK
        uuid author_id FK
        text text_content
        timestamp created_at
        boolean is_deleted
        timestamp deleted_at
    }
    
    SENTIMENT_RESULT {
        uuid result_id PK
        uuid comment_id FK
        uuid model_id FK
        float negativity_score
        float toxicity_score
        float positivity_score
        string primary_sentiment
        float confidence
        string language
        timestamp analysed_at
    }
    
    MODERATION_DECISION {
        uuid decision_id PK
        uuid comment_id FK
        uuid result_id FK
        uuid moderator_id FK
        string decision_type
        string reason
        boolean is_automated
        timestamp decided_at
        string decision_source
    }
    
    DECISION_REVIEW {
        uuid review_id PK
        uuid decision_id FK
        uuid moderator_id FK
        string review_outcome
        text review_comment
        timestamp reviewed_at
    }
    
    ML_MODEL {
        uuid model_id PK
        string model_name
        string model_version
        float f1_score
        float precision
        float recall
        timestamp trained_at
        boolean is_active
    }
    
    USER_BAN {
        uuid ban_id PK
        uuid user_id FK
        string reason
        timestamp banned_at
        timestamp expires_at
        uuid decision_id FK
    }
    
    CONTENT_TYPE {
        uuid type_id PK
        string name
        string description
    }
```

## Документная модель (MongoDB) — сырые комментарии

```json
{
  "_id": "ObjectId",
  "comment_id": "UUID",
  "raw_text": "Оригинальный текст комментария",
  "metadata": {
    "platform": "web|ios|android",
    "client_version": "3.2.1",
    "ip_hash": "sha256...",
    "user_agent": "Mozilla/5.0..."
  },
  "enrichment": {
    "user_reputation": 85,
    "post_category": "politics",
    "thread_position": 12,
    "parent_comment_id": null,
    "has_attachments": false
  },
  "processing_status": "pending|processed|escalated|failed",
  "received_at": "ISO8601 timestamp",
  "processed_at": "ISO8601 timestamp | null"
}
```

## Аналитическая модель (ClickHouse) — агрегация

```sql
-- Пример таблицы для аналитики тональности
CREATE TABLE sentiment_analytics (
    date Date,
    hour UInt8,
    content_type_id UUID,
    sentiment_category Enum8('positive'=1, 'neutral'=2, 'negative'=3, 'toxic'=4),
    total_comments UInt64,
    avg_negativity Float32,
    avg_toxicity Float32,
    auto_moderated UInt64,
    escalated UInt64,
    false_positive_rate Float32
)
ENGINE = MergeTree()
ORDER BY (date, hour, content_type_id);
```

## Распределённый характер данных — обоснование

Различные хранилища необходимы из-за **принципиально разных паттернов доступа**:

1. **PostgreSQL** — транзакционные операции (создание комментария, запись решения модерации). Нужна ACID-целостность для юридически значимых решений модерации и банов пользователей.

2. **MongoDB** — приём и буферизация входящего потока (до 500K/день). Гибкая схема позволяет хранить комментарии разной структуры без миграций. Высокая скорость записи критична для реалтайм-пайплайна.

3. **ClickHouse** — агрегатные запросы для дашбордов и аналитики (тренды тональности по часам, дням, категориям контента). Колонковое хранение обеспечивает производительность на терабайтах данных при миллисекундных откликах.

4. **Redis** — кэширование ML-моделей (загруженных в память для инференса) и rate limiting API. In-memory доступ критичен для <1 секунды времени реакции.

5. **S3** — долговременное хранение артефактов: чекпойнты моделей, батчи предсказаний для дообучения, логи аудита.

Данные перемещаются между хранилищами через **пайплайн Apache Kafka**, обеспечивающий надёжную доставку и разделение продюсеров/консьюмеров.