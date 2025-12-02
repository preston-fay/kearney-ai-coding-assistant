# Living Requirements System Addendum

## Master Plan v2.0 Addendum

**Interview-Driven Intake for All Consultant Work Products with Continuous Refinement and Version Control**

*"Tell me what you're building. I'll ask the right questions."*

---

# I. The Problem with Static Intake

The v2.0 Master Plan includes an intake system, but it has fundamental limitations:

## 1.1 Current Limitations

- **Static questions**: Same questions regardless of project type or context
- **Linear flow**: No branching based on answers
- **One-shot**: Captured once, then frozen
- **Generic**: Doesn't capture domain-specific requirements (ML validation strategy, proposal tone, dashboard interactivity)
- **No refinement**: Can't update requirements as understanding evolves

## 1.2 What Real Projects Need

Real consultant projects are iterative and evolving:

- "Actually, this is more of a classification problem than I thought"
- "The client wants an interactive dashboard, not static charts"
- "We need to add a competitive analysis section to the proposal"
- "The model needs to be interpretable for regulators"

Requirements change as the project progresses. The intake system must be a living document that evolves with the project.

## 1.3 The Interview Insight

The best prompt is actually an interview that extracts exactly what's needed for high-quality output. Generic templates produce generic results. Domain-specific interviews produce domain-specific excellence.

> **INFO**: A pitch deck interview asks about funding stage, competitive moat, and revenue model. A statistical model interview asks about target variable, validation strategy, and interpretability requirements. These are fundamentally different conversations.

---

# II. Living Requirements: The Concept

## 2.1 Core Principles

**1. Interview, Don't Form-Fill**: Claude conducts a conversation, not a survey. It asks follow-up questions, probes for clarity, and adapts based on responses.

**2. Domain-Specific Depth**: Each project type has its own interview tree. A modeling project asks different questions than a proposal project.

**3. Always Editable**: Requirements can be updated at any point. Changed your mind about the target variable? Update the spec.

**4. Version Controlled**: Every change is tracked. You can see the evolution of requirements and roll back if needed.

**5. Machine-Readable Output**: The interview produces a structured spec.yaml that both humans and Claude can parse.

## 2.2 The spec.yaml Contract

The interview produces a specification file that serves as the contract between user intent and system execution:

```
project_state/
  spec.yaml          # The living requirements document
  spec_history/      # Version history
    spec_v1.yaml
    spec_v2.yaml
    changelog.md
  plan.md            # Execution plan (generated from spec)
  status.json        # Task tracking
```

The spec.yaml is the source of truth. The plan.md is generated from the spec. If the spec changes, the plan regenerates.

## 2.3 User Experience Flow

```
User: /interview

Claude: I'll help you define your project. Let's start with the basics.

        What type of work product are you building?
        
        1. Data Engineering (ingestion, transformation, pipelines)
        2. Statistical/ML Model (prediction, classification, clustering)
        3. Analytics Asset (analysis, visualization, insights)
        4. Presentation/Deck (client-facing slides)
        5. Proposal Content (RFP response, pitch, methodology)
        6. Dashboard (interactive data visualization)
        7. Web Application (tool, prototype, MVP)
        8. Research/Synthesis (market research, competitive analysis)

User: 2

Claude: Great, you're building a statistical or ML model. Let me understand
        the problem you're solving.

        What is the business question you're trying to answer?

User: We want to predict which customers are likely to churn...

[Interview continues with domain-specific questions]
```

---

# III. Consultant Work Product Taxonomy

A comprehensive taxonomy of everything Kearney consultants build, organized by primary intent:

## 3.1 Data Engineering Projects

**Intent**: Transform raw data into analysis-ready assets

- Data ingestion (CSV, Excel, SQL, API, PDF extraction)
- Data cleaning and normalization
- Multi-source joins and integration
- Feature engineering
- Pipeline automation

