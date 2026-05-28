# UML-диаграмма компонентов системы

## Описание

Диаграмма компонентов показывает архитектурное разбиение системы на модули, их интерфейсы и зависимости. Каждый компонент отвечает за отдельную бизнес-область и communicates через определённые контракты.

## Диаграмма компонентов

```mermaid
graph TB
    subgraph Frontend["Слой представления"]
        WebUI[Web Client]
        ModDash[Moderator Dashboard]
        AnDash[Analytics Dashboard]
    end

    subgraph Gateway["API-шлюз"]
        APIGW[API Gateway]
    end

    subgraph Backend["Бэкенд-сервисы"]
        CS[Comment Service<br/>––––––––<br/>+ createComment()<br/>+ getComments()<br/>+ deleteComment()]
        PS[Post Service<br/>––––––––<br/>+ getPost()<br/>+ listPosts()]
        MS[Moderation Service<br/>––––––––<br/>+ reviewAction()<br/>+ getQueue()<br/>+ overrideDecision()]
        US[User Service<br/>––––––––<br/>+ getUser()<br/>+ updateTrustScore()]
        AS[Analytics Service<br/>––––––––<br/>+ getSentimentTrends()<br/>+ getModerationStats()]
    end

    subgraph MLCore["ML-ядро"]
        IS[Inference Service<br/>––––––––<br/>+ predictSentiment()<br/>+ predictToxicity()<br/>+ healthCheck()]
        RP[Retraining Pipeline<br/>––––––––<br/>+ collectFeedback()<br/>+ trainModel()<br/>+ deployModel()]
        PP[Preprocessing Module<br/>––––––––<br/>+ normalizeText()<br/>+ tokenize()<br/>+ generateEmbedding()]
    end

    subgraph Infrastructure["Инфраструктура"]
        MQ[Message Queue<br/>Kafka]
        PG[(PostgreSQL)]
        CH[(ClickHouse)]
        S3[(S3 Storage)]
        RD[(Redis)]
    end

    WebUI --> APIGW
    ModDash --> APIGW
    AnDash --> APIGW

    APIGW --> CS
    APIGW --> PS
    APIGW --> MS
    APIGW --> US
    APIGW --> AS

    CS --> MQ
    MS --> MQ
    CS --> PG
    PS --> PG
    US --> PG
    MS --> PG

    MQ --> PP
    PP --> IS
    IS --> CH
    IS --> PG
    IS --> RD

    MQ --> MS
    RP --> S3
    RP --> IS
    IS --> S3

    AS --> CH
    AS --> PG

    style Frontend fill:#e3f2fd
    style Gateway fill:#fff3e0
    style Backend fill:#e8f5e9
    style MLCore fill:#f3e5f5
    style Infrastructure fill:#fce4ec
```

## UML-диаграмма классов (ключевые сущности ML-ядра)

```mermaid
classDiagram
    class SentimentAnalyzer {
        +model: SentimentModel
        +tokenizer: Tokenizer
        +predict(comment: Comment) SentimentResult
        +predict_batch(comments: list~Comment~) list~SentimentResult~
        +warm_up()
    }

    class SentimentModel {
        +model_id: str
        +version: str
        +framework: str
        +threshold_negativity: float
        +threshold_toxicity: float
        +load_from_s3(path: str)
        +predict(embedding: Tensor) Prediction
    }

    class SentimentResult {
        +comment_id: UUID
        +negativity_score: float
        +toxicity_score: float
        +sentiment_label: SentimentLabel
        +confidence: float
        +model_version: str
        +to_dict() dict
    }

    class SentimentLabel {
        <<enumeration>>
        POSITIVE
        NEUTRAL
        NEGATIVE_LOW
        NEGATIVE_HIGH
        TOXIC
    }

    class FeedbackCollector {
        +collect(signal: FeedbackSignal)
        +get_training_data(window: TimeWindow) DataFrame
        +compute_label_distribution() dict
    }

    class FeedbackSignal {
        +signal_id: UUID
        +comment_id: UUID
        +signal_type: SignalType
        +source_user_id: UUID
        +reason: str
        +created_at: datetime
    }

    class SignalType {
        <<enumeration>>
        MODERATOR_OVERRIDE
        USER_APPEAL
        RKN_COMPLAINT
        FALSE_POSITIVE
    }

    class RetrainingPipeline {
        +collector: FeedbackCollector
        +trainer: ModelTrainer
        +validator: ModelValidator
        +deployer: ModelDeployer
        +run_pipeline()
        +schedule_cron(expr: str)
    }

    class ModelTrainer {
        +base_model: str
        +hyperparams: dict
        +train(data: DataFrame) ModelArtifact
        +evaluate(model: ModelArtifact) Metrics
    }

    class ModelDeployer {
        +deploy(model: ModelArtifact) str
        +rollback(version: str)
        +canary_deploy(model: ModelArtifact, traffic_pct: int)
    }

    SentimentAnalyzer --> SentimentModel : uses
    SentimentAnalyzer --> SentimentResult : produces
    SentimentResult --> SentimentLabel : has
    RetrainingPipeline --> FeedbackCollector : uses
    RetrainingPipeline --> ModelTrainer : orchestrates
    RetrainingPipeline --> ModelDeployer : orchestrates
    FeedbackCollector --> FeedbackSignal : collects
    FeedbackSignal --> SignalType : has
    SentimentModel ..> ModelDeployer : deployed by
```