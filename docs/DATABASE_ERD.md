# Implemented data model

```mermaid
erDiagram
    users {
        string id PK
    }
    career_profiles {
        string id PK
    }
    preference_facts {
        string id PK
    }
    conversation_threads {
        string id PK
    }
    messages {
        string id PK
    }
    tool_invocations {
        string id PK
    }
    approval_requests {
        string id PK
    }
    audit_events {
        string id PK
    }
    users ||--o{ preference_facts : owns
    users ||--o{ conversation_threads : owns
    conversation_threads ||--o{ messages : contains
    users ||--o{ approval_requests : reviews
```

This diagram shows implemented tables only. See source for actual field types and keys; gate_policies and index_state use integer singleton keys. Full master-prompt normalization remains pending where documented in README. No invented schema is presented as implemented.
