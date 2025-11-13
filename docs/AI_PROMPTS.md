# watsonx.ai Prompt Engineering

## Model Configuration

**Primary Model**: `ibm/granite-3-2-8b-instruct`  
**Fallback Model**: `ibm/granite-8b-japanese` (if primary unavailable)

**Generation Parameters**:

```python
{
    "decoding_method": "greedy",
    "max_new_tokens": 500,
    "min_new_tokens": 50,
    "temperature": 0.3,        # Lower = more deterministic
    "top_p": 0.85,
    "top_k": 50,
    "repetition_penalty": 1.1,
    "stop_sequences": ["\n\n\n"]
}
```

**Endpoint**: `https://us-south.ml.cloud.ibm.com/ml/v1/text/generation`

---

## Prompt Template Structure

### System Role

```
You are an expert banking compliance analyst specializing in fraud detection and anti-money laundering (AML) compliance. Your role is to assess transaction risk, explain your reasoning clearly, and recommend appropriate actions following regulatory standards (FinCEN, BSA/AML).
```

### User Prompt Template

````
Analyze this flagged banking transaction:

**Transaction Details:**
- Customer: {customer_name}
- Amount: ${amount} USD
- Origin Country: {country}
- Transaction Type: {transaction_type}
- Customer History: {customer_profile}

**Current Risk Indicators:**
- Preliminary Risk Score: {risk_score}
- Flagged Reasons: {flag_reasons}

**Your Task:**
1. Assess the fraud/AML risk on a scale of 0.0 (no risk) to 1.0 (critical risk)
2. Explain your reasoning in 2-3 clear sentences
3. Recommend specific next actions for the compliance officer

**Response Format (JSON):**
```json
{
  "confidence": 0.XX,
  "rationale": "...",
  "recommended_action": "..."
}
````

**Guidelines:**

- Be concise but thorough
- Reference specific red flags
- Consider regulatory compliance requirements
- Recommend proportional actions

````

---

## Example Prompts & Responses

### Example 1: High-Risk International Transfer

**Input Variables:**
```python
{
    "customer_name": "Alice Johnson",
    "amount": 5300.00,
    "country": "Singapore",
    "transaction_type": "International Wire Transfer",
    "customer_profile": "Typical transactions: $200-800 domestic, USA only",
    "risk_score": 0.82,
    "flag_reasons": "Unusual country, amount exceeds typical by 6x"
}
````

**Full Prompt:**

```
You are an expert banking compliance analyst specializing in fraud detection and anti-money laundering (AML) compliance.

Analyze this flagged banking transaction:

**Transaction Details:**
- Customer: Alice Johnson
- Amount: $5300.00 USD
- Origin Country: Singapore
- Transaction Type: International Wire Transfer
- Customer History: Typical transactions: $200-800 domestic, USA only

**Current Risk Indicators:**
- Preliminary Risk Score: 0.82
- Flagged Reasons: Unusual country, amount exceeds typical by 6x

**Your Task:**
1. Assess the fraud/AML risk
2. Explain your reasoning in 2-3 sentences
3. Recommend specific next actions

**Response Format (JSON):**
```

**Expected watsonx.ai Response:**

```json
{
  "confidence": 0.89,
  "rationale": "Transaction exhibits multiple high-risk indicators: first-time international transfer to jurisdiction with elevated AML risk, amount significantly exceeds customer's established pattern ($5300 vs $200-800 average), and represents 6x deviation from baseline. Pattern inconsistent with stated account purpose (domestic retail).",
  "recommended_action": "HOLD transaction for enhanced due diligence. Required: (1) Contact customer via verified phone to confirm legitimacy, (2) Request supporting documentation (invoice, contract, or proof of relationship with recipient), (3) Verify source of funds, (4) File Suspicious Activity Report (SAR) if unable to verify within 24 hours."
}
```

---

### Example 2: Medium-Risk Domestic Large Transaction

**Input Variables:**

```python
{
    "customer_name": "Robert Chen",
    "amount": 12000.00,
    "country": "USA",
    "transaction_type": "Domestic ACH Transfer",
    "customer_profile": "Small business owner, typical monthly transfers $3000-8000",
    "risk_score": 0.54,
    "flag_reasons": "Amount exceeds typical threshold, round number"
}
```

**Expected Response:**

```json
{
  "confidence": 0.72,
  "rationale": "Transaction amount ($12,000) exceeds typical range but remains within reasonable bounds for small business cash flow needs. Round-number amount and domestic destination are minor risk factors. Customer profile supports legitimate business use case with established transaction history.",
  "recommended_action": "APPROVE with enhanced monitoring. Recommended: (1) Flag account for 30-day enhanced surveillance, (2) If similar large transactions repeat within 7 days, escalate for manual review, (3) Document approval rationale in compliance log. No immediate customer contact required."
}
```