**Outputs**: Clean datasets, data dictionaries, transformation scripts, lineage documentation

## 3.2 Statistical/ML Modeling Projects

**Intent**: Build predictive or explanatory models

- Classification (churn, fraud, lead scoring)
- Regression (pricing, demand forecasting, valuation)
- Clustering (segmentation, cohort analysis)
- Time series (forecasting, anomaly detection)
- Causal inference (A/B testing, uplift modeling)
- NLP (sentiment, topic modeling, entity extraction)

**Outputs**: Model artifacts, validation reports, feature importance, interpretation decks, deployment packages

## 3.3 Analytics Assets

**Intent**: Generate insights from data

- Exploratory data analysis
- Benchmarking and competitive analysis
- Market sizing and TAM analysis
- Financial analysis and modeling
- Operational diagnostics

**Outputs**: Charts, tables, insight summaries, Excel models, one-pagers

## 3.4 Presentations and Decks

**Intent**: Communicate findings or recommendations

- Executive summaries
- Project readouts
- Workshop materials
- Board presentations
- Training materials

**Outputs**: PowerPoint decks, speaker notes, handouts

## 3.5 Proposal Content

**Intent**: Win new business

- RFP responses
- Proactive proposals
- Methodology sections
- Team bios and case studies
- Pricing and scope documents

**Outputs**: Structured content blocks, full proposal drafts, appendices

## 3.6 Dashboards

**Intent**: Enable ongoing data exploration

- Executive dashboards (KPI-focused)
- Operational dashboards (real-time monitoring)
- Analytical dashboards (exploration-focused)
- Client portals

**Outputs**: HTML dashboards, Streamlit apps, Tableau/PowerBI specs

## 3.7 Web Applications

**Intent**: Build functional tools

- Internal productivity tools
- Client-facing portals
- Prototypes and MVPs
- Data collection forms
- Calculators and configurators

**Outputs**: Working code, deployment configs, documentation

## 3.8 Research and Synthesis

**Intent**: Aggregate and analyze external information

- Market research
- Competitive intelligence
- Technology landscape analysis
- Best practice synthesis
- Expert interview summaries

**Outputs**: Research reports, comparison matrices, synthesis decks

---

# IV. The Interview Engine

## 4.1 Architecture

The Interview Engine is a conversational system that:

1. Selects the appropriate interview tree based on project type
2. Asks questions one at a time, waiting for responses
3. Applies conditional logic to skip or add questions based on previous answers
4. Probes for clarity when answers are ambiguous
5. Summarizes and confirms before finalizing
6. Generates the structured spec.yaml

## 4.2 Interview Tree Structure

Each project type has an interview tree defined in YAML:

```yaml
# config/interviews/modeling.yaml

id: modeling
name: Statistical/ML Modeling
version: 1.0.0

sections:
  - id: problem_definition
    name: Problem Definition
    questions:
      - id: business_question
        prompt: |
          What is the business question you're trying to answer?
          Be specific about the decision this model will inform.
        type: text
        required: true
        follow_up:
          condition: "len(answer) < 50"
          prompt: |
            Can you elaborate? What decision will stakeholders make
            based on this model's predictions?

      - id: problem_type
        prompt: |
          What type of problem is this?
          
          1. Classification (predict a category)
          2. Regression (predict a number)
          3. Clustering (find natural groups)
          4. Time Series (forecast future values)
          5. Ranking (order items by relevance)
          6. Anomaly Detection (find outliers)
          7. Not sure yet
        type: choice
        options: [classification, regression, clustering, time_series, ranking, anomaly, unsure]
        required: true

      - id: target_variable
        prompt: What is the target variable you're trying to predict?
        type: text
        required: true
        condition: "problem_type != 'clustering' and problem_type != 'unsure'"

      - id: class_balance
        prompt: |
          Is your target variable balanced or imbalanced?
          (e.g., 50/50 split vs 95/5 split)
        type: choice
        options: [balanced, slightly_imbalanced, highly_imbalanced, unknown]
        condition: "problem_type == 'classification'"
```

