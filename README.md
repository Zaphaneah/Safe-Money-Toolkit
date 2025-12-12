# Safe Money Toolkit

## AI-Powered Financial Coaching Platform

An intelligent debt elimination platform that uses Velocity Banking principles and AI-driven coaching to help users achieve financial freedom faster than traditional methods.

---

## Overview

Safe Money Toolkit is designed to function as a personal financial coach, providing:

- **Automated Financial Analysis** - Parse user-submitted data (forms or spreadsheets) to understand complete financial pictures
- **AI-Generated Payoff Strategies** - Using Velocity Banking, Avalanche, Snowball, or hybrid approaches
- **Dynamic Visualizations** - Whiteboard-style explanations inspired by financial educators like Christy Vann
- **Conversational Coaching** - Plain-language guidance through an AI chat interface
- **Automated Progress Tracking** - N8N-powered workflows for notifications, reminders, and milestone celebrations

### Key Differentiators

| Feature | Traditional Budgeting Apps | Money Max Account | Safe Money Toolkit |
|---------|---------------------------|-------------------|-------------------|
| Debt Types | Limited | Mortgages only | All debt types |
| Strategy | Manual | Proprietary/opaque | AI-generated, transparent |
| Flexibility | High effort | Rigid | Adaptive with user control |
| Cost Model | Subscription | High upfront | Flexible |
| Zero Cashflow Support | No guidance | Not supported | Explicit strategies |

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React + TypeScript (Lovable) | User interface |
| **UI Components** | shadcn/ui + Tailwind CSS | Design system |
| **Backend** | Supabase (PostgreSQL + Edge Functions) | Database, Auth, API |
| **Automation** | N8N | Workflow orchestration |
| **AI** | OpenAI GPT-4 / Anthropic Claude | Strategy generation, coaching |
| **Visualizations** | Recharts + Custom Canvas | Financial visualizations |

---

## Documentation

### Core Documentation

| Document | Description |
|----------|-------------|
| [Technical Specification](./TECHNICAL_SPECIFICATION.md) | Complete system overview and feature specifications |
| [Architecture](./docs/architecture/ARCHITECTURE.md) | System architecture, data flows, and deployment topology |
| [Database Schema](./docs/database/SCHEMA.md) | Supabase PostgreSQL schema with RLS policies |
| [N8N Workflows](./docs/workflows/WORKFLOWS.md) | Automation workflow specifications |
| [Components](./docs/components/COMPONENTS.md) | Frontend and backend component specifications |
| [Development Roadmap](./docs/roadmap/ROADMAP.md) | MVP to production development phases |
| [Security](./docs/security/SECURITY.md) | Security architecture and compliance |

### Quick Links

- **Want to understand the system?** Start with [Technical Specification](./TECHNICAL_SPECIFICATION.md)
- **Setting up the database?** See [Database Schema](./docs/database/SCHEMA.md)
- **Building workflows?** Check [N8N Workflows](./docs/workflows/WORKFLOWS.md)
- **Starting development?** Follow [Development Roadmap](./docs/roadmap/ROADMAP.md)

---

## System Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER DEVICES                                    │
│                    (iOS Mobile / Desktop Browsers)                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOVABLE (Frontend)                                 │
│              React + TypeScript + shadcn/ui + Tailwind                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SUPABASE (Backend)                                 │
│      PostgreSQL + Edge Functions + Auth + Storage + Realtime                │
└─────────────────────────────────────────────────────────────────────────────┘
                          │                   │
                          ▼                   ▼
              ┌───────────────────┐  ┌───────────────────┐
              │        N8N        │  │   AI Services     │
              │   (Automation)    │  │  (GPT-4/Claude)   │
              └───────────────────┘  └───────────────────┘
