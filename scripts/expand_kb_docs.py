# Expand the Nexora policy corpus ADDITIVELY.
# Appends new sections to every doc in generate_rich_company_pdfs.COMPREHENSIVE_DOCS,
# then regenerates the .txt + .pdf pairs in knowledge_base/.
#
# Hard rule: existing section text is NEVER edited — quiz banks, the golden eval
# set, and diagnostic questions quote those facts verbatim. New sections only
# extend, cross-reference, and operationalize. They must not contradict any
# existing fact or introduce a second value for any quizzed number.

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
import generate_rich_company_pdfs as gen

EXTRA_SECTIONS = {
    "Company_Basics_and_Culture": [
        ("6. Psychological Safety in Practice",
         "Blameless retrospectives apply beyond engineering: any team may call a blameless review after a missed commitment. Retaliation for raising risks in good faith is treated as a conduct violation under the Employee Handbook."),
        ("7. Documented Decisions",
         "Transparency means decisions live in writing. Material choices must be recorded as short Notion decision logs (context, options, decider, date) so absent teammates and future hires can reconstruct the why."),
        ("8. Values in Performance Reviews",
         "Peer feedback each cycle rates the four cultural pillars alongside delivery. Sustained ownership and transparency weigh equally with technical output in level and compensation decisions."),
    ],
    "Employee_Handbook_v1.0": [
        ("6. Scope: Full-Time and Contractual Staff",
         "All conduct, attendance, and security expectations in this handbook apply to full-time and contractual employees alike. Benefit figures such as stipends and leave refer to full-time entitlements unless stated otherwise."),
        ("7. Reporting Concerns",
         "Concerns about discrimination, harassment, or retaliation may be raised with a direct manager, People Ops, or the anonymous ethics channel. Reports are acknowledged within 2 business days and investigated confidentially."),
        ("8. Handbook Currency",
         "This handbook is reviewed annually by People Ops with Engineering Leadership. The published version in the knowledge base is authoritative; forwarded copies and screenshots are not reliable."),
    ],
    "Security_Policy_v2.1": [
        ("6. Secrets Handling for Engineers",
         "Application secrets, API tokens, and credentials must never be hardcoded, committed to repositories, or pasted into Slack. Local development secrets are injected via HashiCorp Vault CLI or 1Password developer plugins, and pre-commit TruffleHog scans enforce this automatically."),
        ("7. Vendor and Third-Party Reviews",
         "New vendors with access to Nexora or customer data undergo a security review by InfoSec before procurement, covering encryption posture, access controls, and incident notification commitments."),
        ("8. Training Compliance Tracking",
         "Completion of compliance training and phishing refresher courses is tracked per employee. Overdue training blocks production access elevation until resolved, consistent with Zero Trust least-privilege principles."),
    ],
    "Git_Workflow_v1.2": [
        ("6. Hotfix Branches",
         "Emergency production fixes use hotfix/JIRA-123-short-desc branches cut directly from 'main'. They follow the same signing, review, and CI gates as features; only the deployment window differs, per the Deployment SOP out-of-band approval process."),
        ("7. Release Tagging",
         "Each production deployment is tagged release-vX.Y.Z on main immediately after a successful canary rollout, so rollbacks and audits always reference an immutable artifact."),
        ("8. CODEOWNERS Maintenance",
         "Every repository maintains a CODEOWNERS file mapping directories to owning teams. Ownership changes require a PR reviewed by both the outgoing and incoming owners."),
    ],
    "Code_Review_Guidelines": [
        ("6. Security-First Checklist",
         "Reviewers verify authentication, authorization, input validation, secret handling, and logging hygiene against the Security Policy before approving. Any credential or PII exposure is a blocking concern by default."),
        ("7. Documentation in PRs",
         "PRs that change user-visible behavior or operating procedures must update the relevant runbook, README, or knowledge base page in the same PR, so docs never lag the code."),
        ("8. Post-Merge Ownership",
         "Authors own their merged code through the next canary deployment: they monitor rollout health and are first responder if their change triggers the automated rollback criteria."),
    ],
    "Communication_Guidelines": [
        ("6. Meeting Hygiene",
         "Every synchronous meeting needs an agenda, a Notion notes page, and a written decision log. Recurring meetings without an agenda for two consecutive cycles are cancelled by default."),
        ("7. Escalation Paths",
         "Production issues escalate to the #incidents war room, security anomalies to #security-alerts, and deployment exceptions to #hotfix-approvals. Routine discussion stays in topical public channels."),
        ("8. External Communication",
         "Only designated spokespeople communicate with customers, press, or vendors on Nexora's behalf. Employees never disclose unreleased plans, customer data, or security posture outside approved channels."),
    ],
    "Deployment_SOP": [
        ("6. Holiday and Event Freezes",
         "The Engineering VP may declare deployment freezes around major holidays or company events. Freeze calendars are published at least 2 weeks in advance; only Sev1 hotfixes with written approval ship during a freeze."),
        ("7. Database Migration Safety",
         "Schema migrations must be backward-compatible across at least one release (expand-then-contract). Destructive migrations require a reviewed rollback plan and a dedicated maintenance window."),
        ("8. Feature Flags and Kill Switches",
         "User-facing changes ship behind feature flags with a documented kill switch. Any engineer can request a flag-off through the Incident Commander during a suspected incident without prior approval."),
    ],
    "Architecture_Standards": [
        ("6. Service Ownership",
         "Every microservice has a single owning team recorded in CODEOWNERS and the service catalog. Owners are accountable for runbooks, on-call coverage, dependency upgrades, and deprecation notices."),
        ("7. API Versioning and Deprecation",
         "Breaking API changes require a new versioned endpoint. Deprecated endpoints carry Sunset headers and a minimum 90-day notice before removal, announced in the engineering changelog."),
        ("8. Observability Standards",
         "Services emit structured logs (PII-masked per the Data Privacy policy), RED metrics, and distributed traces into Datadog / CloudWatch. Every service ships with dashboards and alert thresholds reviewed quarterly."),
    ],
    "Environment_Setup": [
        ("6. Workstation Provisioning",
         "IT Ops provisions MacBook Pro or ThinkPad workstations with full-disk encryption before Day 1, consistent with the Security Policy device standards and the Remote Work equipment program."),
        ("7. VPN and Zero Trust Enrollment",
         "Engineers enroll devices in the Zero-Trust VPN with posture compliance checks during onboarding week. Production JIT elevation is granted only from compliant, enrolled devices."),
        ("8. Keeping the Environment Current",
         "Engineers pull updated base images and dependency lockfiles weekly. Stale environments older than 30 days are flagged in CI, since drift is a leading cause of works-on-my-machine defects."),
    ],
    "Expense_Policy_v3.0": [
        ("6. Client Entertainment",
         "Alcohol is reimbursable only as part of an authorized client entertainment dinner with documented attendees and business purpose. Team socials follow pre-approved budgets instead of per-person claims."),
        ("7. Foreign Currency",
         "Expenses in foreign currency are reimbursed at the Expensify card rate on the transaction date. Retain original-language itemized receipts; translations are handled by Finance on request."),
        ("8. Audit Sampling",
         "Finance audits a random sample of expense reports monthly. Repeated undocumented claims trigger mandatory retraining and temporary pre-approval requirements for the employee."),
    ],
    "Incident_Response_Plan": [
        ("6. Incident Roles",
         "Every declared incident staffs three roles: Incident Commander (the Primary On-Call), Communications Lead (status page and stakeholder updates), and Scribe (timeline and decision log). One person may cover Comms and Scribe for Sev3 and below."),
        ("7. Customer Communication Ownership",
         "Only the Communications Lead posts to status.nexora.com and customer channels. Engineers post technical updates in #incidents; customer-facing wording is drafted with Support leadership."),
        ("8. Follow-Up Action Tracking",
         "Post-mortem action items become Jira tickets with owners and due dates, reviewed in the weekly Engineering Operations Review until closed. Repeat incidents reopen the original post-mortem."),
    ],
    "Jira_Triage_Process": [
        ("6. Bug Lifecycle States",
         "Tickets move Triage → To Do → In Progress → In Review → Done. Tickets awaiting customer or vendor input sit in Blocked with a dated next-check note, never silently stale."),
        ("7. Sprint Ceremonies",
         "Planning, standups, reviews, and retrospectives run inside the 10:00 AM to 3:00 PM EST core collaboration window so distributed teammates can attend synchronously."),
        ("8. Definition of Done",
         "Done means code merged, tests passing above coverage gates, docs updated, and acceptance criteria verified by the reporter or Product. Partial credit does not close tickets."),
    ],
    "Leave_Policy": [
        ("6. Public Holidays",
         "Nexora observes standard US public holidays with a published annual calendar. Holiday cover is arranged within teams in advance; on-call rotations continue through holidays with holiday pay rules."),
        ("7. Approval Turnaround",
         "Managers respond to Workday leave requests within 2 business days. Requests outstanding beyond that escalate to the skip-level manager so plans are never blocked by silence."),
        ("8. Leave of Absence",
         "Extended medical or personal leave beyond available PTO and sick days is arranged through People Ops as an approved leave of absence, with role protection per applicable law."),
    ],
    "On-Call_Compensation": [
        ("6. Shadow Rotations",
         "Engineers in Day 31-60 of onboarding join on-call shadow rotations: they observe pages, war rooms, and handoffs without primary responsibility, preparing for full rotation membership."),
        ("7. Handoff Procedure",
         "Rotations hand off with a written sync covering active incidents, known flaky alerts, and in-flight deploys. Silent handoffs are not permitted; both engineers acknowledge in PagerDuty."),
        ("8. Secondary Escalation",
         "If the Primary does not acknowledge within 10 minutes, PagerDuty escalates to the Secondary engineer, then to the engineering manager. Gaps in coverage are a Sev3 operational issue."),
    ],
    "Product_Triage_Guide": [
        ("6. Quarterly Roadmap Planning",
         "High-RICE initiatives are committed into quarterly roadmaps with named owners and success metrics. Mid-quarter insertions require displacing lower-RICE work explicitly, never silently."),
        ("7. Success Metrics",
         "Every roadmap item defines one primary metric tied to Reach or Impact before build starts, so prioritization claims remain falsifiable after launch."),
        ("8. Sunset Process",
         "Feature removal follows the same rigor as launch: usage analysis, customer notice period, migration path, and a rollback plan, scored and triaged like any proposal."),
    ],
    "Remote_Work_Policy": [
        ("6. Remote Security Baseline",
         "Remote work requires the same controls as office work: full-disk encryption, locked screens, Zero-Trust VPN for internal systems, and no sensitive work over untrusted networks without VPN."),
        ("7. Timezone Overlap",
         "Distributed teammates outside EST arrange at least 3 hours of overlap with the 10:00 AM to 3:00 PM EST core window on team-agreed days, keeping async-first norms otherwise."),
        ("8. Onsite Gatherings",
         "Teams may expense quarterly onsites for planning and cohesion. Travel follows the Expense Policy flight, hotel, and per diem rules."),
    ],
    "Sales_Playbook": [
        ("6. Sales-to-CS Handoff",
         "Closed deals transfer with a written handoff: Metrics committed, Economic Buyer contacts, Decision Criteria agreed, open pains, and Champion introduction. No handoff, no commission release."),
        ("7. Forecast Hygiene",
         "Pipeline forecasts update weekly with evidence-linked stages. Stalled enterprise deals without Champion contact for 30 days drop a stage automatically."),
        ("8. Discount Discipline",
         "Discounts trade for something: term length, upfront payment, or reference commitments. Unilateral discounting without a give is a performance issue, not a tactic."),
    ],
    "Data_Privacy_and_GDPR": [
        ("6. Access and Portability Requests",
         "Customer data subject requests (access, portability) are fulfilled within 30 days alongside erasure requests, with identity verification before any disclosure."),
        ("7. Sub-processor Management",
         "InfoSec maintains the reviewed sub-processor list with processing purposes and regions. New sub-processors require the same security review as vendors before activation."),
        ("8. Training and Confidentiality",
         "Employees with production data access complete annual privacy training and operate under role-based confidentiality obligations. Access is reviewed quarterly and revoked on role change."),
    ],
}


def main():
    for doc in gen.COMPREHENSIVE_DOCS:
        extra = EXTRA_SECTIONS.get(doc["filename"], [])
        doc["sections"].extend(extra)
    print(f"Extended {len(gen.COMPREHENSIVE_DOCS)} docs with additive sections.")
    gen.generate_pdf_and_txt()


if __name__ == "__main__":
    main()