## 4.3 Question Types

| Type | Description | Example |
|------|-------------|---------|
| text | Free-form text response | Business question, target variable |
| choice | Select one from options | Problem type, validation strategy |
| multi | Select multiple from options | Data sources, deliverable types |
| boolean | Yes/No question | Is interpretability required? |
| number | Numeric value | Number of slides, forecast horizon |
| date | Date or deadline | Delivery deadline, data cutoff |
| list | Comma-separated items | Feature list, stakeholder names |
| file | Reference to uploaded file | Data file, template doc |

## 4.4 Conditional Logic

Questions can be conditional based on previous answers:

```yaml
# Only ask about class balance if this is a classification problem
condition: "problem_type == 'classification'"

# Only ask about seasonality if this is a time series problem
condition: "problem_type == 'time_series'"

# Only ask about regulatory requirements if interpretability is required
condition: "interpretability_required == true"

# Complex conditions
condition: "problem_type in ['classification', 'regression'] and data_volume == 'large'"
```

## 4.5 Follow-Up Probes

The engine can ask follow-up questions when answers are insufficient:

```yaml
follow_up:
  condition: "len(answer) < 50"
  prompt: |
    Can you elaborate? This information helps me design
    the right approach for your analysis.

follow_up:
  condition: "'not sure' in answer.lower() or 'maybe' in answer.lower()"
  prompt: |
    I noticed some uncertainty. Let me help you think through this.
    What outcome would be most valuable for the business?
```

---

# V. Requirements Schema (spec.yaml)

The interview produces a structured specification that serves as the contract between user intent and system execution.

## 5.1 Universal Schema Structure

```yaml
# project_state/spec.yaml

version: 1  # Increments with each edit
created_at: 2025-12-01T10:30:00Z
updated_at: 2025-12-01T14:45:00Z

# ============= META =============
meta:
  project_name: acme-churn-model
  project_type: modeling  # Links to interview tree
  client: Acme Corporation
  deadline: 2025-12-15
  stakeholders:
    - name: Jane Smith
      role: VP of Customer Success
      decision_maker: true
    - name: Bob Johnson
      role: Data Science Lead
      decision_maker: false

# ============= PROBLEM =============
problem:
  business_question: |
    Which customers are most likely to cancel their subscription
    in the next 90 days, and what factors drive churn?
  success_criteria:
    - Identify top 20% of at-risk customers
    - Achieve minimum 0.75 AUC on holdout set
    - Provide interpretable feature importance

# ============= TYPE-SPECIFIC =============
# (This section varies by project_type)
modeling:
  problem_type: classification
  target_variable: churned_90_days
  target_definition: |
    Customer canceled subscription or did not renew
    within 90 days of observation date
  class_balance: imbalanced  # ~8% churn rate
  
  features:
    included:
      - usage_last_30_days
      - support_tickets_count
      - contract_value
      - tenure_months
    excluded:
      - customer_id  # Identifier only
      - email  # PII
    to_engineer:
      - usage_trend  # 30-day vs 60-day usage
      - engagement_score  # Composite metric
  
  validation:
    strategy: time_based_split
    train_period: 2024-01-01 to 2024-09-30
    test_period: 2024-10-01 to 2024-12-31
    metrics:
      - auc_roc
      - precision_at_20pct
      - recall
  
  interpretability:
    required: true
    audience: business_users
    methods:
      - feature_importance
      - partial_dependence
      - individual_explanations  # Top predictions

# ============= DATA =============
data:
  sources:
    - name: customer_data.csv
      type: csv
      location: data/raw/customer_data.csv
      rows: ~50000
      description: Customer attributes and usage metrics
    - name: subscription_events.csv
      type: csv
      location: data/raw/subscription_events.csv
      rows: ~200000
      description: Subscription lifecycle events
  
  quality_notes:
    - Some missing values in tenure_months for new customers
    - Usage data starts from 2023-06-01
  
  sensitive_fields:
    - email
    - phone
    - address

# ============= DELIVERABLES =============
deliverables:
  - type: model_artifact
    format: pickle
    description: Trained model for scoring
  
  - type: validation_report
    format: markdown
    description: Model performance metrics and diagnostics
  
  - type: interpretation_deck
    format: pptx
    slides: 10-15
    audience: c_suite
    description: Business-friendly explanation of model insights
  
  - type: scoring_script
    format: python
    description: Script to score new customers

# ============= CONSTRAINTS =============
constraints:
  brand: kearney  # Use Kearney Design System
  timeline: 2 weeks
  budget: N/A
  regulatory:
    - No use of protected characteristics
    - Model must be explainable for audit

# ============= NOTES =============
notes:
  - Client prefers simpler models over black-box approaches
  - Previous churn model had 0.68 AUC, goal is to beat this
  - VP wants to understand "why" not just "who"
```

