# Диаграмма архитектуры системы

## Описание

Архитектура построена по принципу событийно-ориентированного конвейера (event-driven pipeline). Данные поступают через API Gateway, обрабатываются стриминговым движком, классифицируются ML-сервисом и маршрутизируются. Распределённое хранение обосновано разными паттернами доступа: OLTP для транзакций, OLAP для аналитики, объектное хранилище для артефактов моделей.

## Диаграмма архитектуры

```mermaid
flowchart TB
    subgraph ClientSide["Клиентская часть"]
        UI[Веб / Мобильный клиент]
        ModUI[Модераторский дашборд]
        AnDash[Аналитический дашборд]
    end

    subgraph Ingress["Входной слой"]
        APIGW[API Gateway / Load Balancer]
        Auth[Сервис авторизации]
    end

    subgraph CoreServices["Основные сервисы"]
        CommentSvc[Comment Service]
        PostSvc[Post Service]
        ModerationSvc[Moderation Service]
    end

    subgraph MLPipeline["ML-конвейер"]
        Kafka[(Apache Kafka)]
        StreamProc[Flink / Spark Streaming]
        InferenceAPI[Inference API Service]
        BatchRetrain[Batch Retraining Pipeline]
    end

    subgraph Storage["Распределённое хранилище"]
        PG[(PostgreSQL)]
        CH[(ClickHouse)]
        S3[(S3-совместимое хранилище)]
        Redis[(Redis Cache)]
    end

    subgraph Monitoring["Мониторинг и аналитика"]
        Grafana[Grafana]
        Prometheus[Prometheus]
        AnalyticsSvc[Analytics Service]
    end

    UI --> APIGW
    ModUI --> APIGW
    AnDash --> APIGW

    APIGW --> Auth
    APIGW --> CommentSvc
    APIGW --> PostSvc
    APIGW --> ModerationSvc

    CommentSvc --> Kafka
    CommentSvc --> PG
    PostSvc --> PG
    ModerationSvc --> PG
    ModerationSvc --> Kafka

    Kafka --> StreamProc
    StreamProc --> InferenceAPI
    InferenceAPI --> PG
    InferenceAPI --> CH
    InferenceAPI --> Kafka

    Kafka --> ModerationSvc

    BatchRetrain --> S3
    BatchRetrain --> InferenceAPI
    S3 --> InferenceAPI

    CH --> AnalyticsSvc
    PG --> AnalyticsSvc
    Redis --> InferenceAPI
    InferenceAPI --> Redis

    Prometheus --> Grafana
    AnalyticsSvc --> Grafana
    AnDash --> AnalyticsSvc
    ModUI --> ModerationSvc

    style ClientSide fill:#e3f2fd
    style Ingress fill:#fff3e0
    style CoreServices fill:#e8f5e9
    style MLPipeline fill:#f3e5f5
    style Storage fill:#fce4ec
    style Monitoring fill:#fff9c4
```

## Обоснование распределённого характера хранения

| Данные | Хранилище | Почему распределённо |
|---|---|---|
| Транзакционные (User, Post, Comment, ModerationAction) | PostgreSQL | Классический OLTP: INSERT/UPDATE, ACID-гарантии, реляционная целостность |
| Аналитические (SentimentReport, FeedbackSignal) | ClickHouse | OLAP: миллионные агрегации по времени, колоночное сжатие, быстрые GROUP BY |
| ML-артефакты (модели, токенизаторы) | S3 | Большие бинарные файлы (100 МБ — 5 ГБ), редкие чтения при деплое, версионирование |
| Кэш предсказаний и сессии | Redis | Sub-ms latency для горячих ключей, TTL-политика, ephemeral nature |

Ключевой принцип: разные паттерны доступа = разные хранилища. Единая «大雪 данных» (data lake) не показана, т.к. на MVP-этапе достаточно указанных четырёх, а расширение до lake возможна на следующих итерациях.