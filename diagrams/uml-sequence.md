# UML-диаграмма последовательности: обработка нового комментария

## Описание

Диаграмма последовательности показывает основной сценарий обработки нового пользовательского комментария: от публикации до принятия решения о модерации. Охватывает как автоматический (ИИ), так и ручной (модератор) пути.

## Диаграмма последовательности

```mermaid
sequenceDiagram
    actor User as Пользователь
    participant API as API Gateway
    participant CS as Comment Service
    participant Kafka as Apache Kafka
    participant PP as Preprocessing
    participant Inf as Inference Service
    participant Redis as Redis Cache
    participant CH as ClickHouse
    participant PG as PostgreSQL
    participant MS as Moderation Service
    actor Mod as Модератор
    participant FC as Feedback Collector

    User->>API: POST /comments {post_id, content}
    API->>CS: createComment()
    CS->>PG: INSERT INTO comments
    PG-->>CS: comment_id
    CS->>Kafka: publish comment.created {comment_id, content}
    CS-->>API: 201 Created {comment_id}
    API-->>User: Комментарий временно опубликован (visible)

    Note over Kafka,FC: Асинхронный ML-конвейер

    Kafka->>PP: consume comment.created
    PP->>PP: normalizeText(), tokenize(), embed()
    PP->>Inf: predict(embedding, comment_id)
    Inf->>Redis: check cache for model_version
    Redis-->>Inf: cache hit / miss
    Inf->>Inf: model.predict(embedding)
    Inf-->>PP: SentimentResult {negativity: 0.72, toxicity: 0.45}

    alt negativity >= 0.85 (auto-hide)
        Inf->>CH: INSERT INTO sentiment_reports
        Inf->>Kafka: publish moderation.auto-hide {comment_id, reason}
        Kafka->>MS: consume moderation.auto-hide
        MS->>PG: UPDATE comments SET is_deleted = true
        MS->>PG: INSERT INTO moderation_actions
        MS-->>Mod: Уведомление: комментарий авто-скрыт (информационное)
    else 0.5 <= negativity < 0.85 (queue for review)
        Inf->>CH: INSERT INTO sentiment_reports
        Inf->>Kafka: publish moderation.review-needed {comment_id, scores}
        Kafka->>MS: consume moderation.review-needed
        MS->>PG: INSERT INTO moderation_queue
        MS-->>Mod: Задача в очереди с рекомендацией ИИ

        Mod->>API: POST /moderation/actions {comment_id, action: delete}
        API->>MS: reviewAction()
        MS->>PG: UPDATE comments SET is_deleted = true
        MS->>PG: INSERT INTO moderation_actions
        MS->>FC: collectFeedback(signal)
        FC->>CH: INSERT INTO feedback_signals
    else negativity < 0.5 (auto-approve)
        Inf->>CH: INSERT INTO sentiment_reports
        Note over Inf: No action needed, comment stays published
    end
```

## Альтернативный сценарий: ложноположительный результат (модератор не согласен с ИИ)

```mermaid
sequenceDiagram
    actor Mod as Модератор
    participant API as API Gateway
    participant MS as Moderation Service
    participant PG as PostgreSQL
    participant FC as Feedback Collector
    participant CH as ClickHouse
    participant RP as Retraining Pipeline

    Mod->>API: POST /moderation/actions {comment_id, action: reinstate, override: true}
    API->>MS: overrideDecision()
    MS->>PG: UPDATE comments SET is_deleted = false
    MS->>PG: INSERT INTO moderation_actions {followed_ai: false}
    MS->>FC: collectFeedback(LO Público_POSITIVE)
    FC->>CH: INSERT INTO feedback_signals {type: FALSE_POSITIVE}
    FC->>RP: notify feedback_collected

    Note over RP: Сигнал накапливается;<br/>дообучение запускается по расписанию (еженедельно)

    RP->>RP: После накопления ≥ N сигналов:<br/>train() → validate() → canary_deploy()
```