## 5.2 Type-Specific Sections

The type-specific section varies based on project_type. Here are the schemas for each:

### Modeling Projects
```yaml
modeling:
  problem_type: classification | regression | clustering | time_series | ranking | anomaly
  target_variable: string
  target_definition: string
  class_balance: balanced | imbalanced | highly_imbalanced
  features: { included, excluded, to_engineer }
  validation: { strategy, metrics, train_period, test_period }
  interpretability: { required, audience, methods }
```

### Presentation Projects
```yaml
presentation:
  purpose: readout | workshop | board | training
  audience: c_suite | managers | technical | mixed
  slide_count: number | range
  key_messages: list
  visual_style: data_heavy | narrative | balanced
  includes_appendix: boolean
```

### Proposal Projects
```yaml
proposal:
  type: rfp_response | proactive | sole_source
  sections: list
  tone: formal | conversational | technical
  competitive_context: string
  differentiators: list
  pricing_included: boolean
```

### Dashboard Projects
```yaml
dashboard:
  type: executive | operational | analytical
  update_frequency: realtime | daily | weekly | static
  interactivity: high | medium | low | none
  views: list of { name, metrics, visualizations }
  filters: list
  target_platform: html | streamlit | tableau_spec | powerbi_spec
```

### Web Application Projects
```yaml
webapp:
  type: internal_tool | client_portal | prototype | calculator
  users: list of user personas
  features: list of feature specs
  tech_stack: { frontend, backend, database }
  auth_required: boolean
  deployment_target: local | cloud | client_hosted
```

---

# VI. Interview Flows by Project Type

## 6.1 Universal Questions (All Projects)

Every interview starts with these foundational questions:

```
Section: Basics
Q1: What is this project called? (used for folder naming)
Q2: Who is the client or internal stakeholder?
Q3: What is the deadline or target completion date?
Q4: Who will consume the final deliverables?
Q5: What does success look like for this project?
```

## 6.2 Modeling Interview Flow

```
Section: Problem Definition
Q1: What is the business question you're trying to answer?
Q2: What type of problem is this? [classification/regression/clustering/time_series/ranking/anomaly]
Q3: (if not clustering) What is the target variable?
Q4: (if classification) Is the target balanced or imbalanced?
Q5: (if time_series) What is the forecast horizon?

Section: Data
Q6: What data sources do you have? (describe or upload)
Q7: How much data do you have? (rows/time range)
Q8: Are there any known data quality issues?
Q9: Are there sensitive or protected fields to exclude?

Section: Features
Q10: What features do you expect to be predictive?
Q11: Are there features you want to engineer?
Q12: Are there features that must be excluded?

Section: Validation
Q13: How should the model be validated? [holdout/cv/time_based]
Q14: What metrics matter most? [accuracy/auc/precision/recall/rmse/mae]
Q15: Is there a baseline to beat?

Section: Interpretability
Q16: Is model interpretability required?
Q17: (if yes) Who needs to understand the model? [business/technical/regulators]
Q18: (if regulators) Are there specific compliance requirements?

Section: Deliverables
Q19: What outputs do you need? [model/report/deck/code/all]
Q20: (if deck) How many slides? Who is the audience?
```

