# Component Specifications

## Safe Money Toolkit - Frontend & Backend Components

---

## Table of Contents

1. [Component Architecture](#component-architecture)
2. [Frontend Components](#frontend-components)
3. [Backend Components (Edge Functions)](#backend-components)
4. [Shared Services](#shared-services)
5. [State Management](#state-management)
6. [API Contracts](#api-contracts)

---

## Component Architecture

### Frontend Structure (Lovable/React)

```
src/
├── app/                        # App entry and routing
│   ├── App.tsx
│   ├── routes.tsx
│   └── providers.tsx
│
├── pages/                      # Page components (routes)
│   ├── auth/
│   │   ├── LoginPage.tsx
│   │   ├── SignupPage.tsx
│   │   └── ForgotPasswordPage.tsx
│   ├── onboarding/
│   │   ├── OnboardingWizard.tsx
│   │   ├── steps/
│   │   │   ├── WelcomeStep.tsx
│   │   │   ├── IncomeStep.tsx
│   │   │   ├── ExpensesStep.tsx
│   │   │   ├── DebtsStep.tsx
│   │   │   ├── AssetsStep.tsx
│   │   │   └── ReviewStep.tsx
│   │   └── SpreadsheetUpload.tsx
│   ├── dashboard/
│   │   └── DashboardPage.tsx
│   ├── strategy/
│   │   ├── StrategyPage.tsx
│   │   └── WhatIfPage.tsx
│   ├── progress/
│   │   └── ProgressPage.tsx
│   ├── coach/
│   │   └── CoachPage.tsx
│   ├── education/
│   │   ├── EducationPage.tsx
│   │   └── ModulePage.tsx
│   └── settings/
│       └── SettingsPage.tsx
│
├── components/                 # Reusable components
│   ├── ui/                     # Base UI (shadcn/ui)
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   └── ...
│   ├── layout/
│   │   ├── MainLayout.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── MobileNav.tsx
│   ├── forms/
│   │   ├── DebtForm.tsx
│   │   ├── IncomeForm.tsx
│   │   ├── ExpenseForm.tsx
│   │   └── DataTableEditor.tsx
│   ├── visualizations/
│   │   ├── DebtLandscape.tsx
│   │   ├── CashflowRiver.tsx
│   │   ├── TimelineChart.tsx
│   │   ├── WhiteboardCanvas.tsx
│   │   └── ProgressBar.tsx
│   ├── coaching/
│   │   ├── ChatInterface.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── QuickActions.tsx
│   │   └── CoachingTip.tsx
│   ├── notifications/
│   │   ├── NotificationCenter.tsx
│   │   ├── NotificationToast.tsx
│   │   └── AchievementModal.tsx
│   └── common/
│       ├── LoadingSpinner.tsx
│       ├── ErrorBoundary.tsx
│       ├── ConfirmDialog.tsx
│       └── FileUpload.tsx
│
├── hooks/                      # Custom React hooks
│   ├── useAuth.ts
│   ├── useFinancialData.ts
│   ├── useStrategy.ts
│   ├── useChat.ts
│   ├── useNotifications.ts
│   └── useRealtime.ts
│
├── services/                   # API & external services
│   ├── supabase.ts
│   ├── api.ts
│   ├── storage.ts
│   └── analytics.ts
│
├── stores/                     # State management (Zustand)
│   ├── authStore.ts
│   ├── financialStore.ts
│   ├── uiStore.ts
│   └── notificationStore.ts
│
├── lib/                        # Utilities
│   ├── calculations.ts
│   ├── formatters.ts
│   ├── validators.ts
│   └── constants.ts
│
├── types/                      # TypeScript types
│   ├── database.ts
│   ├── api.ts
│   └── components.ts
│
└── styles/                     # Global styles
    └── globals.css
```

### Backend Structure (Supabase Edge Functions)

```
supabase/
├── functions/
│   ├── onboarding/
│   │   ├── index.ts           # POST /onboarding/profile
│   │   └── validate.ts        # POST /onboarding/validate
│   ├── strategy/
│   │   ├── index.ts           # POST /strategy/generate
│   │   ├── recalculate.ts     # POST /strategy/recalculate
│   │   └── what-if.ts         # POST /strategy/what-if
│   ├── coaching/
│   │   ├── index.ts           # POST /coaching/chat
│   │   └── suggestions.ts     # GET /coaching/suggestions
│   ├── progress/
│   │   ├── index.ts           # GET /progress/summary
│   │   └── log-payment.ts     # POST /progress/log-payment
│   ├── webhooks/
│   │   ├── n8n-callback.ts    # POST /webhooks/n8n
│   │   └── storage-trigger.ts # POST /webhooks/storage
│   └── _shared/
│       ├── cors.ts
│       ├── auth.ts
│       ├── validation.ts
│       └── ai-client.ts
│
├── migrations/
│   ├── 001_initial_schema.sql
│   ├── 002_add_rls_policies.sql
│   └── ...
│
└── seed.sql                    # Development seed data
```

---

## Frontend Components

### 1. Onboarding Components

#### `OnboardingWizard.tsx`

Multi-step onboarding form with progress tracking.

```typescript
interface OnboardingWizardProps {
  initialStep?: number;
  onComplete: () => void;
}

interface OnboardingState {
  currentStep: number;
  completedSteps: number[];
  data: {
    income: IncomeSource[];
    expenses: Expense[];
    debts: Debt[];
    accounts: Account[];
  };
  isSubmitting: boolean;
}

// Steps configuration
const ONBOARDING_STEPS = [
  { id: 'welcome', title: 'Welcome', component: WelcomeStep },
  { id: 'income', title: 'Income', component: IncomeStep },
  { id: 'expenses', title: 'Expenses', component: ExpensesStep },
  { id: 'debts', title: 'Debts', component: DebtsStep },
  { id: 'assets', title: 'Assets', component: AssetsStep },
  { id: 'review', title: 'Review', component: ReviewStep },
];

// Features:
// - Save progress on each step (localStorage + Supabase)
// - Skip and return to steps
// - Validation before proceeding
// - Alternative: Spreadsheet upload path
```

#### `SpreadsheetUpload.tsx`

Drag-and-drop spreadsheet upload with preview.

```typescript
interface SpreadsheetUploadProps {
  onUploadComplete: (data: ParsedSpreadsheetData) => void;
  acceptedFormats: string[]; // ['.xlsx', '.csv', '.ods']
  maxFileSizeMB: number;
}

interface ParsedSpreadsheetData {
  raw: any[][];
  headers: string[];
  rows: any[];
  mappings: ColumnMapping[];
  validationErrors: ValidationError[];
}

// Features:
// - Drag-and-drop zone
// - File type validation
// - Progress indicator during upload
// - Preview table with detected columns
// - AI-suggested column mappings
// - Manual mapping override UI
// - Validation summary
```

#### `DebtForm.tsx`

Form for adding/editing individual debts.

```typescript
interface DebtFormProps {
  debt?: Debt;
  onSubmit: (debt: DebtFormData) => void;
  onCancel: () => void;
}

interface DebtFormData {
  creditor_name: string;
  debt_type: DebtType;
  current_balance: number;
  interest_rate: number;
  minimum_payment: number;
  payment_due_day: number;
  credit_limit?: number;
  // ... other fields
}

// Features:
// - Auto-calculation of available credit
// - Interest type selection (fixed/variable)
// - Promotional rate fields with expiration
// - Real-time validation
// - Smart defaults based on debt type
```

### 2. Visualization Components

#### `DebtLandscape.tsx`

Overview visualization of all debts.

```typescript
interface DebtLandscapeProps {
  debts: Debt[];
  view: 'balance' | 'interest' | 'payment' | 'timeline';
  onDebtClick: (debt: Debt) => void;
  highlightDebtId?: string;
}

// Visualization modes:
// 1. Balance view: Horizontal bars showing relative balances
// 2. Interest view: Color-coded by interest rate (red = high)
// 3. Payment view: Shows minimum payments as proportion
// 4. Timeline view: Projected payoff dates

// Features:
// - Animated transitions between views
// - Hover tooltips with details
// - Click to select/focus debt
// - Total summary footer
```

**Implementation using Recharts:**

```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

const DebtLandscape: React.FC<DebtLandscapeProps> = ({ debts, view }) => {
  const data = debts.map(debt => ({
    name: debt.creditor_name,
    balance: debt.current_balance,
    interest: debt.interest_rate,
    payment: debt.minimum_payment,
    color: getColorByInterest(debt.interest_rate),
  }));

  return (
    <div className="debt-landscape">
      <div className="view-toggle">
        {/* View mode buttons */}
      </div>
      <BarChart width={600} height={300} data={data} layout="vertical">
        <XAxis type="number" />
        <YAxis type="category" dataKey="name" />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey={view === 'balance' ? 'balance' : 'payment'}>
          {data.map((entry, index) => (
            <Cell key={index} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </div>
  );
};
```

#### `CashflowRiver.tsx`

Animated visualization of money flow using Velocity Banking.

```typescript
interface CashflowRiverProps {
  income: number;
  expenses: number;
  locBalance: number;
  targetDebt: Debt;
  chunkPayment: number;
  animationSpeed: 'slow' | 'normal' | 'fast';
}

// Visual representation:
// - Income flows in from left
// - LOC hub in center (shows balance)
// - Expenses flow out to right
// - Chunk payment arrow to target debt
// - Target debt shows decreasing balance

// Features:
// - Animated flow particles
// - Interactive: click to pause/explain
// - Tooltips explaining each flow
// - Mobile-responsive layout
```

**Implementation using Canvas/SVG:**

```tsx
const CashflowRiver: React.FC<CashflowRiverProps> = ({
  income,
  expenses,
  locBalance,
  targetDebt,
  chunkPayment,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let animationId: number;

    const animate = () => {
      // Draw income stream (left side)
      drawFlow(ctx, 'income', income);

      // Draw LOC hub (center)
      drawHub(ctx, locBalance);

      // Draw expense streams (right side)
      drawFlow(ctx, 'expenses', expenses);

      // Draw chunk payment (bottom)
      drawChunkPayment(ctx, chunkPayment, targetDebt);

      animationId = requestAnimationFrame(animate);
    };

    animate();
    return () => cancelAnimationFrame(animationId);
  }, [income, expenses, locBalance, chunkPayment]);

  return (
    <div className="cashflow-river">
      <canvas ref={canvasRef} width={800} height={400} />
      <div className="legend">
        {/* Flow legend */}
      </div>
    </div>
  );
};
```

#### `TimelineChart.tsx`

Projected payoff timeline with milestones.

```typescript
interface TimelineChartProps {
  projections: MonthlyProjection[];
  milestones: Milestone[];
  comparisonProjections?: MonthlyProjection[]; // For what-if comparison
  showConfidenceBands: boolean;
}

interface MonthlyProjection {
  month: number;
  date: Date;
  totalBalance: number;
  balancesByDebt: { debtId: string; balance: number }[];
  interestPaid: number;
  principalPaid: number;
}

// Features:
// - Line chart showing balance over time
// - Milestone markers on timeline
// - Confidence bands (best/worst case)
// - Comparison overlay for what-if
// - Zoom and pan for long timelines
// - Hover to see monthly details
```

#### `WhiteboardCanvas.tsx`

Interactive whiteboard-style strategy explanation.

```typescript
interface WhiteboardCanvasProps {
  strategy: Strategy;
  debts: Debt[];
  isInteractive: boolean;
  onDebtReorder?: (newOrder: string[]) => void;
}

// Visual style:
// - Hand-drawn aesthetic (rough.js or similar)
// - Whiteboard background
// - Marker-style text and lines
// - Arrows showing money flow
// - Boxes for each debt with details

// Features:
// - Drag-and-drop debt reordering
// - Click for detailed explanations
// - Animated step-by-step walkthrough
// - Export as image/PDF
```

### 3. Coaching Components

#### `ChatInterface.tsx`

Conversational AI chat interface.

```typescript
interface ChatInterfaceProps {
  conversationId?: string;
  onNewMessage: (message: string) => Promise<ChatResponse>;
  suggestions?: string[];
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  actions?: QuickAction[];
  attachments?: Attachment[];
}

interface QuickAction {
  type: 'view_strategy' | 'update_balance' | 'view_education' | 'navigate';
  label: string;
  data: any;
}

// Features:
// - Message history with virtual scrolling
// - Typing indicator for AI responses
// - Quick action buttons in responses
// - Suggested follow-up questions
// - Code/calculation formatting
// - Mobile-optimized keyboard handling
```

**Implementation:**

```tsx
const ChatInterface: React.FC<ChatInterfaceProps> = ({
  conversationId,
  onNewMessage,
  suggestions,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await onNewMessage(input);
      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: response.content,
        timestamp: new Date(),
        actions: response.actions,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      // Handle error
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="chat-interface flex flex-col h-full">
      <div className="messages-container flex-1 overflow-y-auto p-4">
        {messages.map(message => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {suggestions && suggestions.length > 0 && (
        <div className="suggestions flex gap-2 p-2 overflow-x-auto">
          {suggestions.map(suggestion => (
            <button
              key={suggestion}
              onClick={() => setInput(suggestion)}
              className="suggestion-chip"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      <div className="input-area flex gap-2 p-4 border-t">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && handleSend()}
          placeholder="Ask your financial coach..."
          className="flex-1 px-4 py-2 border rounded-lg"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isTyping}
          className="px-4 py-2 bg-primary text-white rounded-lg"
        >
          Send
        </button>
      </div>
    </div>
  );
};
```

### 4. Dashboard Components

#### `DashboardPage.tsx`

Main dashboard with key metrics.

```typescript
interface DashboardData {
  totalDebt: number;
  totalDebtChange: number; // vs last month
  monthlyCashflow: number;
  debtFreeDate: Date;
  daysToFreedom: number;
  interestSavedToDate: number;
  currentStreak: number;
  nextMilestone: Milestone;
  upcomingPayments: UpcomingPayment[];
  recentActivity: Activity[];
}

// Dashboard sections:
// 1. Hero metrics (total debt, progress %)
// 2. Quick stats cards
// 3. Mini debt landscape
// 4. Next actions/reminders
// 5. Recent activity feed
// 6. Quick chat access
```

---

## Backend Components

### 1. Edge Function: Strategy Generator

`supabase/functions/strategy/index.ts`

```typescript
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { corsHeaders } from '../_shared/cors.ts';
import { validateAuth } from '../_shared/auth.ts';
import { generateStrategy } from './strategy-engine.ts';

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    // Validate authentication
    const user = await validateAuth(req);
    if (!user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Initialize Supabase client
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    );

    // Load user's financial data
    const { data: profile } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single();

    const { data: debts } = await supabase
      .from('debts')
      .select('*')
      .eq('user_id', user.id)
      .eq('status', 'active');

    const { data: incomes } = await supabase
      .from('income_sources')
      .select('*')
      .eq('user_id', user.id)
      .eq('is_active', true);

    const { data: expenses } = await supabase
      .from('expenses')
      .select('*')
      .eq('user_id', user.id)
      .eq('is_active', true);

    // Calculate financial metrics
    const metrics = calculateFinancialMetrics(incomes, expenses, debts);

    // Generate strategy using AI
    const strategy = await generateStrategy({
      profile,
      debts,
      metrics,
      preferences: {
        strategyType: profile.preferred_strategy,
        riskTolerance: profile.risk_tolerance,
      },
    });

    // Store strategy in database
    const { data: savedStrategy, error: saveError } = await supabase
      .from('strategies')
      .insert({
        user_id: user.id,
        strategy_type: strategy.type,
        config: strategy.config,
        snapshot: metrics,
        projections: strategy.projections,
        ai_generated: true,
        ai_reasoning: strategy.reasoning,
        is_primary: true,
        status: 'active',
      })
      .select()
      .single();

    if (saveError) throw saveError;

    // Generate milestones
    const milestones = generateMilestones(savedStrategy, debts);
    await supabase.from('strategy_milestones').insert(milestones);

    // Return strategy to client
    return new Response(
      JSON.stringify({
        success: true,
        strategy: savedStrategy,
        milestones,
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Strategy generation error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
```

### 2. Edge Function: Coaching Chat

`supabase/functions/coaching/index.ts`

```typescript
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { corsHeaders } from '../_shared/cors.ts';
import { validateAuth } from '../_shared/auth.ts';
import { callOpenAI } from '../_shared/ai-client.ts';

interface ChatRequest {
  conversationId?: string;
  message: string;
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const user = await validateAuth(req);
    if (!user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const { conversationId, message }: ChatRequest = await req.json();

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    );

    // Get or create conversation
    let convId = conversationId;
    if (!convId) {
      const { data: newConv } = await supabase
        .from('conversations')
        .insert({ user_id: user.id, status: 'active' })
        .select()
        .single();
      convId = newConv.id;
    }

    // Get conversation history (last 10 messages)
    const { data: history } = await supabase
      .from('messages')
      .select('role, content')
      .eq('conversation_id', convId)
      .order('created_at', { ascending: false })
      .limit(10);

    // Get user's financial context
    const context = await getUserFinancialContext(supabase, user.id);

    // Store user message
    await supabase.from('messages').insert({
      conversation_id: convId,
      user_id: user.id,
      role: 'user',
      content: message,
    });

    // Build AI prompt
    const systemPrompt = buildCoachingSystemPrompt(context);
    const messages = [
      { role: 'system', content: systemPrompt },
      ...(history || []).reverse(),
      { role: 'user', content: message },
    ];

    // Call AI
    const startTime = Date.now();
    const aiResponse = await callOpenAI({
      model: 'gpt-3.5-turbo',
      messages,
      temperature: 0.7,
      max_tokens: 1000,
    });

    const responseTime = Date.now() - startTime;

    // Extract suggested actions from response
    const suggestedActions = extractActions(aiResponse.content, context);

    // Store assistant message
    const { data: assistantMessage } = await supabase
      .from('messages')
      .insert({
        conversation_id: convId,
        user_id: user.id,
        role: 'assistant',
        content: aiResponse.content,
        ai_model: 'gpt-3.5-turbo',
        tokens_used: aiResponse.usage?.total_tokens,
        response_time_ms: responseTime,
        suggested_actions: suggestedActions,
      })
      .select()
      .single();

    return new Response(
      JSON.stringify({
        conversationId: convId,
        message: assistantMessage,
        suggestions: generateFollowUpSuggestions(message, context),
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Coaching chat error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

function buildCoachingSystemPrompt(context: UserFinancialContext): string {
  return `You are a friendly, knowledgeable financial coach helping users eliminate debt using the Velocity Banking method and other proven strategies.

USER'S FINANCIAL SNAPSHOT:
- Total Debt: $${context.totalDebt.toLocaleString()}
- Monthly Income: $${context.monthlyIncome.toLocaleString()}
- Monthly Expenses: $${context.monthlyExpenses.toLocaleString()}
- Monthly Cashflow: $${context.monthlyCashflow.toLocaleString()}
- Current Strategy: ${context.strategyType}
- Progress: ${context.progressPercentage}% complete
- Target Debt-Free Date: ${context.debtFreeDate}

DEBTS (prioritized):
${context.debts.map((d, i) => `${i + 1}. ${d.creditor_name}: $${d.current_balance.toLocaleString()} @ ${d.interest_rate}% APR`).join('\n')}

GUIDELINES:
1. Be encouraging but realistic
2. Explain financial concepts in simple terms
3. Reference the user's specific numbers when relevant
4. Suggest specific actions when appropriate
5. If asked about calculations, show the math
6. Never give specific investment or tax advice
7. Remind users you're a tool to help them, not a licensed financial advisor

Respond in a conversational, helpful tone.`;
}
```

### 3. Shared AI Client

`supabase/functions/_shared/ai-client.ts`

```typescript
interface OpenAIRequest {
  model: string;
  messages: { role: string; content: string }[];
  temperature?: number;
  max_tokens?: number;
}

interface OpenAIResponse {
  id: string;
  choices: { message: { content: string } }[];
  usage: { total_tokens: number };
}

export async function callOpenAI(request: OpenAIRequest): Promise<{
  content: string;
  usage: { total_tokens: number };
}> {
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`OpenAI API error: ${error}`);
  }

  const data: OpenAIResponse = await response.json();

  return {
    content: data.choices[0].message.content,
    usage: data.usage,
  };
}

// Alternative: Anthropic Claude
export async function callClaude(request: {
  model: string;
  messages: { role: string; content: string }[];
  max_tokens?: number;
}): Promise<{ content: string }> {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': Deno.env.get('ANTHROPIC_API_KEY')!,
      'anthropic-version': '2023-06-01',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: request.model,
      max_tokens: request.max_tokens || 1024,
      messages: request.messages,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Claude API error: ${error}`);
  }

  const data = await response.json();
  return { content: data.content[0].text };
}
```

---

## State Management

### Zustand Store: Financial Data

```typescript
// stores/financialStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface FinancialState {
  // Data
  debts: Debt[];
  incomes: IncomeSource[];
  expenses: Expense[];
  accounts: Account[];
  strategy: Strategy | null;
  projections: Projection[];

  // Loading states
  isLoading: boolean;
  error: string | null;

  // Derived values
  totalDebt: number;
  monthlyIncome: number;
  monthlyExpenses: number;
  monthlyCashflow: number;

  // Actions
  setDebts: (debts: Debt[]) => void;
  addDebt: (debt: Debt) => void;
  updateDebt: (id: string, updates: Partial<Debt>) => void;
  removeDebt: (id: string) => void;

  setIncomes: (incomes: IncomeSource[]) => void;
  setExpenses: (expenses: Expense[]) => void;
  setStrategy: (strategy: Strategy) => void;

  calculateDerived: () => void;
  fetchAllData: () => Promise<void>;
  reset: () => void;
}

export const useFinancialStore = create<FinancialState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        debts: [],
        incomes: [],
        expenses: [],
        accounts: [],
        strategy: null,
        projections: [],
        isLoading: false,
        error: null,
        totalDebt: 0,
        monthlyIncome: 0,
        monthlyExpenses: 0,
        monthlyCashflow: 0,

        // Actions
        setDebts: (debts) => {
          set({ debts });
          get().calculateDerived();
        },

        addDebt: (debt) => {
          set((state) => ({ debts: [...state.debts, debt] }));
          get().calculateDerived();
        },

        updateDebt: (id, updates) => {
          set((state) => ({
            debts: state.debts.map((d) =>
              d.id === id ? { ...d, ...updates } : d
            ),
          }));
          get().calculateDerived();
        },

        removeDebt: (id) => {
          set((state) => ({
            debts: state.debts.filter((d) => d.id !== id),
          }));
          get().calculateDerived();
        },

        setIncomes: (incomes) => {
          set({ incomes });
          get().calculateDerived();
        },

        setExpenses: (expenses) => {
          set({ expenses });
          get().calculateDerived();
        },

        setStrategy: (strategy) => set({ strategy }),

        calculateDerived: () => {
          const { debts, incomes, expenses } = get();

          const totalDebt = debts
            .filter((d) => d.status === 'active')
            .reduce((sum, d) => sum + d.current_balance, 0);

          const monthlyIncome = incomes
            .filter((i) => i.is_active)
            .reduce((sum, i) => sum + normalizeToMonthly(i.net_amount, i.frequency), 0);

          const monthlyExpenses = expenses
            .filter((e) => e.is_active)
            .reduce((sum, e) => sum + normalizeToMonthly(e.amount, e.frequency), 0);

          set({
            totalDebt,
            monthlyIncome,
            monthlyExpenses,
            monthlyCashflow: monthlyIncome - monthlyExpenses,
          });
        },

        fetchAllData: async () => {
          set({ isLoading: true, error: null });
          try {
            const [debts, incomes, expenses, accounts, strategy] = await Promise.all([
              api.getDebts(),
              api.getIncomes(),
              api.getExpenses(),
              api.getAccounts(),
              api.getActiveStrategy(),
            ]);
            set({ debts, incomes, expenses, accounts, strategy });
            get().calculateDerived();
          } catch (error) {
            set({ error: error.message });
          } finally {
            set({ isLoading: false });
          }
        },

        reset: () => {
          set({
            debts: [],
            incomes: [],
            expenses: [],
            accounts: [],
            strategy: null,
            projections: [],
            totalDebt: 0,
            monthlyIncome: 0,
            monthlyExpenses: 0,
            monthlyCashflow: 0,
          });
        },
      }),
      {
        name: 'financial-storage',
        partialize: (state) => ({
          // Only persist certain fields
          debts: state.debts,
          incomes: state.incomes,
          expenses: state.expenses,
        }),
      }
    )
  )
);

