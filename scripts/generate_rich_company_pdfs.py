import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors

KB_DIR = "knowledge_base"
os.makedirs(KB_DIR, exist_ok=True)

COMPREHENSIVE_DOCS = [
    {
        "filename": "Company_Basics_and_Culture",
        "title": "Company Basics and Culture",
        "role": "all",
        "sections": [
            ("1. Company Overview and Mission", 
             "Nexora is an enterprise-grade cloud innovation platform founded to simplify distributed systems, adaptive learning, and intelligent automation. Our mission is to empower global teams with resilient software architecture, transparent operations, and psychological safety."),
            ("2. Core Cultural Pillars",
             "• Ownership: Every team member owns their outcomes end-to-end.\n• Transparency: Default to open communication and documented decisions.\n• Empathy: Treat colleagues and users with continuous respect and active listening.\n• Continuous Innovation: Encourage calculated risk-taking, fast feedback loops, and blameless retrospectives."),
            ("3. Working Hours and Core Collaboration Window",
             "Nexora operates on a flexible, asynchronous-first schedule with a designated Core Collaboration Window from 10:00 AM to 3:00 PM EST (Monday through Friday). All synchronous meetings, sprint ceremonies, and cross-functional alignments must be scheduled within this window. Outside core hours, employees have complete autonomy over their working hours."),
            ("4. Onboarding Milestones (30-60-90 Days)",
             "• Day 1-30: Complete compliance training, environment setup, attend welcome mentor sessions, and submit first peer-reviewed PR.\n• Day 31-60: Drive independent feature tasks, participate in on-call shadow rotations, and contribute to sprint planning.\n• Day 61-90: Lead a technical design or operational improvement initiative, present at engineering demo day, and complete the role readiness assessment."),
            ("5. Communication and Perks",
             "Company all-hands meetings take place bi-weekly on Thursdays at 2:00 PM EST with open AMA (Ask Me Anything) sessions. Every employee is assigned a dedicated onboarding buddy during their first 90 days.")
        ]
    },
    {
        "filename": "Employee_Handbook_v1.0",
        "title": "Employee Handbook v1.0",
        "role": "all",
        "sections": [
            ("1. Welcome to Nexora",
             "Welcome to the Nexora team. This handbook sets forth the foundational policies, expectations, and benefits for all full-time and contractual employees."),
            ("2. Working Hours & Attendance",
             "Core collaboration hours are 10:00 AM to 3:00 PM EST. Flexible working arrangements allow team members to complete their 40-hour work week according to their local preferences while maintaining presence during core hours."),
            ("3. Flexible Paid Time Off (PTO)",
             "Nexora offers an Unlimited Flexible Paid Time Off policy for all full-time employees. We recommend taking a minimum of 20 PTO days annually to maintain work-life balance. Planned vacations over 3 consecutive days must be submitted via Workday at least 2 weeks in advance."),
            ("4. Professional Development & Learning Stipend",
             "Every full-time employee receives an annual $1,500 USD Professional Development Stipend for conferences, certifications, books, and courses. Approvals are managed through the People Ops portal."),
            ("5. Equal Opportunity and Anti-Harassment",
             "Nexora is committed to maintaining a safe, inclusive, and harassment-free workplace. Any discriminatory behavior, harassment, or retaliation will result in immediate disciplinary action up to termination.")
        ]
    },
    {
        "filename": "Security_Policy_v2.1",
        "title": "Security Policy v2.1",
        "role": "all",
        "sections": [
            ("1. Workstation & Physical Security",
             "Employees must ensure workstations are locked whenever left unattended (Win+L / Cmd+Ctrl+Q). Workstation screen lock timeout is enforced at 5 minutes of inactivity. Physical laptops must use full-disk encryption (FileVault / BitLocker)."),
            ("2. Password & Authentication Standards",
             "Mandatory password rotation occurs every 90 days. Passwords must contain a minimum of 16 characters including uppercase, lowercase, numbers, and symbols. Multi-Factor Authentication (MFA / 2FA) using hardware security keys or authenticator apps (TOTP) is strictly enforced on all corporate SSO accounts. SMS-based 2FA is prohibited."),
            ("3. Phishing Simulations & Awareness",
             "Security awareness drills and quarterly phishing simulations are conducted by the InfoSec team. Employees who fail simulated drills are required to complete a 30-minute refresher security course within 5 business days."),
            ("4. Incident Reporting Protocol",
             "Any suspected security anomaly, leaked credential, lost laptop, or malware alert must be reported to security@nexora.com and in the private Slack channel #security-alerts within 15 minutes of discovery."),
            ("5. Zero Trust Access Control",
             "Access to internal networks, databases, and admin dashboards requires connection through Nexora's Zero-Trust VPN with device posture compliance checks. Production access requires just-in-time (JIT) privilege elevation.")
        ]
    },
    {
        "filename": "Git_Workflow_v1.2",
        "title": "Git Workflow v1.2",
        "role": "engineering",
        "sections": [
            ("1. Trunk-Based Development",
             "Nexora engineering adheres strictly to Trunk-Based Development. Feature branches must be short-lived (maximum lifespan of 24-48 hours) and branched directly from 'main'."),
            ("2. Branch Naming Conventions",
             "Branches must follow standard prefixes: feature/JIRA-123-short-desc, bugfix/JIRA-123-short-desc, hotfix/JIRA-123-short-desc, or chore/JIRA-123-short-desc."),
            ("3. Commit Hygiene & Mandatory Signing",
             "All Git commits must be cryptographically signed using GPG or SSH keys verified in GitHub. Commit messages must follow the Conventional Commits specification (feat:, fix:, docs:, refactor:, test:, chore:)."),
            ("4. Pull Request Requirements",
             "Every Pull Request (PR) requires at least 1 peer approval from an engineer in the CODEOWNERS file. All automated CI checks (linters, unit tests, security vulnerability scans, build verification) must pass with zero errors before merge."),
            ("5. Merging Strategy",
             "Use 'Squash and Merge' for feature branches to keep the main commit log clean and linear. Rebase on main prior to final merge.")
        ]
    },
    {
        "filename": "Code_Review_Guidelines",
        "title": "Code Review Guidelines",
        "role": "engineering",
        "sections": [
            ("1. Review Objectives",
             "Code reviews ensure correctness, readability, architectural compliance, security, and test coverage (>80% required on new code)."),
            ("2. Review Speed and Turnaround",
             "PRs should be reviewed within 4 business hours during core collaboration hours. If a PR is larger than 400 lines of diff, the author must provide an architectural walkthrough or split the PR into smaller atomic increments."),
            ("3. Constructive Feedback & Etiquette",
             "Reviewers must distinguish between blocking concerns (e.g. security vulnerability, memory leak, logic flaw) and non-blocking suggestions (prefix with 'nit: ' or 'suggestion: '). Automated formatters (Prettier, Black, GoFmt) handle styling."),
            ("4. Testing Standards",
             "Every PR modifying business logic must include automated unit tests, and where appropriate, integration tests. Flaky tests must be quarantined and resolved immediately.")
        ]
    },
    {
        "filename": "Deployment_SOP",
        "title": "Deployment SOP",
        "role": "devops,engineering",
        "sections": [
            ("1. Deployment Schedule & Cadence",
             "Standard production deployments take place on Tuesdays and Thursdays between 10:00 AM and 2:00 PM EST. Friday deployments, weekend deployments, and deployments after 3:00 PM EST are strictly prohibited to prevent off-hours incidents."),
            ("2. Emergency Out-of-Band Hotfixes",
             "Emergency hotfixes outside the scheduled deployment window require explicit written approval from the Engineering VP or Director of Infrastructure in the #hotfix-approvals channel."),
            ("3. Progressive Rollout & Canary Strategy",
             "Deployments follow a canary progression: 5% traffic for 15 minutes -> 25% for 30 minutes -> 100% full rollout. Automated health checks monitor HTTP 5xx error rates, latency p99, and CPU/memory saturation."),
            ("4. Automated Rollback Criteria",
             "If error rates exceed 0.5% or p99 latency increases by >25% during canary rollout, the automated CD pipeline immediately triggers a 1-click rollback to the previous stable release artifact.")
        ]
    },
    {
        "filename": "Incident_Response_Plan",
        "title": "Incident Response Plan",
        "role": "all",
        "sections": [
            ("1. Incident Severity Definitions",
             "• Sev1 (Critical): Total service outage, critical data loss, or active security breach affecting >10% of customers. SLA response: < 15 minutes.\n• Sev2 (Major): Partial system degradation or core feature failure with no workaround. SLA response: < 30 minutes.\n• Sev3 (Moderate): Non-critical service failure with available workaround. SLA response: < 2 hours.\n• Sev4 (Minor): Minor UI defect or operational inconvenience. SLA response: Next business day."),
            ("2. Escalation & Communication Protocol",
             "Sev1 and Sev2 incidents automatically trigger PagerDuty alarms to the Primary On-Call Engineer. The Primary On-Call assumes the role of Incident Commander (IC). All live coordination takes place in the dedicated Slack war room '#incidents' and an active Zoom incident bridge."),
            ("3. Status Page Updates",
             "The Incident Commander or Communications Lead must post an initial customer-facing update to status.nexora.com within 20 minutes of Sev1 declaration and provide updates every 30 minutes until resolution."),
            ("4. Blameless Post-Mortem",
             "For all Sev1 and Sev2 incidents, a blameless post-mortem document must be drafted within 48 hours and reviewed in the weekly Engineering Operations Review.")
        ]
    },
    {
        "filename": "Remote_Work_Policy",
        "title": "Remote Work Policy",
        "role": "all",
        "sections": [
            ("1. Remote-First Philosophy",
             "Nexora is a remote-first organization. Employees can work from any approved domestic or international location with reliable high-speed internet (>50 Mbps download / >10 Mbps upload)."),
            ("2. Equipment and Home Office Stipend",
             "Upon joining, every full-time employee is eligible for a one-time $500 USD Ergonomic Home Office Stipend for desks, chairs, monitors, and peripherals. Company-issued MacBook Pro or ThinkPad workstations are provided directly by IT Ops."),
            ("3. Monthly Internet Allowance",
             "Nexora provides a monthly recurring $50 USD internet stipend to subsidize high-speed residential broadband. This allowance is automatically reimbursed on monthly payroll."),
            ("4. Coworking Space Subsidies",
             "Employees who prefer working outside the home can expense up to $250 USD per month for hot-desk memberships at certified coworking spaces (e.g. WeWork, Industrious).")
        ]
    },
    {
        "filename": "Expense_Policy_v3.0",
        "title": "Expense Policy v3.0",
        "role": "all",
        "sections": [
            ("1. General Expense Principles",
             "Employees must exercise prudent judgment when incurring business expenses on behalf of Nexora. All expenses must be legitimate, reasonable, and substantiated."),
            ("2. Receipt Requirements & Thresholds",
             "Itemized receipts are required for all business expenses exceeding $25 USD. Receipts must be submitted via Expensify within 30 days of the transaction date. Undocumented expenses over $25 will not be reimbursed."),
            ("3. Travel & Meals Per Diem",
             "The standard meal per diem allowance during business travel is $75 USD per day ($20 breakfast, $25 lunch, $30 dinner). Alcohol is non-reimbursable unless part of an authorized client entertainment dinner."),
            ("4. Flight & Accommodation Rules",
             "Economy class is standard for flights under 6 hours. Business class is permitted for international flights over 8 continuous flight hours with VP pre-approval. Hotel nightly rates should not exceed $250/night in standard cities or $350/night in tier-1 metro areas.")
        ]
    },
    {
        "filename": "Leave_Policy",
        "title": "Leave Policy",
        "role": "all",
        "sections": [
            ("1. Paid Time Off (PTO) Structure",
             "Nexora provides unlimited flexible PTO. Employees are encouraged to take at least 4 to 5 weeks off per calendar year. All planned PTO must be entered in Workday at least 2 weeks prior to departure."),
            ("2. Sick Leave & Mental Health Days",
             "Employees are provided up to 10 paid sick and mental health wellness days annually without requiring medical certificate documentation for absences under 3 consecutive days."),
            ("3. Parental & Family Leave",
             "Nexora offers 16 weeks of 100% paid parental leave for all new parents (birth, adoption, or surrogacy), eligible after 90 days of continuous employment."),
            ("4. Bereavement and Civic Duty Leave",
             "Up to 5 paid days of bereavement leave are granted for immediate family members. Paid time off is also provided for jury duty and public elections.")
        ]
    },
    {
        "filename": "Architecture_Standards",
        "title": "Architecture Standards",
        "role": "engineering",
        "sections": [
            ("1. Architectural Paradigm",
             "Nexora systems follow a decoupled, microservices architecture. Core backend services are written in Go for high-throughput concurrency, machine learning & analytics pipelines in Python 3.11+, and frontend web applications in React 19 / TypeScript with Vite."),
            ("2. API Gateway & Communication",
             "External and frontend-to-backend communication uses GraphQL and REST over HTTPS with strict OpenAPI / JSON schema validation. Inter-service backend communication uses gRPC with Protocol Buffers and Kafka message streams for asynchronous event-driven workflows."),
            ("3. Database & Caching Standards",
             "Transactional persistence uses PostgreSQL 16 with read replicas and connection pooling via PgBouncer. Caching layers utilize Redis clusters with defined TTL policies. Vector search is powered by ChromaDB / pgvector."),
            ("4. Infrastructure & Container Orchestration",
             "All workloads run as Docker containers orchestrated via Kubernetes (EKS/GKE). Infrastructure is provisioned strictly via Terraform (Infrastructure as Code).")
        ]
    },
    {
        "filename": "Data_Privacy_and_GDPR",
        "title": "Data Privacy and GDPR",
        "role": "all",
        "sections": [
            ("1. Compliance Framework",
             "Nexora complies with the European Union General Data Protection Regulation (GDPR), California Consumer Privacy Act (CCPA), and SOC 2 Type II controls."),
            ("2. PII Logging Prohibitions",
             "Personally Identifiable Information (PII) such as email addresses, social security numbers, passwords, payment details, and IP addresses must NEVER be logged in plain text. Logs must pass through automated masking filters before ingestion into Datadog / CloudWatch."),
            ("3. Data Encryption Standards",
             "All sensitive data in transit must use TLS 1.3 encryption. All data at rest must use AES-256 encryption. Database snapshots and backups must be encrypted with dedicated AWS KMS keys."),
            ("4. Right to be Forgotten & Data Deletion",
             "GDPR data erasure requests ('Right to be Forgotten') must be executed across all production and backup stores within 30 days of verified customer request.")
        ]
    },
    {
        "filename": "Environment_Setup",
        "title": "Environment Setup",
        "role": "engineering",
        "sections": [
            ("1. Local Development Environment",
             "Engineers use Docker Desktop or OrbStack to spin up local database, cache, and service dependencies via 'docker-compose up -d'. Standard package managers are Node (pnpm / npm), Go (go modules), and Python (uv / pip)."),
            ("2. Secrets Management & Vault",
             "Local development secrets must never be committed to repositories or shared in Slack. Secrets are fetched dynamically via HashiCorp Vault CLI or 1Password developer plugins."),
            ("3. Pre-Commit Hooks",
             "All repositories configure 'pre-commit' hooks to run linter checks, GPG sign validation, and secret detection scans (TruffleHog) before code can be committed locally.")
        ]
    },
    {
        "filename": "Communication_Guidelines",
        "title": "Communication Guidelines",
        "role": "all",
        "sections": [
            ("1. Channel Standards",
             "• Slack: Primary platform for internal real-time and asynchronous messaging. Use public channels by default; reserve DMs for 1-on-1s and private feedback.\n• Email: Reserved for external vendors, formal HR announcements, and legal communication.\n• Zoom / Google Meet: Used for synchronous meetings with video-on preference during standups.\n• Notion / Confluence: Single source of truth for documentation, RFCs, and engineering specifications."),
            ("2. Slack Etiquette",
             "Always use message threads to keep channels readable. Use status indicators (e.g. 🌴 Vacation, 🎧 Deep Work, 🥪 Lunch) to manage availability expectations.")
        ]
    },
    {
        "filename": "Jira_Triage_Process",
        "title": "Jira Triage Process",
        "role": "product,engineering",
        "sections": [
            ("1. Ticket Creation Standards",
             "Every bug ticket in Jira must include: (1) Clear summary, (2) Step-by-step reproduction steps, (3) Expected behavior, (4) Actual behavior, (5) Environment/Browser details, and (6) Sentry error trace or screenshot."),
            ("2. Epic & Story Sizing",
             "Epics must be scoped to complete within a maximum of 2 agile sprints (4 weeks). User stories must be sized in Fibonacci story points (1, 2, 3, 5, 8). Stories larger than 8 points must be broken down."),
            ("3. Triage & SLA Priority",
             "Product managers and engineering leads triage incoming tickets daily. Blockers (P0) are assigned immediately to current sprint; P1 bugs are scheduled within 24 hours.")
        ]
    },
    {
        "filename": "On-Call_Compensation",
        "title": "On-Call Compensation",
        "role": "engineering",
        "sections": [
            ("1. On-Call Rotation Structure",
             "Engineering services participate in a 7-day weekly on-call rotation with a Primary and Secondary engineer. Schedules are published 6 weeks in advance via PagerDuty."),
            ("2. Financial Compensation",
             "Engineers receive an additional $500 USD stipend per completed on-call week, paid on the subsequent payroll cycle."),
            ("3. Time in Lieu & Recovery",
             "If an on-call engineer is paged during the night (10:00 PM to 7:00 AM) to resolve a Sev1/Sev2 incident, they are entitled to take the morning off (up to 4 hours) as paid recovery time.")
        ]
    },
    {
        "filename": "Sales_Playbook",
        "title": "Sales Playbook",
        "role": "sales",
        "sections": [
            ("1. Nexora Value Proposition",
             "Nexora provides enterprise teams with unified developer productivity, automated compliance governance, and AI-assisted onboarding, reducing engineering ramp-up time by 60%."),
            ("2. Qualification Framework (MEDDIC)",
             "Sales reps qualify enterprise opportunities using MEDDIC: Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, and Champion."),
            ("3. Discount Approval Matrix",
             "Discounts up to 10% can be approved by Account Executives; 11-20% requires Sales Director sign-off; discounts exceeding 20% require VP of Sales and CFO approval.")
        ]
    },
    {
        "filename": "Product_Triage_Guide",
        "title": "Product Triage Guide",
        "role": "product",
        "sections": [
            ("1. Feature Prioritization (RICE Scoring)",
             "Feature proposals are prioritized using the RICE framework: (Reach × Impact × Confidence) / Effort. High-RICE initiatives are slotted into quarterly product roadmaps."),
            ("2. User Feedback Loops",
             "Customer feature requests from Zendesk, Gong, and sales calls are aggregated in Productboard and reviewed bi-weekly with engineering leads.")
        ]
    }
]

