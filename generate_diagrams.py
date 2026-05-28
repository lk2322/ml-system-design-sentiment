# -*- coding: utf-8 -*-
import os

def create_directory():
    os.makedirs("docs/assets/diagrams", exist_ok=True)

# SVG templates & components
def header(title, subtitle):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 680" width="100%" height="100%">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
    </marker>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="#020617" />
  <rect width="100%" height="100%" fill="url(#grid)" />
  
  <!-- Title -->
  <text x="30" y="40" fill="#f8fafc" font-family="'JetBrains Mono', monospace" font-size="16" font-weight="bold">{title}</text>
  <text x="30" y="60" fill="#94a3b8" font-family="'JetBrains Mono', monospace" font-size="10">{subtitle}</text>
"""

def footer():
    return "\n</svg>"

def block(x, y, w, h, title, sub="", fill="rgba(8, 51, 68, 0.4)", stroke="#22d3ee", lines=None):
    if lines is None:
        lines = []
    # double rect for transparency masking
    svg = f"""
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#0f172a" />
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5" />
  <text x="{x + w/2}" y="{y + 22}" fill="#f1f5f9" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="bold" text-anchor="middle">{title}</text>
  <text x="{x + w/2}" y="{y + 36}" fill="#94a3b8" font-family="'JetBrains Mono', monospace" font-size="8.5" text-anchor="middle">{sub}</text>
"""
    y_off = y + 48
    for line in lines:
        svg += f'  <text x="{x + 12}" y="{y_off}" fill="#e2e8f0" font-family="\'JetBrains Mono\', monospace" font-size="8">{line}</text>\n'
        y_off += 12
    return svg

def connection(x1, y1, x2, y2, label="", stroke="#475569", dash=""):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    svg = f"""
  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="1.5" marker-end="url(#arrowhead)"{dash_attr} />