// Helper function
function normalizeToMonthly(amount: number, frequency: string): number {
  const multipliers: Record<string, number> = {
    weekly: 4.33,
    biweekly: 2.17,
    semimonthly: 2,
    monthly: 1,
    quarterly: 1 / 3,
    annually: 1 / 12,
  };
  return amount * (multipliers[frequency] || 1);
}
```

### React Query Setup

```typescript
// services/api.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { supabase } from './supabase';

// Query keys
export const queryKeys = {
  debts: ['debts'] as const,
  incomes: ['incomes'] as const,
  expenses: ['expenses'] as const,
  strategy: ['strategy'] as const,
  projections: (strategyId: string) => ['projections', strategyId] as const,
  conversations: ['conversations'] as const,
  notifications: ['notifications'] as const,
};

// Hooks
export function useDebts() {
  return useQuery({
    queryKey: queryKeys.debts,
    queryFn: async () => {
      const { data, error } = await supabase
        .from('debts')
        .select('*')
        .eq('status', 'active')
        .order('priority_rank');
      if (error) throw error;
      return data;
    },
  });
}

export function useUpdateDebt() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, updates }: { id: string; updates: Partial<Debt> }) => {
      const { data, error } = await supabase
        .from('debts')
        .update(updates)
        .eq('id', id)
        .select()
        .single();
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.debts });
      queryClient.invalidateQueries({ queryKey: queryKeys.strategy });
    },
  });
}

