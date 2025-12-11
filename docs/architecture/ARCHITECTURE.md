# System Architecture

## Safe Money Toolkit - Architecture Deep Dive

---

## 1. Architecture Principles

### Design Philosophy

1. **Modularity First**: Each component is independently deployable and testable
2. **Security by Default**: Zero-trust architecture with defense in depth
3. **User Data Sovereignty**: Users own their data; easy export, deletion, and portability
4. **Graceful Degradation**: System remains functional even when components fail
5. **Cost Efficiency**: Leverage serverless and pay-per-use where possible

### Technology Decisions Rationale

| Decision | Rationale |
|----------|-----------|
| **Supabase over Firebase** | PostgreSQL power, better RLS, open source, no vendor lock-in |
| **Lovable for Frontend** | Rapid development, built-in hosting, React-based ecosystem |
| **N8N over Zapier** | Self-hostable, more complex logic support, cost-effective at scale |
| **Edge Functions over traditional servers** | Low latency, auto-scaling, reduced infrastructure management |

---

## 2. Detailed System Architecture

### 2.1 Client Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND APPLICATION                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        PRESENTATION LAYER                            │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Pages/Views          Components           UI Library               │   │
│  │  ├── Dashboard        ├── Charts           ├── shadcn/ui           │   │
│  │  ├── Onboarding       ├── Forms            ├── Tailwind CSS        │   │
│  │  ├── Strategy         ├── Tables           ├── Radix Primitives    │   │
│  │  ├── Progress         ├── Whiteboard       └────────────────────   │   │
│  │  ├── Education        ├── Chat Interface                           │   │
│  │  ├── Settings         └── Notifications                            │   │
│  │  └── Profile                                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┴───────────────────────────────────┐   │
│  │                         STATE LAYER                                  │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Client State (Zustand)         Server State (TanStack Query)       │   │
│  │  ├── UI State                   ├── User Profile                    │   │
│  │  ├── Form State                 ├── Financial Data                  │   │
│  │  ├── Modal/Dialog State         ├── Strategy Results                │   │
│  │  └── Theme Preferences          ├── Chat History                    │   │
│  │                                 └── Notifications                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┴───────────────────────────────────┐   │
│  │                        SERVICE LAYER                                 │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  API Client             Auth Service           Storage Service       │   │
│  │  ├── Supabase Client    ├── Login/Logout       ├── File Upload      │   │
│  │  ├── Edge Function      ├── Token Refresh      ├── File Download    │   │
│  │  │   Calls              ├── Session Mgmt       └── Presigned URLs   │   │
│  │  └── Error Handling     └── MFA Flow                                │   │
│  │                                                                      │   │
│  │  Calculation Service    Realtime Service                            │   │
│  │  ├── Local Previews     ├── Subscription Mgmt                       │   │
│  │  ├── Validation         ├── Live Updates                            │   │
│  │  └── Formatting         └── Presence (future)                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Backend Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SUPABASE LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EDGE FUNCTIONS (Deno)                             │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  /api/onboarding                /api/strategy                       │   │
│  │  ├── POST /profile              ├── POST /generate                  │   │
│  │  ├── POST /upload-spreadsheet   ├── GET /current                    │   │
│  │  ├── POST /validate-data        ├── PUT /update                     │   │
│  │  └── GET /status                └── POST /what-if                   │   │
│  │                                                                      │   │
│  │  /api/coaching                  /api/progress                       │   │
│  │  ├── POST /chat                 ├── GET /summary                    │   │
│  │  ├── GET /suggestions           ├── POST /log-payment               │   │
│  │  └── POST /feedback             ├── GET /timeline                   │   │
│  │                                 └── GET /achievements               │   │
│  │                                                                      │   │
│  │  /api/webhooks                  /api/admin (internal)               │   │
│  │  ├── POST /n8n-callback         ├── GET /metrics                    │   │
│  │  ├── POST /plaid-webhook        └── POST /recalculate-all           │   │
│  │  └── POST /payment-webhook                                          │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┴───────────────────────────────────┐   │
│  │                         DATABASE (PostgreSQL)                        │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  See DATABASE SCHEMA document for complete table definitions        │   │
│  │                                                                      │   │
│  │  Core Tables:           Financial Tables:      System Tables:        │   │
│  │  ├── users              ├── debts              ├── audit_logs       │   │
│  │  ├── profiles           ├── income_sources     ├── notifications    │   │
│  │  └── sessions           ├── expenses           ├── feature_flags    │   │
│  │                         ├── accounts           └── calculations     │   │
│  │  Strategy Tables:       ├── transactions                            │   │
│  │  ├── strategies         └── balances                                │   │
│  │  ├── milestones                                                     │   │
│  │  ├── projections        Education Tables:                           │   │
│  │  └── what_if_scenarios  ├── content_modules                         │   │
│  │                         ├── user_progress                           │   │
│  │  Chat Tables:           └── achievements                            │   │
│  │  ├── conversations                                                  │   │
│  │  └── messages                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┴───────────────────────────────────┐   │
│  │                         ROW LEVEL SECURITY                           │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  Policy: user_data_isolation                                        │   │
│  │  ────────────────────────────────────────────────────────────────   │   │
│  │  All user-specific tables enforce:                                  │   │
│  │    auth.uid() = user_id                                             │   │
│  │                                                                      │   │
│  │  Policy: admin_access                                               │   │
│  │  ────────────────────────────────────────────────────────────────   │   │
│  │  Admin tables check:                                                │   │
│  │    auth.jwt() ->> 'role' = 'admin'                                  │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┴───────────────────────────────────┐   │
│  │                         STORAGE BUCKETS                              │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  spreadsheet-uploads/           user-documents/                     │   │
│  │  ├── {user_id}/                 ├── {user_id}/                      │   │
│  │  │   └── {timestamp}_{file}     │   └── {document_type}_{file}      │   │
│  │  └── Access: private            └── Access: private                 │   │
│  │                                                                      │   │
│  │  education-content/             exports/                            │   │
│  │  ├── videos/                    ├── {user_id}/                      │   │
│  │  ├── thumbnails/                │   └── {export_type}_{date}.pdf    │   │
│  │  └── Access: public             └── Access: private, time-limited   │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 N8N Automation Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            N8N WORKFLOW ENGINE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        TRIGGER SOURCES                               │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  Webhook Triggers:              Schedule Triggers:                   │   │
│  │  ├── Supabase DB webhooks       ├── Daily: Balance reminders        │   │
│  │  ├── Auth events                ├── Weekly: Progress reports        │   │
│  │  ├── Storage events             ├── Monthly: Strategy review        │   │
│  │  └── Manual API calls           └── Quarterly: Goal assessment      │   │
│  │                                                                      │   │
│  │  Database Triggers:             External Triggers (Phase 2+):       │   │
│  │  ├── New user created           ├── Plaid transactions              │   │
│  │  ├── Data updated               ├── Bank balance changes            │   │
│  │  ├── Strategy generated         └── Payment confirmations           │   │
│  │  └── Milestone reached                                              │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┴───────────────────────────────────┐   │
│  │                      WORKFLOW CATEGORIES                             │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  DATA PROCESSING          STRATEGY AUTOMATION     NOTIFICATIONS     │   │
│  │  ──────────────────       ───────────────────     ──────────────    │   │
│  │  • Spreadsheet Parser     • AI Strategy Gen       • Push Alerts     │   │
│  │  • Data Validator         • Recalculation         • Email Digest    │   │
│  │  • Normalizer             • What-If Runner        • SMS Reminders   │   │
│  │  • Enrichment             • Timeline Update       • In-App Notify   │   │
│  │                                                                      │   │
│  │  PROGRESS TRACKING        USER ENGAGEMENT         SYSTEM HEALTH     │   │
│  │  ──────────────────       ───────────────────     ──────────────    │   │
│  │  • Payment Logger         • Milestone Checker     • Error Monitor   │   │
│  │  • Balance Reconciler     • Achievement Award     • Usage Analytics │   │
│  │  • Deviation Detector     • Coaching Trigger      • Backup Runner   │   │
│  │  • Report Generator       • Content Suggester     • Cleanup Jobs    │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┴───────────────────────────────────┐   │
│  │                      INTEGRATION POINTS                              │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │   │
│  │  │   Supabase   │    │  AI Services │    │   External   │          │   │
│  │  │   Direct DB  │    │  (OpenAI/    │    │   Services   │          │   │
│  │  │   Connection │    │   Claude)    │    │  (Phase 2+)  │          │   │
│  │  └──────────────┘    └──────────────┘    └──────────────┘          │   │
│  │         │                   │                   │                   │   │
│  │         └───────────────────┼───────────────────┘                   │   │
│  │                             ▼                                       │   │
│  │                    ┌──────────────────┐                             │   │
│  │                    │  Error Handler   │                             │   │
│  │                    │  & Retry Logic   │                             │   │
│  │                    └──────────────────┘                             │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.4 AI Services Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI SERVICES LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     AI SERVICE GATEWAY                               │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  Request Router → Rate Limiter → Cost Tracker → Model Selector      │   │
│  │                                                                      │   │
│  │  Model Selection Logic:                                              │   │
│  │  ─────────────────────                                              │   │
│  │  Task Type          │ Primary Model    │ Fallback      │ Cost Tier  │   │
│  │  ─────────────────────────────────────────────────────────────────  │   │
│  │  Strategy Gen       │ GPT-4 / Claude   │ GPT-3.5       │ High       │   │
│  │  Chat Response      │ GPT-3.5-turbo    │ Claude Haiku  │ Low        │   │
│  │  Document Parse     │ GPT-4 Vision     │ Custom OCR    │ Medium     │   │
│  │  Quick Calculations │ GPT-3.5-turbo    │ Local         │ Low        │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┴───────────────────────────────────┐   │
│  │                      AI MODULES                                      │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ┌────────────────────────┐    ┌────────────────────────┐          │   │
│  │  │   STRATEGY GENERATOR   │    │   CONVERSATIONAL AI    │          │   │
│  │  ├────────────────────────┤    ├────────────────────────┤          │   │
│  │  │ Input:                 │    │ Input:                 │          │   │
│  │  │ • Financial profile    │    │ • User message         │          │   │
│  │  │ • User preferences     │    │ • Conversation history │          │   │
│  │  │ • Risk tolerance       │    │ • Financial context    │          │   │
│  │  │                        │    │                        │          │   │
│  │  │ Output:                │    │ Output:                │          │   │
│  │  │ • Debt priority order  │    │ • Response text        │          │   │
│  │  │ • Payment schedule     │    │ • Suggested actions    │          │   │
│  │  │ • LOC utilization plan │    │ • Related content      │          │   │
│  │  │ • Timeline projection  │    │ • Follow-up prompts    │          │   │
│  │  └────────────────────────┘    └────────────────────────┘          │   │
│  │                                                                      │   │
│  │  ┌────────────────────────┐    ┌────────────────────────┐          │   │
│  │  │   DOCUMENT PARSER      │    │   INSIGHT GENERATOR    │          │   │
│  │  ├────────────────────────┤    ├────────────────────────┤          │   │
│  │  │ Input:                 │    │ Input:                 │          │   │
│  │  │ • Spreadsheet file     │    │ • Historical data      │          │   │
│  │  │ • Bank statement PDF   │    │ • User patterns        │          │   │
│  │  │                        │    │ • Market conditions    │          │   │
│  │  │ Output:                │    │                        │          │   │
│  │  │ • Structured data      │    │ Output:                │          │   │
│  │  │ • Column mapping       │    │ • Spending insights    │          │   │
│  │  │ • Validation errors    │    │ • Optimization tips    │          │   │
│  │  │ • Confidence scores    │    │ • Risk warnings        │          │   │
│  │  └────────────────────────┘    └────────────────────────┘          │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┴───────────────────────────────────┐   │
│  │                      PROMPT MANAGEMENT                               │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  System Prompts (versioned in database):                            │   │
│  │  ├── strategy_generator_v1.0                                        │   │
│  │  ├── coach_conversation_v1.0                                        │   │
│  │  ├── document_parser_v1.0                                           │   │
│  │  └── insight_generator_v1.0                                         │   │
│  │                                                                      │   │
│  │  Context Injection:                                                  │   │
│  │  ├── User financial summary                                         │   │
│  │  ├── Current strategy state                                         │   │
│  │  ├── Recent conversation history (last 10 messages)                 │   │
│  │  └── Relevant achievements/milestones                               │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow Diagrams

