# Диаграмма архитектуры системы

## Общий обзор

Система **Sentinel AI** построена по микросервисной архитектуре с событийно-ориентированным взаимодействием через Apache Kafka. Распределённый характер данных обусловлен различными паттернами доступа и требованиями к производительности.

## Диаграмма архитектуры

```mermaid
flowchart TB
    subgraph Client["Клиентский слой"]
        WebUI[Веб-приложение]
        MobileApp[Мобильное приложение]
        AdminUI[Панель модератора]
        Dashboard[Аналитический дашборд]
    end
    
    subgraph Gateway["API Gateway"]
        APIGW[API Gateway<br/>Kong / Nginx]
        RateLimit[Rate Limiter<br/>Redis]
        Auth[Аутентификация<br/>JWT / OAuth2]
    end
    
    subgraph Ingestion["Слой приёма данных"]
        CommentSvc[Comment Ingestion Service]
        PostSvc[Post Metadata Service]
        UserSvc[User Profile Service]
    end
    
    subgraph Processing["Слой обработки — ИИ-ядро"]
        NLP[Sentiment Analysis<br/>Service]
        Toxic[Toxicity Detection<br/>Service]
        Topic[Topic Classification<br/>Service]
        Decision[AUTO-Decision<br/>Engine]
    end
    
    subgraph Moderation["Слой модерации"]
        EscalationSvc[Escalation Service]
        ModAPI[Moderator API]
        Feedback[Feedback Collector<br/>Service]
    end
    
    subgraph Analytics["Аналитический слой"]
        Aggregator[Trend Aggregator<br/>Service]
        Alert[Alert Service<br/>пороговые уведомления]
        Report[Report Generator]
    end
    
    subgraph DataLayer["Распределённое хранилище данных"]
        PG[(PostgreSQL<br/>Основные сущности)]
        Mongo[(MongoDB<br/>Сырые комментарии)]
        CH[(ClickHouse<br/>Аналитика)]
        Redis[(Redis<br/>Кэш / Rate Limit)]
        S3[(S3-хранилище<br/>ML-артефакты)]
    end
    
    subgraph MLOps["ML-Ops слой"]
        Training[Model Training<br/>Pipeline]
        Registry[Model Registry]
        Serving[Model Serving<br/>Triton / vLLM]
    end
    
    subgraph Messaging["Сообщение-ориентированная шина"]
        Kafka[(Apache Kafka)]
    end
    
    Client --> APIGW
    APIGW --> RateLimit
    APIGW --> Auth
    APIGW --> CommentSvc
    APIGW --> PostSvc
    APIGW --> UserSvc
    APIGW --> ModAPI
    APIGW --> Dashboard
    
    CommentSvc --> Kafka
    PostSvc --> Kafka
    UserSvc --> PG
    
    Kafka --> NLP
    Kafka --> Toxic
    Kafka --> Topic
    Kafka --> Aggregator
    
    NLP --> Decision
    Toxic --> Decision
    Topic --> Decision
    
    Decision --> Kafka
    Decision --> PG
    
    Kafka --> EscalationSvc
    EscalationSvc --> ModAPI
    ModAPI --> AdminUI
    
    Feedback --> Training
    Feedback --> Kafka
    
    Aggregator --> CH
    Aggregator --> Alert
    Alert --> Dashboard
    
    Report --> CH
    Dashboard --> CH
    
    CommentSvc --> Mongo
    Decision --> PG
    NLP --> Redis
    Toxic --> Redis
    
    Training --> S3
    Registry --> S3
    Serving --> Redis
    
    Training --> Registry
    Registry --> Serving
    
    style NLP fill:#ccffcc,stroke:#006600
    style Toxic fill:#ccffcc,stroke:#006600
    style Topic fill:#ccffcc,stroke:#006600
    style Decision fill:#ffffcc,stroke:#cc9900
    style Kafka fill:#ffcccc,stroke:#cc0000
    style PG fill:#ccccff,stroke:#0000cc
    style Mongo fill:#ccccff,stroke:#0000cc
    style CH fill:#ccccff,stroke:#0000cc
    style Redis fill:#ccccff,stroke:#0000cc
    style S3 fill:#ccccff,stroke:#0000cc
```

## Обоснование распределённого характера работы с данными

Данные в системе распределены между несколькими хранилищами по причине **фундаментально разных паттернов доступа**:

### 1. Разделение по типу нагрузки (OLTP vs OLAP)

| Хранилище | Паттерн нагрузки | Причина разделения |
|---|---|---|
| **PostgreSQL** | OLTP — транзакции | ACID-гарантии для модерационных решений (юридическая значимость), пользовательских банов. Строгая схема данных. |
| **ClickHouse** | OLAP — аналитика | Агрегация миллионов записей по времени, категориям, тональности. Колонковое хранение даёт 10–100x ускорение на аналитических запросах vs PostgreSQL. |
| **MongoDB** | High-Volume Writes | Приём 500K комментариев/день с гибкой схемой. Горизонтальное масштабирование через шардинг. |

### 2. Разделение по требованиям к задержке

| Хранилище | Задержка | Использование |
|---|---|---|
| **Redis** | < 1 мс | Кэш загруженных ML-моделей, rate limiting, сессии модераторов |
| **PostgreSQL** | 1–10 мс | Чтение/запись решений модерации |
| **MongoDB** | 1–10 мс | Запись входящих комментариев |
| **ClickHouse** | 10–100 мс | Агрегатные запросы для дашбордов |
| **S3** | 100–500 мс | Хранение артефактов (модели, логи) |

### 3. Разделение по формату данных

- **Структурированные данные** (пользователи, решения, баны) → PostgreSQL
- **Полуструктурированные данные** (комментарии с меняющейся метаинформацией) → MongoDB
- **Временные ряды / агрегаты** (тренды тональности) → ClickHouse
- **Бинарные артефакты** (ML-модели) → S3

### 4. Kafka как связующая ткань

Apache Kafka обеспечивает:
- **Децентрализацию**: продюсеры и консьюмеры не знают друг о друге
- **Гарантию доставки**: at-least-once семантика для модерационных решений
- **Реплей**: возможность переобработки комментариев при обновлении ML-модели
- **Масштабирование**: консьюмер-группы позволяют горизонтально масштабировать обработку

## Характеристики развёртывания

| Компонент | Развёртывание | Масштабирование |
|---|---|---|
| API Gateway | Kubernetes, 2+ реплики | По CPU/RPS |
| Ingestion Services | Kubernetes, 3+ реплики | По объёму входящего потока |
| ML-Services | Kubernetes + GPU-узлы | По GPU-утилизации |
| Kafka | 3+ брокера, replication factor=3 | По throughput |
| PostgreSQL | Primary + 2 Replica | Read-replica для аналитики |
| MongoDB | Replica Set (3 узла) | Шардинг при росте |
| ClickHouse | Кластер 3+ узлов | По объёму аналитики |
| Redis | Sentinel (3 узла) | По hit-rate |