---

### Example 3: Low-Risk Regular Transaction

**Input Variables:**

```python
{
    "customer_name": "Maria Gonzalez",
    "amount": 450.00,
    "country": "USA",
    "transaction_type": "ATM Withdrawal",
    "customer_profile": "Weekly ATM withdrawals $400-600, consistent for 18 months",
    "risk_score": 0.18,
    "flag_reasons": "Routine pattern check"
}
```

**Expected Response:**

```json
{
  "confidence": 0.91,
  "rationale": "Transaction aligns perfectly with established customer behavior pattern. Amount, frequency, and location consistent with 18-month history. No unusual indicators present. Withdrawal amount reasonable for personal cash needs.",
  "recommended_action": "APPROVE immediately. No further action required. Continue standard automated monitoring. Transaction represents normal account activity within expected parameters."
}
```

---

### Example 4: Structuring Suspicion (Multiple Small Transactions)

**Input Variables:**

```python
{
    "customer_name": "John Smith",
    "amount": 9800.00,
    "country": "USA",
    "transaction_type": "Cash Deposit",
    "customer_profile": "Recent deposits: $9700, $9900, $9850 within 7 days",
    "risk_score": 0.94,
    "flag_reasons": "Possible structuring (avoids $10k reporting threshold)"
}
```

**Expected Response:**

```json
{
  "confidence": 0.96,
  "rationale": "Strong indicators of deliberate structuring to evade Currency Transaction Report (CTR) requirements. Multiple deposits just below $10,000 threshold within short timeframe (7 days, totaling $29,450) suggests intentional avoidance of BSA reporting. Pattern inconsistent with legitimate business or personal banking needs.",
  "recommended_action": "IMMEDIATE HOLD and escalate to senior compliance officer. Required: (1) File Suspicious Activity Report (SAR) within 30 days, (2) Conduct enhanced due diligence on all account activity past 90 days, (3) Consider account freeze pending investigation, (4) Do NOT notify customer (tipping off prohibition under 31 USC 5318(g)(2)). Refer to law enforcement if criminal intent suspected."
}
```

---

## Prompt Engineering Best Practices

### 1. Context Window Management

- Keep total prompt <2000 tokens to stay within budget
- Summarize customer history instead of including full transaction lists
- Use bullet points for structured data

### 2. Consistency

- Always use same template structure
- Maintain consistent JSON response format
- Use same risk scale (0.0-1.0) across all prompts

### 3. Temperature Settings

- **Low risk cases** (0.0-0.3): Use `temperature=0.2` for consistent, conservative responses
- **Medium risk** (0.4-0.7): Use `temperature=0.3` for balanced analysis
- **High risk** (0.8-1.0): Use `temperature=0.25` for thorough, detailed explanations

### 4. Response Parsing

Always validate response contains required fields:

```python
required_fields = ["confidence", "rationale", "recommended_action"]
```

Handle malformed responses with fallback:

```python
if not all(field in response for field in required_fields):
    return cached_explanation_or_default()
```

---

## Token Optimization Tips

1. **Reuse system prompts**: Cache the system role message (don't regenerate)
2. **Truncate long histories**: Summarize instead of listing all transactions
3. **Batch requests**: Group similar risk levels together (if using batch API)
4. **Set `max_new_tokens` conservatively**: 500 tokens = ~350 words (sufficient)
5. **Monitor per-request cost**:
   ```python
   tokens_used = response["results"][0]["generated_token_count"]
   cost_usd = (tokens_used / 1000) * 0.0001  # $0.0001 per 1K tokens
   ```

---

## Fallback Strategy

If watsonx.ai is unavailable:

1. **Check cache** (1-hour TTL per case_id)
2. **Use rule-based system**:
   ```python
   if risk_score >= 0.8:
       return high_risk_template
   elif risk_score >= 0.5:
       return medium_risk_template
   else:
       return low_risk_template
   ```
3. **Return cached response** with disclaimer:
   ```json
   {
     "confidence": 0.0,
     "rationale": "AI service temporarily unavailable. Using cached analysis.",
     "recommended_action": "Manual review required."
   }
   ```

---

## Testing Prompts in Prompt Lab

1. Log in to watsonx.ai Prompt Lab
2. Select `ibm/granite-3-2-8b-instruct` model
3. Paste template prompt with sample variables
4. Set parameters (temperature=0.3, max_tokens=500)
5. Click "Generate" and evaluate response quality
6. Iterate on prompt wording for better results
7. Use "View code" to get Python SDK snippet

**Prompt Lab URL**: https://dataplatform.cloud.ibm.com/wx/home?context=wx