"""
    if label:
        cx, cy = (x1 + x2)/2, (y1 + y2)/2
        svg += f'  <text x="{cx}" y="{cy - 4}" fill="#94a3b8" font-family="\'JetBrains Mono\', monospace" font-size="8" text-anchor="middle">{label}</text>\n'
    return svg

def text_element(x, y, txt, fill="#94a3b8", size="9", anchor="start", bold=False):
    weight = ' font-weight="bold"' if bold else ""
    return f'  <text x="{x}" y="{y}" fill="{fill}" font-family="\'JetBrains Mono\', monospace" font-size="{size}"{weight} text-anchor="{anchor}">{txt}</text>\n'

# 1. Generate IDEF0 Context (A0) and IDEF0 Decomposition (A1)
def build_idef0():
    # IDEF0 A1: Ingestion, ML Inference, Routing / Queue, Action & Log
    svg = header("IDEF0 A1: ML-Powered Content Moderation Functional Decomposition", "Inputs (L), Controls (T), Mechanisms (B), Outputs (R)")
    
    # Add controls label top
    svg += text_element(500, 30, "CONTROLS: RKN Rules, Internal SLA (<200ms), FZ-152, CPU/GPU Budget", fill="#f43f5e", size="10", anchor="middle", bold=True)
    # Add mechanisms label bottom
    svg += text_element(500, 650, "MECHANISMS: RuBERT (DeepPavlov), Triton Inference Server, Human Moderators, K8s Auto-scalers", fill="#a855f7", size="10", anchor="middle", bold=True)

    # Function Blocks
    # 1. Ingest (x=100, y=140)
    svg += block(100, 140, 150, 80, "A1.1", "Ingest Comment Stream", fill="rgba(8, 51, 68, 0.4)", stroke="#22d3ee", 
                 lines=["• Read 500k/day posts", "• Tokenize & validate", "• Push to Kafka topic"])
    
    # 2. ML Inference (x=330, y=260)
    svg += block(330, 260, 170, 90, "A1.2", "Classify Comment ML", fill="rgba(6, 78, 59, 0.4)", stroke="#34d399", 
                 lines=["• Fine-tuned RuBERT", "• Predict Sentiment & Tox", "• Confidence scoring", "• Triton Server GPU"])
    
    # 3. Route Work Queue (x=580, y=380)
    svg += block(580, 380, 170, 80, "A1.3", "Queue & Route", fill="rgba(120, 53, 15, 0.3)", stroke="#fbbf24", 
                 lines=["• High conf: auto-action", "• Low conf: to humans", "• Redis cache metadata"])
    
    # 4. Action & Log (x=800, y=500)
    svg += block(800, 500, 170, 80, "A1.4", "Action, Log & Retrain", fill="rgba(76, 29, 149, 0.4)", stroke="#a78bfa", 
                 lines=["• Hide/ban on platforms", "• Analytics in ClickHouse", "• Active learning data"])

    # Connections - Inputs from left
    svg += connection(20, 180, 95, 180, "Raw Comments Stream")
    
    # Connect block 1 to 2
    svg += connection(250, 180, 330, 305, "Validated Comments")
    svg += connection(175, 220, 175, 420, "Metadata Log", stroke="#94a3b8")
    svg += connection(175, 420, 575, 420)
    
    # Connect block 2 to 3
    svg += connection(500, 305, 575, 410, "Inference Output")
    
    # Connect block 3 to 4
    svg += connection(750, 420, 795, 540, "Moderation Task")
    
    # Direct auto-actions (bypass block 3 human queue)
    svg += connection(500, 290, 885, 290, "Auto-Action Signal", stroke="#10b981")
    svg += connection(885, 290, 885, 495)
    
    # Outputs to right
    svg += connection(970, 540, 1020, 540, "Action / Audit Record")
    svg += text_element(920, 530, "Moderated DB", fill="#a78bfa", size="8")
    
    # Controls connections (from top to each block)
    svg += connection(175, 45, 175, 135, stroke="#f43f5e", dash="4,4")
    svg += connection(415, 45, 415, 255, stroke="#f43f5e", dash="4,4")
    svg += connection(665, 45, 665, 375, stroke="#f43f5e", dash="4,4")
    svg += connection(885, 45, 885, 495, stroke="#f43f5e", dash="4,4")
    
    # Mechanisms connections (from bottom to each block)
    svg += connection(175, 635, 175, 225, stroke="#a855f7", dash="2,2")
    svg += connection(415, 635, 415, 355, stroke="#a855f7", dash="2,2")
    svg += connection(665, 635, 665, 465, stroke="#a855f7", dash="2,2")
    svg += connection(885, 635, 885, 585, stroke="#a855f7", dash="2,2")

    svg += footer()
    
    path = "docs/assets/diagrams/idef0_a1.svg"
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Built IDEF0: {path}")

# 2. Build BPMN TO-BE Process
def build_bpmn_to_be():
    svg = header("BPMN 2.0 TO-BE Process: Automated Comment Pipeline & Human Escalation", "Lanes: User, Frontend System, ML Pipeline, Human Moderator")
    
    # Draw horizontal swimlane lines
    svg += f"""
  <line x1="120" y1="80" x2="980" y2="80" stroke="#334155" stroke-width="1" />
  <line x1="120" y1="210" x2="980" y2="210" stroke="#334155" stroke-width="1" />
  <line x1="120" y1="360" x2="980" y2="360" stroke="#334155" stroke-width="1" />
  <line x1="120" y1="510" x2="980" y2="510" stroke="#334155" stroke-width="1" />
  <line x1="120" y1="640" x2="980" y2="640" stroke="#334155" stroke-width="1" />
 stream line
