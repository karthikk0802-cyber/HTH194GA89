# Graph Report - HTH194GA89  (2026-09-25)

## Corpus Check
- 108 files · ~50,951 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 34 file(s) not represented in the graph (top: .bin 20, .db 4, .css 4)

## Summary
- 581 nodes · 1235 edges · 48 communities (34 shown, 14 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 79 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Core Services Tests
- React Frontend Pages
- Knowledge Ingestion Pipeline
- Baseline Scoring Engine
- Policy Concepts Docs
- API Read Handlers
- Database Models Engine
- Admin Auth Management
- Frontend Dependencies
- Ops Culture Docs
- LLM Teaching Pipeline
- API Request Models
- Admin Token Guard
- Static Quiz Bank
- Adaptive Quiz Policy
- Held-Out Eval Engine
- Data Architecture Docs
- Quiz Validation Gate
- Diagnostic Submit Flow
- Seen Tracking Store
- Brief Fix Tests
- Auth Schema Helper
- Social Icons Set
- Lint Configuration
- Hero Illustration Asset
- Leave Policy Docs
- Plan Architecture Docs
- Quiz Submit State
- Doc Approval Gate
- Vite Logo Asset
- Sales Playbook Docs
- Diagnostic Evaluate Wrap
- Favicon Brand Mark
- React Logo Asset
- Backend Stack Concept
- PII Masking Link
- PTO Policy Docs
- Local Dev Concepts
- Expense Remote Docs
- On-Call Incident Docs
- Quiz Next Policy
- Admin Seed Logic
- Compliance Framework Doc
- Commit Signing Concept
- Vite Template Doc

## God Nodes (most connected - your core abstractions)
1. `useAuth()` - 25 edges
2. `UserAuthModel` - 24 edges
3. `UserTopicState` - 24 edges
4. `react` - 21 edges
5. `UserProfileModel` - 16 edges
6. `generate_completion()` - 16 edges
7. `api` - 16 edges
8. `get_role_topics()` - 15 edges
9. `hash_password()` - 14 edges
10. `evaluate_diagnostic()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `test_auth_database_isolation()` --uses--> `UserAuthModel`  [INFERRED]
  tests/test_core_logic.py → services/auth_db.py
- `Jira P0 P1 SLA Triage and Sizing` --semantically_similar_to--> `RICE Prioritization Framework`  [INFERRED] [semantically similar]
  knowledge_base/Jira_Triage_Process.pdf → knowledge_base/Product_Triage_Guide.txt
- `main()` --calls--> `build_competency_graph()`  [EXTRACTED]
  scripts/validate_dag.py → services/adaptive.py
- `_self_seed_on_boot()` --uses--> `UserAuthModel`  [INFERRED]
  server.py → services/auth_db.py
- `_self_seed_on_boot()` --uses--> `DocumentModel`  [INFERRED]
  server.py → services/db.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Frozen v1 diagnostic and quiz contracts** — plan_api_diagnostic_questions, plan_api_diagnostic_evaluate, plan_api_quiz_generate [EXTRACTED 1.00]
- **Adaptive v2 sidecars wrapping v1 functions** — plan_get_baseline_questions, plan_score_baseline, plan_generate_personalized_quiz [EXTRACTED 1.00]
- **Progressive Delivery Safety Net** — knowledge_base_deployment_sop_canary_rollout, knowledge_base_deployment_sop_automated_rollback, knowledge_base_git_workflow_v1_2_trunk_based_development [EXTRACTED 0.75]
- **Incident Management System** — knowledge_base_incident_response_plan_severity_levels, knowledge_base_incident_response_plan_incident_commander, knowledge_base_on_call_compensation_oncall_rotation, knowledge_base_communication_guidelines_escalation_paths [INFERRED 0.75]
- **Deployment Safety Net** — knowledge_base_deployment_sop_canary_rollout, knowledge_base_deployment_sop_rollback_criteria, knowledge_base_deployment_sop_feature_flags, knowledge_base_code_review_guidelines_canary_ownership [EXTRACTED 1.00]
- **Incident Response Flow** — knowledge_base_incident_response_plan_sev_definitions, knowledge_base_incident_response_plan_commander_warroom, knowledge_base_incident_response_plan_postmortem, knowledge_base_on_call_compensation_rotation_stipend [EXTRACTED 1.00]
- **Secure Development Lifecycle** — knowledge_base_security_policy_v2_1_secrets_handling, knowledge_base_environment_setup_precommit_trufflehog, knowledge_base_code_review_guidelines_security_checklist, knowledge_base_environment_setup_vault_secrets [EXTRACTED 1.00]

## Communities (48 total, 14 thin omitted)

### Community 0 - "Core Services Tests"
Cohesion: 0.05
Nodes (55): docx, io, networkx, pymupdf, pytest, build_competency_graph(), rank_next_topics(), Deterministically update mastery score, difficulty, and spaced review schedules. (+47 more)

### Community 1 - "React Frontend Pages"
Cohesion: 0.09
Nodes (38): GET /api/diagnostic/questions, GET /api/learning-path, GET /api/quiz/generate, build_competency_graph, generate_personalized_quiz, generate_quiz_for_topic, get_baseline_questions, get_diagnostic_questions_for_role (+30 more)

### Community 2 - "Knowledge Ingestion Pipeline"
Cohesion: 0.07
Nodes (35): csv, datetime, os, reportlab_lib, reportlab_lib_pagesizes, reportlab_lib_styles, reportlab_platypus, main() (+27 more)

### Community 3 - "Baseline Scoring Engine"
Cohesion: 0.09
Nodes (32): v2_diagnostic_questions(), get_baseline_questions(), Score baseline via v1, then add per-topic strength profile. Returns ALL v1 keys…, Role-card baseline: per_topic general questions per required topic. Returns v1…, score_baseline(), evaluate_diagnostic(), get_diagnostic_questions_for_role(), is_answer_match() (+24 more)

### Community 4 - "Policy Concepts Docs"
Cohesion: 0.07
Nodes (29): OnboardIQ Adaptive Onboarding App, Post-Merge Canary Ownership and Rollback Watch, Code Review Process, Code Review Guidelines, PR Turnaround 4 Hours 400 Line Limit, Security-First Code Review Checklist, Core Cultural Pillars Ownership Transparency Empathy Innovation, Automated Rollback Criteria (+21 more)

### Community 5 - "API Read Handlers"
Cohesion: 0.11
Nodes (27): fastapi, fastapi_middleware_cors, get, pydantic, admin_list_users(), ask_knowledge_coach(), buddy_attention(), get_current_user_profile() (+19 more)

### Community 6 - "Database Models Engine"
Cohesion: 0.13
Nodes (24): Base, delete, seed_demo_users(), admin_delete_user(), delete_document(), get_dashboard_summary(), get_employee_readiness_report(), get_manager_team() (+16 more)

### Community 7 - "Admin Auth Management"
Cohesion: 0.14
Nodes (25): Any, AuthBase, post, put, admin_create_user(), admin_login(), admin_reset_baseline(), admin_transfer_role() (+17 more)

### Community 8 - "Frontend Dependencies"
Cohesion: 0.08
Nodes (23): dependencies, react, react-dom, devDependencies, oxlint, @types/react, @types/react-dom, vite (+15 more)

### Community 9 - "Ops Culture Docs"
Cohesion: 0.10
Nodes (21): Communication Guidelines, Escalation Paths to War Rooms, Slack Channel Standards and Etiquette, Blameless Retrospectives and Psychological Safety, Core Collaboration Window 10AM-3PM EST, Core Collaboration Window 10AM-3PM EST, Company Basics and Culture, Incident Commander PagerDuty War Room (+13 more)

### Community 10 - "LLM Teaching Pipeline"
Cohesion: 0.18
Nodes (15): dotenv, json, re, clean_json_response(), generate_completion(), Generate completion with Mistral AI, with graceful multi-model fallback and…, Extract clean JSON substring from LLM output., Intelligent context-aware fallback responses when Mistral AI API key is not… (+7 more)

### Community 11 - "API Request Models"
Cohesion: 0.12
Nodes (16): BaseModel, AdminCreateUserRequest, AdminLoginRequest, ChangePasswordRequest, EvalSubmitRequest, ExplainAgainRequest, get_quiz_explain_again(), LoginRequest (+8 more)

### Community 12 - "Admin Token Guard"
Cohesion: 0.15
Nodes (15): on_event, _admin_guard(), get_auth_users(), List all accounts — admin-only (used by admin portal + gated demo switch)., Header-injecting wrapper so Depends gets the Authorization header., Clone → run → working demo: fill empty stores, never touch live data. Each…, _self_seed_on_boot(), admin_username_from_token() (+7 more)

### Community 13 - "Static Quiz Bank"
Cohesion: 0.18
Nodes (13): get_mistral_client(), Retrieve an authenticated Mistral AI client or None if key is…, get_topic_bank(), Full static bank for a topic key (base bank merged in by caller)., generate_quiz_session(), _norm_question(), _normalize_topic_key(), Map a human topic title to the static bank key. Pure rename, same rules. (+5 more)

### Community 14 - "Adaptive Quiz Policy"
Cohesion: 0.19
Nodes (13): random, get_quiz_session(), 20-question no-repeat session. Difficulty auto-resolves from the user's topic…, v2_quiz_next(), effective_mastery(), generate_personalized_quiz(), pick_difficulty(), pick_next_topic() (+5 more)

### Community 15 - "Held-Out Eval Engine"
Cohesion: 0.26
Nodes (11): Grade eval, update mastery via the standard (frozen) updater. No XP: measures…, v2_eval_submit(), qhash(), build_graded_eval(), _eval_id(), _full_static_bank(), grade_graded_eval(), Base bank + expanded bank for a key, deduplicated by question text. (+3 more)

### Community 16 - "Data Architecture Docs"
Cohesion: 0.20
Nodes (10): Architecture Standards, API Gateway gRPC Kafka Event-Driven Communication, Kubernetes Docker Terraform Infrastructure, Microservices Architecture Go Python React, Observability with PII-Masked Structured Logs, PostgreSQL Redis pgvector Persistence and Caching, Data Privacy and GDPR, TLS 1.3 and AES-256 Encryption with KMS (+2 more)

### Community 17 - "Quiz Validation Gate"
Cohesion: 0.22
Nodes (9): get_quiz_question(), generate_quiz_for_topic(), Generate a dynamic, novel, grounded multiple-choice question for a given topic…, Two-tier validation gate. Tier 1 (always): structural check — shape, 4 distinct…, Deterministic validity: shape + answer-in-options + evidence present., _structural_check(), validate_quiz_question(), Verify Error 4 fix: Quiz generator generates distinct topic-specific questions… (+1 more)

### Community 18 - "Diagnostic Submit Flow"
Cohesion: 0.22
Nodes (9): DiagnosticSubmitRequest, evaluate_scenario(), QuizSubmitRequest, ScenarioEvaluateRequest, submit_diagnostic(), submit_quiz_answer(), v2_diagnostic_evaluate(), award_xp() (+1 more)

### Community 19 - "Seen Tracking Store"
Cohesion: 0.36
Nodes (7): Held-out graded assessment: unseen questions only. Answers stripped; server…, v2_graded_eval(), _ensure_table(), get_seen_hashes(), log_seen(), Connection, Record served questions. Idempotent. Returns new rows added.

### Community 20 - "Brief Fix Tests"
Cohesion: 0.38
Nodes (5): fastapi_testclient, grounded_fallback_question(), Last-resort question: always a verbatim bank item, never synthesized. Used when…, _bank_texts(), test_grounded_fallback_never_synthesizes()

### Community 21 - "Auth Schema Helper"
Cohesion: 0.29
Nodes (6): hashlib, ensure_auth_schema(), get_auth_db(), Additive columns for pre-existing auth.db files., sqlalchemy, sqlalchemy_orm

### Community 22 - "Social Icons Set"
Cohesion: 0.29
Nodes (6): bluesky-icon symbol, discord-icon symbol, documentation-icon symbol, github-icon symbol, social-icon symbol, x-icon symbol

### Community 23 - "Lint Configuration"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 24 - "Hero Illustration Asset"
Cohesion: 0.40
Nodes (6): Bottom purple square layer, Dashed vertical connector, hero.png image asset, Layered architecture concept, Layered platform illustration, Top black square layer

### Community 25 - "Leave Policy Docs"
Cohesion: 0.40
Nodes (5): Professional Development Stipend 1500 USD, Employee Handbook v1.0, Unlimited Flexible PTO Minimum 20 Days, Leave Policy, Parental Leave 16 Weeks Sick Leave 10 Days

### Community 26 - "Plan Architecture Docs"
Cohesion: 0.50
Nodes (5): Adaptive quiz v2 sidecars and v2 endpoints, Admin portal append-only with frontend hide, Frozen contracts blast-radius-safe principle, require_admin, Taxonomy DEPARTMENTS ROLE_BASELINE GENERAL DEEP

### Community 27 - "Quiz Submit State"
Cohesion: 0.40
Nodes (5): POST /api/quiz/submit, pick_difficulty, update_topic_state, UserProfileModel, UserTopicState

### Community 28 - "Doc Approval Gate"
Cohesion: 0.50
Nodes (4): approve_document(), Review gate: draft -> active. New endpoint, guarded from day one., doc_topics_for_title(), Map a doc title to affected topic keys (stable, no LLM).

### Community 29 - "Vite Logo Asset"
Cohesion: 0.50
Nodes (4): Purple-blue gradient palette with blur filters and alpha mask, Lightning bolt central shape, Vite logo SVG asset, Parenthesis side marks with dark-mode adaptive fill

### Community 30 - "Sales Playbook Docs"
Cohesion: 0.67
Nodes (3): Discount Approval Matrix 10pct 20pct, Sales Playbook, MEDDIC Qualification Framework

### Community 31 - "Diagnostic Evaluate Wrap"
Cohesion: 0.67
Nodes (3): POST /api/diagnostic/evaluate, evaluate_diagnostic, score_baseline

### Community 32 - "Favicon Brand Mark"
Cohesion: 1.00
Nodes (3): Angular Bolt Letterform Shape, Favicon SVG Brand Mark, Purple Lavender Blue Gradient Palette

### Community 33 - "React Logo Asset"
Cohesion: 0.67
Nodes (3): React cyan brand color #00D8FF, React logo, React logo SVG asset

## Ambiguous Edges - Review These
- `OnboardIQ Adaptive Onboarding App` → `Core Cultural Pillars Ownership Transparency Empathy Innovation`  [AMBIGUOUS]
  index.html · relation: conceptually_related_to

## Knowledge Gaps
- **90 isolated node(s):** `$schema`, `plugins`, `react/rules-of-hooks`, `react/only-export-components`, `name` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 213 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `OnboardIQ Adaptive Onboarding App` and `Core Cultural Pillars Ownership Transparency Empathy Innovation`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `grounded_fallback_question()` connect `Brief Fix Tests` to `Quiz Validation Gate`, `Static Quiz Bank`, `API Read Handlers`, `Held-Out Eval Engine`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Why does `generate_rag_response()` connect `Core Services Tests` to `Knowledge Ingestion Pipeline`, `LLM Teaching Pipeline`, `API Read Handlers`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `react` connect `React Frontend Pages` to `Frontend Dependencies`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `UserAuthModel` (e.g. with `admin_create_user()` and `admin_delete_user()`) actually correct?**
  _`UserAuthModel` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `UserTopicState` (e.g. with `admin_delete_user()` and `admin_reset_baseline()`) actually correct?**
  _`UserTopicState` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `plugins`, `react/rules-of-hooks` to the rest of the system?**
  _90 weakly-connected nodes found - possible documentation gaps or missing edges._