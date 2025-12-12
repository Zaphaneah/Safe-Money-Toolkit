# N8N Workflow Specifications

## Safe Money Toolkit - Automation Workflows

---

## Table of Contents

1. [Workflow Architecture](#workflow-architecture)
2. [Core Workflows](#core-workflows)
3. [Data Processing Workflows](#data-processing-workflows)
4. [Strategy Workflows](#strategy-workflows)
5. [Notification Workflows](#notification-workflows)
6. [Progress Tracking Workflows](#progress-tracking-workflows)
7. [Scheduled Workflows](#scheduled-workflows)
8. [Error Handling](#error-handling)
9. [Deployment & Configuration](#deployment--configuration)

---

## Workflow Architecture

### N8N Setup Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          N8N WORKFLOW ENGINE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │   WEBHOOK       │    │    SCHEDULE     │    │    DATABASE     │        │
│  │   TRIGGERS      │    │    TRIGGERS     │    │    TRIGGERS     │        │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘        │
│           │                      │                      │                  │
│           └──────────────────────┼──────────────────────┘                  │
│                                  │                                          │
│                                  ▼                                          │
│                    ┌─────────────────────────┐                             │
│                    │    WORKFLOW ROUTER      │                             │
│                    └─────────────────────────┘                             │
│                                  │                                          │
│         ┌────────────────────────┼────────────────────────┐                │
│         │                        │                        │                │
│         ▼                        ▼                        ▼                │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐        │
│  │   DATA      │          │  STRATEGY   │          │  NOTIFICATION│        │
│  │ PROCESSING  │          │  GENERATION │          │    ENGINE    │        │
│  └─────────────┘          └─────────────┘          └─────────────┘        │
│         │                        │                        │                │
│         └────────────────────────┼────────────────────────┘                │
│                                  │                                          │
│                                  ▼                                          │
│                    ┌─────────────────────────┐                             │
│                    │      SUPABASE DB        │                             │
│                    │      (PostgreSQL)       │                             │
│                    └─────────────────────────┘                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Integration Configuration

**Supabase Connection:**
```json
{
  "credentials": {
    "supabaseApi": {
      "host": "https://your-project.supabase.co",
      "serviceRoleKey": "{{$env.SUPABASE_SERVICE_ROLE_KEY}}"
    }
  }
}
```

**OpenAI Connection:**
```json
{
  "credentials": {
    "openAiApi": {
      "apiKey": "{{$env.OPENAI_API_KEY}}"
    }
  }
}
```

---

## Core Workflows

### Workflow Naming Convention

```
SMT-{Category}-{Number}-{Name}

Categories:
- ONBOARD  : Onboarding flows
- DATA     : Data processing
- STRAT    : Strategy generation
- NOTIFY   : Notifications
- TRACK    : Progress tracking
- MAINT    : Maintenance/cleanup
- INTEG    : External integrations
```

### Master Workflow List

| ID | Name | Trigger | Description |
|----|------|---------|-------------|
| SMT-ONBOARD-001 | New User Setup | Auth webhook | Initialize new user profile |
| SMT-ONBOARD-002 | Onboarding Reminder | Schedule | Nudge incomplete onboarding |
| SMT-DATA-001 | Spreadsheet Parser | Webhook | Process uploaded spreadsheets |
| SMT-DATA-002 | Data Validator | Webhook | Validate financial data |
| SMT-DATA-003 | Balance Reconciler | Schedule | Weekly balance check |
| SMT-STRAT-001 | Strategy Generator | Webhook/Schedule | Generate AI strategy |
| SMT-STRAT-002 | Timeline Recalculator | Webhook | Update projections |
| SMT-STRAT-003 | What-If Processor | Webhook | Process scenario requests |
| SMT-NOTIFY-001 | Payment Reminder | Schedule | Due date reminders |
| SMT-NOTIFY-002 | Milestone Achiever | Webhook | Achievement notifications |
| SMT-NOTIFY-003 | Weekly Digest | Schedule | Weekly summary email |
| SMT-NOTIFY-004 | Alert Dispatcher | Webhook | Real-time alerts |
| SMT-TRACK-001 | Progress Logger | Webhook | Log payment progress |
| SMT-TRACK-002 | Milestone Checker | Schedule | Check milestone status |
| SMT-TRACK-003 | Achievement Evaluator | Webhook | Check achievement criteria |
| SMT-MAINT-001 | Data Cleanup | Schedule | Remove stale data |
| SMT-MAINT-002 | Audit Log Archiver | Schedule | Archive old logs |

---

## Data Processing Workflows

### SMT-DATA-001: Spreadsheet Parser

**Purpose:** Parse and extract financial data from user-uploaded spreadsheets.

**Trigger:** Supabase Storage webhook on file upload to `spreadsheet-uploads` bucket.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMT-DATA-001: SPREADSHEET PARSER                          │
└─────────────────────────────────────────────────────────────────────────────┘

[Storage Webhook] ──► [Download File] ──► [Detect Format]
                                                 │
                          ┌──────────────────────┴──────────────────────┐
                          │                      │                      │
                          ▼                      ▼                      ▼
                    [Parse XLSX]           [Parse CSV]           [Parse ODS]
                          │                      │                      │
                          └──────────────────────┼──────────────────────┘
                                                 │
                                                 ▼
                                      [Normalize Structure]
                                                 │
                                                 ▼
                                      [AI Column Mapper]
                                        (GPT-3.5 call)
                                                 │
                                                 ▼
                                       [Validate Data]
                                                 │
                                    ┌────────────┴────────────┐
                                    │                         │
                                    ▼                         ▼
                            [Validation OK]          [Validation Failed]
                                    │                         │
                                    ▼                         ▼
                         [Store in Database]        [Store Errors]
                                    │                         │
                                    ▼                         ▼
                        [Trigger SMT-DATA-002]      [Notify User]
                                    │
                                    ▼
                              [Notify User]
                              (Success + Preview)
```

**Workflow JSON Structure:**

```json
{
  "name": "SMT-DATA-001: Spreadsheet Parser",
  "nodes": [
    {
      "name": "Storage Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "spreadsheet-upload",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Download File",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$json.file_url}}",
        "method": "GET",
        "responseFormat": "file"
      }
    },
    {
      "name": "Detect Format",
      "type": "n8n-nodes-base.switch",
      "parameters": {
        "rules": [
          { "output": 0, "conditions": [{ "value1": "={{$json.file_name}}", "operation": "endsWith", "value2": ".xlsx" }] },
          { "output": 1, "conditions": [{ "value1": "={{$json.file_name}}", "operation": "endsWith", "value2": ".csv" }] },
          { "output": 2, "conditions": [{ "value1": "={{$json.file_name}}", "operation": "endsWith", "value2": ".ods" }] }
        ]
      }
    },
    {
      "name": "Parse XLSX",
      "type": "n8n-nodes-base.spreadsheetFile",
      "parameters": {
        "operation": "fromFile",
        "fileFormat": "xlsx"
      }
    },
    {
      "name": "AI Column Mapper",
      "type": "n8n-nodes-base.openAi",
      "parameters": {
        "operation": "message",
        "model": "gpt-3.5-turbo",
        "messages": {
          "values": [
            {
              "role": "system",
              "content": "You are a data mapping assistant. Given spreadsheet column headers and sample data, map them to our standard schema fields: creditor_name, debt_type, current_balance, interest_rate, minimum_payment, due_day. Return a JSON object with mappings."
            },
            {
              "role": "user",
              "content": "Headers: {{$json.headers}}\nSample row: {{$json.sample_row}}"
            }
          ]
        }
      }
    },
    {
      "name": "Store in Database",
      "type": "n8n-nodes-base.supabase",
      "parameters": {
        "operation": "insert",
        "tableId": "debts",
        "fieldsUi": {
          "fieldValues": "={{$json.mapped_data}}"
        }
      }
    }
  ]
}
```

**AI Column Mapping Prompt:**

```
System: You are a financial data mapping assistant. Given spreadsheet headers
and sample data, identify which columns map to our standard debt fields.

Standard Fields:
- creditor_name: Name of the lender/creditor
- debt_type: One of [credit_card, personal_loan, auto_loan, student_loan,
  mortgage, home_equity_loan, heloc, medical_debt, other]
- current_balance: Current amount owed
- interest_rate: APR as a percentage (e.g., 19.99)
- minimum_payment: Monthly minimum payment amount
- due_day: Day of month payment is due (1-31)
- credit_limit: For revolving accounts, the credit limit

Return JSON:
{
  "mappings": {
    "creditor_name": "column_header_or_null",
    "debt_type": "column_header_or_null",
    ...
  },
  "confidence": 0.0-1.0,
  "unmapped_columns": ["col1", "col2"],
  "suggestions": "Any recommendations for the user"
}
```

### SMT-DATA-002: Data Validator

**Purpose:** Validate financial data for completeness and consistency.

**Trigger:** Called after data entry or spreadsheet import.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMT-DATA-002: DATA VALIDATOR                              │
└─────────────────────────────────────────────────────────────────────────────┘

[Webhook Trigger] ──► [Load User Data] ──► [Validate Income]
        │                                         │
        │                              ┌──────────┴──────────┐
        │                              │                     │
        │                              ▼                     ▼
        │                         [Valid]              [Invalid]
        │                              │                     │
        │                              └──────────┬──────────┘
        │                                         │
        │                                         ▼
        │                               [Validate Expenses]
        │                                         │
        │                              ┌──────────┴──────────┐
        │                              │                     │
        │                              ▼                     ▼
        │                         [Valid]              [Invalid]
        │                              │                     │
        │                              └──────────┬──────────┘
        │                                         │
        │                                         ▼
        │                                [Validate Debts]
        │                                         │
        │                              ┌──────────┴──────────┐
        │                              │                     │
        │                              ▼                     ▼
        │                         [Valid]              [Invalid]
        │                              │                     │
        │                              └──────────┬──────────┘
        │                                         │
        │                                         ▼
        │                             [Cross-Validation]
        │                         (DTI check, cashflow calc)
        │                                         │
        │                                         ▼
        │                          [Calculate Confidence Score]
        │                                         │
        │                                         ▼
        │                          [Update Profile Status]
        │                                         │
        │                    ┌────────────────────┴────────────────────┐
        │                    │                                         │
        │                    ▼                                         ▼
        │           [All Valid: Score > 0.8]               [Needs Review: Score < 0.8]
        │                    │                                         │
        │                    ▼                                         ▼
        │         [Trigger Strategy Gen]                    [Notify User]
        │                                                  (with specific issues)
```

**Validation Rules:**

```javascript
const validationRules = {
  income: {
    required: ['name', 'type', 'gross_amount', 'frequency'],
    rules: [
      { field: 'gross_amount', rule: 'positive_number' },
      { field: 'net_amount', rule: 'less_than_or_equal', compare: 'gross_amount' },
      { field: 'frequency', rule: 'in_list', values: ['weekly', 'biweekly', 'semimonthly', 'monthly', 'quarterly', 'annually'] }
    ]
  },
  debts: {
    required: ['creditor_name', 'debt_type', 'current_balance', 'interest_rate', 'minimum_payment', 'payment_due_day'],
    rules: [
      { field: 'current_balance', rule: 'positive_number' },
      { field: 'interest_rate', rule: 'between', min: 0, max: 100 },
      { field: 'minimum_payment', rule: 'positive_number' },
      { field: 'payment_due_day', rule: 'between', min: 1, max: 31 }
    ],
    crossValidation: [
      { rule: 'minimum_payment_reasonable', description: 'Min payment should be > interest portion' }
    ]
  },
  crossValidation: {
    rules: [
      { rule: 'debt_to_income_check', maxDTI: 0.50, warningDTI: 0.43 },
      { rule: 'cashflow_calculation', warnIfNegative: true }
    ]
  }
};
```

### SMT-DATA-003: Balance Reconciler

**Purpose:** Prompt users to verify/update account balances periodically.

**Trigger:** Weekly schedule (Sundays at 10:00 AM user local time).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMT-DATA-003: BALANCE RECONCILER                          │
└─────────────────────────────────────────────────────────────────────────────┘

[Weekly Schedule] ──► [Get Active Users] ──► [Filter by Last Update]
                            │
                            │ For each user where last_data_update > 7 days
                            ▼
                    [Get User's Debts]
                            │
                            ▼
                  [Generate Update Request]
                            │
                            ▼
                  [Create Notification]
                  (In-app + Email if enabled)
                            │
                            ▼
                  [Log Scheduled Task]
```

---

## Strategy Workflows

### SMT-STRAT-001: Strategy Generator

**Purpose:** Generate or regenerate a user's debt payoff strategy using AI.

**Trigger:**
- Webhook: After successful data validation (SMT-DATA-002)
- Webhook: Manual user request
- Schedule: Monthly strategy review

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMT-STRAT-001: STRATEGY GENERATOR                         │
└─────────────────────────────────────────────────────────────────────────────┘

[Trigger] ──► [Load Complete Financial Profile]
                            │
                            ▼
              [Calculate Financial Health Metrics]
              • Total debt
              • Monthly income
              • Monthly expenses
              • Cashflow
              • DTI ratio
              • Weighted avg interest
                            │
                            ▼
              [Determine Strategy Type]
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
   [Positive Cash]   [Zero Cash]      [Negative Cash]
          │                 │                 │
          ▼                 ▼                 ▼
   [Has LOC?]        [Expense Audit]   [Crisis Mode]
    │      │               │                 │
    ▼      ▼               ▼                 ▼
 [Yes]  [No]         [Income Boost]    [Hardship Opts]
    │      │               │                 │
    ▼      ▼               │                 │
[Full   [Avalanche/        │                 │
Velocity] Snowball]        │                 │
    │      │               │                 │
    └──────┴───────────────┴─────────────────┘
                            │
                            ▼
              [Build Strategy Prompt]
                            │
                            ▼
              [Call AI (GPT-4/Claude)]
                            │
                            ▼
              [Parse AI Response]
                            │
                            ▼
              [Calculate Projections]
              • Month-by-month balances
              • Payoff dates
              • Interest savings
              • Milestones
                            │
                            ▼
              [Store Strategy]
                            │
                            ▼
              [Generate Milestones]
                            │
                            ▼
              [Notify User via Realtime]
                            │
                            ▼
              [Store Calculation Record]
              (for audit)
```

**AI Strategy Generation Prompt:**

```
System Prompt:
You are a financial strategy advisor specializing in debt elimination using
Velocity Banking and traditional debt payoff methods. Analyze the user's
financial profile and generate a personalized debt payoff strategy.

Guidelines:
1. If the user has positive cashflow AND access to a line of credit (HELOC or
   personal LOC), recommend Velocity Banking as the primary strategy.
2. If no LOC is available, recommend Avalanche (highest interest first) or
   Snowball (lowest balance first) based on user preference.
3. For zero or negative cashflow, focus on expense optimization and crisis
   management strategies.
4. Always explain WHY each recommendation is made.
5. Provide specific action items for the first 30 days.

User Profile:
{{$json.financial_summary}}

Debts:
{{$json.debts_list}}

User Preferences:
- Strategy preference: {{$json.preferred_strategy}}
- Risk tolerance: {{$json.risk_tolerance}}

Respond with JSON:
{
  "recommended_strategy_type": "velocity_banking|avalanche|snowball|hybrid|crisis",
  "reasoning": "explanation of why this strategy fits the user",
  "debt_priority_order": ["debt_id_1", "debt_id_2", ...],
  "loc_recommendation": {
    "should_use_loc": true/false,
    "recommended_loc_debt_id": "debt_id or null",
    "loc_guidance": "how to use the LOC"
  },
  "monthly_plan": {
    "extra_payment_amount": 500,
    "chunk_payment_amount": 1200,
    "chunk_frequency": "monthly|biweekly"
  },
  "first_30_days_actions": [
    "action 1",
    "action 2"
  ],
  "warnings": ["any concerns or cautions"],
  "estimated_payoff_months": 54
}
```

### SMT-STRAT-002: Timeline Recalculator

**Purpose:** Recalculate projections when data changes.

**Trigger:** Webhook on debt balance update, payment logged, or settings change.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMT-STRAT-002: TIMELINE RECALCULATOR                      │
└─────────────────────────────────────────────────────────────────────────────┘

[Data Change Webhook] ──► [Load Active Strategy]
                                  │
                                  ▼
                        [Load Current Debts]
                                  │
                                  ▼
                        [Recalculate Projections]
                        (month-by-month simulation)
                                  │
                                  ▼
                        [Compare to Previous]
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
           [Significant Change]        [Minor/No Change]
           (> 1 month difference)              │
                    │                           │
                    ▼                           │
           [Update Strategy]                   │
           [Update Milestones]                 │
                    │                           │
                    ▼                           │
           [Notify User]                       │
           (timeline update)                   │
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                        [Store Calculation Record]
```

**Projection Calculation Algorithm:**

```javascript
function calculateProjections(debts, strategy, monthlyExtra) {
  const projections = [];
  let remainingDebts = [...debts].sort((a, b) => {
    // Sort by strategy priority
    return a.priority_rank - b.priority_rank;
  });

  let month = 0;
  let totalInterestPaid = 0;

  while (remainingDebts.some(d => d.current_balance > 0) && month < 360) {
    month++;
    const monthData = { month, debts: [], totalBalance: 0, interestThisMonth: 0 };

    // Calculate minimum payments and interest for all debts
    remainingDebts.forEach(debt => {
      const monthlyInterest = debt.current_balance * (debt.interest_rate / 100 / 12);
      debt.current_balance += monthlyInterest;
      debt.current_balance -= debt.minimum_payment;
      totalInterestPaid += monthlyInterest;
      monthData.interestThisMonth += monthlyInterest;
    });

    // Apply extra payment to target debt
    const targetDebt = remainingDebts.find(d => d.current_balance > 0);
    if (targetDebt) {
      targetDebt.current_balance -= monthlyExtra;
    }

    // Check for payoffs
    remainingDebts.forEach(debt => {
      if (debt.current_balance <= 0) {
        debt.current_balance = 0;
        debt.payoff_month = month;
      }
      monthData.debts.push({ id: debt.id, balance: debt.current_balance });
      monthData.totalBalance += debt.current_balance;
    });

    projections.push(monthData);

    // Remove paid off debts, add their minimum to extra payment
    const paidOff = remainingDebts.filter(d => d.current_balance === 0);
    paidOff.forEach(d => monthlyExtra += d.minimum_payment);
    remainingDebts = remainingDebts.filter(d => d.current_balance > 0);
  }

  return {
    projections,
    totalMonths: month,
    totalInterestPaid,
    debtFreeDate: addMonths(new Date(), month)
  };
}
```

### SMT-STRAT-003: What-If Processor

**Purpose:** Process user-created scenario comparisons.

**Trigger:** Webhook when user submits a what-if scenario.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMT-STRAT-003: WHAT-IF PROCESSOR                          │
└─────────────────────────────────────────────────────────────────────────────┘

[Scenario Webhook] ──► [Load Base Strategy]
                              │
                              ▼
                    [Apply Scenario Changes]
                    • Extra payment change
                    • Income change
                    • Expense change
                    • Lump sum payment
                    • Interest rate change
                              │
                              ▼
                    [Run Projection Calculator]
                              │
                              ▼
                    [Compare to Base Strategy]
                              │
                              ▼
                    [Store Scenario Results]
                              │
                              ▼
                    [Return Results to User]
                    (via webhook response)
```

---

## Notification Workflows

### SMT-NOTIFY-001: Payment Reminder

**Purpose:** Send reminders before payment due dates.

**Trigger:** Daily schedule at 9:00 AM.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMT-NOTIFY-001: PAYMENT REMINDER                          │
└─────────────────────────────────────────────────────────────────────────────┘

[Daily Schedule] ──► [Get All Active Debts]
                            │
                            ▼
            [Filter: Due in 3 days OR Due today]
                            │
                            ▼
            [Group by User]
                            │
                     For each user
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
    [Due in 3 days]                   [Due Today]
            │                               │
            ▼                               ▼
    [Create Reminder]                [Create Urgent Alert]
    (Low priority)                   (High priority)
            │                               │
            └───────────────┬───────────────┘
                            │
                            ▼
            [Check User Notification Prefs]
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
      [In-App]         [Email]          [SMS]
      (always)      (if enabled)    (if enabled)
                            │
                            ▼
            [Store Notification Record]
```

**Notification Templates:**

```javascript
const notificationTemplates = {
  payment_reminder_3day: {
    title: "Payment Due Soon",
    body: "Your {{creditor_name}} payment of {{amount}} is due in 3 days ({{due_date}}).",
    action_url: "/debts/{{debt_id}}"
  },
  payment_reminder_today: {
    title: "Payment Due Today!",
    body: "Don't forget: Your {{creditor_name}} payment of {{amount}} is due today.",
    action_url: "/debts/{{debt_id}}"
  },
  payment_reminder_urgent: {
    title: "⚠️ Payment Overdue",
    body: "Your {{creditor_name}} payment was due {{days_overdue}} day(s) ago. Pay now to avoid late fees.",
    action_url: "/debts/{{debt_id}}"
  }
};
```

### SMT-NOTIFY-002: Milestone Achiever

**Purpose:** Celebrate user achievements and milestones.

**Trigger:** Webhook when milestone or achievement is reached.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMT-NOTIFY-002: MILESTONE ACHIEVER                        │
└─────────────────────────────────────────────────────────────────────────────┘

[Milestone Webhook] ──► [Load Milestone Details]
                              │
                              ▼
                      [Determine Celebration Level]
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
          [Minor]       [Major]       [Epic]
        (e.g., 10%    (e.g., debt   (e.g., debt
         complete)     paid off)      free!)
                │             │             │
                ▼             ▼             ▼
          [Badge]       [Badge +      [Badge +
          [Points]       Confetti]     Confetti +
                        [Points]       Special
                                       Message]
                │             │             │
                └─────────────┴─────────────┘
                              │
                              ▼
                    [Check for Achievement Unlock]
                              │
                              ▼
                    [Award Achievement if new]
                              │
                              ▼
                    [Generate Celebration Message]
                              │
                              ▼
                    [Send Push Notification]
                              │
                              ▼
                    [Update Strategy Milestones]
                              │
                              ▼
                    [Log to Audit Trail]
```

### SMT-NOTIFY-003: Weekly Digest

**Purpose:** Send weekly progress summary via email.

**Trigger:** Weekly schedule (Mondays at 8:00 AM user local time).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMT-NOTIFY-003: WEEKLY DIGEST                             │
└─────────────────────────────────────────────────────────────────────────────┘

[Weekly Schedule] ──► [Get Users with Weekly Digest Enabled]
                              │
                       For each user
                              │
                              ▼
                    [Calculate Week's Progress]
                    • Payments made
                    • Balance change
                    • Interest saved
                    • Timeline change
                    • Milestones reached
                              │
                              ▼
                    [Generate AI Summary]
                    (encouraging, personalized)
                              │
                              ▼
                    [Build Email HTML]
                              │
                              ▼
                    [Send via SendGrid/Resend]
                              │
                              ▼
                    [Log Email Sent]
```

**Weekly Digest Email Template Structure:**

```html
Subject: Your Week in Review: {{net_progress}} Progress! 🎯

Hi {{first_name}},

Here's your financial progress for the week of {{week_start}} - {{week_end}}:

📊 THIS WEEK'S HIGHLIGHTS
━━━━━━━━━━━━━━━━━━━━━━━━
• Total Paid: {{total_payments}}
• Balance Reduction: {{balance_change}}
• Interest Saved: {{interest_saved}} (compared to minimum payments)

📈 YOUR JOURNEY
━━━━━━━━━━━━━━━━━━━━━━━━
[Progress Bar Visualization]
{{percentage_complete}}% Complete | {{estimated_months_remaining}} months to go

🎯 NEXT WEEK'S FOCUS
━━━━━━━━━━━━━━━━━━━━━━━━
{{ai_generated_tip}}

{{#if achievements}}
🏆 ACHIEVEMENTS UNLOCKED
━━━━━━━━━━━━━━━━━━━━━━━━
{{#each achievements}}
• {{this.title}}: {{this.description}}
{{/each}}
{{/if}}

Keep up the great work! Every payment brings you closer to financial freedom.

[View Full Dashboard Button]

- Your Safe Money Toolkit AI Coach
```

### SMT-NOTIFY-004: Alert Dispatcher

**Purpose:** Send real-time alerts for important events.

**Trigger:** Webhook for various alert types.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMT-NOTIFY-004: ALERT DISPATCHER                          │
└─────────────────────────────────────────────────────────────────────────────┘

[Alert Webhook] ──► [Parse Alert Type]
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
      ▼                    ▼                    ▼
[Strategy Alert]    [Budget Alert]      [System Alert]
      │                    │                    │
      ▼                    ▼                    ▼
• Deviation from    • Overspending      • Data sync issue
  plan detected       warning            • Balance discrepancy
• Upcoming chunk    • Unusual            • Action required
  payment             transaction
                           │
                           ▼
                  [Determine Severity]
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       [Info]          [Warning]        [Critical]
          │                │                │
          ▼                ▼                ▼
    [In-app only]   [In-app + Push]  [All channels]
                           │
                           ▼
                  [Dispatch Notifications]
                           │
                           ▼
                  [Log Alert]
```

---

## Progress Tracking Workflows

### SMT-TRACK-001: Progress Logger

**Purpose:** Log debt payments and progress updates.

**Trigger:** Webhook when payment is recorded (manual or automatic).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMT-TRACK-001: PROGRESS LOGGER                            │
└─────────────────────────────────────────────────────────────────────────────┘

[Payment Webhook] ──► [Validate Payment Data]
                              │
                              ▼
                    [Update Debt Balance]
                              │
                              ▼
                    [Record in debt_history]
                              │
                              ▼
                    [Check for Payoff]
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
             [Debt Paid Off]     [Continue]
                    │                   │
                    ▼                   │
             [Update Debt Status]       │
             [Trigger Milestone]        │
             [Update Strategy]          │
                    │                   │
                    └─────────┬─────────┘
                              │
                              ▼
                    [Trigger Recalculation]
                    (SMT-STRAT-002)
                              │
                              ▼
                    [Log to Audit Trail]
```

### SMT-TRACK-002: Milestone Checker

**Purpose:** Check if users have reached projected milestones.

**Trigger:** Daily schedule at midnight.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMT-TRACK-002: MILESTONE CHECKER                          │
└─────────────────────────────────────────────────────────────────────────────┘

[Daily Schedule] ──► [Get All Pending Milestones]
                            │
                     For each milestone
                            │
                            ▼
            [Load User's Current Progress]
                            │
                            ▼
            [Compare to Milestone Target]
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
      [Target Met]                   [Target Not Met]
            │                               │
            ▼                               │
      [Mark Achieved]                       │
      [Trigger SMT-NOTIFY-002]              │
            │                               │
            │               ┌───────────────┴───────────────┐
            │               │                               │
            │               ▼                               ▼
            │        [Past Due Date]              [Before Due Date]
            │               │                               │
            │               ▼                               │
            │        [Mark as Missed]                       │
            │        [Notify User]                          │
            │               │                               │
            └───────────────┴───────────────┬───────────────┘
                                            │
                                            ▼
                                    [Log Check Results]
```

### SMT-TRACK-003: Achievement Evaluator

**Purpose:** Check if users have unlocked achievements.

**Trigger:** Webhook after various user actions.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMT-TRACK-003: ACHIEVEMENT EVALUATOR                      │
└─────────────────────────────────────────────────────────────────────────────┘

[Action Webhook] ──► [Identify Action Type]
                            │
                            ▼
            [Get Relevant Achievement Criteria]
                            │
                     For each potential achievement
                            │
                            ▼
            [Check if Already Earned]
                            │
                    ┌───────┴───────┐
                    │               │
                    ▼               ▼
             [Not Earned]      [Already Earned]
                    │               │
                    ▼               │
            [Evaluate Criteria]     │
                    │               │
            ┌───────┴───────┐       │
            │               │       │
            ▼               ▼       │
        [Met]          [Not Met]    │
            │               │       │
            ▼               │       │
      [Award Achievement]   │       │
      [Insert user_achievements]    │
      [Trigger Celebration] │       │
            │               │       │
            └───────────────┴───────┘
                            │
                            ▼
                    [Log Evaluation]
```

**Achievement Criteria Evaluation:**

```javascript
const achievementEvaluators = {
  debt_payoff: async (userId, context) => {
    const paidOffDebts = await getDebtsByStatus(userId, 'paid_off');
    const criteria = context.criteria_config.debts_paid;
    return paidOffDebts.length >= criteria;
  },

  streak: async (userId, context) => {
    const { streak_days, action } = context.criteria_config;
    const userStreak = await getStreak(userId, action);
    return userStreak >= streak_days;
  },

  percentage_complete: async (userId, context) => {
    const { percentage_complete } = context.criteria_config;
    const progress = await getOverallProgress(userId);
    return progress.percentage >= percentage_complete;
  },

  education: async (userId, context) => {
    const { modules_completed } = context.criteria_config;
    const completed = await getCompletedModules(userId);
    return completed.length >= modules_completed;
  }
};
```

---

## Scheduled Workflows

### Schedule Configuration

| Workflow | Schedule | Timezone | Description |
|----------|----------|----------|-------------|
| SMT-DATA-003 | `0 10 * * 0` | User local | Weekly balance reminder |
| SMT-NOTIFY-001 | `0 9 * * *` | User local | Daily payment reminders |
| SMT-NOTIFY-003 | `0 8 * * 1` | User local | Monday weekly digest |
| SMT-TRACK-002 | `0 0 * * *` | UTC | Daily milestone check |
| SMT-MAINT-001 | `0 3 * * 0` | UTC | Weekly data cleanup |
| SMT-MAINT-002 | `0 4 1 * *` | UTC | Monthly audit archive |
| Monthly Review | `0 9 1 * *` | User local | Monthly strategy review |

### Handling User Timezones

```javascript
// N8N Code node for timezone-aware scheduling
const userTimezone = items[0].json.timezone || 'America/New_York';
const localTime = moment().tz(userTimezone);
const targetHour = 9; // 9 AM local time

// Check if we should execute for this user now
const shouldExecute = localTime.hour() === targetHour;

return [{ json: { shouldExecute, userTimezone, localTime: localTime.format() } }];
```

---

## Error Handling

### Global Error Handler

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ERROR HANDLING STRATEGY                               │
└─────────────────────────────────────────────────────────────────────────────┘

[Any Node Error] ──► [Error Trigger Node]
                            │
                            ▼
                    [Classify Error Type]
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
   [Transient]        [Validation]        [Critical]
   (network, etc)     (bad data)          (system)
        │                   │                   │
        ▼                   ▼                   ▼
   [Retry with         [Log Error]        [Alert DevOps]
    Backoff]           [Notify User]      [Log Error]
    (up to 3x)                            [Pause Workflow]
        │                   │                   │
        │                   │                   │
        ▼                   ▼                   ▼
   [Still Failed?]     [Store for         [Incident Created]
        │               Review]
        ▼
   [Move to DLQ]
   [Alert DevOps]
```

### Retry Configuration

```json
{
  "retry": {
    "enabled": true,
    "maxAttempts": 3,
    "initialDelay": 1000,
    "backoffMultiplier": 2,
    "maxDelay": 30000,
    "retryOn": ["ETIMEDOUT", "ECONNRESET", "502", "503", "504"]
  }
}
```

### Dead Letter Queue

For workflows that fail after retries:

```sql
-- Store failed executions for manual review
CREATE TABLE n8n_dead_letter_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_name TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    error_message TEXT,
    error_stack TEXT,
    input_data JSONB,
    attempts INTEGER,
    failed_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolved_by TEXT,
    resolution_notes TEXT
);
```

---

## Deployment & Configuration

### Environment Variables

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# AI Services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Email (SendGrid or Resend)
SENDGRID_API_KEY=SG...
EMAIL_FROM=noreply@safemoneytoolkit.com

# Push Notifications (optional)
FIREBASE_PROJECT_ID=your-project
FIREBASE_PRIVATE_KEY=...

# SMS (optional)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_NUMBER=+1...

# N8N
N8N_ENCRYPTION_KEY=your-encryption-key
WEBHOOK_URL=https://n8n.your-domain.com/webhook
```

### N8N Deployment Options

**Option 1: N8N Cloud (Recommended for MVP)**
- Managed service
- Easy setup
- Scales automatically
- ~$20/month starter tier

**Option 2: Self-Hosted (Cost-effective for scale)**
- Docker deployment
- Full control
- ~$10-50/month on VPS
- Requires DevOps management

**Docker Compose for Self-Hosted:**

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - WEBHOOK_URL=${WEBHOOK_URL}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=${POSTGRES_USER}
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    restart: always
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  n8n_data:
  postgres_data:
```

### Webhook Security

```javascript
// Validate webhook signatures
const crypto = require('crypto');

function validateWebhookSignature(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(JSON.stringify(payload))
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

// In N8N Code node:
const isValid = validateWebhookSignature(
  $json.body,
  $json.headers['x-webhook-signature'],
  $env.WEBHOOK_SECRET
);

if (!isValid) {
  throw new Error('Invalid webhook signature');
}
```

### Rate Limiting

```javascript
// Rate limit AI API calls
const rateLimiter = {
  openai: {
    requestsPerMinute: 60,
    tokensPerMinute: 90000
  }
};

// Implement in N8N with Queue + Wait nodes
```

---

## Monitoring & Logging

### Key Metrics to Track

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| Workflow success rate | N8N | < 95% |
| Execution duration | N8N | > 30s avg |
| AI API errors | N8N logs | > 5% |
| Notification delivery | SendGrid/Twilio | < 98% |
| Queue depth | N8N | > 100 pending |

### Logging Strategy

```javascript
// Structured logging in N8N Code nodes
const logEntry = {
  workflow: 'SMT-STRAT-001',
  timestamp: new Date().toISOString(),
  user_id: $json.user_id,
  action: 'strategy_generated',
  duration_ms: Date.now() - $json.start_time,
  result: 'success',
  metadata: {
    strategy_type: $json.strategy_type,
    debts_count: $json.debts.length
  }
};

// Send to logging service or store in database
```