## 6.3 Presentation Interview Flow

```
Section: Purpose
Q1: What is the purpose of this presentation?
   [project_readout/recommendation/workshop/board_update/training]
Q2: What is the single most important message?
Q3: What do you want the audience to do after seeing this?

Section: Audience
Q4: Who is the primary audience? [c_suite/managers/technical/mixed]
Q5: What do they already know about this topic?
Q6: What are their concerns or objections?

Section: Content
Q7: What are the 3-5 key messages to convey?
Q8: Do you have data/analysis to include? (describe or upload)
Q9: Are there specific examples or case studies to feature?
Q10: Should this include an appendix for detailed backup?

Section: Format
Q11: How many slides? (or range)
Q12: Presentation style? [data_heavy/narrative/balanced]
Q13: Will this be presented live or sent as a read-ahead?
Q14: Any specific template or style requirements?
```

## 6.4 Proposal Interview Flow

```
Section: Opportunity
Q1: What type of proposal is this?
   [rfp_response/proactive/sole_source/extension]
Q2: What is the client's stated need or problem?
Q3: What is the opportunity size (revenue/strategic value)?

Section: Competitive Context
Q4: Is this competitive? Who else is bidding?
Q5: What are our key differentiators?
Q6: What are the client's decision criteria?

Section: Solution
Q7: What approach/methodology are we proposing?
Q8: What team structure and roles?
Q9: What is the timeline and phasing?
Q10: Is pricing included in this proposal?

Section: Content
Q11: What sections are required?
   [exec_summary/methodology/team/timeline/pricing/case_studies/appendix]
Q12: What is the required tone? [formal/conversational/technical]
Q13: Are there page limits or format requirements?
Q14: Do you have case studies or credentials to include?
```

## 6.5 Dashboard Interview Flow

```
Section: Purpose
Q1: What type of dashboard is this?
   [executive/operational/analytical/client_portal]
Q2: What decisions will this dashboard inform?
Q3: How often will users view this? [daily/weekly/ad_hoc]

Section: Data
Q4: What data sources will feed the dashboard?
Q5: How often does the data update? [realtime/daily/weekly/static]
Q6: How much historical data should be available?

Section: Views & Metrics
Q7: What are the key metrics to display?
Q8: What views or pages do you need?
Q9: What drill-down capabilities are needed?
Q10: What filters should users have access to?

Section: Interactivity
Q11: How interactive should this be? [high/medium/low/static]
Q12: Should users be able to export data?
Q13: Are there alerts or thresholds to highlight?

Section: Deployment
Q14: Where will this be deployed?
   [html_file/streamlit_app/tableau/powerbi/spec_only]
Q15: Who needs access? Any authentication requirements?
```

---

# VII. Edit and Refinement Mechanics

## 7.1 The Edit Interface

Requirements evolve throughout a project. The system provides multiple ways to update the spec:

### Option 1: Conversational Edit

```
User: Actually, I want to change the target variable to churn_60_days
      instead of churn_90_days.

Claude: I'll update the spec. Changing:

        modeling.target_variable: churn_90_days -> churn_60_days
        modeling.target_definition: ...within 90 days... -> ...within 60 days...

        This will affect the validation strategy since the observation
        window is shorter. Should I also adjust the train/test split?

User: Yes, please.

Claude: Updated. spec.yaml is now at version 2.
        Changelog: "Changed churn window from 90 to 60 days"
```

### Option 2: Direct Section Edit