"""
    # Swimlane vertical divider
    svg += '<line x1="120" y1="80" x2="120" y2="640" stroke="#334155" stroke-width="2" />\n'
    
    # Swimlane titles
    svg += text_element(40, 145, "User", fill="#f8fafc", size="12", anchor="left", bold=True)
    svg += text_element(40, 285, "API / PubSub", fill="#f8fafc", size="12", anchor="left", bold=True)
    svg += text_element(40, 435, "ML Engine", fill="#f8fafc", size="12", anchor="left", bold=True)
    svg += text_element(40, 575, "Moderator", fill="#f8fafc", size="12", anchor="left", bold=True)
    
    # BPMN Elements
    # Start Event (circle)
    svg += '  <circle cx="160" cy="140" r="15" fill="none" stroke="#22c55e" stroke-width="2" />\n'
    svg += '  <circle cx="160" cy="140" r="6" fill="#22c55e" />\n'
    svg += text_element(160, 170, "Write comment", fill="#94a3b8", size="8", anchor="middle")
    
    # Task 1: API Receives (x=220, y=250)
    svg += block(210, 245, 110, 50, "Accept Comment", "API / Kafka Ingest", fill="rgba(8, 51, 68, 0.3)", stroke="#22d3ee")
    svg += connection(175, 140, 210, 270, "Comment POST")
    
    # Task 2: ML Process (x=360, y=395)
    svg += block(350, 395, 110, 55, "ML Classify", "RuBERT Inference", fill="rgba(6, 78, 59, 0.3)", stroke="#34d399")
    svg += connection(320, 270, 350, 420, "Stream event")
    
    # Gateway (diamond) for Toxicity & Confidence check (x=505, y=395)
    gw_x, gw_y = 530, 422
    svg += f"""
  <polygon points="{gw_x} {gw_y - 20}, {gw_x + 25} {gw_y}, {gw_x} {gw_y + 20}, {gw_x - 25} {gw_y}" fill="none" stroke="#fbbf24" stroke-width="2" />
"""
    svg += text_element(gw_x, gw_y - 25, "Is Confident?", fill="#fbbf24", size="8", anchor="middle")
    svg += connection(460, 422, 505, 422)

    # Route: Highly Confident & Toxic -> Auto hide (x=600, y=245)
    svg += block(590, 245, 110, 50, "Auto-Hide", "Flag DB / Update UI", fill="rgba(136, 19, 55, 0.3)", stroke="#fb7185")
    svg += connection(530, 402, 530, 270, "High Conf / Toxic")
    svg += connection(530, 270, 590, 270)
    
    # End Event for highly toxic (x=750, y=270)
    svg += '  <circle cx="760" cy="270" r="15" fill="none" stroke="#ef4444" stroke-width="3" />\n'
    svg += text_element(760, 300, "Hidden & Logged", fill="#ef4444", size="8", anchor="middle")
    svg += connection(700, 270, 745, 270)
    
    # Route: Low Confidence -> Escalation task (x=590, y=542)
    svg += block(590, 542, 120, 55, "Human Review", "Moderator Panel UI", fill="rgba(120, 53, 15, 0.3)", stroke="#fbbf24")
    svg += connection(555, 422, 590, 570, "Low Conf", stroke="#fbbf24")
    
    # Gateway for human choice (x=770, y=570)
    hgw_x, hgw_y = 780, 570
    svg += f"""
  <polygon points="{hgw_x} {hgw_y - 20}, {hgw_x + 25} {hgw_y}, {hgw_x} {hgw_y + 20}, {hgw_x - 25} {hgw_y}" fill="none" stroke="#fbbf24" stroke-width="2" />
