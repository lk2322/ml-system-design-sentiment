# UML-диаграмма последовательности

## Сценарий: Обработка нового комментария через ИИ-систему

Основной сценарий — автоматическая обработка комментария с высокой уверенностью ИИ (покрывает ≥ 85% случаев).

```mermaid
sequenceDiagram
    actor User as Пользователь
    participant API as API Gateway
    participant CI as Comment Ingestion<br/>Service
    participant K as Apache Kafka
    participant SA as Sentiment Analysis
    participant TD as Toxicity Detection
    participant DE as Decision Engine
    participant PG as PostgreSQL
    participant MG as MongoDB
    participant RD as Redis
    participant ESC as Escalation Service
    participant MOD as Модератор
    participant AN as Analytics Service
    participant CH as ClickHouse
    
    User->>API: POST /api/comments<br/>{post_id, text}
    API->>API: Аутентификация + Rate Limit
    API->>CI: Валидированный запрос
    
    CI->>CI: Валидация и обогащение метаданными
    CI->>MG: Сохранение raw-комментария
    CI->>K: Публикация события<br/>comment.received
    CI-->>API: 202 Accepted<br/>{comment_id, status: "processing"}
    API-->>User: Ответ: комментарий принят
    
    Note over K: Асинхронная обработка
    
    K->>SA: consumer: comment.received
    K->>TD: consumer: comment.received
    
    SA->>RD: Загрузка модели (кэш)
    SA->>SA: Инференс модели тональности
    SA->>K: Публикация sentiment.result
    
    TD->>RD: Загрузка модели (кэш)
    TD->>TD: Инференс модели токсичности
    TD->>K: Публикация toxicity.result
    
    K->>DE: consumer: sentiment.result<br/>+ toxicity.result
    
    DE->>DE: Агрегация оценок<br/>Применение правил и порогов
    
    alt Высокая уверенность — автоматическое решение
        DE->>PG: INSERT moderation_decision<br/>(is_automated=true)
        DE->>K: decision.made
        
        alt Комментарий токсичный → удаление
            DE-->>User: Push: комментарий удалён
        else Комментарий нейтральный/позитивный
            Note over User: Без уведомления
        end
        
    else Низкая уверенность — эскалация
        DE->>PG: INSERT moderation_decision<br/>(is_automated=false, escalated=true)
        DE->>ESC: Эскалация модератору
        ESC->>MOD: Уведомление + подсказки ИИ<br/>(WebSocket/push)
        MOD->>ESC: Решение модератора<br/>(confirm / override / modify)
        ESC->>PG: UPDATE moderation_decision
        ESC->>K: feedback.collected
    end
    
    K->>AN: consumer: decision.made
    AN->>AN: Агрегация метрик
    AN->>CH: INSERT в аналитику
    
    Note over AN: Проверка пороговых правил
    
    alt Всплеск негатива обнаружен
        AN->>AN: Отправка алерта<br/>PR / контент-менеджерам
    end
```

## Сценарий: Дообучение модели на основе фидбека модераторов

```mermaid
sequenceDiagram
    participant MOD as Модератор
    participant FC as Feedback Collector
    participant K as Apache Kafka
    participant PG as PostgreSQL
    participant TP as Training Pipeline
    participant MR as Model Registry
    participant S3 as S3 Storage
    participant MS as Model Serving
    
    MOD->>FC: Подтверждение / отклонение решения ИИ
    FC->>PG: Сохранение DecisionReview
    FC->>K: feedback.collected
    
    K->>TP: consumer: feedback.collected
    TP->>PG: SELECT комментариев + решений<br/>WHERE reviewed = true<br/>AND created_at > last_train
    
    Note over TP: Накопление батча<br/>(минимум 10 000 примеров<br/>или еженедельно)
    
    TP->>TP: Предобработка данных<br/>+ аугментация
    TP->>TP: Дообучение модели<br/>на новом датасете
    
    TP->>TP: Оценка на hold-out<br/>сравнение с текущей моделью
    
    alt F1_NEW > F1_CURRENT + margin
        TP->>MR: Регистрация новой версии модели
        MR->>S3: Сохранение артефактов модели
        MR->>MS: Deploy новой версии<br/>(canary: 10% трафика)
        
        Note over MS: Canary deployment<br/>на 10% трафика
        
        MS->>MS: Мониторинг метрик<br/>canary vs baseline
        
        alt Canary метрики в норме
            MS->>MS: Увеличение до 100%<br/>полное переключение
        else Canary метрики хуже
            MS->>MS: Откат на предыдущую версию
            MR->>MR: Маркировка версии как failed
        end
    else F1_NEW не лучше текущей
        TP->>MR: Логирование неудачной попытки
        Note over TP: Модель не обновляется
    end
```