```

---

## Core Features

### 1. User Onboarding + Data Intake

- Multi-step guided wizard for financial data entry
- Spreadsheet upload with AI-powered column mapping
- Real-time validation and data confidence scoring
- Save and resume functionality

### 2. AI-Generated Financial Strategy

- **Velocity Banking**: For users with positive cashflow and access to lines of credit
- **Avalanche Method**: Target highest interest debts first
- **Snowball Method**: Target smallest balances for quick wins
- **Crisis Mode**: Strategies for zero or negative cashflow situations

### 3. Dynamic Visualizations

- **Debt Landscape**: Overview of all debts with interest rate heat mapping
- **Cashflow River**: Animated visualization of money flow in Velocity Banking
- **Timeline Chart**: Projected payoff timeline with confidence bands
- **Whiteboard Canvas**: Interactive strategy explanation (inspired by Christy Vann)

### 4. Conversational AI Coach

- Plain-language explanations of financial concepts
- Contextual suggestions based on user's situation
- Quick action buttons for common tasks
- Educational content recommendations

### 5. Automated Workflows (N8N)

- Payment due date reminders
- Weekly progress digest emails
- Milestone achievement celebrations
- Balance reconciliation prompts
- Strategy deviation alerts

### 6. Progress Tracking

- Payment logging with automatic recalculation
- Milestone tracking with projected vs. actual dates
- Achievement system with gamification elements
- Historical progress visualization

---

## Development Phases

| Phase | Focus | Key Deliverables |
|-------|-------|------------------|
| **Phase 1** | Foundation | Auth, database, onboarding, basic UI |
| **Phase 2** | AI Core | Strategy engine, visualizations, chat |
| **Phase 3** | Automation | N8N workflows, notifications, tracking |
| **Phase 4** | Polish | Mobile optimization, education, gamification |
| **Phase 5** | Scale | Banking integrations, advanced features |

See [Development Roadmap](./docs/roadmap/ROADMAP.md) for detailed sprint breakdowns.

---

## Getting Started

### Prerequisites

- Node.js 18+
- Supabase account
- N8N account (Cloud or self-hosted)
- OpenAI or Anthropic API key

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/your-org/safe-money-toolkit.git
cd safe-money-toolkit

# Install dependencies (when frontend is initialized)
npm install

# Copy environment template
cp .env.example .env.local

# Configure environment variables
# See docs/security/SECURITY.md for required variables
```

### Database Setup

```bash
# Apply migrations to Supabase
supabase db push

# Or manually run migrations
# See docs/database/SCHEMA.md for SQL scripts
```

---

## Project Structure

```
safe-money-toolkit/
├── README.md                       # This file
├── TECHNICAL_SPECIFICATION.md      # Complete technical specification
├── docs/
│   ├── architecture/
│   │   └── ARCHITECTURE.md         # System architecture
│   ├── database/
│   │   └── SCHEMA.md               # Database schema
│   ├── workflows/
│   │   └── WORKFLOWS.md            # N8N workflow specs
│   ├── components/
│   │   └── COMPONENTS.md           # Component specifications
│   ├── roadmap/
│   │   └── ROADMAP.md              # Development roadmap
│   └── security/
│       └── SECURITY.md             # Security documentation
├── src/                            # Frontend source (to be created)
├── supabase/                       # Supabase configuration (to be created)
│   ├── functions/                  # Edge functions
│   └── migrations/                 # Database migrations
└── n8n/                            # N8N workflow exports (to be created)
```

---

## Key Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| **Supabase over Firebase** | PostgreSQL power, better RLS, open source ecosystem |
| **N8N over Zapier** | Self-hostable, complex logic support, cost-effective |
| **Lovable for Frontend** | Rapid development, built-in hosting, React ecosystem |
| **GPT-4 for Strategy** | Best reasoning for complex financial decisions |
| **GPT-3.5 for Chat** | Cost-effective for conversational interactions |

---

## Security Highlights

- **Row Level Security (RLS)** on all user data tables
- **JWT Authentication** via Supabase Auth
- **Encryption at rest** (AES-256) and in transit (TLS 1.3)
- **No storage of sensitive banking credentials**
- **Comprehensive audit logging**
- **GDPR-compliant data handling**

See [Security Documentation](./docs/security/SECURITY.md) for complete details.

---

## Contributing

This project is currently in the design phase. Contributions to documentation and architecture feedback are welcome.

---

## Disclaimer

Safe Money Toolkit is an educational tool designed to help users understand and manage personal finances. It is **not** a substitute for professional financial advice. Users should consult qualified professionals before making significant financial decisions.

---

## License

[To be determined]

---

## Contact

[To be added]
