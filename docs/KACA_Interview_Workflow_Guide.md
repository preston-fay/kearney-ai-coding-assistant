# Kearney AI Coding Assistant - Interview Workflow Guide

## What is the Interview?

The interview (`/interview`) is how you tell Claude what you're building. Unlike a form, it's a **conversation** - Claude asks questions, listens to your answers, and adapts based on what you say.

**Why this matters**: Better input = better output. The interview captures exactly what you need so Claude can deliver exactly what you want.

---

## How It Works

### 1. Choose Your Project Type

When you type `/interview`, Claude asks:

```
What type of work product are you building?

1. Data Engineering (ingestion, transformation, pipelines)
2. Statistical/ML Model (prediction, classification, clustering)
3. Analytics Asset (analysis, visualization, insights)
4. Presentation/Deck (client-facing slides)
5. Proposal Content (RFP response, pitch, methodology)
6. Dashboard (interactive data visualization)
7. Web Application (tool, prototype, MVP)
8. Research/Synthesis (market research, competitive analysis)
```

**Just type the number** (e.g., `2` for ML Model).

### 2. Answer Questions One at a Time

Claude asks questions **one at a time** and waits for your response. This isn't a form - it's a conversation.

**Example flow for ML Model:**

```
Claude: What is the business question you're trying to answer?
        Be specific about the decision this model will inform.

You:    We want to predict which customers will churn

Claude: Got it - customer churn prediction. Can you elaborate on how 
        this prediction will be used? What action will the business 
        take based on the model's output?

You:    Customer success team will prioritize outreach to at-risk customers

Claude: Perfect. What type of prediction problem is this?
        1. Classification (predict yes/no)
        2. Regression (predict a number)
        3. Not sure yet

You:    1

[continues...]
```

### 3. Claude Adapts to Your Answers

The interview is **smart** - it skips irrelevant questions:

| If you say... | Claude skips... |
|---------------|-----------------|
| "Clustering" (no target) | Questions about target variable |
| "Interpretability not needed" | Questions about compliance requirements |
| "Time series forecasting" | Questions about class balance |

### 4. Review and Confirm

At the end, Claude summarizes everything:

```
Claude: Great, I have everything I need. Here's a summary:

        PROJECT: Customer Churn Prediction Model
        TYPE: Binary Classification
        TARGET: churned_90_days (8% positive rate)
        
        DATA:
        - customer_data.csv (~50,000 rows)
        - subscription_events.csv (~200,000 rows)
        
        VALIDATION:
        - Time-based split (train: Jan-Sep, test: Oct-Dec)
        - Metrics: AUC, Precision@20%, Recall
        
        DELIVERABLES:
        - Trained model artifact
        - Validation report
        - Executive deck (10-15 slides)
        - Scoring script
        
        Does this look correct? Type 'yes' to save, or tell me
        what needs to change.
```

**Type `yes`** to save, or tell Claude what to fix.

---

## Interview Sections by Project Type

### ML/Statistics Model

| Section | Questions About |
|---------|-----------------|
| Problem Definition | Business question, problem type, target variable |
| Data | Sources, volume, quality issues, sensitive fields |
| Features | Predictive features, engineering needs, exclusions |
| Validation | Strategy, metrics, baseline |
| Interpretability | Required?, audience, compliance |
| Deliverables | Model, report, deck, code |

### Presentation/Deck

| Section | Questions About |
|---------|-----------------|
| Purpose | Type (readout, workshop, board), main message |
| Audience | Who, what they know, their concerns |
| Content | Key messages, data to include, examples |
| Format | Slide count, style, live vs read-ahead |

### Dashboard

| Section | Questions About |
|---------|-----------------|
| Purpose | Type (executive, operational, analytical), decisions informed |
| Data | Sources, update frequency, history depth |
| Views & Metrics | KPIs, pages, drill-downs, filters |
| Interactivity | Level, exports, alerts |
| Deployment | Platform, access, authentication |

### Proposal Content

| Section | Questions About |
|---------|-----------------|
| Opportunity | Type (RFP, proactive), client need, size |
| Competitive Context | Who else, differentiators, criteria |
| Solution | Approach, team, timeline, pricing |
| Content | Required sections, tone, page limits |

### Other Types

Each project type has its own tailored interview. The system asks what's relevant and skips what's not.

---

## Tips for Better Interviews

### Be Specific

```
❌ "We want to predict stuff"
✅ "We want to predict which customers will cancel their subscription 
    within 90 days so the retention team can intervene"
```

### Mention Constraints Early

```
✅ "The model needs to be explainable because regulators will audit it"
✅ "This deck is for the board - max 15 slides, very high level"
✅ "Client uses Tableau so dashboard needs to export to that"
```

### It's Okay to Say "I Don't Know"

Claude will either:
- Suggest a sensible default
- Ask a follow-up to help you figure it out
- Note it as TBD and move on

### You Can Go Back

Made a mistake? After the interview, use:

```
/edit
```

Claude will ask what you want to change.

---

## After the Interview

Your requirements are saved in `project_state/spec.yaml`. This is the **source of truth** that drives everything else.

### Next Steps

```
/plan      ← Generate your execution plan
/execute   ← Start building
```

### Changing Requirements Later

Requirements change - that's consulting. Use these commands:

| Command | When to Use |
|---------|-------------|
| `/edit` | Change specific fields |
| `/spec` | View current requirements |
| `/history` | See what changed when |
| `/interview --section data` | Re-interview just one section |

