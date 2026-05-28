# UML-диаграмма компонентов

## Диаграмма компонентов системы Sentinel AI

```mermaid
flowchart TB
    subgraph Frontend["Фронтенд-компоненты"]
        WebApp[Web Application<br/>React SPA]
        MobileApp[Mobile App<br/>iOS / Android]
        ModUI[Moderator Dashboard<br/>React SPA]
        DashUI[Analytics Dashboard<br/>React SPA]
    end
    
    subgraph API["API-слой"]
        APIGW[API Gateway]
        AuthComp[Auth Component<br/>JWT + OAuth2]
    end
    
    subgraph Core["Основные сервисы"]
        direction LR
        CommentIngest[Comment Ingestion<br/>Service]
        PostService[Post Service]
        UserService[User Service]
        Notification[Notification<br/>Service]
    end
    
    subgraph AI["ИИ-компоненты"]
        SentimentComp[Sentiment Analysis<br/>Component]
        ToxicityComp[Toxicity Detection<br/>Component]
        TopicComp[Topic Classifier<br/>Component]
        DecisionEngine[Decision Engine<br/>Component]
    end
    
    subgraph Mod["Компоненты модерации"]
        Escalation[Escalation<br/>Component]
        ModDecision[Moderator Decision<br/>Component]
        FeedbackComp[Feedback Collector<br/>Component]
    end
    
    subgraph Analytics["Аналитические компоненты"]
        TrendAgg[Trend Aggregator<br/>Component]
        AlertComp[Alert Component<br/>Threshold-based]
        ReportComp[Report Generator<br/>Component]
    end
    
    subgraph MLOps["ML-Ops компоненты"]
        TrainPipeline[Training Pipeline<br/>Component]
        ModelReg[Model Registry<br/>Component]
        ModelServe[Model Serving<br/>Component]
    end
    
    subgraph Data["Компоненты данных"]
        PGComp[PostgreSQL<br/>Adapter]
        MongoComp[MongoDB<br/>Adapter]
        CHComp[ClickHouse<br/>Adapter]
        RedisComp[Redis<br/>Adapter]
        S3Comp[S3<br/>Adapter]
    end
    
    subgraph Bus["Шина сообщений"]
        KafkaBus[Apache Kafka<br/>Event Bus]
    end
    
    WebApp --> APIGW
    MobileApp --> APIGW
    ModUI --> APIGW
    DashUI --> APIGW
    
    APIGW --> AuthComp
    APIGW --> CommentIngest
    APIGW --> PostService
    APIGW --> UserService
    APIGW --> ModDecision
    APIGW --> DashUI
    
    CommentIngest --> KafkaBus
    CommentIngest --> MongoComp
    PostService --> PGComp
    UserService --> PGComp
    
    KafkaBus --> SentimentComp
    KafkaBus --> ToxicityComp
    KafkaBus --> TopicComp
    KafkaBus --> TrendAgg
    
    SentimentComp --> DecisionEngine
    ToxicityComp --> DecisionEngine
    TopicComp --> DecisionEngine
    
    DecisionEngine --> KafkaBus
    DecisionEngine --> PGComp
    DecisionEngine --> Escalation
    
    Escalation --> ModDecision
    ModDecision --> FeedbackComp
    FeedbackComp --> TrainPipeline
    FeedbackComp --> KafkaBus
    
    TrendAgg --> CHComp
    TrendAgg --> AlertComp
    AlertComp --> Notification
    ReportComp --> CHComp
    
    TrainPipeline --> ModelReg
    TrainPipeline --> S3Comp
    ModelReg --> S3Comp
    ModelReg --> ModelServe
    
    SentimentComp --> RedisComp
    ToxicityComp --> RedisComp
    ModelServe --> RedisComp
    
    DecisionEngine --> PGComp

    style SentimentComp fill:#ccffcc,stroke:#006600
    style ToxicityComp fill:#ccffcc,stroke:#006600
    style TopicComp fill:#ccffcc,stroke:#006600
    style DecisionEngine fill:#ffffcc,stroke:#cc9900
    style KafkaBus fill:#ffcccc,stroke:#cc0000
```

## Описание компонентов

| Компонент | Ответственность | Интерфейсы |
|---|---|---|
| **Comment Ingestion** | Приём и валидация входящих комментариев | REST API (POST /comments), Kafka Producer |
| **Post Service** | Управление метаданными постов | REST API (CRUD /posts) |
| **User Service** | Управление профилями пользователей | REST API (CRUD /users) |
| **Sentiment Analysis** | Классификация тональности текста | Kafka Consumer, gRPC (internal) |
| **Toxicity Detection** | Определение токсичности | Kafka Consumer, gRPC (internal) |
| **Topic Classifier** | Категоризация тематики | Kafka Consumer, gRPC (internal) |
| **Decision Engine** | Принятие решения на основе ИИ-оценок | Kafka Consumer/Producer, REST internal |
| **Escalation** | Маршрутизация пограничных случаев | Kafka Consumer, gRPC |
| **Moderator Decision** | Интерфейс для ручной модерации | REST API, WebSocket (real-time) |
| **Feedback Collector** | Сбор фидбека для дообучения моделей | Kafka Consumer, REST internal |
| **Trend Aggregator** | Агрегация трендов тональности | Kafka Consumer, ClickHouse Writer |
| **Alert Component** | Пороговые уведомления | SSE, Push notifications |
| **Training Pipeline** | Дообучение ML-моделей на новых данных | Internal gRPC, S3 Reader/Writer |
| **Model Registry** | Версионирование ML-моделей | REST internal, S3 |
| **Model Serving** | Сервинг моделей для инференса | gRPC, Redis cache |