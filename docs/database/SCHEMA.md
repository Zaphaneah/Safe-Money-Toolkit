# Database Schema

## Supabase PostgreSQL Schema for Safe Money Toolkit

---

## Table of Contents

1. [Schema Overview](#schema-overview)
2. [Core Tables](#core-tables)
3. [Financial Data Tables](#financial-data-tables)
4. [Strategy Tables](#strategy-tables)
5. [Coaching & Education Tables](#coaching--education-tables)
6. [System Tables](#system-tables)
7. [Row Level Security Policies](#row-level-security-policies)
8. [Database Functions](#database-functions)
9. [Triggers](#triggers)
10. [Indexes](#indexes)
11. [Migration Strategy](#migration-strategy)

---

## Schema Overview

### Entity Relationship Diagram (Textual)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCHEMA RELATIONSHIPS                               │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌───────────────┐
                           │    users      │
                           │  (auth.users) │
                           └───────┬───────┘
                                   │ 1
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼ 1            ▼ 1            ▼ *
           ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
           │   profiles    │ │   settings    │ │ audit_logs    │
           └───────┬───────┘ └───────────────┘ └───────────────┘
                   │ 1
                   │
    ┌──────────────┼──────────────┬──────────────┬──────────────┐
    │              │              │              │              │
    ▼ *            ▼ *            ▼ *            ▼ *            ▼ *
┌─────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐
│  debts  │  │  incomes  │  │ expenses │  │ accounts │  │ strategies│
└────┬────┘  └───────────┘  └──────────┘  └────┬─────┘  └─────┬─────┘
     │                                         │              │
     │ *                                       │ *            │ *
     ▼                                         ▼              ▼
┌─────────────┐                         ┌────────────┐  ┌────────────┐
│ debt_history│                         │transactions│  │ milestones │
└─────────────┘                         └────────────┘  └────────────┘
                                                              │
                           ┌──────────────────────────────────┘
                           │ *
                           ▼
                    ┌────────────────┐
                    │  achievements  │
                    └────────────────┘


┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ project_folders │ 1─* │  conversations  │ 1─* │    messages     │
└─────────────────┘     └─────────────────┘     └─────────────────┘

┌─────────────────┐
│   ai_prompts    │
└─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ content_modules │ 1─* │ content_progress│ *─1 │    profiles     │
└─────────────────┘     └─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  notifications  │     │ scheduled_tasks │     │  feature_flags  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Core Tables

### `profiles`

Extends Supabase auth.users with application-specific user data.

```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Basic Info
    email TEXT NOT NULL,
    full_name TEXT,
    phone TEXT,
    timezone TEXT DEFAULT 'America/New_York',

    -- Onboarding Status
    onboarding_completed BOOLEAN DEFAULT FALSE,
    onboarding_step INTEGER DEFAULT 0,
    onboarding_data JSONB DEFAULT '{}',

    -- Financial Profile Status
    financial_profile_complete BOOLEAN DEFAULT FALSE,
    last_data_update TIMESTAMPTZ,
    data_confidence_score DECIMAL(3,2) DEFAULT 0.00,

    -- Preferences
    preferred_strategy TEXT CHECK (preferred_strategy IN ('velocity', 'avalanche', 'snowball', 'custom')),
    risk_tolerance TEXT CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive')),
    notification_preferences JSONB DEFAULT '{
        "email": true,
        "push": true,
        "sms": false,
        "weekly_digest": true,
        "milestone_alerts": true,
        "payment_reminders": true
    }',

    -- Subscription/Plan (for future monetization)
    plan_type TEXT DEFAULT 'free' CHECK (plan_type IN ('free', 'pro', 'enterprise')),
    plan_expires_at TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,

    -- Soft delete
    deleted_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_profiles_onboarding ON profiles(onboarding_completed) WHERE NOT onboarding_completed;
CREATE INDEX idx_profiles_plan ON profiles(plan_type);
```

### `user_settings`

User-configurable application settings.

```sql
CREATE TABLE user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Display Settings
    currency TEXT DEFAULT 'USD',
    date_format TEXT DEFAULT 'MM/DD/YYYY',
    number_format TEXT DEFAULT 'en-US',
    theme TEXT DEFAULT 'system' CHECK (theme IN ('light', 'dark', 'system')),

    -- Calculation Settings
    include_interest_in_minimum BOOLEAN DEFAULT TRUE,
    round_payments_to INTEGER DEFAULT 1, -- Nearest dollar

    -- Privacy Settings
    share_anonymous_data BOOLEAN DEFAULT FALSE,

    -- Feature Toggles
    enable_ai_coaching BOOLEAN DEFAULT TRUE,
    enable_gamification BOOLEAN DEFAULT TRUE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id)
);
```

---

## Financial Data Tables

### `income_sources`

All income streams for a user.

```sql
CREATE TABLE income_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Income Details
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN (
        'salary', 'hourly', 'self_employment', 'freelance',
        'rental', 'investment', 'social_security', 'pension',
        'alimony', 'child_support', 'other'
    )),

    -- Amount & Frequency
    gross_amount DECIMAL(12,2) NOT NULL,
    net_amount DECIMAL(12,2), -- After taxes/deductions
    frequency TEXT NOT NULL CHECK (frequency IN (
        'weekly', 'biweekly', 'semimonthly', 'monthly',
        'quarterly', 'annually', 'irregular'
    )),

    -- For irregular income
    is_variable BOOLEAN DEFAULT FALSE,
    variable_min DECIMAL(12,2),
    variable_max DECIMAL(12,2),
    variable_average DECIMAL(12,2),

    -- Timing
    pay_day INTEGER, -- Day of month (1-31) or day of week (1-7)
    next_pay_date DATE,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    start_date DATE,
    end_date DATE,

    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_income_user ON income_sources(user_id);
CREATE INDEX idx_income_active ON income_sources(user_id, is_active) WHERE is_active;
```

### `expenses`

Fixed and variable expenses.

```sql
CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Expense Details
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN (
        'housing', 'utilities', 'transportation', 'insurance',
        'food', 'healthcare', 'debt_payment', 'childcare',
        'education', 'entertainment', 'personal', 'savings',
        'charitable', 'subscriptions', 'other'
    )),

    -- Amount & Frequency
    amount DECIMAL(12,2) NOT NULL,
    frequency TEXT NOT NULL CHECK (frequency IN (
        'weekly', 'biweekly', 'semimonthly', 'monthly',
        'quarterly', 'annually', 'one_time'
    )),

    -- For variable expenses
    is_variable BOOLEAN DEFAULT FALSE,
    variable_min DECIMAL(12,2),
    variable_max DECIMAL(12,2),

    -- Classification
    is_essential BOOLEAN DEFAULT TRUE,
    is_reducible BOOLEAN DEFAULT FALSE, -- Can this be cut/reduced?
    reduction_potential DECIMAL(12,2), -- How much could be saved

    -- Timing
    due_day INTEGER, -- Day of month

    -- Linked debt (for debt payments)
    linked_debt_id UUID REFERENCES debts(id) ON DELETE SET NULL,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_expenses_user ON expenses(user_id);
CREATE INDEX idx_expenses_category ON expenses(user_id, category);
CREATE INDEX idx_expenses_essential ON expenses(user_id, is_essential);
```

### `debts`

All debt accounts for a user.

```sql
CREATE TABLE debts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Creditor Information
    creditor_name TEXT NOT NULL,
    account_nickname TEXT, -- User-friendly name
    account_number_last4 TEXT, -- Last 4 digits only (security)

    -- Debt Type
    debt_type TEXT NOT NULL CHECK (debt_type IN (
        'credit_card', 'personal_loan', 'auto_loan', 'student_loan',
        'mortgage', 'home_equity_loan', 'heloc', 'medical_debt',
        'payday_loan', 'collections', 'irs_debt', 'other'
    )),

    -- Balance & Terms
    original_balance DECIMAL(12,2),
    current_balance DECIMAL(12,2) NOT NULL,
    credit_limit DECIMAL(12,2), -- For revolving credit
    available_credit DECIMAL(12,2), -- Calculated: limit - balance

    -- Interest
    interest_rate DECIMAL(5,3) NOT NULL, -- APR as decimal (e.g., 19.99)
    interest_type TEXT DEFAULT 'fixed' CHECK (interest_type IN ('fixed', 'variable')),
    promotional_rate DECIMAL(5,3),
    promotional_rate_expires DATE,

    -- Payments
    minimum_payment DECIMAL(12,2) NOT NULL,
    minimum_payment_type TEXT DEFAULT 'fixed' CHECK (minimum_payment_type IN (
        'fixed', 'percentage', 'interest_plus_percent'
    )),
    minimum_payment_percentage DECIMAL(5,3), -- If type is percentage
    payment_due_day INTEGER NOT NULL, -- Day of month (1-31)

    -- Loan-specific
    original_term_months INTEGER,
    remaining_term_months INTEGER,
    maturity_date DATE,

    -- Strategy Fields
    priority_rank INTEGER, -- User or AI assigned priority
    is_velocity_target BOOLEAN DEFAULT FALSE, -- Current velocity banking target
    is_loc_hub BOOLEAN DEFAULT FALSE, -- Used as Line of Credit hub

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN (
        'active', 'paid_off', 'closed', 'deferred', 'in_collections'
    )),
    paid_off_date DATE,

    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_debts_user ON debts(user_id);
CREATE INDEX idx_debts_status ON debts(user_id, status);
CREATE INDEX idx_debts_type ON debts(user_id, debt_type);
CREATE INDEX idx_debts_priority ON debts(user_id, priority_rank) WHERE status = 'active';
```

### `debt_history`

Historical balance tracking for debts.

```sql
CREATE TABLE debt_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    debt_id UUID NOT NULL REFERENCES debts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Snapshot Data
    balance DECIMAL(12,2) NOT NULL,
    interest_rate DECIMAL(5,3),
    minimum_payment DECIMAL(12,2),

    -- Change Info
    change_amount DECIMAL(12,2), -- Positive = increase, Negative = decrease
    change_type TEXT CHECK (change_type IN (
        'payment', 'charge', 'interest', 'fee', 'adjustment', 'initial'
    )),
    change_description TEXT,

    -- Recorded At
    recorded_at DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_debt_history_debt ON debt_history(debt_id);
CREATE INDEX idx_debt_history_user ON debt_history(user_id);
CREATE INDEX idx_debt_history_date ON debt_history(debt_id, recorded_at);
```

### `accounts`

Bank accounts and financial accounts (not debts).

```sql
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Account Info
    institution_name TEXT NOT NULL,
    account_name TEXT NOT NULL,
    account_type TEXT NOT NULL CHECK (account_type IN (
        'checking', 'savings', 'money_market', 'cd',
        'brokerage', 'retirement_401k', 'retirement_ira',
        'hsa', 'cash', 'other'
    )),
    account_number_last4 TEXT,

    -- Balance
    current_balance DECIMAL(12,2) NOT NULL DEFAULT 0,
    available_balance DECIMAL(12,2),

    -- Interest (for savings accounts)
    interest_rate DECIMAL(5,3) DEFAULT 0,

    -- Flags
    is_primary BOOLEAN DEFAULT FALSE, -- Primary checking
    is_emergency_fund BOOLEAN DEFAULT FALSE,

    -- Integration (Phase 2+)
    plaid_account_id TEXT,
    plaid_item_id TEXT,
    last_synced_at TIMESTAMPTZ,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_accounts_user ON accounts(user_id);
CREATE INDEX idx_accounts_type ON accounts(user_id, account_type);
```

### `transactions`

Transaction records (manual or synced).

```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
    debt_id UUID REFERENCES debts(id) ON DELETE SET NULL,

    -- Transaction Details
    transaction_date DATE NOT NULL,
    posted_date DATE,
    description TEXT NOT NULL,

    -- Amount (positive = credit/income, negative = debit/expense)
    amount DECIMAL(12,2) NOT NULL,

    -- Classification
    category TEXT,
    transaction_type TEXT CHECK (transaction_type IN (
        'income', 'expense', 'transfer', 'debt_payment', 'refund'
    )),

    -- For debt payments
    is_extra_payment BOOLEAN DEFAULT FALSE,
    applies_to_principal BOOLEAN DEFAULT FALSE,

    -- Source
    source TEXT DEFAULT 'manual' CHECK (source IN (
        'manual', 'plaid', 'csv_import', 'recurring'
    )),
    external_id TEXT, -- For deduplication with Plaid

    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_debt ON transactions(debt_id);
CREATE INDEX idx_transactions_date ON transactions(user_id, transaction_date);
CREATE INDEX idx_transactions_external ON transactions(external_id) WHERE external_id IS NOT NULL;
```

---

## Strategy Tables

### `strategies`

AI-generated and user-modified financial strategies.

```sql
CREATE TABLE strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Strategy Identification
    name TEXT DEFAULT 'Primary Strategy',
    strategy_type TEXT NOT NULL CHECK (strategy_type IN (
        'velocity_banking', 'avalanche', 'snowball', 'hybrid', 'custom', 'crisis'
    )),

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN (
        'draft', 'active', 'paused', 'completed', 'archived'
    )),
    is_primary BOOLEAN DEFAULT FALSE,

    -- Configuration
    config JSONB NOT NULL DEFAULT '{}',
    /*
    config structure:
    {
        "loc_debt_id": "uuid",           // Line of credit used as hub
        "target_debt_order": ["uuid"],   // Ordered list of debt IDs
        "monthly_extra_payment": 500,
        "chunk_payment_amount": 1200,
        "chunk_payment_frequency": "monthly",
        "emergency_fund_target": 1000,
        "include_windfalls": true
    }
    */

    -- Financial Snapshot (at strategy creation)
    snapshot JSONB NOT NULL DEFAULT '{}',
    /*
    snapshot structure:
    {
        "total_debt": 87450,
        "monthly_income": 5200,
        "monthly_expenses": 4100,
        "monthly_cashflow": 1100,
        "weighted_avg_interest": 12.5
    }
    */

    -- Projections
    projections JSONB NOT NULL DEFAULT '{}',
    /*
    projections structure:
    {
        "debt_free_date": "2029-06-15",
        "months_to_payoff": 54,
        "total_interest_standard": 45000,
        "total_interest_strategy": 18000,
        "interest_savings": 27000,
        "confidence_score": 0.85
    }
    */

    -- AI Generation Info
    ai_generated BOOLEAN DEFAULT FALSE,
    ai_model_version TEXT,
    ai_prompt_version TEXT,
    ai_reasoning TEXT, -- Explanation of why this strategy was chosen

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    activated_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_strategies_user ON strategies(user_id);
CREATE INDEX idx_strategies_active ON strategies(user_id, status) WHERE status = 'active';
CREATE UNIQUE INDEX idx_strategies_primary ON strategies(user_id) WHERE is_primary = TRUE;
```

### `strategy_milestones`

Milestones within a strategy.

```sql
CREATE TABLE strategy_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Milestone Info
    milestone_type TEXT NOT NULL CHECK (milestone_type IN (
        'debt_payoff', 'percentage_complete', 'interest_saved',
        'emergency_fund', 'custom', 'halfway', 'almost_done'
    )),

    title TEXT NOT NULL,
    description TEXT,

    -- Target
    target_debt_id UUID REFERENCES debts(id) ON DELETE SET NULL,
    target_value DECIMAL(12,2),
    target_percentage DECIMAL(5,2),

    -- Projected & Actual Dates
    projected_date DATE,
    achieved_date DATE,

    -- Status
    status TEXT DEFAULT 'pending' CHECK (status IN (
        'pending', 'achieved', 'missed', 'skipped'
    )),

    -- Display Order
    sort_order INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_milestones_strategy ON strategy_milestones(strategy_id);
CREATE INDEX idx_milestones_user ON strategy_milestones(user_id);
CREATE INDEX idx_milestones_status ON strategy_milestones(strategy_id, status);
```

### `what_if_scenarios`

User-created "what-if" scenario comparisons.

```sql
CREATE TABLE what_if_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    base_strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,

    -- Scenario Info
    name TEXT NOT NULL,
    description TEXT,

    -- Variable Changes
    changes JSONB NOT NULL DEFAULT '{}',
    /*
    changes structure:
    {
        "extra_monthly_payment": 200,
        "income_change": 500,
        "expense_reduction": 150,
        "lump_sum_payment": { "amount": 5000, "date": "2024-03-01" },
        "interest_rate_change": { "debt_id": "uuid", "new_rate": 15.99 }
    }
    */

    -- Results
    results JSONB NOT NULL DEFAULT '{}',
    /*
    results structure:
    {
        "debt_free_date": "2028-03-15",
        "months_saved": 8,
        "interest_saved": 4500,
        "comparison_to_base": {
            "months_difference": -8,
            "interest_difference": -4500
        }
    }
    */

    -- Status
    is_saved BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scenarios_user ON what_if_scenarios(user_id);
```

### `strategy_calculations`

Detailed calculation records for audit and debugging.

```sql
CREATE TABLE strategy_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Calculation Type
    calc_type TEXT NOT NULL CHECK (calc_type IN (
        'full_projection', 'monthly_update', 'debt_payoff', 'recalculation'
    )),

    -- Input Data (snapshot)
    input_data JSONB NOT NULL,

    -- Output Data
    output_data JSONB NOT NULL,

    -- Calculation Metadata
    calculation_version TEXT NOT NULL,
    duration_ms INTEGER, -- How long the calculation took

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_calculations_strategy ON strategy_calculations(strategy_id);
CREATE INDEX idx_calculations_date ON strategy_calculations(created_at);
```

---

## Coaching & Education Tables

### `project_folders`

User-created folders for organizing conversations.

```sql
CREATE TABLE project_folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Folder Info
    name TEXT NOT NULL,
    description TEXT,

    -- Display
    color_tag TEXT DEFAULT '#4F46E5', -- Hex color for UI
    icon_name TEXT DEFAULT 'folder',  -- Icon identifier

    -- Ordering
    sort_order INTEGER DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique name per user
    UNIQUE(user_id, name)
);

CREATE INDEX idx_project_folders_user ON project_folders(user_id);
CREATE INDEX idx_project_folders_active ON project_folders(user_id, is_active) WHERE is_active;
```

### `conversations`

Chat conversation sessions.

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Conversation Info
    title TEXT,
    summary TEXT, -- AI-generated summary

    -- Context
    context_type TEXT DEFAULT 'general' CHECK (context_type IN (
        'general', 'strategy', 'debt_specific', 'education', 'troubleshooting'
    )),
    context_reference_id UUID, -- Could reference strategy, debt, etc.

    -- Project Folder Organization
    project_folder_id UUID REFERENCES project_folders(id) ON DELETE SET NULL,

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN (
        'active', 'archived', 'deleted'
    )),

    -- Metadata
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_recent ON conversations(user_id, last_message_at DESC);
CREATE INDEX idx_conversations_folder ON conversations(project_folder_id) WHERE project_folder_id IS NOT NULL;
```

### `messages`

Individual chat messages.

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Message Content
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,

    -- AI Response Metadata
    ai_model TEXT,
    tokens_used INTEGER,
    response_time_ms INTEGER,

    -- Actions Suggested/Taken
    suggested_actions JSONB DEFAULT '[]',
    /*
    suggested_actions structure:
    [
        { "type": "view_strategy", "label": "View your strategy", "data": {} },
        { "type": "update_balance", "label": "Update balance", "data": { "debt_id": "uuid" } }
    ]
    */

    -- Feedback
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    user_feedback TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_user ON messages(user_id);
CREATE INDEX idx_messages_date ON messages(conversation_id, created_at);
```

### `content_modules`

Educational content library.

```sql
CREATE TABLE content_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Content Info
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,

    -- Content Type
    content_type TEXT NOT NULL CHECK (content_type IN (
        'video', 'article', 'interactive', 'checklist', 'quiz'
    )),

    -- Content Data
    content_url TEXT, -- For videos
    content_body TEXT, -- For articles (markdown)
    content_data JSONB, -- For interactive/quiz
    thumbnail_url TEXT,
    duration_seconds INTEGER, -- For videos

    -- Categorization
    category TEXT NOT NULL CHECK (category IN (
        'getting_started', 'velocity_banking', 'budgeting',
        'debt_strategies', 'credit_management', 'savings',
        'behavioral', 'advanced'
    )),
    tags TEXT[] DEFAULT '{}',

    -- Prerequisites
    prerequisites UUID[] DEFAULT '{}', -- Other module IDs
    recommended_after UUID[] DEFAULT '{}',

    -- Metadata
    difficulty_level TEXT DEFAULT 'beginner' CHECK (difficulty_level IN (
        'beginner', 'intermediate', 'advanced'
    )),
    estimated_time_minutes INTEGER,

    -- Status
    is_published BOOLEAN DEFAULT FALSE,
    is_premium BOOLEAN DEFAULT FALSE, -- Requires paid plan

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_content_category ON content_modules(category);
CREATE INDEX idx_content_published ON content_modules(is_published) WHERE is_published;
```

### `user_content_progress`

Tracking user progress through educational content.

```sql
CREATE TABLE user_content_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    content_id UUID NOT NULL REFERENCES content_modules(id) ON DELETE CASCADE,

    -- Progress
    status TEXT DEFAULT 'not_started' CHECK (status IN (
        'not_started', 'in_progress', 'completed'
    )),
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage BETWEEN 0 AND 100),

    -- For videos
    last_position_seconds INTEGER DEFAULT 0,

    -- For quizzes
    quiz_score INTEGER,
    quiz_attempts INTEGER DEFAULT 0,

    -- Timestamps
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    last_accessed_at TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, content_id)
);

CREATE INDEX idx_progress_user ON user_content_progress(user_id);
CREATE INDEX idx_progress_content ON user_content_progress(content_id);
```

### `achievements`

Gamification achievements.

```sql
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Achievement Info
    code TEXT UNIQUE NOT NULL, -- e.g., 'first_debt_payoff'
    title TEXT NOT NULL,
    description TEXT NOT NULL,

    -- Display
    icon_name TEXT,
    badge_color TEXT DEFAULT '#4F46E5',

    -- Criteria
    criteria_type TEXT NOT NULL CHECK (criteria_type IN (
        'debt_payoff', 'streak', 'milestone', 'engagement',
        'education', 'savings', 'custom'
    )),
    criteria_config JSONB NOT NULL DEFAULT '{}',
    /*
    criteria_config examples:
    { "debts_paid": 1 }
    { "streak_days": 30, "action": "data_update" }
    { "percentage_complete": 50 }
    { "modules_completed": 5 }
    */

    -- Points/Rewards
    points INTEGER DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_hidden BOOLEAN DEFAULT FALSE, -- Secret achievements

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_achievements_type ON achievements(criteria_type);
```

### `user_achievements`

User's earned achievements.

```sql
CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,

    -- Achievement Context
    context_data JSONB DEFAULT '{}', -- What triggered it

    -- Timestamps
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    viewed_at TIMESTAMPTZ, -- When user saw the notification

    UNIQUE(user_id, achievement_id)
);

CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_date ON user_achievements(earned_at);
```

---

## System Tables

### `audit_logs`

Comprehensive audit trail.

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Actor
    user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    actor_type TEXT NOT NULL CHECK (actor_type IN (
        'user', 'system', 'ai', 'admin', 'n8n'
    )),

    -- Action
    action TEXT NOT NULL, -- e.g., 'debt.create', 'strategy.generate'
    resource_type TEXT NOT NULL, -- e.g., 'debt', 'strategy'
    resource_id UUID,

    -- Data
    old_values JSONB,
    new_values JSONB,

    -- Context
    ip_address INET,
    user_agent TEXT,
    request_id TEXT, -- For tracing

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Partition by month for performance
-- CREATE TABLE audit_logs_YYYY_MM PARTITION OF audit_logs FOR VALUES FROM ('YYYY-MM-01') TO ('YYYY-MM+1-01');

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_date ON audit_logs(created_at);
```

### `notifications`

User notifications.

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Notification Content
    title TEXT NOT NULL,
    body TEXT NOT NULL,

    -- Type & Priority
    notification_type TEXT NOT NULL CHECK (notification_type IN (
        'info', 'success', 'warning', 'error', 'achievement',
        'reminder', 'milestone', 'insight'
    )),
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),

    -- Action
    action_url TEXT, -- Deep link
    action_data JSONB DEFAULT '{}',

    -- Delivery
    channels TEXT[] DEFAULT ARRAY['in_app'], -- 'in_app', 'email', 'push', 'sms'

    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,

    -- Scheduling
    scheduled_for TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE NOT is_read;
CREATE INDEX idx_notifications_scheduled ON notifications(scheduled_for) WHERE sent_at IS NULL;
```

### `scheduled_tasks`

N8N scheduled task tracking.

```sql
CREATE TABLE scheduled_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,

    -- Task Info
    task_type TEXT NOT NULL,
    task_name TEXT NOT NULL,

    -- Scheduling
    schedule_cron TEXT, -- Cron expression
    next_run_at TIMESTAMPTZ,
    last_run_at TIMESTAMPTZ,

    -- Configuration
    config JSONB DEFAULT '{}',

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN (
        'active', 'paused', 'completed', 'failed'
    )),
    last_result JSONB,
    failure_count INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scheduled_user ON scheduled_tasks(user_id);
CREATE INDEX idx_scheduled_next_run ON scheduled_tasks(next_run_at) WHERE status = 'active';
```

### `feature_flags`

Feature flag management.

```sql
CREATE TABLE feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Flag Info
    flag_key TEXT UNIQUE NOT NULL,
    description TEXT,

    -- Status
    is_enabled BOOLEAN DEFAULT FALSE,

    -- Targeting
    enabled_for_users UUID[] DEFAULT '{}', -- Specific user IDs
    enabled_for_plans TEXT[] DEFAULT '{}', -- Plan types
    percentage_rollout INTEGER DEFAULT 0 CHECK (percentage_rollout BETWEEN 0 AND 100),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_feature_flags_key ON feature_flags(flag_key);
```

### `ai_prompts`

Versioned AI prompts.

```sql
CREATE TABLE ai_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Prompt Info
    prompt_key TEXT NOT NULL, -- e.g., 'strategy_generator'
    version TEXT NOT NULL,

    -- Content
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT,

    -- Configuration
    model_config JSONB DEFAULT '{}',
    /*
    model_config structure:
    {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000
    }
    */

    -- Status
    is_active BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT,
    notes TEXT,

    UNIQUE(prompt_key, version)
);

CREATE INDEX idx_prompts_key ON ai_prompts(prompt_key);
CREATE INDEX idx_prompts_active ON ai_prompts(prompt_key, is_active) WHERE is_active;
```

---

## Row Level Security Policies

### Enable RLS on All Tables

```sql
-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE income_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE debts ENABLE ROW LEVEL SECURITY;
ALTER TABLE debt_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategy_milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE what_if_scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategy_calculations ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_folders ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_content_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE scheduled_tasks ENABLE ROW LEVEL SECURITY;

-- Public read tables (no user filter needed)
ALTER TABLE content_modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE feature_flags ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_prompts ENABLE ROW LEVEL SECURITY;
```

### User Data Isolation Policies

```sql
-- Template policy for user-owned data
-- Apply to: profiles, user_settings, income_sources, expenses, debts,
--           debt_history, accounts, transactions, strategies, strategy_milestones,
--           what_if_scenarios, strategy_calculations, project_folders, conversations,
--           messages, user_content_progress, user_achievements, notifications, scheduled_tasks

-- Example for profiles table
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Example for debts table
CREATE POLICY "Users can view own debts" ON debts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own debts" ON debts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own debts" ON debts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own debts" ON debts
    FOR DELETE USING (auth.uid() = user_id);

-- Example for project_folders table
CREATE POLICY "Users can view own folders" ON project_folders
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own folders" ON project_folders
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own folders" ON project_folders
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own folders" ON project_folders
    FOR DELETE USING (auth.uid() = user_id);

-- Public content tables
CREATE POLICY "Anyone can view published content" ON content_modules
    FOR SELECT USING (is_published = true);

CREATE POLICY "Anyone can view active achievements" ON achievements
    FOR SELECT USING (is_active = true);

-- Service role bypass for N8N/system operations
-- (Service role automatically bypasses RLS)
```

---

## Database Functions

### Calculate Monthly Cashflow

```sql
CREATE OR REPLACE FUNCTION calculate_monthly_cashflow(p_user_id UUID)
RETURNS DECIMAL AS $$
DECLARE
    v_income DECIMAL;
    v_expenses DECIMAL;
BEGIN
    -- Sum monthly income
    SELECT COALESCE(SUM(
        CASE frequency
            WHEN 'weekly' THEN net_amount * 4.33
            WHEN 'biweekly' THEN net_amount * 2.17
            WHEN 'semimonthly' THEN net_amount * 2
            WHEN 'monthly' THEN net_amount
            WHEN 'quarterly' THEN net_amount / 3
            WHEN 'annually' THEN net_amount / 12
            ELSE net_amount
        END
    ), 0) INTO v_income
    FROM income_sources
    WHERE user_id = p_user_id AND is_active = true;

    -- Sum monthly expenses
    SELECT COALESCE(SUM(
        CASE frequency
            WHEN 'weekly' THEN amount * 4.33
            WHEN 'biweekly' THEN amount * 2.17
            WHEN 'semimonthly' THEN amount * 2
            WHEN 'monthly' THEN amount
            WHEN 'quarterly' THEN amount / 3
            WHEN 'annually' THEN amount / 12
            ELSE amount
        END
    ), 0) INTO v_expenses
    FROM expenses
    WHERE user_id = p_user_id AND is_active = true;

    RETURN v_income - v_expenses;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### Calculate Total Debt

```sql
CREATE OR REPLACE FUNCTION calculate_total_debt(p_user_id UUID)
RETURNS TABLE(
    total_balance DECIMAL,
    total_minimum_payment DECIMAL,
    weighted_avg_interest DECIMAL,
    debt_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(SUM(current_balance), 0)::DECIMAL,
        COALESCE(SUM(minimum_payment), 0)::DECIMAL,
        CASE
            WHEN SUM(current_balance) > 0 THEN
                (SUM(current_balance * interest_rate) / SUM(current_balance))::DECIMAL
            ELSE 0::DECIMAL
        END,
        COUNT(*)::INTEGER
    FROM debts
    WHERE user_id = p_user_id AND status = 'active';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### Record Debt History

```sql
CREATE OR REPLACE FUNCTION record_debt_snapshot()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO debt_history (
        debt_id,
        user_id,
        balance,
        interest_rate,
        minimum_payment,
        change_amount,
        change_type,
        recorded_at
    ) VALUES (
        NEW.id,
        NEW.user_id,
        NEW.current_balance,
        NEW.interest_rate,
        NEW.minimum_payment,
        NEW.current_balance - COALESCE(OLD.current_balance, NEW.original_balance),
        CASE
            WHEN OLD IS NULL THEN 'initial'
            WHEN NEW.current_balance < OLD.current_balance THEN 'payment'
            WHEN NEW.current_balance > OLD.current_balance THEN 'charge'
            ELSE 'adjustment'
        END,
        CURRENT_DATE
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## Triggers

### Debt History Trigger

```sql
CREATE TRIGGER trigger_debt_history
    AFTER INSERT OR UPDATE OF current_balance ON debts
    FOR EACH ROW
    EXECUTE FUNCTION record_debt_snapshot();
```

### Updated At Trigger

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at column
CREATE TRIGGER set_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON income_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON expenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON debts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON strategy_milestones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON project_folders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON content_modules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON scheduled_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at BEFORE UPDATE ON feature_flags
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### Conversation Message Count Trigger

```sql
CREATE OR REPLACE FUNCTION update_conversation_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET
        message_count = message_count + 1,
        last_message_at = NEW.created_at,
        updated_at = NOW()
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_conversation_stats
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_stats();
```

---

## Indexes

Summary of critical indexes (already defined inline with tables):

| Table | Index | Purpose |
|-------|-------|---------|
| profiles | idx_profiles_email | Email lookups |
| debts | idx_debts_priority | Strategy ordering |
| debt_history | idx_debt_history_date | Timeline queries |
| transactions | idx_transactions_date | Date range queries |
| strategies | idx_strategies_primary | Find active strategy |
| project_folders | idx_project_folders_user | User folder lookups |
| conversations | idx_conversations_folder | Folder-based filtering |
| messages | idx_messages_date | Conversation loading |
| notifications | idx_notifications_unread | Unread count |
| audit_logs | idx_audit_date | Time-based auditing |

---

## Migration Strategy

### Initial Setup Order

```sql
-- 1. Core tables (no dependencies)
CREATE TABLE profiles ...
CREATE TABLE user_settings ...
CREATE TABLE content_modules ...
CREATE TABLE achievements ...
CREATE TABLE feature_flags ...
CREATE TABLE ai_prompts ...

-- 2. Financial tables (depend on profiles)
CREATE TABLE income_sources ...
CREATE TABLE accounts ...
CREATE TABLE debts ...
CREATE TABLE expenses ...

-- 3. Dependent tables
CREATE TABLE debt_history ...
CREATE TABLE transactions ...

-- 4. Strategy tables
CREATE TABLE strategies ...
CREATE TABLE strategy_milestones ...
CREATE TABLE what_if_scenarios ...
CREATE TABLE strategy_calculations ...

-- 5. Coaching tables
CREATE TABLE project_folders ...
CREATE TABLE conversations ... -- Depends on project_folders
CREATE TABLE messages ...
CREATE TABLE user_content_progress ...
CREATE TABLE user_achievements ...

-- 6. System tables
CREATE TABLE audit_logs ...
CREATE TABLE notifications ...
CREATE TABLE scheduled_tasks ...

-- 7. Enable RLS
-- 8. Create policies
-- 9. Create functions
-- 10. Create triggers
-- 11. Create indexes (if not inline)
```

### Version Control

Each migration should be versioned:
- `001_initial_schema.sql`
- `002_add_rls_policies.sql`
- `003_create_functions.sql`
- `004_create_triggers.sql`
- etc.

Use Supabase migrations or a tool like `dbmate` for version control.