def generate_pdf_and_txt():
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e1b4b'),
        spaceAfter=10
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=14
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#3730a3'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'SectionBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=8
    )

    for doc_info in COMPREHENSIVE_DOCS:
        # 1. Generate PDF
        pdf_path = os.path.join(KB_DIR, f"{doc_info['filename']}.pdf")
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
        )
        story = []
        
        story.append(Paragraph(f"Nexora Corporate Knowledge Base: {doc_info['title']}", title_style))
        story.append(Paragraph(f"<b>Target Role:</b> {doc_info['role'].upper()} &nbsp;|&nbsp; <b>Version:</b> Official &nbsp;|&nbsp; <b>Published:</b> {datetime.date.today().isoformat()}", meta_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#6366f1'), spaceBefore=2, spaceAfter=14))
        
        full_text_content = f"Title: {doc_info['title']}\nRole: {doc_info['role']}\nDate: {datetime.date.today().isoformat()}\n" + ("-" * 40) + "\n\n"

        for heading, body in doc_info['sections']:
            story.append(Paragraph(heading, heading_style))
            # Format bullets or paragraphs nicely
            formatted_body = body.replace("\n", "<br/>")
            story.append(Paragraph(formatted_body, body_style))
            story.append(Spacer(1, 4))
            
            full_text_content += f"{heading}\n{body}\n\n"

        doc.build(story)
        print(f"[PDF Created] {pdf_path}")

        # 2. Also write/overwrite TXT version
        txt_path = os.path.join(KB_DIR, f"{doc_info['filename']}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(full_text_content)
        print(f"[TXT Created] {txt_path}")

if __name__ == "__main__":
    generate_pdf_and_txt()
    print("All rich PDF and TXT documents generated successfully!")