"""
    svg += text_element(hgw_x, hgw_y - 25, "Approve?", fill="#fbbf24", size="8", anchor="middle")
    svg += connection(710, 570, 755, 570)
    
    # Target content system (approved/safe) (x=850, y=245)
    svg += block(850, 245, 110, 50, "Publish", "Render to users", fill="rgba(6, 78, 59, 0.3)", stroke="#34d399")
    
    # Connect High Conf & OK to Publish
    svg += connection(555, 422, 850, 270, "High Conf / OK", stroke="#34d399")
    
    # Connect human approval -> Publish
    svg += connection(780, 550, 780, 290, "YES")
    svg += connection(780, 290, 850, 290)
    
    # Connect human rejection -> Auto-hide
    svg += connection(805, 570, 830, 570)
    svg += connection(830, 570, 830, 310)
    svg += connection(830, 310, 680, 310)
    svg += connection(680, 310, 680, 295)
    svg += text_element(845, 565, "NO", fill="#fb7185", size="8")
    
    # Connect human check to ML active-learning log
    svg += block(730, 420, 110, 45, "Log Feedback", "Active Learning", fill="rgba(76, 29, 149, 0.3)", stroke="#a78bfa")
    svg += connection(780, 550, 780, 465, "Action logged", stroke="#a78bfa", dash="2,2")
    
    # Final End Event (circle for normal finish)
    svg += '  <circle cx="910" cy="140" r="15" fill="none" stroke="#000" stroke-width="1" />\n'
    svg += '  <circle cx="910" cy="140" r="12" fill="none" stroke="#10b981" stroke-width="2" />\n'
    svg += text_element(910, 170, "Published", fill="#10b981", size="8", anchor="middle")
    svg += connection(905, 245, 905, 155)

    svg += footer()
    path = "docs/assets/diagrams/bpmn_to_be.svg"
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Built BPMN: {path}")

# 3. Build DB / ER Diagram
def build_er_diagram():
    svg = header("Relational and Analytical Data Schema (Hybrid OLTP/OLAP)", "Primary storage (PostgreSQL, sharded) & Cold Analytics (ClickHouse)")
    
    # Define entities
    # 1. users
    svg += block(50, 120, 220, 150, "users (PostgreSQL Sharded)", "Primary key: id", fill="rgba(8, 51, 68, 0.4)", stroke="#22d3ee", lines=[
        "id: VARCHAR(36) [PK]",
        "username: VARCHAR(64) [UNIQUE]",
        "reputation: FLOAT [DEFAULT 1.0]",
        "registration_date: TIMESTAMP",
        "status: VARCHAR(20) [active/banned]",
        "platform_id: VARCHAR(36)"
    ])
    
    # 2. comments
    svg += block(380, 120, 240, 170, "comments (PostgreSQL Sharded)", "Shard Key: user_id", fill="rgba(8, 51, 68, 0.4)", stroke="#22d3ee", lines=[
        "id: VARCHAR(36) [PK]",
        "user_id: VARCHAR(36) [FK -> users.id]",
        "content: TEXT [UTF-8, Unmasked]",
        "created_at: TIMESTAMP [INDEX]",
        "post_id: VARCHAR(36)",
        "platform_id: VARCHAR(36)",
        "status: VARCHAR(20) [approved/hidden]"
    ])
    
    # 3. ml_sentiment_results
    svg += block(720, 120, 240, 160, "ml_sentiment_results", "FK: comment_id", fill="rgba(6, 78, 59, 0.4)", stroke="#34d399", lines=[
        "id: VARCHAR(36) [PK]",
        "comment_id: VARCHAR(36) [FK -> comments.id]",
        "toxicity_score: FLOAT",
        "label: VARCHAR(16) [toxic/threat/neutral]",
        "confidence: FLOAT",
        "processed_at: TIMESTAMP",
        "model_version: VARCHAR(32)"
    ])
    
    # 4. moderation_actions
    svg += block(200, 380, 260, 160, "moderation_actions", "History Logs", fill="rgba(120, 53, 15, 0.3)", stroke="#fbbf24", lines=[
        "id: VARCHAR(36) [PK]",
        "comment_id: VARCHAR(36) [FK -> comments.id]",
        "action_type: VARCHAR(24) [auto_hide/manual]",
        "reason: VARCHAR(128)",
        "moderator_id: VARCHAR(36) [NULL for AI]",
        "executed_at: TIMESTAMP [INDEX]"
    ])

    # 5. moderation_analytics (ClickHouse Columnar OLAP)
    svg += block(580, 380, 280, 180, "moderation_analytics (ClickHouse)", "Engine: MergeTree ORDER BY date", fill="rgba(76, 29, 149, 0.4)", stroke="#a78bfa", lines=[
        "date: Date [PARTITION KEY]",
        "comment_id: String",
        "user_id: String",
        "toxicity_score: Float32",
        "sentiment_label: LowCardinality(String)",
        "action_type: LowCardinality(String)",
        "processing_latency_ms: UInt32",
        "platform_id: String",
        "timestamp: DateTime"
    ])

    # Relationships as lines
    # users -> comments (1:N)
    svg += "  <!-- Users -> Comments -->\n"
    svg += '  <path d="M 270 195 L 380 195" stroke="#22d3ee" stroke-width="1.5" />\n'
    svg += text_element(280, 190, "1", fill="#22d3ee", size="9")
    svg += text_element(365, 190, "0..*", fill="#22d3ee", size="9")
    
    # comments -> ml_sentiment_results (1:1)
    svg += "  <!-- Comments -> ML Results -->\n"
    svg += '  <path d="M 620 200 L 720 200" stroke="#34d399" stroke-width="1.5" />\n'
    svg += text_element(628, 195, "1", fill="#34d399", size="9")
    svg += text_element(705, 195, "1", fill="#34d399", size="9")
    
    # comments -> moderation_actions (1:N)
    svg += "  <!-- Comments -> Moderation Actions -->\n"
    svg += '  <path d="M 440 290 L 440 330 L 330 330 L 330 380" fill="none" stroke="#fbbf24" stroke-width="1.5" />\n'
    svg += text_element(445, 305, "1", fill="#fbbf24", size="9")
    svg += text_element(315, 375, "0..*", fill="#fbbf24", size="9")
    
    # comments & ML -> ClickHouse OLAP (Replica sync/ETL)
    svg += "  <!-- ETL to ClickHouse -->\n"
    svg += '  <path d="M 500 290 L 500 350 L 720 350 L 720 380" fill="none" stroke="#a78bfa" stroke-width="1.5" stroke-dasharray="4,4" />\n'
    svg += text_element(540, 345, "ETL / Kafka Engine", fill="#a78bfa", size="8")

    svg += footer()
    path = "docs/assets/diagrams/er_diagram.svg"
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Built ER: {path}")

# 4. Build Distributed Storage Architecture Map
def build_dist_arch():
    svg = header("Distributed Storage & Real-Time Processing Architecture Map", "Showing separate read/write paths, messaging clusters and target layers")
    
    # Boundary: K8s / Service Cluster
    svg += """
  <rect x="50" y="80" width="900" height="570" rx="12" fill="rgba(15, 23, 42, 0.1)" stroke="#475569" stroke-width="1.5" stroke-dasharray="8,4" />