### 3.1 User Onboarding Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        USER ONBOARDING DATA FLOW                             │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────┐     ┌─────────────────────────────────────────────────────────────┐
│  USER   │     │                      SYSTEM                                  │
└────┬────┘     └─────────────────────────────────────────────────────────────┘
     │
     │  1. Signs up (email/OAuth)
     │─────────────────────────────────────────────────────────────────────────►
     │                                        │
     │                                        ▼
     │                              ┌──────────────────┐
     │                              │  Supabase Auth   │
     │                              │  Creates user    │
     │                              │  Sends confirm   │
     │                              └────────┬─────────┘
     │                                       │
     │                                       ▼
     │                              ┌──────────────────┐
     │                              │  N8N Workflow    │
     │                              │  "New User"      │
     │                              │  - Create profile│
     │                              │  - Send welcome  │
     │                              └────────┬─────────┘
     │                                       │
     │  2. Receives welcome email            │
     │◄──────────────────────────────────────┘
     │
     │  3. Starts onboarding wizard
     │─────────────────────────────────────────────────────────────────────────►
     │                                        │
     │                                        ▼
     │                              ┌──────────────────┐
     │                              │  Frontend        │
     │                              │  Multi-step form │
     │                              │  Real-time valid │
     │                              └────────┬─────────┘
     │                                       │
     │  4a. Enters data manually             │
     │  OR                                   │
     │  4b. Uploads spreadsheet              │
     │─────────────────────────────────────────────────────────────────────────►
     │                                        │
     │                          ┌─────────────┴──────────────┐
     │                          ▼                            ▼
     │                 ┌────────────────┐          ┌────────────────┐
     │                 │ Manual Entry   │          │ Spreadsheet    │
     │                 │ Validation     │          │ Upload Handler │
     │                 └───────┬────────┘          └───────┬────────┘
     │                         │                           │
     │                         │                           ▼
     │                         │                  ┌────────────────┐
     │                         │                  │ Supabase       │
     │                         │                  │ Storage        │
     │                         │                  │ (temp bucket)  │
     │                         │                  └───────┬────────┘
     │                         │                          │
     │                         │                          ▼
     │                         │                  ┌────────────────┐
     │                         │                  │ N8N Workflow   │
     │                         │                  │ "Parse Sheet"  │
     │                         │                  │ - Extract data │
     │                         │                  │ - AI mapping   │
     │                         │                  │ - Validate     │
     │                         │                  └───────┬────────┘
     │                         │                          │
     │                         └──────────┬───────────────┘
     │                                    ▼
     │                          ┌────────────────┐
     │                          │ Data Normalizer│
     │                          │ - Standard fmt │
     │                          │ - Enrichment   │
     │                          └───────┬────────┘
     │                                  │
     │                                  ▼
     │                          ┌────────────────┐
     │                          │ Supabase DB    │
     │                          │ Store profile  │
     │                          │ + financial    │
     │                          │ data           │
     │                          └───────┬────────┘
     │                                  │
     │  5. Sees validation results      │
     │◄─────────────────────────────────┘
     │
     │  6. Confirms data / makes corrections
     │─────────────────────────────────────────────────────────────────────────►
     │                                        │
     │                                        ▼
     │                              ┌──────────────────┐
     │                              │  Finalize Profile│
     │                              │  Trigger Strategy│
     │                              │  Generation      │
     │                              └────────┬─────────┘
     │                                       │
     │  7. Redirected to Strategy view       │
     │◄──────────────────────────────────────┘
     │
     ▼
