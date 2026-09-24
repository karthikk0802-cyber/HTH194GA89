# Graph Report - HTH194GA89  (2026-09-25)

## Corpus Check
- Corpus is ~34,659 words - fits in a single context window. You may not need a graph.

## Summary
- 420 nodes · 868 edges · 37 communities (25 shown, 12 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 54 edges (avg confidence: 0.88)
- Token cost: 8,120 input · 2,910 output

## Community Hubs (Navigation)
- API Request Models
- Auth Utilities Tests
- LLM Quiz Generation
- React Frontend App
- Learning Path Engine
- Document Ingestion Pipeline
- Frontend Dependencies
- Incident On-Call Culture
- Code Review Workflow
- Auth Database Security
- Streamlit Page Wrappers
- System Architecture Standards
- Leave Compensation Policy
- Social Icons Set
- Lint Configuration
- Hero Illustration Asset
- Product Triage Process
- Data Privacy GDPR
- Incident Management Concepts
- Vite Logo Asset
- Communication Standards
- Expense Policy Rules
- Triage Scoring Frameworks
- Sales Playbook MEDDIC
- Favicon Brand Mark
- React Logo Asset
- OnboardIQ Mission
- AI Data Stack
- Trunk Development Flow
- Leave Policy Concepts
- Slack Standards
- Expense Policy Concept
- Vite Template Doc

## God Nodes (most connected - your core abstractions)
1. `useAuth()` - 19 edges
2. `get_role_topics()` - 18 edges
3. `UserTopicState` - 17 edges
4. `react` - 16 edges
5. `UserProfileModel` - 16 edges
6. `generate_completion()` - 15 edges
7. `api` - 13 edges
8. `get_db()` - 12 edges
9. `UserAuthModel` - 11 edges
10. `DocumentModel` - 11 edges

## Surprising Connections (you probably didn't know these)
- `register_user()` --uses--> `UserAuthModel`  [INFERRED]
  server.py → services/auth_db.py
- `login_user()` --uses--> `UserAuthModel`  [INFERRED]
  server.py → services/auth_db.py
- `get_auth_users()` --uses--> `UserAuthModel`  [INFERRED]
  server.py → services/auth_db.py
- `get_current_user_profile()` --uses--> `UserAuthModel`  [INFERRED]
  server.py → services/auth_db.py
- `get_user_learning_path()` --uses--> `UserTopicState`  [INFERRED]
  server.py → services/db.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Reliability and Incident Management** — knowledge_base_incident_response_plan_severity_levels, knowledge_base_on_call_compensation_oncall_rotation, knowledge_base_deployment_sop_canary_strategy [INFERRED 0.85]
- **Engineering Delivery Workflow** — knowledge_base_git_workflow_v1_2_trunk_development, knowledge_base_code_review_guidelines_review_process, knowledge_base_environment_setup_local_development [INFERRED 0.80]
- **Progressive Delivery Safety Net** — knowledge_base_deployment_sop_canary, knowledge_base_deployment_sop_rollback, knowledge_base_incident_response_plan_severity [INFERRED 0.85]
- **On-Call Incident Management Loop** — knowledge_base_on_call_compensation_rotation, knowledge_base_incident_response_plan_command, knowledge_base_incident_response_plan_postmortem [INFERRED 0.85]

## Communities (37 total, 12 thin omitted)

### Community 0 - "API Request Models"
Cohesion: 0.08
Nodes (52): Base, BaseModel, fastapi, fastapi_middleware_cors, get, post, pydantic, ask_knowledge_coach() (+44 more)

### Community 1 - "Auth Utilities Tests"
Cohesion: 0.07
Nodes (44): AuthBase, docx, io, pymupdf, pytest, get_topic_resources(), upload_document(), Deterministically update mastery score, difficulty, and spaced review schedules. (+36 more)

### Community 2 - "LLM Quiz Generation"
Cohesion: 0.09
Nodes (34): json, random, re, get_quiz_question(), Search for relevant chunks., search_chroma(), clean_json_response(), generate_completion() (+26 more)

### Community 3 - "React Frontend App"
Cohesion: 0.16
Nodes (22): react, react-dom, App(), MainApp(), Navbar(), Sidebar(), AuthContext, AuthProvider() (+14 more)

### Community 4 - "Learning Path Engine"
Cohesion: 0.09
Nodes (30): check_env(), main(), dotenv, networkx, plotly_graph_objects, get_diagnostic_questions(), get_user_learning_path(), build_competency_graph() (+22 more)

### Community 5 - "Document Ingestion Pipeline"
Cohesion: 0.13
Nodes (21): datetime, delete, os, pandas, reportlab_lib, reportlab_lib_pagesizes, reportlab_lib_styles, reportlab_platypus (+13 more)

### Community 6 - "Frontend Dependencies"
Cohesion: 0.08
Nodes (23): dependencies, react, react-dom, devDependencies, oxlint, @types/react, @types/react-dom, vite (+15 more)

### Community 7 - "Incident On-Call Culture"
Cohesion: 0.09
Nodes (23): Core Collaboration Window, Cultural Pillars Ownership Transparency, Company Basics and Culture Document, 30-60-90 Onboarding Milestones, GDPR Compliance, Canary Rollout 5-25-100 Percent, Tue Thu Deployment Window No Friday Deploys, Deployment SOP Document (+15 more)

### Community 8 - "Code Review Workflow"
Cohesion: 0.17
Nodes (12): 80 Percent Test Coverage Requirement, Code Review Guidelines Document, 400-Line PR Limit Walkthrough, 4-Hour Review Turnaround, Environment Setup Document, Docker Compose Local Environment, Pre-commit TruffleHog Secret Scan, Vault 1Password Secrets Management (+4 more)

### Community 9 - "Auth Database Security"
Cohesion: 0.24
Nodes (10): hashlib, get_auth_db(), hash_password(), Hash a password using SHA-256 with salt., Seed default authentication accounts into auth.db, seed_default_auth_users(), verify_password(), sqlalchemy (+2 more)

### Community 11 - "System Architecture Standards"
Cohesion: 0.25
Nodes (8): GraphQL REST API Gateway OpenAPI Validation, Architecture Standards Document, gRPC Kafka Inter-service Communication, Kubernetes Terraform Infrastructure, Kubernetes Docker Terraform Infrastructure, Microservices Architecture, PostgreSQL Redis ChromaDB Data Layer, Docker Local Development

### Community 12 - "Leave Compensation Policy"
Cohesion: 0.29
Nodes (7): Employee Handbook v1.0 Document, Unlimited Flexible PTO 20 Days Workday, 1500 USD Development Stipend, Leave Policy Document, 16-Week Paid Parental Leave, Unlimited PTO Workday 2 Weeks, 10-Day Sick Wellness Leave

### Community 13 - "Social Icons Set"
Cohesion: 0.29
Nodes (6): bluesky-icon symbol, discord-icon symbol, documentation-icon symbol, github-icon symbol, social-icon symbol, x-icon symbol

### Community 14 - "Lint Configuration"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 15 - "Hero Illustration Asset"
Cohesion: 0.40
Nodes (6): Bottom purple square layer, Dashed vertical connector, hero.png image asset, Layered architecture concept, Layered platform illustration, Top black square layer

### Community 16 - "Product Triage Process"
Cohesion: 0.40
Nodes (5): Jira Triage Process Document, Epic Story Fibonacci Sizing, Jira Bug Ticket Reproduction Standard, Product Triage Guide Document, RICE Prioritization Framework

### Community 17 - "Data Privacy GDPR"
Cohesion: 0.50
Nodes (4): Data Privacy and GDPR Document, TLS 1.3 AES-256 KMS Encryption, Right to be Forgotten 30 Days, PII Logging Prohibition Masking

### Community 18 - "Incident Management Concepts"
Cohesion: 0.50
Nodes (4): Canary Deployment Strategy, Blameless Post-Mortem, Incident Severity Levels, On-Call Rotation

### Community 19 - "Vite Logo Asset"
Cohesion: 0.50
Nodes (4): Purple-blue gradient palette with blur filters and alpha mask, Lightning bolt central shape, Vite logo SVG asset, Parenthesis side marks with dark-mode adaptive fill

### Community 20 - "Communication Standards"
Cohesion: 0.67
Nodes (3): Communication Guidelines Document, Notion Confluence Source of Truth, Slack Primary Channel Standard

### Community 21 - "Expense Policy Rules"
Cohesion: 0.67
Nodes (3): Expense Policy v3.0 Document, 75 USD Meal Per Diem Travel Rules, Receipt Threshold 25 USD Expensify

### Community 22 - "Triage Scoring Frameworks"
Cohesion: 0.67
Nodes (3): Jira Triage Process, RICE Scoring, MEDDIC Qualification

### Community 23 - "Sales Playbook MEDDIC"
Cohesion: 0.67
Nodes (3): Discount Approval Matrix, Sales Playbook Document, MEDDIC Qualification Framework

### Community 24 - "Favicon Brand Mark"
Cohesion: 1.00
Nodes (3): Angular Bolt Letterform Shape, Favicon SVG Brand Mark, Purple Lavender Blue Gradient Palette

### Community 25 - "React Logo Asset"
Cohesion: 0.67
Nodes (3): React cyan brand color #00D8FF, React logo, React logo SVG asset

## Knowledge Gaps
- **81 isolated node(s):** `$schema`, `plugins`, `react/rules-of-hooks`, `react/only-export-components`, `name` (+76 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 160 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `react` connect `React Frontend App` to `Frontend Dependencies`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `generate_quiz_for_topic()` connect `LLM Quiz Generation` to `API Request Models`, `Auth Utilities Tests`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `UserTopicState` (e.g. with `evaluate_scenario()` and `get_dashboard_summary()`) actually correct?**
  _`UserTopicState` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `UserProfileModel` (e.g. with `evaluate_scenario()` and `get_dashboard_summary()`) actually correct?**
  _`UserProfileModel` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `plugins`, `react/rules-of-hooks` to the rest of the system?**
  _81 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `API Request Models` be split into smaller, more focused modules?**
  _Cohesion score 0.08246753246753247 - nodes in this community are weakly interconnected._
- **Should `Auth Utilities Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.06509803921568627 - nodes in this community are weakly interconnected._