"""
    svg += text_element(65, 100, "COGNITIVE MODERATION PLATFORM CONTEXT (K8s CLUSTER)", fill="#94a3b8", size="11", bold=True)

    # 1. API Ingestion Pods (FastAPI)
    svg += block(80, 140, 160, 80, "API Gateway / Ingest", "Uvicorn FastAPIs", fill="rgba(8, 51, 68, 0.4)", stroke="#22d3ee", lines=[
        "• Handle webhook spikes",
        "• Client auth & validation",
        "• High throughput HTTP"
    ])
    
    # 2. Redis Cache
    svg += block(80, 310, 160, 75, "Redis Broker/Cache", "In-Memory Storage", fill="rgba(136, 19, 55, 0.4)", stroke="#fb7185", lines=[
        "• Deduplication locks",
        "• Rate-limiting counts",
        "• Pub/Sub state cache"
    ])
    
    # Connect API to Redis
    svg += connection(160, 220, 160, 305, "Cache lookup")

    # 3. Message Queue: Kafka Clusters
    svg += block(320, 140, 180, 90, "Kafka Cluster", "Streaming Event Bus", fill="rgba(120, 53, 15, 0.3)", stroke="#fbbf24", lines=[
        "• Topic: raw_comments (3 shards)",
        "• Topic: verified_predictions",
        "• Partitioned by user_id",
        "• Persistent repl factor: 3"
    ])
    svg += connection(240, 180, 315, 180, "Publish JSON")

    # 4. ML Inference Worker pods
    svg += block(580, 140, 190, 95, "ML Worker Pipeline", "RuBERT Inference", fill="rgba(6, 78, 59, 0.4)", stroke="#34d399", lines=[
        "• Pull raw_comments",
        "• Batch size 32",
        "• Triton GPU Server client",
        "• Auto-scalaing by K8s HPA"
    ])
    svg += connection(500, 180, 575, 180, "Consume Task")
    
    # 5. Sharded PostgreSQL
    svg += block(320, 340, 180, 100, "Sharded PostgreSQL", "Transactional DB", fill="rgba(8, 51, 68, 0.4)", stroke="#22d3ee", lines=[
        "• Node A: users A-M",
        "• Node B: users N-Z",
        "• Primary OLTP engine",
        "• ACID Compliant record"
    ])
    svg += connection(160, 385, 315, 385, "Write/Read User Meta")
    svg += connection(410, 230, 410, 335, "Sync/Ack")

    # 6. ClickHouse Analytics Cluster
    svg += block(580, 340, 190, 100, "ClickHouse Analytics", "Columnar OLAP Engine", fill="rgba(76, 29, 149, 0.4)", stroke="#a78bfa", lines=[
        "• MergeTree engine tables",
        "• Low latency aggregates",
        "• High speed log query",
        "• Read-only dashboards"
    ])
    svg += connection(675, 235, 675, 335, "Stream predictions")

    # 7. Elasticsearch node
    svg += block(800, 340, 140, 100, "Elasticsearch", "Context Search", fill="rgba(120, 53, 15, 0.3)", stroke="#fbbf24", lines=[
        "• Full-text indexes",
        "• Fuzzy search",
        "• Audit queues"
    ])
    svg += connection(770, 195, 870, 195)
    svg += connection(870, 195, 870, 335, "Index toxic texts")

    # 8. Admin & Compliance Portal
    svg += block(320, 520, 450, 80, "Compliance Audit Portal & Active Learning ETL", "Next.js / Celery backend on Python 3.11", fill="rgba(30, 41, 59, 0.5)", stroke="#94a3b8", lines=[
        "• Manual mod queue from low confidence results",
        "• ClickHouse logs querying for RKN compliance SLA auditing",
        "• Relabeling feedback pipeline to trigger retraining (MLflow registry updates)"
    ])
    
    # Connections to Compliance Portal
    svg += connection(410, 440, 410, 515, "Fetch tasks/Save changes")
    svg += connection(675, 440, 675, 515, "Query metrics", stroke="#a78bfa")
    
    svg += footer()
    path = "docs/assets/diagrams/system_architecture.svg"
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Built Dist Architecture: {path}")

# 5. UML Diagrams (Combines Component & Sequence)
def build_uml_diagrams():
    svg = header("UML Package Components and Class System Map", "Microservice packaging scope and precise OOP structural representation")
    
    # System Component diagram subgraph
    svg += """
  <rect x="40" y="80" width="440" height="560" rx="8" fill="rgba(15, 23, 42, 0.1)" stroke="#34d399" stroke-width="1.5" />