```

### 3.2 Strategy Generation Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      STRATEGY GENERATION DATA FLOW                           │
└──────────────────────────────────────────────────────────────────────────────┘

                    ┌───────────────────┐
                    │   TRIGGER EVENT   │
                    │ • New profile     │
                    │ • Data update     │
                    │ • Manual request  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  LOAD USER DATA   │
                    │ • Debts           │
                    │ • Income          │
                    │ • Expenses        │
                    │ • Assets          │
                    │ • Preferences     │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ FINANCIAL HEALTH  │
                    │   ASSESSMENT      │
                    ├───────────────────┤
                    │ Calculate:        │
                    │ • DTI ratio       │
                    │ • Cashflow        │
                    │ • Interest burden │
                    │ • Emergency fund  │
                    └─────────┬─────────┘
                              │
                              ▼
               ┌──────────────┴──────────────┐
               │      STRATEGY ROUTER        │
               └──────────────┬──────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  POSITIVE       │ │  ZERO           │ │  NEGATIVE       │
│  CASHFLOW       │ │  CASHFLOW       │ │  CASHFLOW       │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ Has LOC?        │ │ Expense audit   │ │ Crisis mode     │
│ ├─ Yes: Full    │ │ Income boost    │ │ Hardship opts   │
│ │   Velocity    │ │ Micro-velocity  │ │ Consolidation   │
│ └─ No: Modified │ │ Debt restructure│ │ Budget rebuild  │
│   Avalanche/    │ │                 │ │                 │
│   Snowball      │ │                 │ │                 │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                   ┌───────────────────┐
                   │   AI STRATEGY     │
                   │   GENERATOR       │
                   ├───────────────────┤
                   │ Input:            │
                   │ • Financial data  │
                   │ • Health scores   │
                   │ • User prefs      │
                   │                   │
                   │ Output:           │
                   │ • Priority order  │
                   │ • Payment amounts │
                   │ • LOC schedule    │
                   │ • Explanations    │
                   └─────────┬─────────┘
                             │
                             ▼
                   ┌───────────────────┐
                   │  TIMELINE         │
                   │  CALCULATOR       │
                   ├───────────────────┤
                   │ For each debt:    │
                   │ • Payoff date     │
                   │ • Interest saved  │
                   │ • Milestones      │
                   │                   │
                   │ Confidence bands: │
                   │ • Best case       │
                   │ • Expected        │
                   │ • Worst case      │
                   └─────────┬─────────┘
                             │
                             ▼
                   ┌───────────────────┐
                   │  STORE STRATEGY   │
                   │  IN DATABASE      │
                   └─────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
    ┌───────────────────┐        ┌───────────────────┐
    │  NOTIFY USER      │        │  TRIGGER          │
    │  (realtime +      │        │  VISUALIZATION    │
    │   push)           │        │  GENERATION       │
    └───────────────────┘        └───────────────────┘
```

