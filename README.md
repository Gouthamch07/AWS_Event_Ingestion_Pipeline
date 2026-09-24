# AWS Event Ingestion Pipeline

Serverless event ingestion: raw events land in S3, get validated by Lambda consumers,
routed to curated storage or quarantined with alerts, and analyzed with Athena SQL.

## Architecture

```mermaid
flowchart TB
    P[Producers] -->|upload| S0[(S3: raw/)]
    S0 -->|event notification| Q[SQS]
    Q --> L[Lambda: validate + transform]
    L -->|valid| S1[(S3: curated/)]
    L -->|invalid| S2[(S3: quarantine/)]
    L -->|alert| N[SNS]
    S1 --> A[Athena]
```

## Status

- [x] Event generator + S3 raw landing
- [x] Lambda validation, quarantine routing, SNS alerting
- [x] Athena external table + pytest validation suite
- [ ] CDC with SCD Type 2 dimensions (in progress)