"""
    svg += text_element(50, 102, "UML COMPONENT DIAGRAM", fill="#34d399", size="11", bold=True)
    
    # Ingestion Component
    svg += block(70, 130, 170, 85, "&lt;&lt;component&gt;&gt;\nIngestionService", "REST API FastAPI", fill="rgba(8, 51, 68, 0.4)", stroke="#22d3ee", lines=[
        "• raw_comments POST",
        "• healthcheck GET"
    ])
    # ML Worker Component
    svg += block(280, 130, 170, 85, "&lt;&lt;component&gt;&gt;\nMLInferenceWorker", "Kafka Stream Consumer", fill="rgba(6, 78, 59, 0.4)", stroke="#34d399", lines=[
        "• comment processing",
        "• batching classifier"
    ])
    svg += connection(240, 175, 275, 175, "Kafka Queue")

    # DB manager Component
    svg += block(175, 280, 180, 90, "&lt;&lt;component&gt;&gt;\nDataStorageManager", "SQLModel Connections", fill="rgba(120, 53, 15, 0.3)", stroke="#fbbf24", lines=[
        "• Postgres pooler",
        "• ClickHouse driver",
        "• Elasticsearch engine"
    ])
    svg += connection(155, 215, 220, 275)
    svg += connection(365, 215, 310, 275)

    # Compliance Portal Component
    svg += block(175, 430, 180, 90, "&lt;&lt;component&gt;&gt;\nModerationDashboard", "NextJS / Web Portal", fill="rgba(76, 29, 149, 0.4)", stroke="#a78bfa", lines=[
        "• Task manager",
        "• Audit dashboard",
        "• Active learning portal"
    ])
    svg += connection(265, 370, 265, 425)

    # Class OOP details graph
    svg += """
  <rect x="510" y="80" width="450" height="560" rx="8" fill="rgba(15, 23, 42, 0.1)" stroke="#a78bfa" stroke-width="1.5" />