### 3.3 Coaching Conversation Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      COACHING CONVERSATION FLOW                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────┐                                                         ┌─────────┐
│  USER   │                                                         │ASSISTANT│
└────┬────┘                                                         └────┬────┘
     │                                                                   │
     │  User sends message                                               │
     │──────────────────────────────────────────────────────────────────►│
     │                                                                   │
     │                              ┌────────────────────────────────────┴──┐
     │                              │           PROCESS MESSAGE             │
     │                              ├───────────────────────────────────────┤
     │                              │                                       │
     │                              │  1. Intent Classification             │
     │                              │     ├── Question about strategy       │
     │                              │     ├── Request for action            │
     │                              │     ├── Update data request           │
     │                              │     ├── Educational query             │
     │                              │     └── General conversation          │
     │                              │                                       │
     │                              │  2. Context Assembly                  │
     │                              │     ├── User profile summary          │
     │                              │     ├── Current strategy state        │
     │                              │     ├── Recent 10 messages            │
     │                              │     └── Relevant metrics              │
     │                              │                                       │
     │                              │  3. Generate Response                 │
     │                              │     ├── Call AI (GPT-3.5/Claude)      │
     │                              │     ├── Include calculations          │
     │                              │     └── Add action suggestions        │
     │                              │                                       │
     │                              │  4. Post-process                      │
     │                              │     ├── Format for display            │
     │                              │     ├── Extract follow-ups            │
     │                              │     └── Log interaction               │
     │                              │                                       │
     │                              └────────────────────────────────────┬──┘
     │                                                                   │
     │  Receives response with:                                          │
     │  • Answer text                                                    │
     │  • Quick action buttons                                           │
     │  • Related content links                                          │
     │◄──────────────────────────────────────────────────────────────────│
     │                                                                   │
     │  [Optional] Clicks action button                                  │
     │──────────────────────────────────────────────────────────────────►│
     │                                                                   │
     │                              ┌────────────────────────────────────┴──┐
     │                              │         EXECUTE ACTION                │
     │                              ├───────────────────────────────────────┤
     │                              │ • Trigger workflow (N8N)              │
     │                              │ • Update data (Supabase)              │
     │                              │ • Navigate user (Frontend)            │
     │                              │ • Show content (Modal/Page)           │
     │                              └────────────────────────────────────┬──┘
     │                                                                   │
     │  Receives action confirmation                                     │
     │◄──────────────────────────────────────────────────────────────────│
     │                                                                   │
     ▼                                                                   ▼