---

## Example: Full Modeling Interview

Here's a complete example so you know what to expect:

```
You:    /interview

Claude: I'll help you define your project. Let's start.

        What type of work product are you building?
        
        1. Data Engineering
        2. Statistical/ML Model
        3. Analytics Asset
        4. Presentation/Deck
        5. Proposal Content
        6. Dashboard
        7. Web Application
        8. Research/Synthesis

You:    2

Claude: You're building a statistical or ML model. Let's understand 
        the problem you're solving.

        What is the business question you're trying to answer?
        Be specific about the decision this model will inform.

You:    Predict which customers will churn so we can prioritize retention efforts

Claude: Got it. What type of prediction problem is this?

        1. Classification (predict a category: churn yes/no)
        2. Regression (predict a number: churn probability 0-100%)
        3. Clustering (find natural groups)
        4. Time Series (forecast future values)
        5. Not sure yet

You:    1

Claude: Classification it is. We can also output probability scores 
        alongside the yes/no prediction.

        What is the target variable? What defines "churn" in your data?

You:    churned_90_days - customers who cancelled within 90 days

Claude: Clear. Is the target balanced or imbalanced?
        (What percentage of customers typically churn?)

        1. Balanced (~40-60% churn)
        2. Slightly imbalanced (~20-40% or ~60-80%)
        3. Highly imbalanced (<20% or >80%)
        4. I don't know

You:    3 - about 8% churn

Claude: Highly imbalanced at 8%. I'll plan for techniques like 
        class weighting and appropriate metrics like Precision@K.

        Now let's talk about your data. What data sources do you have?

You:    Customer table with demographics and usage, events table with 
        subscription changes. Both are CSVs.

Claude: Two CSV files. Can you tell me:
        - Approximate row counts?
        - What time period does the data cover?

You:    Customer table is about 50,000 rows. Events table is 200,000 rows.
        Data covers Jan 2023 to Dec 2024.

Claude: Good volume for modeling. Any known data quality issues?

You:    Some missing values in the tenure field for new customers

Claude: Noted. Are there sensitive or protected fields we should exclude?

You:    Email and phone should not be used as features

Claude: Got it - will exclude PII.

        Moving to features. What features do you expect to be predictive?

You:    Usage metrics, support ticket count, contract value, tenure

Claude: Those sound reasonable. Any features you want to engineer?

You:    Usage trend - compare last 30 days to previous 30 days

Claude: Good idea. Now validation.

        How should the model be validated?

        1. Simple holdout (train/test split)
        2. Cross-validation
        3. Time-based split (train on past, test on future)

You:    3 - time based makes sense for this

Claude: Agreed. What time periods?

You:    Train on Jan-Sep 2024, test on Oct-Dec 2024

Claude: And what metrics matter most?

        1. AUC (overall ranking quality)
        2. Precision@K (accuracy in top predictions)
        3. Recall (catching all churners)
        4. F1 (balance of precision/recall)
        5. Multiple - tell me which

You:    AUC and Precision at top 20%

Claude: Is there a baseline to beat?

You:    Previous model had 0.68 AUC

Claude: Target is to beat 0.68 AUC. 

        Is model interpretability required?

You:    Yes, the VP wants to understand why, not just who

Claude: Who needs to understand the model?

        1. Business users (non-technical)
        2. Technical team (data scientists)
        3. Regulators/auditors
        4. Multiple audiences

You:    1 - business users

Claude: I'll plan for business-friendly explanations like feature 
        importance and simple rules.

        Finally, what outputs do you need?

        1. Trained model file only
        2. Model + validation report
        3. Model + report + executive deck
        4. Everything (model, report, deck, scoring script)

You:    4 - everything

Claude: How many slides for the executive deck?

You:    10-15 slides, C-suite audience

Claude: Perfect. Here's the summary:

        PROJECT: Customer Churn Prediction Model
        TYPE: Binary Classification
        TARGET: churned_90_days (8% positive rate)
        
        DATA:
        - customer_data.csv (~50,000 rows)
        - subscription_events.csv (~200,000 rows)
        - Period: Jan 2023 - Dec 2024
        - Quality: Some missing tenure values
        - Excluded: email, phone (PII)
        
        FEATURES:
        - Usage metrics, support tickets, contract value, tenure
        - Engineer: usage_trend (30d vs prior 30d)
        
        VALIDATION:
        - Time-based split
        - Train: Jan-Sep 2024
        - Test: Oct-Dec 2024
        - Metrics: AUC (beat 0.68), Precision@20%
        
        INTERPRETABILITY:
        - Required for business users
        - Feature importance, simple explanations
        
        DELIVERABLES:
        - Trained model artifact
        - Validation report
        - Executive deck (10-15 slides, C-suite)
        - Scoring script
        
        Does this look correct? Type 'yes' to save.

You:    yes

Claude: Saved to project_state/spec.yaml (version 1).

        Next step: Run /plan to generate your execution plan.
```

---

## Common Questions

### How long does the interview take?

**5-15 minutes** depending on project complexity.

### Can I skip questions?

Yes - say "skip" or "not sure" and Claude will use sensible defaults or move on.

### What if I realize I was wrong after saving?

Use `/edit` to change anything. Your changes are tracked with version history.

### Can I see my requirements later?

Yes - `/spec` shows your full requirements anytime.

### What if I want to start over?

`/project:reset` archives your current state and lets you start fresh.

---

*Kearney Digital & Analytics*