```
User: /edit modeling.validation

Claude: Current validation settings:

        strategy: time_based_split
        train_period: 2024-01-01 to 2024-09-30
        test_period: 2024-10-01 to 2024-12-31
        metrics: [auc_roc, precision_at_20pct, recall]

        What would you like to change?

User: Add f1_score to the metrics

Claude: Added f1_score to metrics. spec.yaml updated to version 3.
```

### Option 3: Re-Interview a Section

```
User: /interview --section deliverables

Claude: Let's revisit the deliverables. Currently you have:
        - Model artifact (pickle)
        - Validation report (markdown)
        - Interpretation deck (pptx, 10-15 slides)
        - Scoring script (python)

        Do you want to keep these and add more, or start fresh?
```

## 7.2 Version History

Every edit creates a new version. The system maintains a changelog:

```
project_state/
  spec.yaml             # Current version (v4)
  spec_history/
    spec_v1.yaml        # Initial interview
    spec_v2.yaml        # Changed churn window
    spec_v3.yaml        # Added f1_score
    changelog.md        # Human-readable history
```

```markdown
# spec_history/changelog.md

# Specification Changelog

## Version 4 (2025-12-01 15:30)
- Added executive_summary to deliverables
- Changed deck audience from c_suite to board

## Version 3 (2025-12-01 14:45)
- Added f1_score to validation metrics

## Version 2 (2025-12-01 12:00)
- Changed target from churn_90_days to churn_60_days
- Adjusted train/test split accordingly

## Version 1 (2025-12-01 10:30)
- Initial specification from interview
```

## 7.3 Impact Analysis

When requirements change, the system analyzes impact on the plan:

```
User: I want to change this from classification to regression.
      Predict the probability of churn, not just yes/no.

Claude: This is a significant change. Impact analysis:

        PLAN IMPACT:
        - Task 2.1 (Train classifier) -> Task 2.1 (Train regressor)
        - Task 2.3 (Confusion matrix) -> Task 2.3 (Residual analysis)
        - Task 3.1 (Precision/Recall curves) -> Task 3.1 (Calibration plot)

        COMPLETED WORK IMPACT:
        - Task 1.2 (Feature engineering) is still valid
        - Task 1.3 (Train/test split) needs adjustment (no stratification)

        METRICS CHANGE:
        - Remove: auc_roc, precision_at_20pct
        - Add: rmse, mae, calibration_error

        Proceed with this change?
```

---

# VIII. Integration with Router and State

## 8.1 Updated State Architecture

The spec.yaml becomes the source of truth that drives everything else:

```
project_state/
  spec.yaml           # SOURCE OF TRUTH - Living requirements
  spec_history/       # Version history
  plan.md             # DERIVED - Generated from spec
  status.json         # EXECUTION STATE - Task tracking
```

The relationship:

```
spec.yaml --> (planning) --> plan.md --> (execution) --> status.json
    ^                                                        |
    |_________________ (refinement) _________________________|
```

## 8.2 Updated Router Pattern

CLAUDE.md gains new routing rules for the interview system:

```markdown
## AGENT ROUTING RULES (Updated)

| Command | Agent | Context | Output |
|---------|-------|---------|--------|
| /interview | INTERVIEWER | config/interviews/*.yaml | spec.yaml |
| /edit | SPEC_EDITOR | spec.yaml | spec.yaml (new version) |
| /plan | PLANNER | spec.yaml | plan.md, status.json |
| /execute | STEWARD | status.json, spec.yaml | outputs/* |
```

## 8.3 New Agents

### @interviewer Agent

```markdown
# .claude/agents/interviewer.md

---
name: interviewer
model: sonnet
tools: [Read, Write(project_state/spec.yaml)]
---

# Interviewer Agent

You conduct structured interviews to gather project requirements.

## Behavior

1. Load the appropriate interview tree from config/interviews/
2. Ask questions ONE AT A TIME
3. Wait for the user's response before proceeding
4. Apply conditional logic to skip irrelevant questions
5. Probe for clarity when answers are vague
6. Summarize and confirm before finalizing
7. Generate spec.yaml with all captured requirements

## Interview Style

- Be conversational, not robotic
- Acknowledge good answers ("Got it", "That's helpful")
- Ask clarifying follow-ups when needed
- Offer examples when questions might be unclear
- Allow "I don't know" with sensible defaults
```