```

---

## 4. Deployment Architecture

### 4.1 Infrastructure Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT TOPOLOGY                                  │
└──────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────────┐
                              │     CLOUDFLARE      │
                              │     (CDN/WAF)       │
                              └──────────┬──────────┘
                                         │
                         ┌───────────────┴───────────────┐
                         │                               │
                         ▼                               ▼
              ┌─────────────────────┐        ┌─────────────────────┐
              │      LOVABLE        │        │     SUPABASE        │
              │   (Frontend Host)   │        │    (Backend)        │
              ├─────────────────────┤        ├─────────────────────┤
              │ • Static assets     │        │ • Database          │
              │ • React SPA         │        │ • Auth              │
              │ • Edge workers      │        │ • Storage           │
              │ • SSL/TLS           │        │ • Edge Functions    │
              └─────────────────────┘        │ • Realtime          │
                                             └──────────┬──────────┘
                                                        │
                                             ┌──────────┴──────────┐
                                             │                     │
                                             ▼                     ▼
                                  ┌─────────────────┐   ┌─────────────────┐
                                  │      N8N        │   │  AI SERVICES    │
                                  │  (Self-hosted   │   │  (OpenAI/       │
                                  │   or Cloud)     │   │   Anthropic)    │
                                  └─────────────────┘   └─────────────────┘
```

