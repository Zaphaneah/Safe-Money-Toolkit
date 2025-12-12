# Security & Compliance Documentation

## Safe Money Toolkit - Security Architecture

---

## Table of Contents

1. [Security Overview](#security-overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Data Protection](#data-protection)
4. [API Security](#api-security)
5. [Infrastructure Security](#infrastructure-security)
6. [Compliance Considerations](#compliance-considerations)
7. [Audit & Logging](#audit--logging)
8. [Incident Response](#incident-response)
9. [Security Checklist](#security-checklist)

---

## Security Overview

### Security Principles

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Minimal access rights for all components
3. **Zero Trust**: Verify everything, trust nothing by default
4. **Data Minimization**: Collect only necessary data
5. **Transparency**: Clear privacy policies and user control

### Threat Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THREAT LANDSCAPE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EXTERNAL THREATS                  INTERNAL THREATS                         │
│  ─────────────────                 ─────────────────                        │
│  • Unauthorized access             • Accidental data exposure               │
│  • Credential stuffing             • Misconfiguration                       │
│  • API abuse                       • Insider threat                         │
│  • DDoS attacks                    • Third-party vulnerabilities            │
│  • Data scraping                   • Supply chain attacks                   │
│  • Phishing                        • Logging sensitive data                 │
│                                                                             │
│  DATA RISKS                        COMPLIANCE RISKS                         │
│  ──────────                        ─────────────────                        │
│  • Financial data exposure         • GDPR violations (if EU)                │
│  • PII leakage                     • State privacy laws                     │
│  • Unauthorized data sharing       • Financial regulation                   │
│  • Inadequate encryption           • Audit failures                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Security Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Layer 1: PERIMETER                                                         │
│  ├── Cloudflare WAF (optional)                                              │
│  ├── DDoS Protection                                                        │
│  └── SSL/TLS Termination                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  Layer 2: APPLICATION                                                       │
│  ├── Supabase Auth (JWT tokens)                                             │
│  ├── Rate Limiting                                                          │
│  ├── Input Validation                                                       │
│  └── CORS Configuration                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  Layer 3: DATA                                                              │
│  ├── Row Level Security (RLS)                                               │
│  ├── Column-level Encryption                                                │
│  ├── Encryption at Rest (AES-256)                                           │
│  └── Encryption in Transit (TLS 1.3)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  Layer 4: MONITORING                                                        │
│  ├── Audit Logging                                                          │
│  ├── Anomaly Detection                                                      │
│  └── Security Alerting                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Authentication & Authorization

### Authentication Methods

#### Supabase Auth Configuration

```typescript
// supabase/config.toml settings
[auth]
enabled = true
site_url = "https://app.safemoneytoolkit.com"
jwt_expiry = 3600  # 1 hour
enable_signup = true
enable_confirmations = true

[auth.email]
enable_signup = true
double_confirm_changes = true
enable_confirmations = true

[auth.external.google]
enabled = true
client_id = "env(GOOGLE_CLIENT_ID)"
secret = "env(GOOGLE_CLIENT_SECRET)"

[auth.external.apple]
enabled = true
client_id = "env(APPLE_CLIENT_ID)"
secret = "env(APPLE_CLIENT_SECRET)"
```

#### Password Requirements

```typescript
const PASSWORD_POLICY = {
  minLength: 8,
  requireUppercase: true,
  requireLowercase: true,
  requireNumber: true,
  requireSpecialChar: false, // Recommended but not required
  maxLength: 128,
  preventCommonPasswords: true,
};

// Supabase handles password hashing with bcrypt (10 rounds)
```

#### Multi-Factor Authentication (Recommended)

```typescript
// Enable MFA for users (optional but recommended)
// Supabase Auth supports TOTP (Time-based One-Time Password)

// User can enable MFA in settings:
const enableMFA = async () => {
  const { data, error } = await supabase.auth.mfa.enroll({
    factorType: 'totp',
    issuer: 'Safe Money Toolkit',
    friendlyName: 'Authenticator App',
  });

  // Display QR code for user to scan
  // User verifies with code from authenticator
};
```

### Session Management

```typescript
// Session configuration
const SESSION_CONFIG = {
  // JWT tokens
  accessTokenExpiry: 3600, // 1 hour
  refreshTokenExpiry: 604800, // 7 days

  // Session settings
  persistSession: true, // Store in localStorage
  detectSessionInUrl: true, // Handle OAuth redirects

  // Security settings
  autoRefreshToken: true,
  debug: false, // Disable in production
};

// Session handling in application
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    storage: window.localStorage,
  },
});

// Logout handling
const handleLogout = async () => {
  await supabase.auth.signOut({ scope: 'global' }); // Sign out all sessions
};
```

### Authorization: Row Level Security

#### RLS Policy Patterns

```sql
-- Pattern 1: User owns the data
CREATE POLICY "Users can only access own data" ON debts
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Pattern 2: Admin access
CREATE POLICY "Admins can access all data" ON debts
  FOR SELECT
  USING (
    auth.jwt() ->> 'role' = 'admin'
  );

-- Pattern 3: Read-only public data
CREATE POLICY "Anyone can read published content" ON content_modules
  FOR SELECT
  USING (is_published = true);

-- Pattern 4: Insert only own data
CREATE POLICY "Users can only insert own debts" ON debts
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Pattern 5: Service role bypass
-- Note: Service role automatically bypasses RLS
-- Use only for backend operations (N8N, Edge Functions)
```

#### RLS Testing

```sql
-- Test RLS as a specific user
SET request.jwt.claim.sub = 'user-uuid-here';
SET request.jwt.claim.role = 'authenticated';

-- Try to access data
SELECT * FROM debts WHERE id = 'some-debt-id';
-- Should only return if user_id matches

-- Reset
RESET ALL;
```

---

## Data Protection

### Encryption at Rest

Supabase uses PostgreSQL with encryption at rest via:
- AWS RDS encryption (AES-256)
- Storage bucket encryption

### Encryption in Transit

- All connections use TLS 1.3
- HSTS enabled
- Certificate pinning for mobile (optional)

### Sensitive Data Handling

#### Data Classification

| Classification | Examples | Handling |
|---------------|----------|----------|
| **Highly Sensitive** | Passwords, tokens | Never stored (hashed), never logged |
| **Sensitive** | Account balances, income | Encrypted, access-controlled, audit logged |
| **Internal** | User preferences | Access-controlled |
| **Public** | Educational content | No restrictions |

#### Field-Level Encryption (Optional Enhancement)

```typescript
// For extra-sensitive fields, consider application-level encryption
import { createCipheriv, createDecipheriv, randomBytes } from 'crypto';

const ENCRYPTION_KEY = process.env.DATA_ENCRYPTION_KEY!; // 32 bytes

function encryptField(plaintext: string): string {
  const iv = randomBytes(16);
  const cipher = createCipheriv('aes-256-gcm', Buffer.from(ENCRYPTION_KEY, 'hex'), iv);
  let encrypted = cipher.update(plaintext, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  const authTag = cipher.getAuthTag();
  return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`;
}

function decryptField(ciphertext: string): string {
  const [ivHex, authTagHex, encrypted] = ciphertext.split(':');
  const decipher = createDecipheriv(
    'aes-256-gcm',
    Buffer.from(ENCRYPTION_KEY, 'hex'),
    Buffer.from(ivHex, 'hex')
  );
  decipher.setAuthTag(Buffer.from(authTagHex, 'hex'));
  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

// Usage: Encrypt account numbers, SSN (if ever collected), etc.
```

### Data Minimization

**Data We Collect:**
- Email address (required for auth)
- Financial data (user-provided, necessary for service)
- Usage analytics (optional, anonymized)

**Data We Do NOT Collect:**
- Full bank account numbers (only last 4 digits)
- Social Security Numbers
- Full credit card numbers
- Bank login credentials

### Data Retention

```sql
-- Data retention policy
-- Active users: Retain all data
-- Inactive users (no login > 2 years): Send reminder, then archive
-- Deleted accounts: Soft delete, hard delete after 30 days

-- Audit logs: Archive after 90 days, delete after 2 years
-- Chat history: Retain for 1 year, then summarize and delete messages
```

### User Data Rights

```typescript
// Data export (GDPR Article 20)
async function exportUserData(userId: string): Promise<UserDataExport> {
  const [profile, debts, income, expenses, strategies, messages] = await Promise.all([
    supabase.from('profiles').select('*').eq('id', userId).single(),
    supabase.from('debts').select('*').eq('user_id', userId),
    supabase.from('income_sources').select('*').eq('user_id', userId),
    supabase.from('expenses').select('*').eq('user_id', userId),
    supabase.from('strategies').select('*').eq('user_id', userId),
    supabase.from('messages').select('*').eq('user_id', userId),
  ]);

  return {
    profile: profile.data,
    financialData: { debts: debts.data, income: income.data, expenses: expenses.data },
    strategies: strategies.data,
    conversations: messages.data,
    exportedAt: new Date().toISOString(),
  };
}

// Data deletion (GDPR Article 17)
async function deleteUserData(userId: string): Promise<void> {
  // Soft delete first (30 day grace period)
  await supabase.from('profiles').update({ deleted_at: new Date() }).eq('id', userId);

  // Schedule hard delete after 30 days
  await scheduleHardDelete(userId, 30);
}

// Hard delete (after grace period)
async function hardDeleteUserData(userId: string): Promise<void> {
  // Delete in order of dependencies (foreign keys)
  await supabase.from('messages').delete().eq('user_id', userId);
  await supabase.from('conversations').delete().eq('user_id', userId);
  await supabase.from('user_achievements').delete().eq('user_id', userId);
  await supabase.from('strategy_milestones').delete().eq('user_id', userId);
  await supabase.from('strategies').delete().eq('user_id', userId);
  await supabase.from('debt_history').delete().eq('user_id', userId);
  await supabase.from('transactions').delete().eq('user_id', userId);
  await supabase.from('debts').delete().eq('user_id', userId);
  await supabase.from('expenses').delete().eq('user_id', userId);
  await supabase.from('income_sources').delete().eq('user_id', userId);
  await supabase.from('accounts').delete().eq('user_id', userId);
  await supabase.from('notifications').delete().eq('user_id', userId);
  await supabase.from('user_settings').delete().eq('user_id', userId);
  await supabase.from('profiles').delete().eq('id', userId);

  // Delete from Supabase Auth
  await supabase.auth.admin.deleteUser(userId);
}
```

---

## API Security

### Rate Limiting

```typescript
// Edge Function rate limiting
const RATE_LIMITS = {
  '/api/strategy/generate': { requests: 10, window: '1h' },
  '/api/coaching/chat': { requests: 100, window: '1h' },
  '/api/progress/*': { requests: 60, window: '1m' },
  default: { requests: 1000, window: '1h' },
};

// Implementation using Supabase Edge Function
import { RateLimiter } from 'rate-limiter-flexible';

const rateLimiter = new RateLimiter({
  points: 100, // requests
  duration: 3600, // per hour
});

async function checkRateLimit(userId: string, endpoint: string): Promise<boolean> {
  try {
    await rateLimiter.consume(`${userId}:${endpoint}`);
    return true;
  } catch (error) {
    return false; // Rate limit exceeded
  }
}
```

### Input Validation

```typescript
// Zod schemas for all inputs
import { z } from 'zod';

// Debt input validation
const debtSchema = z.object({
  creditor_name: z.string().min(1).max(100).trim(),
  debt_type: z.enum([
    'credit_card', 'personal_loan', 'auto_loan', 'student_loan',
    'mortgage', 'home_equity_loan', 'heloc', 'medical_debt', 'other'
  ]),
  current_balance: z.number().positive().max(100_000_000), // Max $100M
  interest_rate: z.number().min(0).max(100), // 0-100%
  minimum_payment: z.number().positive().max(1_000_000),
  payment_due_day: z.number().int().min(1).max(31),
  credit_limit: z.number().positive().optional(),
});

// Chat message validation
const chatMessageSchema = z.object({
  message: z.string().min(1).max(4000).trim(),
  conversationId: z.string().uuid().optional(),
});

// Validate in Edge Functions
function validateInput<T>(schema: z.ZodSchema<T>, data: unknown): T {
  const result = schema.safeParse(data);
  if (!result.success) {
    throw new ValidationError(result.error.issues);
  }
  return result.data;
}
```

### SQL Injection Prevention

```typescript
// Always use parameterized queries (Supabase handles this)

// GOOD: Using Supabase client
const { data } = await supabase
  .from('debts')
  .select('*')
  .eq('user_id', userId)
  .eq('id', debtId);

// BAD: Never build raw SQL strings
// const query = `SELECT * FROM debts WHERE id = '${debtId}'`; // NEVER DO THIS
```

### XSS Prevention

```typescript
// React automatically escapes output
// For HTML content, use DOMPurify
import DOMPurify from 'dompurify';

// When rendering markdown/HTML from AI
const sanitizedHtml = DOMPurify.sanitize(aiResponse, {
  ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'code', 'pre'],
  ALLOWED_ATTR: [],
});

// Content Security Policy
const CSP_HEADER = `
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://cdn.lovable.dev;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://*.supabase.co https://api.openai.com;
  frame-ancestors 'none';
`.replace(/\n/g, ' ');
```

### CORS Configuration

```typescript
// supabase/functions/_shared/cors.ts
export const corsHeaders = {
  'Access-Control-Allow-Origin': process.env.ALLOWED_ORIGIN || 'https://app.safemoneytoolkit.com',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Max-Age': '86400', // 24 hours
};

// In Edge Functions
if (req.method === 'OPTIONS') {
  return new Response('ok', { headers: corsHeaders });
}
```

---

## Infrastructure Security

### Secrets Management

```bash
# Environment variables (never commit to git)
# .env.local (development)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ... # Public, safe for client
SUPABASE_SERVICE_ROLE_KEY=eyJ... # NEVER expose to client

# AI APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Application secrets
DATA_ENCRYPTION_KEY=... # 32 bytes hex
WEBHOOK_SECRET=... # For validating webhooks

# Store in:
# - Lovable: Environment Variables settings
# - Supabase: Edge Function secrets
# - N8N: Credentials store
```

### Network Security

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NETWORK ARCHITECTURE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Internet                                                                   │
│      │                                                                      │
│      ▼                                                                      │
│  ┌──────────────────┐                                                       │
│  │  Cloudflare      │  ← WAF, DDoS protection                               │
│  │  (Optional)      │                                                       │
│  └────────┬─────────┘                                                       │
│           │                                                                 │
│      ┌────┴────┐                                                            │
│      │         │                                                            │
│      ▼         ▼                                                            │
│  ┌───────┐ ┌───────────┐                                                    │
│  │Lovable│ │ Supabase  │  ← Managed platforms (their security)              │
│  │(CDN)  │ │           │                                                    │
│  └───────┘ └─────┬─────┘                                                    │
│                  │                                                          │
│           ┌──────┴──────┐                                                   │
│           │             │                                                   │
│           ▼             ▼                                                   │
│     ┌──────────┐  ┌──────────┐                                              │
│     │Edge Funcs│  │ Database │  ← Private, no direct access                 │
│     └──────────┘  └──────────┘                                              │
│                                                                             │
│  N8N (Self-hosted option):                                                  │
│  ┌──────────────────┐                                                       │
│  │  VPS with        │  ← Firewall: Only allow Supabase IPs                  │
│  │  Docker + N8N    │    and your IP for admin                              │
│  └──────────────────┘                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Dependency Security

```json
// package.json scripts
{
  "scripts": {
    "audit": "npm audit",
    "audit:fix": "npm audit fix",
    "deps:check": "npx npm-check-updates"
  }
}

// Automated scanning
// - GitHub Dependabot enabled
// - Snyk integration (optional)
// - npm audit in CI pipeline
```

---

## Compliance Considerations

### Disclaimer Requirements

**Mandatory Disclaimers:**

```typescript
// Display on signup and in app
const FINANCIAL_DISCLAIMER = `
Safe Money Toolkit is an educational tool designed to help you understand
and manage your personal finances. It is NOT a substitute for professional
financial advice.

We do not provide:
- Investment advice
- Tax advice
- Legal advice
- Licensed financial planning services

The strategies and projections provided are based on the information you
supply and general financial principles. Your actual results may vary.

Always consult with qualified professionals before making significant
financial decisions.
`;

// Display in all AI responses
const AI_DISCLAIMER = `
Note: I'm an AI assistant, not a licensed financial advisor. My suggestions
are based on general financial principles and the data you've provided.
`;
```

### Privacy Policy Requirements

Must include:
- What data we collect
- How we use the data
- Data retention periods
- Third-party sharing (AI APIs, analytics)
- User rights (access, export, delete)
- Contact information

### Terms of Service Requirements

Must include:
- Service description
- User responsibilities
- Financial disclaimer
- Limitation of liability
- Dispute resolution
- Termination conditions

### GDPR Compliance (If serving EU users)

| Requirement | Implementation |
|-------------|----------------|
| Legal basis | Legitimate interest + consent |
| Data portability | Export function |
| Right to erasure | Delete function |
| Data processing agreements | With Supabase, OpenAI |
| Cookie consent | Consent banner if using analytics |
| Privacy by design | Data minimization, encryption |

### State Privacy Laws (US)

- CCPA (California): Right to know, delete, opt-out of sale
- VCDPA (Virginia): Similar to GDPR
- CPA (Colorado): Consumer privacy rights

**Implementation:** Single privacy framework meeting highest standard.

---

## Audit & Logging

### Audit Log Schema

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Who
    user_id UUID REFERENCES profiles(id),
    actor_type TEXT NOT NULL, -- 'user', 'system', 'ai', 'admin', 'n8n'

    -- What
    action TEXT NOT NULL, -- 'debt.create', 'strategy.generate', etc.
    resource_type TEXT NOT NULL,
    resource_id UUID,

    -- Data (what changed)
    old_values JSONB,
    new_values JSONB,

    -- Context
    ip_address INET,
    user_agent TEXT,
    request_id TEXT,

    -- When
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for querying
CREATE INDEX idx_audit_user_date ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
```

### What to Log

| Category | Events | Retention |
|----------|--------|-----------|
| Authentication | Login, logout, password change, MFA changes | 2 years |
| Data Access | Read sensitive data (bulk) | 90 days |
| Data Modification | Create, update, delete | 2 years |
| AI Interactions | Strategy generation, chat | 1 year |
| Admin Actions | All admin operations | 5 years |
| Security Events | Failed logins, rate limit hits | 90 days |

### What NOT to Log

- Passwords (even hashed)
- Full financial account numbers
- Session tokens
- AI prompt contents (summarize instead)

### Logging Implementation

```typescript
// Audit logging helper
async function auditLog(params: {
  userId?: string;
  actorType: 'user' | 'system' | 'ai' | 'admin' | 'n8n';
  action: string;
  resourceType: string;
  resourceId?: string;
  oldValues?: any;
  newValues?: any;
  context?: { ip?: string; userAgent?: string; requestId?: string };
}) {
  // Sanitize sensitive fields before logging
  const sanitizedOld = sanitizeForLog(params.oldValues);
  const sanitizedNew = sanitizeForLog(params.newValues);

  await supabase.from('audit_logs').insert({
    user_id: params.userId,
    actor_type: params.actorType,
    action: params.action,
    resource_type: params.resourceType,
    resource_id: params.resourceId,
    old_values: sanitizedOld,
    new_values: sanitizedNew,
    ip_address: params.context?.ip,
    user_agent: params.context?.userAgent,
    request_id: params.context?.requestId,
  });
}

function sanitizeForLog(data: any): any {
  if (!data) return data;

  const sensitiveFields = ['password', 'token', 'secret', 'account_number'];
  const sanitized = { ...data };

  for (const field of sensitiveFields) {
    if (field in sanitized) {
      sanitized[field] = '[REDACTED]';
    }
  }

  return sanitized;
}
```

---

## Incident Response

### Incident Classification

| Severity | Examples | Response Time |
|----------|----------|---------------|
| **Critical** | Data breach, service down | Immediate |
| **High** | Security vulnerability, data loss | < 4 hours |
| **Medium** | Unauthorized access attempt, performance issue | < 24 hours |
| **Low** | Minor bug, user complaint | < 1 week |

### Incident Response Plan

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INCIDENT RESPONSE WORKFLOW                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. DETECTION                                                               │
│     ├── Automated monitoring alert                                          │
│     ├── User report                                                         │
│     └── Security scan finding                                               │
│                                                                             │
│  2. TRIAGE                                                                  │
│     ├── Assess severity                                                     │
│     ├── Identify affected systems/users                                     │
│     └── Escalate if needed                                                  │
│                                                                             │
│  3. CONTAINMENT                                                             │
│     ├── Isolate affected systems                                            │
│     ├── Revoke compromised credentials                                      │
│     └── Block malicious actors                                              │
│                                                                             │
│  4. INVESTIGATION                                                           │
│     ├── Collect logs and evidence                                           │
│     ├── Determine root cause                                                │
│     └── Assess scope of impact                                              │
│                                                                             │
│  5. REMEDIATION                                                             │
│     ├── Fix vulnerability                                                   │
│     ├── Restore from backup if needed                                       │
│     └── Implement additional controls                                       │
│                                                                             │
│  6. COMMUNICATION                                                           │
│     ├── Notify affected users (if required)                                 │
│     ├── Report to authorities (if required)                                 │
│     └── Update status page                                                  │
│                                                                             │
│  7. POST-INCIDENT                                                           │
│     ├── Document lessons learned                                            │
│     ├── Update procedures                                                   │
│     └── Conduct post-mortem                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Breach Notification

If a breach occurs:

1. **Within 72 hours** (GDPR requirement):
   - Notify supervisory authority (if EU users)
   - Document the breach

2. **Without undue delay**:
   - Notify affected users
   - Explain what happened
   - Describe mitigation steps
   - Provide guidance

**Template:**

```
Subject: Important Security Notice from Safe Money Toolkit

Dear [User],

We are writing to inform you of a security incident that may have affected
your account.

What Happened:
[Description of incident]

What Information Was Involved:
[Types of data potentially affected]

What We Are Doing:
[Steps taken to address the incident]

What You Can Do:
[Recommended actions for user]

For More Information:
[Contact details]

We sincerely apologize for this incident and are committed to protecting
your information.

Sincerely,
The Safe Money Toolkit Team
```

---

## Security Checklist

### Pre-Launch Security Checklist

**Authentication & Authorization:**
- [ ] Strong password policy enforced
- [ ] Email verification required
- [ ] MFA option available
- [ ] Session timeout configured
- [ ] RLS policies tested with multiple users
- [ ] Service role key not exposed to client

**Data Protection:**
- [ ] TLS 1.2+ for all connections
- [ ] Encryption at rest enabled
- [ ] Sensitive fields not logged
- [ ] Data retention policy documented
- [ ] Data export function working
- [ ] Data deletion function working

**API Security:**
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] CORS properly configured
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Error messages don't leak info

**Infrastructure:**
- [ ] Secrets stored securely (not in code)
- [ ] Dependencies up to date
- [ ] No known vulnerabilities in deps
- [ ] Monitoring and alerting configured
- [ ] Backup strategy in place

**Compliance:**
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] Financial disclaimer displayed
- [ ] Cookie consent (if applicable)
- [ ] Data processing agreements signed

**Documentation:**
- [ ] Security documentation complete
- [ ] Incident response plan documented
- [ ] Runbook for common issues
- [ ] Contact info for security issues

### Ongoing Security Tasks

**Weekly:**
- [ ] Review security alerts
- [ ] Check for dependency updates
- [ ] Monitor error rates

**Monthly:**
- [ ] Review access logs
- [ ] Update dependencies
- [ ] Review rate limit effectiveness
- [ ] Check backup integrity

**Quarterly:**
- [ ] Security review of new features
- [ ] Penetration testing (recommended)
- [ ] Review and update policies
- [ ] Team security training

**Annually:**
- [ ] Full security audit
- [ ] Update incident response plan
- [ ] Review compliance requirements
- [ ] Update privacy policy if needed