### @spec-editor Agent

```markdown
# .claude/agents/spec-editor.md

---
name: spec-editor
model: sonnet
tools: [Read, Write(project_state/**)]
---

# Spec Editor Agent

You modify the project specification based on user requests.

## Behavior

1. Load current spec.yaml
2. Understand the requested change
3. Analyze impact on plan and completed work
4. Confirm change with user
5. Save new version to spec.yaml
6. Archive old version to spec_history/
7. Update changelog.md
8. Flag if plan needs regeneration
```

---

# IX. The /interview Command

## 9.1 Command Specification

```markdown
# .claude/commands/interview.md

---
name: interview
description: Conduct structured requirements gathering
agent: @interviewer
---

# /interview

## Usage

/interview                    # Start new interview
/interview --type modeling   # Start with specific type
/interview --section data    # Re-interview specific section
/interview --continue        # Continue interrupted interview

## Behavior

1. If spec.yaml exists, offer to:
   - Start fresh (archive current)
   - Edit existing spec
   - Re-interview specific section

2. If starting fresh:
   - Ask project type first
   - Load appropriate interview tree
   - Conduct full interview

3. At completion:
   - Display summary of captured requirements
   - Ask for confirmation
   - Save spec.yaml
   - Suggest /plan as next step
```

## 9.2 Related Commands

### /edit
```
# Edit specific part of spec
/edit meta.deadline           # Edit single field
/edit modeling.validation     # Edit section
/edit                         # Open general edit mode
```

### /spec
```
# View current specification
/spec                         # Show full spec
/spec --section modeling      # Show specific section
/spec --diff                  # Show changes from last version
```

### /history
```
# View specification history
/history                      # Show changelog
/history --version 2          # Show specific version
/history --rollback 2         # Rollback to version
```

---

# X. Example: Full Interview Transcript

Here's a complete example of an interview for a modeling project:

```
User: /interview

Claude: I'll help you define your project requirements. Let's start.

        What type of work product are you building?

        1. Data Engineering (ingestion, transformation, pipelines)
        2. Statistical/ML Model (prediction, classification, clustering)
        3. Analytics Asset (analysis, visualization, insights)
        4. Presentation/Deck (client-facing slides)
        5. Proposal Content (RFP response, pitch, methodology)
        6. Dashboard (interactive data visualization)
        7. Web Application (tool, prototype, MVP)
        8. Research/Synthesis (market research, competitive analysis)

User: 2

Claude: You're building a statistical or ML model. Let's understand the
        problem you're solving.

        What is the business question you're trying to answer?
        Be specific about the decision this model will inform.

User: We want to predict which customers will churn

Claude: Got it - customer churn prediction. Can you elaborate on how this
        prediction will be used? What action will the business take
        based on the model's output?

User: The customer success team will use it to prioritize outreach.
      They want to focus retention efforts on customers most likely to leave.

Claude: Perfect. That helps me understand the use case.

        What type of prediction problem is this?

        1. Classification (predict a category: churn yes/no)
        2. Regression (predict a number: churn probability 0-100%)
        3. Not sure yet

User: 1, but they also want to know the probability

Claude: Good news - classification models can output both a prediction
        (yes/no) and a probability score. I'll set this up as a
        classification problem with probability output.

        What is the target variable? In other words, what defines
        "churn" in your data?

User: Customers who cancel within 90 days

Claude: I'll define the target as 'churned_90_days'.

        Is the target balanced or imbalanced?
        (What percentage of customers typically churn?)

        1. Balanced (~40-60% churn)
        2. Slightly imbalanced (~20-40% or ~60-80%)
        3. Highly imbalanced (<20% or >80%)
        4. I don't know

User: 3 - about 8% churn

Claude: Highly imbalanced at 8% churn rate. I'll plan for techniques
        like class weighting or SMOTE, and focus on metrics like
        precision-at-K rather than raw accuracy.

        Now let's talk about your data. What data sources do you have?

User: I have a customer table with demographics and usage, and an events
      table with subscription changes

Claude: Two tables: customer attributes/usage and subscription events.

        Can you upload these files or tell me more about:
        - How many customers (rows)?
        - What time period does the data cover?
        - What fields are in each table?

[Interview continues through all sections...]

Claude: Great, I have everything I need. Here's a summary:

        PROJECT: Customer Churn Prediction Model
        TYPE: Binary Classification
        TARGET: churned_90_days (8% positive rate)

        DATA:
        - customer_data.csv (~50,000 rows)
        - subscription_events.csv (~200,000 rows)

        VALIDATION:
        - Time-based split (train: Jan-Sep 2024, test: Oct-Dec 2024)
        - Metrics: AUC, Precision@20%, Recall, F1

        DELIVERABLES:
        - Trained model artifact
        - Validation report
        - Executive deck (10-15 slides for C-suite)
        - Scoring script

        Does this look correct? Type 'yes' to save, or tell me
        what needs to change.

User: Yes, looks good

Claude: Saved to project_state/spec.yaml (version 1).

        Next step: Run /plan to generate the execution plan.
```