export function useGenerateStrategy() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const response = await fetch('/functions/v1/strategy', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error('Strategy generation failed');
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.strategy, data.strategy);
      queryClient.invalidateQueries({ queryKey: ['milestones'] });
    },
  });
}
```

---

## API Contracts

### Strategy Generation

**POST** `/functions/v1/strategy`

Request:
```typescript
interface GenerateStrategyRequest {
  forceRegenerate?: boolean;
  preferences?: {
    strategyType?: 'velocity' | 'avalanche' | 'snowball' | 'auto';
    riskTolerance?: 'conservative' | 'moderate' | 'aggressive';
  };
}
```

Response:
```typescript
interface GenerateStrategyResponse {
  success: boolean;
  strategy: {
    id: string;
    strategy_type: string;
    config: StrategyConfig;
    projections: Projections;
    ai_reasoning: string;
  };
  milestones: Milestone[];
}

interface StrategyConfig {
  loc_debt_id: string | null;
  target_debt_order: string[];
  monthly_extra_payment: number;
  chunk_payment_amount: number;
  chunk_payment_frequency: 'weekly' | 'biweekly' | 'monthly';
}

interface Projections {
  debt_free_date: string;
  months_to_payoff: number;
  total_interest_standard: number;
  total_interest_strategy: number;
  interest_savings: number;
  confidence_score: number;
  monthly_projections: MonthlyProjection[];
}
```

### Coaching Chat

**POST** `/functions/v1/coaching/chat`

Request:
```typescript
interface ChatRequest {
  conversationId?: string;
  message: string;
}
```

Response:
```typescript
interface ChatResponse {
  conversationId: string;
  message: {
    id: string;
    role: 'assistant';
    content: string;
    suggested_actions: QuickAction[];
    created_at: string;
  };
  suggestions: string[];
}
```

### Progress Logging

**POST** `/functions/v1/progress/log-payment`

Request:
```typescript
interface LogPaymentRequest {
  debt_id: string;
  amount: number;
  payment_date: string;
  is_extra_payment: boolean;
  notes?: string;
}
```

Response:
```typescript
interface LogPaymentResponse {
  success: boolean;
  debt: Debt; // Updated debt
  milestone_achieved?: Milestone;
  new_projections?: Projections;
}
```