"""
    svg += text_element(520, 102, "UML CLASS DIAGRAM (ML PIPELINE)", fill="#a78bfa", size="11", bold=True)

    # Class 1: CommentIngestor
    svg += block(530, 130, 190, 100, "CommentIngestor", "API Endpoint Handler", fill="rgba(8, 51, 68, 0.4)", stroke="#22d3ee", lines=[
        "+ validate_payload(comment)",
        "+ publish_to_kafka(payload)",
        "- db_pool: PostgresPool",
        "- auth_provider: JWTAuth"
    ])

    # Class 2: ClassifierEngine
    svg += block(750, 130, 190, 110, "ClassifierEngine", "Model Inference Orchestrator", fill="rgba(6, 78, 59, 0.4)", stroke="#34d399", lines=[
        "+ predict_sentiment(text)",
        "+ get_toxicity_score(text)",
        "- load_triton_config()",
        "- tokenizer: RuBertTokenizer",
        "- model_version: String"
    ])

    # Class 3: ModerationManager
    svg += block(640, 310, 210, 120, "ModerationActionManager", "Orchestrates actions", fill="rgba(120, 53, 15, 0.3)", stroke="#fbbf24", lines=[
        "+ apply_auto_hide(comment_id)",
        "+ escalate_to_human(comment_id)",
        "+ log_action(audit_record)",
        "- pg_session: Session",
        "- ch_client: ClickHouseClient",
        "- es_client: ESClient"
    ])

    # Class connections
    svg += connection(625, 230, 690, 305)
    svg += connection(845, 240, 770, 305)

    svg += footer()
    path = "docs/assets/diagrams/uml_components.svg"
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Built UML Components & Classes: {path}")

# 6. Behavioral UML Diagrams (UML Sequence & UML Activity)
def build_uml_behavioral():
    svg = header("Behavioral Activity & Stream Processing Sequence Chart", "Chronological workflows and state progression paths")
    
    # Left Box: Activity flow
    svg += """
  <rect x="40" y="80" width="400" height="560" rx="8" fill="rgba(15, 23, 42, 0.1)" stroke="#fbbf24" stroke-width="1.5" />
"""
    svg += text_element(50, 102, "UML ACTIVITY DIAGRAM", fill="#fbbf24", size="11", bold=True)
    
    # Activity nodes
    # Start node (black circles)
    svg += '  <circle cx="240" cy="130" r="10" fill="#22c55e" />\n'
    
    # Action 1: Receive
    svg += block(160, 160, 160, 45, "Comment posted", "Async HTTP Influx", fill="rgba(8, 51, 68, 0.3)", stroke="#22d3ee")
    svg += connection(240, 140, 240, 155)
    
    # Action 2: Model class
    svg += block(150, 240, 180, 50, "Compute Sentiment/Tox", "Inference Worker", fill="rgba(6, 78, 59, 0.4)", stroke="#34d399")
    svg += connection(240, 205, 240, 235)

    # Activity Decision diamond (x=240, y=340)
    dc_x, dc_y = 240, 335
    svg += f"""
  <polygon points="{dc_x} {dc_y - 15}, {dc_x + 20} {dc_y}, {dc_x} {dc_y + 15}, {dc_x - 20} {dc_y}" fill="none" stroke="#fbbf24" stroke-width="1.5" />
"""
    svg += text_element(dc_x, dc_y - 20, "Conf &gt; 0.85?", fill="#fbbf24", size="8.5", anchor="middle")
    svg += connection(240, 290, 240, 320)

    # Decision branches
    # YES: Hide if negative (x=240, y=410)
    svg += block(70, 400, 150, 50, "Apply Auto-Hide", "High confident Toxic", fill="rgba(136, 19, 55, 0.3)", stroke="#fb7185")
    svg += connection(220, 335, 145, 335)
    svg += connection(145, 335, 145, 395, "YES")
    
    # NO: human review (x=240, y=410)
    svg += block(260, 400, 155, 50, "Escalate User Queue", "Low sentiment confidence", fill="rgba(120, 53, 15, 0.3)", stroke="#fbbf24")
    svg += connection(260, 335, 330, 335)
    svg += connection(330, 335, 330, 395, "NO")

    # Joint node (thick horizontal bar) (x=100-380, y=485)
    svg += '  <rect x="80" y="480" width="320" height="6" rx="3" fill="#64748b" />\n'
    svg += connection(145, 450, 145, 478)
    svg += connection(330, 450, 330, 478)

    # Action 4: Analytics
    svg += block(160, 510, 160, 45, "Write Analytics Log", "Log to ClickHouse", fill="rgba(76, 29, 149, 0.4)", stroke="#a78bfa")
    svg += connection(240, 486, 240, 505)

    # End node (bullseye)
    svg += '  <circle cx="240" cy="595" r="12" fill="none" stroke="#ef4444" stroke-width="2" />\n'
    svg += '  <circle cx="240" cy="595" r="6" fill="#ef4444" />\n'
    svg += connection(240, 555, 240, 580)


    # Right Box: Sequence Chart
    svg += """
  <rect x="470" y="80" width="490" height="560" rx="8" fill="rgba(15, 23, 42, 0.1)" stroke="#a78bfa" stroke-width="1.5" />