---

# XI. Implementation Additions to v2.0

## 11.1 New Files Required

```
# Interview Engine
core/interview_engine.py              # Interview orchestration
core/spec_manager.py                  # Spec CRUD + versioning

# Interview Trees (one per project type)
config/interviews/
  modeling.yaml
  presentation.yaml
  proposal.yaml
  dashboard.yaml
  webapp.yaml
  data_engineering.yaml
  analytics.yaml
  research.yaml

# New Agents
.claude/agents/
  interviewer.md
  spec-editor.md

# New Commands
.claude/commands/
  interview.md
  edit.md
  spec.md
  history.md
```

## 11.2 Updated Implementation Sequence

Revised to include interview system:

**Phase 1: Core Engine (Days 1-3)** - No change

**Phase 2: Bootstrap (Days 4-5)** - No change

**Phase 3: Router + Hooks (Days 6-7)** - No change

**Phase 4: Interview System (NEW - Days 8-10)**

1. Implement core/interview_engine.py
2. Implement core/spec_manager.py
3. Write config/interviews/modeling.yaml
4. Write config/interviews/presentation.yaml
5. Write config/interviews/dashboard.yaml
6. Write remaining interview trees
7. Write .claude/agents/interviewer.md
8. Write .claude/agents/spec-editor.md
9. Write .claude/commands/interview.md
10. Test full interview flow for each project type

**Phase 5: Remaining Agents + Commands (Days 11-13)**

1. Write .claude/agents/planner.md (updated for spec.yaml)
2. Write .claude/agents/steward.md
3. Write .claude/agents/kds-reviewer.md
4. Write remaining commands
5. Test full workflow: interview -> plan -> execute

**Phase 6: Templates + Documentation (Days 14-16)**

**Phase 7: Testing + Launch (Days 17-20)**

## 11.3 Updated Success Metrics

| Metric | Target |
|--------|--------|
| Interview completion rate | > 90% of started interviews finish |
| Spec completeness | > 95% of required fields captured |
| Plan accuracy | > 85% of plans require no major revision |
| Edit success rate | > 95% of edits correctly applied |
| Consultant satisfaction | > 4.0/5.0 on "understood my needs" |

---

# END OF LIVING REQUIREMENTS SYSTEM ADDENDUM

*"Tell me what you're building. I'll ask the right questions."*

**Kearney Digital & Analytics**