### 4.2 Environment Configuration

| Environment | Purpose | Database | AI Model | N8N |
|-------------|---------|----------|----------|-----|
| Development | Local development | Supabase local | GPT-3.5 (cost saving) | Local Docker |
| Staging | QA and testing | Supabase project (staging) | GPT-4 | N8N Cloud (test) |
| Production | Live users | Supabase project (prod) | GPT-4 / Claude | N8N Cloud (prod) |

### 4.3 Scaling Considerations

| Component | Scaling Strategy | Trigger |
|-----------|------------------|---------|
| Frontend | Auto (Lovable CDN) | Traffic increase |
| Database | Vertical then horizontal read replicas | Query load |
| Edge Functions | Auto (Supabase) | Request volume |
| N8N | Horizontal workers | Queue depth |
| AI Calls | Rate limiting + queue | Cost management |

---

## 5. Security Architecture

See [Security Documentation](../security/SECURITY.md) for complete details.

### Quick Security Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         SECURITY LAYERS                                      │
└──────────────────────────────────────────────────────────────────────────────┘

Layer 1: NETWORK
├── Cloudflare WAF (DDoS, bot protection)
├── TLS 1.3 encryption in transit
└── IP allowlisting for admin endpoints

Layer 2: APPLICATION
├── Supabase Auth (JWT, OAuth, MFA)
├── CORS configuration
├── Rate limiting
└── Input validation (Zod schemas)

Layer 3: DATA
├── Row Level Security (PostgreSQL RLS)
├── Column-level encryption for sensitive fields
├── Audit logging
└── Data retention policies

Layer 4: INFRASTRUCTURE
├── Secrets management (env vars, Supabase vault)
├── Regular security updates
├── Penetration testing (scheduled)
└── Incident response plan
```

---

## 6. Monitoring & Observability

### Monitoring Stack

| Tool | Purpose |
|------|---------|
| Supabase Dashboard | Database metrics, auth stats |
| Lovable Analytics | Frontend performance, user flows |
| N8N Execution Logs | Workflow success/failure rates |
| Sentry | Error tracking, performance monitoring |
| Custom Dashboard | Business metrics, user progress |

### Key Metrics to Track

**System Health:**
- API response times (p50, p95, p99)
- Error rates by endpoint
- Database connection pool usage
- N8N workflow execution times

**User Engagement:**
- Daily/Weekly/Monthly active users
- Onboarding completion rate
- Feature adoption rates
- Chat interaction frequency

**Business Outcomes:**
- Users reaching milestones
- Average debt payoff acceleration
- User-reported savings
- NPS scores

---

## Next Steps

Continue to the following documents for deeper technical specifications:

1. [Database Schema](../database/SCHEMA.md) - Complete table definitions
2. [N8N Workflows](../workflows/WORKFLOWS.md) - Detailed workflow specifications
3. [Component Specs](../components/COMPONENTS.md) - Frontend/Backend component details
4. [Development Roadmap](../roadmap/ROADMAP.md) - Phase-by-phase implementation plan
5. [Security Guide](../security/SECURITY.md) - Comprehensive security documentation