"""
    svg += text_element(480, 102, "UML SEQUENCE DIAGRAM", fill="#a78bfa", size="11", bold=True)

    # Lifelines
    svg += text_element(510, 130, "User", fill="#f8fafc", size="9", bold=True)
    svg += '<line x1="530" y1="140" x2="530" y2="600" stroke="#475569" stroke-width="1" stroke-dasharray="4,4" />\n'

    svg += text_element(610, 130, "API Gateway", fill="#f8fafc", size="9", bold=True)
    svg += '<line x1="650" y1="140" x2="650" y2="600" stroke="#475569" stroke-width="1" stroke-dasharray="4,4" />\n'

    svg += text_element(710, 130, "Kafka Queue", fill="#f8fafc", size="9", bold=True)
    svg += '<line x1="750" y1="140" x2="750" y2="600" stroke="#475569" stroke-width="1" stroke-dasharray="4,4" />\n'

    svg += text_element(810, 130, "ML Worker", fill="#f8fafc", size="9", bold=True)
    svg += '<line x1="850" y1="140" x2="850" y2="600" stroke="#475569" stroke-width="1" stroke-dasharray="4,4" />\n'

    svg += text_element(910, 130, "ClickHouse", fill="#f8fafc", size="9", bold=True)
    svg += '<line x1="940" y1="140" x2="940" y2="600" stroke="#475569" stroke-width="1" stroke-dasharray="4,4" />\n'

    # Messages
    # User -> API
    svg += connection(530, 175, 646, 175, "POST comment")
    # API -> Kafka
    svg += connection(650, 205, 746, 205, "enqueue comment")
    # API -> User (202 Accepted)
    svg += connection(650, 235, 534, 235, "202 Accepted")
    
    # Kafka -> ML Worker
    svg += connection(750, 280, 846, 280, "comment event")
    # ML Worker processes (Self loop)
    svg += '  <path d="M 850 310 L 880 310 L 880 340 L 853 340" fill="none" stroke="#34d399" stroke-width="1.5" marker-end="url(#arrowhead)" />\n'
    svg += text_element(885, 328, "Run RuBERT", fill="#34d399", size="8")

    # ML Worker -> DB / ClickHouse
    svg += connection(850, 390, 936, 390, "INSERT log")
    # ML Worker -> API (to hide) if toxic
    svg += connection(850, 440, 654, 440, "hide comment request", stroke="#fb7185")

    sv_b_x = 490
    svg += f"""
  <rect x="{sv_b_x}" y="475" width="455" height="110" rx="4" fill="rgba(244, 63, 94, 0.05)" stroke="#fb7185" stroke-width="1" stroke-dasharray="2,2" />
"""
    svg += text_element(sv_b_x + 10, 492, "alt: low confidence", fill="#fb7185", size="8", bold=True)
    
    # ML Worker -> Manual queue (ClickHouse task)
    svg += connection(850, 520, 654, 520, "enqueue human moderate")
    svg += connection(650, 555, 534, 555, "render placeholder")

    svg += footer()
    path = "docs/assets/diagrams/uml_behavioral.svg"
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Built UML Behavioral diagrams: {path}")


if __name__ == "__main__":
    create_directory()
    build_idef0()
    build_bpmn_to_be()
    build_er_diagram()
    build_dist_arch()
    build_uml_diagrams()
    build_uml_behavioral()
