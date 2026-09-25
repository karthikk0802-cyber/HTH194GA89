# Expanded static question bank — guarantees 20 unique questions per topic
# for offline 20-question quiz sessions (no Mistral key configured).
# Every item is grounded in knowledge_base/*.txt. Schema matches
# services/quiz_generator.FALLBACK_QUIZ_BANK exactly.
# Counts (added here): company_basics 16, security 16, git_workflow 16,
# tools 17, architecture 17, deployment 17, product_triage 18, sales_playbook 18.

BANK_EXTRA = {
    "company_basics": [
        {
            "question": "What is Nexora's stated mission as an enterprise-grade platform?",
            "options": ["Simplify distributed systems, adaptive learning, and intelligent automation", "Maximize quarterly advertising revenue", "Build consumer social networking apps", "Provide on-premise hardware sales"],
            "correct_answer": "Simplify distributed systems, adaptive learning, and intelligent automation",
            "learning_objective": "Know Nexora mission and platform purpose",
            "evidence_quote": "founded to simplify distributed systems, adaptive learning, and intelligent automation."
        },
        {
            "question": "Which of these is NOT one of Nexora's four core cultural pillars?",
            "options": ["Ownership", "Transparency", "Empathy", "Aggressive internal competition"],
            "correct_answer": "Aggressive internal competition",
            "learning_objective": "Recall the four cultural pillars",
            "evidence_quote": "Ownership, Transparency, Empathy, Continuous Innovation."
        },
        {
            "question": "What must a new hire accomplish within Day 1-30 of the 30-60-90 onboarding plan?",
            "options": ["Submit first peer-reviewed PR", "Lead a technical design initiative", "Present at engineering demo day", "Complete the role readiness assessment"],
            "correct_answer": "Submit first peer-reviewed PR",
            "learning_objective": "Know Day 1-30 onboarding expectations",
            "evidence_quote": "Day 1-30: Complete compliance training, environment setup, attend welcome mentor sessions, and submit first peer-reviewed PR."
        },
        {
            "question": "When do Nexora company all-hands meetings take place?",
            "options": ["Bi-weekly on Thursdays at 2:00 PM EST", "Daily at 9:00 AM EST", "Monthly on Mondays at 10:00 AM EST", "Quarterly on Fridays at 4:00 PM EST"],
            "correct_answer": "Bi-weekly on Thursdays at 2:00 PM EST",
            "learning_objective": "Know all-hands cadence and AMA format",
            "evidence_quote": "Company all-hands meetings take place bi-weekly on Thursdays at 2:00 PM EST with open AMA sessions."
        },
        {
            "question": "How long is every new employee assigned a dedicated onboarding buddy?",
            "options": ["First 90 days", "First 2 weeks", "First year", "No buddy is assigned"],
            "correct_answer": "First 90 days",
            "learning_objective": "Know onboarding buddy support window",
            "evidence_quote": "Every employee is assigned a dedicated onboarding buddy during their first 90 days."
        },
        {
            "question": "What is the minimum annual PTO Nexora recommends under its flexible policy?",
            "options": ["20 PTO days annually", "5 PTO days annually", "10 PTO days annually", "No recommendation given"],
            "correct_answer": "20 PTO days annually",
            "learning_objective": "Know PTO minimum recommendation",
            "evidence_quote": "We recommend taking a minimum of 20 PTO days annually."
        },
        {
            "question": "How many paid sick and mental health wellness days do employees receive annually?",
            "options": ["10 days, no certificate needed under 3 consecutive days", "3 days with mandatory certificate", "Unlimited without any notice", "5 days only with HR pre-approval"],
            "correct_answer": "10 days, no certificate needed under 3 consecutive days",
            "learning_objective": "Know sick and wellness leave allowance",
            "evidence_quote": "up to 10 paid sick and mental health wellness days annually without requiring medical certificate for absences under 3 consecutive days."
        },
        {
            "question": "What parental leave does Nexora offer new parents?",
            "options": ["16 weeks of 100% paid leave, eligible after 90 days", "4 weeks unpaid leave immediately", "8 weeks at 50% pay after 1 year", "No parental leave policy"],
            "correct_answer": "16 weeks of 100% paid leave, eligible after 90 days",
            "learning_objective": "Know parental leave duration and eligibility",
            "evidence_quote": "16 weeks of 100% paid parental leave for all new parents, eligible after 90 days of continuous employment."
        },
        {
            "question": "How many paid bereavement days are granted for immediate family members?",
            "options": ["Up to 5 paid days", "Up to 2 paid days", "Up to 10 paid days", "Unpaid only"],
            "correct_answer": "Up to 5 paid days",
            "learning_objective": "Know bereavement leave allowance",
            "evidence_quote": "Up to 5 paid days of bereavement leave are granted for immediate family members."
        },
        {
            "question": "What is the annual Professional Development Stipend amount?",
            "options": ["$1,500 USD", "$500 USD", "$2,500 USD", "$750 USD"],
            "correct_answer": "$1,500 USD",
            "learning_objective": "Know learning stipend for conferences and courses",
            "evidence_quote": "annual $1,500 USD Professional Development Stipend for conferences, certifications, books, and courses."
        },
        {
            "question": "What minimum internet speed must remote employees maintain?",
            "options": [">50 Mbps download / >10 Mbps upload", ">10 Mbps download / >2 Mbps upload", ">100 Mbps symmetric fiber only", "No minimum requirement"],
            "correct_answer": ">50 Mbps download / >10 Mbps upload",
            "learning_objective": "Know remote connectivity requirements",
            "evidence_quote": "reliable high-speed internet (>50 Mbps download / >10 Mbps upload)."
        },
        {
            "question": "What is the monthly coworking hot-desk subsidy limit?",
            "options": ["Up to $250 USD per month", "Up to $100 USD per month", "Up to $500 USD per month", "No coworking subsidy exists"],
            "correct_answer": "Up to $250 USD per month",
            "learning_objective": "Know coworking space subsidy rules",
            "evidence_quote": "expense up to $250 USD per month for hot-desk memberships at certified coworking spaces."
        },
        {
            "question": "Which laptop workstations does IT Ops provide?",
            "options": ["MacBook Pro or ThinkPad", "Employee must buy their own laptop", "Chromebook only", "Desktop towers only"],
            "correct_answer": "MacBook Pro or ThinkPad",
            "learning_objective": "Know company-issued hardware policy",
            "evidence_quote": "Company-issued MacBook Pro or ThinkPad workstations are provided directly by IT Ops."
        },
        {
            "question": "What does Nexora's 40-hour work week require regarding core hours?",
            "options": ["Presence during 10:00 AM to 3:00 PM EST core hours", "Fixed 9-to-5 desk presence daily", "Weekend availability every week", "No core hours presence at all"],
            "correct_answer": "Presence during 10:00 AM to 3:00 PM EST core hours",
            "learning_objective": "Understand flexible week plus core presence",
            "evidence_quote": "complete their 40-hour work week according to local preferences while maintaining presence during core hours."
        },
        {
            "question": "What happens in cases of discriminatory behavior or harassment at Nexora?",
            "options": ["Immediate disciplinary action up to termination", "Verbal reminder with no record", "Transfer to another team only", "No formal policy exists"],
            "correct_answer": "Immediate disciplinary action up to termination",
            "learning_objective": "Know anti-harassment enforcement stance",
            "evidence_quote": "Any discriminatory behavior, harassment, or retaliation will result in immediate disciplinary action up to termination."
        },
        {
            "question": "What should employees do in Day 61-90 of onboarding?",
            "options": ["Lead a design or improvement initiative and present at demo day", "Only shadow other engineers", "Take a sabbatical month", "Rotate to an unrelated department"],
            "correct_answer": "Lead a design or improvement initiative and present at demo day",
            "learning_objective": "Know Day 61-90 ownership expectations",
            "evidence_quote": "Day 61-90: Lead a technical design or operational improvement initiative, present at engineering demo day."
        },
    ],
    "security": [
        {
            "question": "Which form of two-factor authentication is prohibited at Nexora?",
            "options": ["SMS-based 2FA", "Hardware security keys", "TOTP authenticator apps", "Biometric-backed passkeys"],
            "correct_answer": "SMS-based 2FA",
            "learning_objective": "Know prohibited authentication factors",
            "evidence_quote": "SMS-based 2FA is prohibited."
        },
        {
            "question": "What encryption must laptops use for full-disk protection?",
            "options": ["FileVault / BitLocker", "No encryption required", "ZIP password archives", "ROT13 obfuscation"],
            "correct_answer": "FileVault / BitLocker",
            "learning_objective": "Know workstation encryption standards",
            "evidence_quote": "Physical laptops must use full-disk encryption (FileVault / BitLocker)."
        },
        {
            "question": "How do you lock a workstation when leaving it unattended?",
            "options": ["Win+L / Cmd+Ctrl+Q", "Close the lid only", "Unplug the monitor", "Log out of Slack only"],
            "correct_answer": "Win+L / Cmd+Ctrl+Q",
            "learning_objective": "Know manual workstation lock shortcuts",
            "evidence_quote": "workstations are locked whenever left unattended (Win+L / Cmd+Ctrl+Q)."
        },
        {
            "question": "What happens if you fail a simulated phishing drill?",
            "options": ["Complete a 30-minute refresher course within 5 business days", "Immediate termination", "Nothing happens", "Lose internet stipend for a month"],
            "correct_answer": "Complete a 30-minute refresher course within 5 business days",
            "learning_objective": "Know phishing drill remediation path",
            "evidence_quote": "Employees who fail simulated drills must complete a 30-minute refresher security course within 5 business days."
        },
        {
            "question": "What is required to access internal networks and admin dashboards?",
            "options": ["Zero-Trust VPN with device posture compliance checks", "Open public Wi-Fi connection", "Personal hotspot without VPN", "Shared team credentials"],
            "correct_answer": "Zero-Trust VPN with device posture compliance checks",
            "learning_objective": "Know Zero Trust network access rules",
            "evidence_quote": "requires connection through Nexora's Zero-Trust VPN with device posture compliance checks."
        },
        {
            "question": "How is production access granted at Nexora?",
            "options": ["Just-in-time (JIT) privilege elevation", "Permanent standing admin rights", "Shared root passwords", "No access controls"],
            "correct_answer": "Just-in-time (JIT) privilege elevation",
            "learning_objective": "Know production access elevation model",
            "evidence_quote": "Production access requires just-in-time (JIT) privilege elevation."
        },
        {
            "question": "Which regulations and controls does Nexora comply with?",
            "options": ["GDPR, CCPA, and SOC 2 Type II", "HIPAA only", "PCI-DSS only", "No formal compliance framework"],
            "correct_answer": "GDPR, CCPA, and SOC 2 Type II",
            "learning_objective": "Know compliance framework scope",
            "evidence_quote": "complies with GDPR, California Consumer Privacy Act (CCPA), and SOC 2 Type II controls."
        },
        {
            "question": "Which of these must NEVER appear in plain-text logs?",
            "options": ["Email addresses, SSNs, passwords, payment details, IP addresses", "Timestamps and log levels", "Service names and regions", "HTTP status codes"],
            "correct_answer": "Email addresses, SSNs, passwords, payment details, IP addresses",
            "learning_objective": "Know PII categories banned from logs",
            "evidence_quote": "PII such as email addresses, social security numbers, passwords, payment details, and IP addresses must NEVER be logged in plain text."
        },
        {
            "question": "Where must logs pass before ingestion into Datadog / CloudWatch?",
            "options": ["Automated masking filters", "Public paste sites", "Personal email archives", "Unencrypted USB drives"],
            "correct_answer": "Automated masking filters",
            "learning_objective": "Know log masking pipeline requirement",
            "evidence_quote": "Logs must pass through automated masking filters before ingestion into Datadog / CloudWatch."
        },
        {
            "question": "What encryption protects sensitive data in transit and at rest?",
            "options": ["TLS 1.3 in transit, AES-256 at rest", "Plain HTTP and unencrypted disks", "MD5 hashing for transport", "Base64 encoding only"],
            "correct_answer": "TLS 1.3 in transit, AES-256 at rest",
            "learning_objective": "Know encryption standards for data states",
            "evidence_quote": "All sensitive data in transit must use TLS 1.3. All data at rest must use AES-256."
        },
        {
            "question": "How are database snapshots and backups encrypted?",
            "options": ["Dedicated AWS KMS keys", "Shared public keys on GitHub", "No encryption on backups", "Plain-text S3 buckets"],
            "correct_answer": "Dedicated AWS KMS keys",
            "learning_objective": "Know backup encryption key management",
            "evidence_quote": "Database snapshots and backups must be encrypted with dedicated AWS KMS keys."
        },
        {
            "question": "Within what timeframe must Right to be Forgotten requests be executed?",
            "options": ["Within 30 days across production and backup stores", "Within 1 year", "Within 7 years", "Never — requests are ignored"],
            "correct_answer": "Within 30 days across production and backup stores",
            "learning_objective": "Know GDPR erasure SLA",
            "evidence_quote": "must be executed across all production and backup stores within 30 days of verified customer request."
        },
        {
            "question": "In which Slack channel must security anomalies also be reported?",
            "options": ["#security-alerts (private channel)", "#random", "#general", "#pets"],
            "correct_answer": "#security-alerts (private channel)",
            "learning_objective": "Know security reporting channel",
            "evidence_quote": "in the private Slack channel #security-alerts within 15 minutes of discovery."
        },
        {
            "question": "To which email must suspected breaches be reported?",
            "options": ["security@nexora.com", "support@nexora.com", "sales@nexora.com", "info@nexora.com"],
            "correct_answer": "security@nexora.com",
            "learning_objective": "Know security reporting email",
            "evidence_quote": "must be reported to security@nexora.com."
        },
        {
            "question": "How often are phishing simulations conducted?",
            "options": ["Quarterly", "Monthly", "Yearly", "Never"],
            "correct_answer": "Quarterly",
            "learning_objective": "Know phishing simulation cadence",
            "evidence_quote": "quarterly phishing simulations are conducted by the InfoSec team."
        },
        {
            "question": "Which of these is a reportable security event?",
            "options": ["Lost laptop", "Clean desk photo", "Completed training module", "Upgraded monitor"],
            "correct_answer": "Lost laptop",
            "learning_objective": "Recognize reportable physical security events",
            "evidence_quote": "leaked credential, lost laptop, or malware alert must be reported."
        },
    ],
    "git_workflow": [
        {
            "question": "What is the maximum lifespan of a feature branch at Nexora?",
            "options": ["24-48 hours", "6 months", "1 year", "No limit"],
            "correct_answer": "24-48 hours",
            "learning_objective": "Know short-lived branch rule",
            "evidence_quote": "Feature branches must be short-lived (maximum lifespan of 24-48 hours)."
        },
        {
            "question": "Which branch naming format is correct?",
            "options": ["feature/JIRA-123-short-desc", "my-stuff-final-v2", "test123", "main-copy"],
            "correct_answer": "feature/JIRA-123-short-desc",
            "learning_objective": "Apply branch naming conventions",
            "evidence_quote": "Branches must follow standard prefixes: feature/JIRA-123-short-desc, bugfix/..., hotfix/..., chore/..."
        },
        {
            "question": "Which commit message follows Conventional Commits?",
            "options": ["feat: add SSO login flow", "stuff", "fixed things friday", "UPDATE"],
            "correct_answer": "feat: add SSO login flow",
            "learning_objective": "Write Conventional Commits messages",
            "evidence_quote": "Commit messages must follow the Conventional Commits specification (feat:, fix:, docs:, refactor:, test:, chore:)."
        },
        {
            "question": "What must pass with zero errors before a PR can merge?",
            "options": ["All automated CI checks: linters, tests, security scans, build", "Only the title spellcheck", "Manager verbal approval alone", "Nothing — merge anytime"],
            "correct_answer": "All automated CI checks: linters, tests, security scans, build",
            "learning_objective": "Know CI merge gates",
            "evidence_quote": "All automated CI checks (linters, unit tests, security vulnerability scans, build verification) must pass with zero errors."
        },
        {
            "question": "Which merge strategy keeps the main log clean and linear?",
            "options": ["Squash and Merge", "Create a merge commit per commit", "Fast-forward 50 commits", "Merge without review"],
            "correct_answer": "Squash and Merge",
            "learning_objective": "Know squash merge strategy",
            "evidence_quote": "Use 'Squash and Merge' for feature branches to keep the main commit log clean and linear."
        },
        {
            "question": "What must you do on main before final merge?",
            "options": ["Rebase on main", "Delete the main branch", "Force-push to main", "Close all issues blindly"],
            "correct_answer": "Rebase on main",
            "learning_objective": "Know rebase-before-merge rule",
            "evidence_quote": "Rebase on main prior to final merge."
        },
        {
            "question": "Within what time should PRs be reviewed during core hours?",
            "options": ["Within 4 business hours", "Within 4 weeks", "Within 4 quarters", "No SLA exists"],
            "correct_answer": "Within 4 business hours",
            "learning_objective": "Know review turnaround SLA",
            "evidence_quote": "PRs should be reviewed within 4 business hours during core collaboration hours."
        },
        {
            "question": "A PR has a 600-line diff. What must the author do?",
            "options": ["Provide an architectural walkthrough or split into atomic increments", "Merge immediately without review", "Hide files from reviewers", "Mark it as documentation-only"],
            "correct_answer": "Provide an architectural walkthrough or split into atomic increments",
            "learning_objective": "Handle oversized PRs correctly",
            "evidence_quote": "If a PR is larger than 400 lines of diff, the author must provide an architectural walkthrough or split the PR."
        },
        {
            "question": "How should reviewers mark non-blocking suggestions?",
            "options": ["Prefix with 'nit: ' or 'suggestion: '", "Reject the PR outright", "DM the author privately only", "Edit code silently without comment"],
            "correct_answer": "Prefix with 'nit: ' or 'suggestion: '",
            "learning_objective": "Distinguish blocking vs non-blocking feedback",
            "evidence_quote": "non-blocking suggestions (prefix with 'nit: ' or 'suggestion: ')."
        },
        {
            "question": "Which tools handle code styling so reviewers don't have to?",
            "options": ["Prettier, Black, GoFmt", "Microsoft Paint", "WinZip", "Notepad"],
            "correct_answer": "Prettier, Black, GoFmt",
            "learning_objective": "Know automated formatter standards",
            "evidence_quote": "Automated formatters (Prettier, Black, GoFmt) handle styling."
        },
        {
            "question": "What test evidence must accompany business-logic PRs?",
            "options": ["Automated unit tests, plus integration tests where appropriate", "No tests needed", "Screenshots of passing local runs only", "A promise to test later"],
            "correct_answer": "Automated unit tests, plus integration tests where appropriate",
            "learning_objective": "Know PR testing requirements",
            "evidence_quote": "Every PR modifying business logic must include automated unit tests, and where appropriate, integration tests."
        },
        {
            "question": "What must happen to flaky tests?",
            "options": ["Quarantined and resolved immediately", "Ignored forever", "Deleted without investigation", "Blamed on CI"],
            "correct_answer": "Quarantined and resolved immediately",
            "learning_objective": "Handle flaky tests per policy",
            "evidence_quote": "Flaky tests must be quarantined and resolved immediately."
        },
        {
            "question": "What do pre-commit hooks run before local commits?",
            "options": ["Linter checks, GPG sign validation, TruffleHog secret scans", "Video games", "Music playlists", "Nothing at all"],
            "correct_answer": "Linter checks, GPG sign validation, TruffleHog secret scans",
            "learning_objective": "Know pre-commit hook checks",
            "evidence_quote": "configure 'pre-commit' hooks to run linter checks, GPG sign validation, and secret detection scans (TruffleHog)."
        },
        {
            "question": "Which prefix is used for emergency production fix branches?",
            "options": ["hotfix/JIRA-123-short-desc", "yolo/", "temp/", "final-final/"],
            "correct_answer": "hotfix/JIRA-123-short-desc",
            "learning_objective": "Use hotfix branch naming",
            "evidence_quote": "hotfix/JIRA-123-short-desc."
        },
        {
            "question": "From which branch must feature branches be created?",
            "options": ["Directly from 'main'", "From a teammate's laptop", "From last year's release tag", "From an unreviewed fork"],
            "correct_answer": "Directly from 'main'",
            "learning_objective": "Know trunk branching origin",
            "evidence_quote": "branched directly from 'main'."
        },
        {
            "question": "What do code reviews verify beyond correctness?",
            "options": ["Readability, architectural compliance, security, and test coverage", "Author's job title", "Length of variable names only", "Number of emojis in comments"],
            "correct_answer": "Readability, architectural compliance, security, and test coverage",
            "learning_objective": "Know review objective dimensions",
            "evidence_quote": "Code reviews ensure correctness, readability, architectural compliance, security, and test coverage."
        },
    ],
    "tools": [
        {
            "question": "What is email reserved for at Nexora?",
            "options": ["External vendors, formal HR announcements, legal communication", "All engineering discussions", "Daily standups", "Code reviews"],
            "correct_answer": "External vendors, formal HR announcements, legal communication",
            "learning_objective": "Know email usage boundaries",
            "evidence_quote": "Email: Reserved for external vendors, formal HR announcements, and legal communication."
        },
        {
            "question": "What is the video preference for standups on Zoom / Google Meet?",
            "options": ["Video-on preference during standups", "Cameras permanently banned", "Audio-only always", "No meetings allowed"],
            "correct_answer": "Video-on preference during standups",
            "learning_objective": "Know synchronous meeting norms",
            "evidence_quote": "Used for synchronous meetings with video-on preference during standups."
        },
        {
            "question": "What is the single source of truth for RFCs and specs?",
            "options": ["Notion / Confluence", "Whiteboard photos", "DM threads", "Sticky notes"],
            "correct_answer": "Notion / Confluence",
            "learning_objective": "Know documentation source of truth",
            "evidence_quote": "Notion / Confluence: Single source of truth for documentation, RFCs, and engineering specifications."
        },
        {
            "question": "When should you use Slack DMs instead of public channels?",
            "options": ["1-on-1s and private feedback only", "All architecture debates", "Incident coordination", "Release announcements"],
            "correct_answer": "1-on-1s and private feedback only",
            "learning_objective": "Know DM vs public channel norms",
            "evidence_quote": "Use public channels by default; reserve DMs for 1-on-1s and private feedback."
        },
        {
            "question": "What Slack practice keeps channels readable?",
            "options": ["Always use message threads", "Posting in ALL CAPS", "One giant channel for everything", "@channel for every message"],
            "correct_answer": "Always use message threads",
            "learning_objective": "Apply Slack thread etiquette",
            "evidence_quote": "Always use message threads to keep channels readable."
        },
        {
            "question": "What do Slack status indicators communicate?",
            "options": ["Availability expectations like Vacation or Deep Work", "Salary bands", "Performance ratings", "Office seating charts"],
            "correct_answer": "Availability expectations like Vacation or Deep Work",
            "learning_objective": "Use Slack status indicators",
            "evidence_quote": "Use status indicators (Vacation, Deep Work, Lunch) to manage availability expectations."
        },
        {
            "question": "How do engineers spin up local dependencies?",
            "options": ["Docker Desktop or OrbStack via 'docker-compose up -d'", "Manual production database dumps", "Shared staging credentials", "FTP uploads"],
            "correct_answer": "Docker Desktop or OrbStack via 'docker-compose up -d'",
            "learning_objective": "Know local environment bootstrap",
            "evidence_quote": "spin up local database, cache, and service dependencies via 'docker-compose up -d'."
        },
        {
            "question": "Which package managers are standard per language?",
            "options": ["Node: pnpm/npm, Go: modules, Python: uv/pip", "Only manual tarballs", "Copy-paste from StackOverflow", "Emailing zip files"],
            "correct_answer": "Node: pnpm/npm, Go: modules, Python: uv/pip",
            "learning_objective": "Know standard package managers",
            "evidence_quote": "Standard package managers are Node (pnpm / npm), Go (go modules), and Python (uv / pip)."
        },
        {
            "question": "Where must local development secrets never appear?",
            "options": ["Committed repos or shared in Slack", "HashiCorp Vault", "1Password plugins", "Environment variables"],
            "correct_answer": "Committed repos or shared in Slack",
            "learning_objective": "Know secrets handling prohibitions",
            "evidence_quote": "must never be committed to repositories or shared in Slack."
        },
        {
            "question": "Within how many days must Expensify receipts be submitted?",
            "options": ["Within 30 days of transaction", "Within 1 year", "Within 5 years", "Never required"],
            "correct_answer": "Within 30 days of transaction",
            "learning_objective": "Know expense submission deadline",
            "evidence_quote": "Receipts must be submitted via Expensify within 30 days of the transaction date."
        },
        {
            "question": "What happens to undocumented expenses over $25?",
            "options": ["They will not be reimbursed", "Auto-approved double", "Paid in cash under the table", "Forwarded to sales"],
            "correct_answer": "They will not be reimbursed",
            "learning_objective": "Know undocumented expense consequence",
            "evidence_quote": "Undocumented expenses over $25 will not be reimbursed."
        },
        {
            "question": "What meal split makes up the $75 travel per diem?",
            "options": ["$20 breakfast, $25 lunch, $30 dinner", "$75 for snacks only", "$25 × 3 identical meals", "$75 alcohol allowance"],
            "correct_answer": "$20 breakfast, $25 lunch, $30 dinner",
            "learning_objective": "Know per diem meal breakdown",
            "evidence_quote": "$75 USD per day ($20 breakfast, $25 lunch, $30 dinner)."
        },
        {
            "question": "When is business class permitted for flights?",
            "options": ["International flights over 8 hours with VP pre-approval", "All domestic hops", "Whenever preferred", "Never permitted"],
            "correct_answer": "International flights over 8 hours with VP pre-approval",
            "learning_objective": "Know flight class policy",
            "evidence_quote": "Business class is permitted for international flights over 8 continuous flight hours with VP pre-approval."
        },
        {
            "question": "What are the hotel nightly rate caps?",
            "options": ["$250 standard cities, $350 tier-1 metros", "$1000 anywhere", "$50 flat worldwide", "No cap exists"],
            "correct_answer": "$250 standard cities, $350 tier-1 metros",
            "learning_objective": "Know hotel rate caps",
            "evidence_quote": "should not exceed $250/night in standard cities or $350/night in tier-1 metro areas."
        },
        {
            "question": "How are PagerDuty on-call schedules published?",
            "options": ["6 weeks in advance via PagerDuty", "Day-of via sticky note", "Never published", "By word of mouth"],
            "correct_answer": "6 weeks in advance via PagerDuty",
            "learning_objective": "Know on-call schedule visibility",
            "evidence_quote": "Schedules are published 6 weeks in advance via PagerDuty."
        },
        {
            "question": "What is the on-call rotation structure?",
            "options": ["7-day weekly rotation with Primary and Secondary engineer", "Permanent single on-call hero", "Monthly lottery draw", "No rotation exists"],
            "correct_answer": "7-day weekly rotation with Primary and Secondary engineer",
            "learning_objective": "Know on-call rotation model",
            "evidence_quote": "7-day weekly on-call rotation with a Primary and Secondary engineer."
        },
        {
            "question": "What recovery applies after a night Sev1/Sev2 page (10 PM–7 AM)?",
            "options": ["Morning off up to 4 hours paid recovery", "Double shift next day", "No recovery time", "Unpaid leave deduction"],
            "correct_answer": "Morning off up to 4 hours paid recovery",
            "learning_objective": "Know night-page recovery entitlement",
            "evidence_quote": "entitled to take the morning off (up to 4 hours) as paid recovery time."
        },
    ],
    "architecture": [
        {
            "question": "Which language powers Nexora ML and analytics pipelines?",
            "options": ["Python 3.11+", "COBOL", "Visual Basic", "Assembly"],
            "correct_answer": "Python 3.11+",
            "learning_objective": "Know ML pipeline language standard",
            "evidence_quote": "machine learning & analytics pipelines in Python 3.11+."
        },
        {
            "question": "What stack builds Nexora frontend web applications?",
            "options": ["React 19 / TypeScript with Vite", "jQuery with tables", "Flash applets", "Server-rendered Perl"],
            "correct_answer": "React 19 / TypeScript with Vite",
            "learning_objective": "Know frontend stack standard",
            "evidence_quote": "frontend web applications in React 19 / TypeScript with Vite."
        },
        {
            "question": "How does frontend-to-backend communication happen?",
            "options": ["GraphQL and REST over HTTPS with OpenAPI/JSON schema validation", "Plain-text FTP", "Carrier pigeons", "Shared Excel files"],
            "correct_answer": "GraphQL and REST over HTTPS with OpenAPI/JSON schema validation",
            "learning_objective": "Know external API communication standards",
            "evidence_quote": "External and frontend-to-backend communication uses GraphQL and REST over HTTPS with strict OpenAPI / JSON schema validation."
        },
        {
            "question": "What handles asynchronous event-driven workflows between services?",
            "options": ["Kafka message streams", "Fax machines", "USB sneakernet", "Smoke signals"],
            "correct_answer": "Kafka message streams",
            "learning_objective": "Know async messaging backbone",
            "evidence_quote": "Kafka message streams for asynchronous event-driven workflows."
        },
        {
            "question": "What serialization does inter-service gRPC use?",
            "options": ["Protocol Buffers", "YAML over telnet", "Pickle over email", "CSV attachments"],
            "correct_answer": "Protocol Buffers",
            "learning_objective": "Know gRPC serialization format",
            "evidence_quote": "Inter-service backend communication uses gRPC with Protocol Buffers."
        },
        {
            "question": "How does PostgreSQL scale reads at Nexora?",
            "options": ["Read replicas with PgBouncer connection pooling", "Single laptop database", "SQLite on NFS", "No scaling strategy"],
            "correct_answer": "Read replicas with PgBouncer connection pooling",
            "learning_objective": "Know transactional scaling pattern",
            "evidence_quote": "PostgreSQL 16 with read replicas and connection pooling via PgBouncer."
        },
        {
            "question": "How are Redis caching layers configured?",
            "options": ["Redis clusters with defined TTL policies", "Single Redis without persistence", "Memcached on developer laptops", "No caching layer"],
            "correct_answer": "Redis clusters with defined TTL policies",
            "learning_objective": "Know caching topology",
            "evidence_quote": "Caching layers utilize Redis clusters with defined TTL policies."
        },
        {
            "question": "How are all Nexora workloads packaged and run?",
            "options": ["Docker containers on Kubernetes (EKS/GKE)", "Bare-metal pets with manual SSH", "VirtualBox VMs on laptops", "Mainframe batch jobs"],
            "correct_answer": "Docker containers on Kubernetes (EKS/GKE)",
            "learning_objective": "Know container orchestration platform",
            "evidence_quote": "All workloads run as Docker containers orchestrated via Kubernetes (EKS/GKE)."
        },
        {
            "question": "How is infrastructure provisioned?",
            "options": ["Strictly via Terraform (Infrastructure as Code)", "ClickOps in the console", "Tickets to a colo provider", "Whiteboard drawings"],
            "correct_answer": "Strictly via Terraform (Infrastructure as Code)",
            "learning_objective": "Know IaC provisioning mandate",
            "evidence_quote": "Infrastructure is provisioned strictly via Terraform (Infrastructure as Code)."
        },
        {
            "question": "What architectural paradigm do Nexora systems follow?",
            "options": ["Decoupled microservices architecture", "Single monolithic mainframe", "Peer-to-peer Napster clone", "Blockchain everything"],
            "correct_answer": "Decoupled microservices architecture",
            "learning_objective": "Know architectural paradigm",
            "evidence_quote": "Nexora systems follow a decoupled, microservices architecture."
        },
        {
            "question": "Why is Go standardized for core backend services?",
            "options": ["High-throughput concurrency", "Nostalgia for the 1970s", "Smallest logo", "Alphabetical order"],
            "correct_answer": "High-throughput concurrency",
            "learning_objective": "Know Go selection rationale",
            "evidence_quote": "Core backend services are written in Go for high-throughput concurrency."
        },
        {
            "question": "Which database serves vector search workloads?",
            "options": ["ChromaDB / pgvector", "Microsoft Access", "Flat CSV files", "Etch-a-Sketch"],
            "correct_answer": "ChromaDB / pgvector",
            "learning_objective": "Know vector search platform",
            "evidence_quote": "Vector search is powered by ChromaDB / pgvector."
        },
        {
            "question": "What validates external API payloads?",
            "options": ["Strict OpenAPI / JSON schema validation", "Hope and prayers", "Client-side alerts only", "No validation performed"],
            "correct_answer": "Strict OpenAPI / JSON schema validation",
            "learning_objective": "Know API validation requirement",
            "evidence_quote": "with strict OpenAPI / JSON schema validation."
        },
        {
            "question": "Which two container platforms orchestrate workloads?",
            "options": ["EKS/GKE", "Docker Swarm on a Raspberry Pi", "Nomad on a toaster", "No orchestration"],
            "correct_answer": "EKS/GKE",
            "learning_objective": "Know Kubernetes distributions",
            "evidence_quote": "orchestrated via Kubernetes (EKS/GKE)."
        },
        {
            "question": "What distinguishes frontend-to-backend from inter-service communication?",
            "options": ["GraphQL/REST externally vs gRPC+Kafka internally", "Both use fax", "Both use shared databases", "No distinction exists"],
            "correct_answer": "GraphQL/REST externally vs gRPC+Kafka internally",
            "learning_objective": "Contrast communication planes",
            "evidence_quote": "External communication uses GraphQL and REST. Inter-service backend communication uses gRPC with Protocol Buffers and Kafka."
        },
        {
            "question": "What pooling middleware fronts PostgreSQL?",
            "options": ["PgBouncer", "A garden hose", "No pooling", "Excel ODBC links"],
            "correct_answer": "PgBouncer",
            "learning_objective": "Know connection pooling layer",
            "evidence_quote": "connection pooling via PgBouncer."
        },
        {
            "question": "Which frontend build tool is standard?",
            "options": ["Vite", "Grunt 2012", "Manual script tags", "Dreamweaver"],
            "correct_answer": "Vite",
            "learning_objective": "Know frontend build tooling",
            "evidence_quote": "React 19 / TypeScript with Vite."
        },
    ],
    "deployment": [
        {
            "question": "Which deployments are strictly prohibited?",
            "options": ["Friday, weekend, and after-3:00 PM EST deployments", "Tuesday morning deployments", "Canary deployments", "Rollback executions"],
            "correct_answer": "Friday, weekend, and after-3:00 PM EST deployments",
            "learning_objective": "Know deployment blackout periods",
            "evidence_quote": "Friday deployments, weekend deployments, and deployments after 3:00 PM EST are strictly prohibited."
        },
        {
            "question": "What is the canary traffic progression?",
            "options": ["5% for 15 min → 25% for 30 min → 100%", "100% immediately", "0% forever", "Random percentages"],
            "correct_answer": "5% for 15 min → 25% for 30 min → 100%",
            "learning_objective": "Know canary stage schedule",
            "evidence_quote": "canary progression: 5% traffic for 15 minutes -> 25% for 30 minutes -> 100% full rollout."
        },
        {
            "question": "Which signals do automated canary health checks monitor?",
            "options": ["HTTP 5xx rates, p99 latency, CPU/memory saturation", "Office temperature", "Coffee consumption", "Parking availability"],
            "correct_answer": "HTTP 5xx rates, p99 latency, CPU/memory saturation",
            "learning_objective": "Know canary health signals",
            "evidence_quote": "monitor HTTP 5xx error rates, latency p99, and CPU/memory saturation."
        },
        {
            "question": "What latency trigger fires automated rollback?",
            "options": ["p99 latency increase >25%", "p99 decrease of 1%", "Any latency change", "Latency is not monitored"],
            "correct_answer": "p99 latency increase >25%",
            "learning_objective": "Know latency rollback threshold",
            "evidence_quote": "p99 latency increases by >25% during canary rollout."
        },
        {
            "question": "Where must hotfix approvals be recorded?",
            "options": ["#hotfix-approvals channel with written VP/Director approval", "Verbal hallway approval", "No record needed", "Personal diary"],
            "correct_answer": "#hotfix-approvals channel with written VP/Director approval",
            "learning_objective": "Know hotfix approval channel",
            "evidence_quote": "require explicit written approval from the Engineering VP or Director of Infrastructure in the #hotfix-approvals channel."
        },
        {
            "question": "Who can approve an emergency out-of-band hotfix?",
            "options": ["Engineering VP or Director of Infrastructure", "Any intern", "External vendor", "Nobody — hotfixes banned"],
            "correct_answer": "Engineering VP or Director of Infrastructure",
            "learning_objective": "Know hotfix authority matrix",
            "evidence_quote": "explicit written approval from the Engineering VP or Director of Infrastructure."
        },
        {
            "question": "What is the Sev1 SLA response time?",
            "options": ["< 15 minutes", "< 4 hours", "Next quarter", "No SLA"],
            "correct_answer": "< 15 minutes",
            "learning_objective": "Know Sev1 response SLA",
            "evidence_quote": "Sev1 (Critical): SLA response: < 15 minutes."
        },
        {
            "question": "What is the Sev2 SLA response time?",
            "options": ["< 30 minutes", "< 1 week", "Next sprint", "Best effort"],
            "correct_answer": "< 30 minutes",
            "learning_objective": "Know Sev2 response SLA",
            "evidence_quote": "Sev2 (Major): SLA response: < 30 minutes."
        },
        {
            "question": "What is the Sev3 SLA response time?",
            "options": ["< 2 hours", "< 2 months", "Next year", "Whenever"],
            "correct_answer": "< 2 hours",
            "learning_objective": "Know Sev3 response SLA",
            "evidence_quote": "Sev3 (Moderate): SLA response: < 2 hours."
        },
        {
            "question": "Who assumes the Incident Commander role?",
            "options": ["Primary On-Call Engineer", "The intern on shadow rotation", "A random volunteer", "The CEO always"],
            "correct_answer": "Primary On-Call Engineer",
            "learning_objective": "Know IC assignment rule",
            "evidence_quote": "The Primary On-Call assumes the role of Incident Commander (IC)."
        },
        {
            "question": "Where does live incident coordination happen?",
            "options": ["#incidents Slack war room plus Zoom incident bridge", "Public Twitter thread", "Email chain", "Hallway conversations"],
            "correct_answer": "#incidents Slack war room plus Zoom incident bridge",
            "learning_objective": "Know incident coordination venues",
            "evidence_quote": "All live coordination takes place in the dedicated Slack war room '#incidents' and an active Zoom incident bridge."
        },
        {
            "question": "When must the first status-page update post for Sev1?",
            "options": ["Within 20 minutes of declaration, then every 30 minutes", "After full resolution only", "Never required", "Once per quarter"],
            "correct_answer": "Within 20 minutes of declaration, then every 30 minutes",
            "learning_objective": "Know status-page update cadence",
            "evidence_quote": "must post an initial customer-facing update within 20 minutes of Sev1 declaration and provide updates every 30 minutes."
        },
        {
            "question": "When is a blameless post-mortem due after Sev1/Sev2?",
            "options": ["Drafted within 48 hours", "Drafted within 48 weeks", "Optional after 1 year", "Never required"],
            "correct_answer": "Drafted within 48 hours",
            "learning_objective": "Know post-mortem deadline",
            "evidence_quote": "a blameless post-mortem document must be drafted within 48 hours."
        },
        {
            "question": "What defines a Sev1 incident?",
            "options": ["Total outage, critical data loss, or breach affecting >10% of customers", "A typo in a tooltip", "Slow CI on Fridays", "A full inbox"],
            "correct_answer": "Total outage, critical data loss, or breach affecting >10% of customers",
            "learning_objective": "Recognize Sev1 criteria",
            "evidence_quote": "Sev1 (Critical): Total service outage, critical data loss, or active security breach affecting >10% of customers."
        },
        {
            "question": "What is the on-call stipend per completed week?",
            "options": ["$500 USD on the subsequent payroll", "$5 USD in stickers", "$50,000 USD cash", "No stipend"],
            "correct_answer": "$500 USD on the subsequent payroll",
            "learning_objective": "Know on-call compensation",
            "evidence_quote": "Engineers receive an additional $500 USD stipend per completed on-call week."
        },
        {
            "question": "What production deployment window is standard?",
            "options": ["Tuesdays and Thursdays 10:00 AM–2:00 PM EST", "Midnight weekends", "Friday happy hour", "Anytime without notice"],
            "correct_answer": "Tuesdays and Thursdays 10:00 AM–2:00 PM EST",
            "learning_objective": "Recall standard deploy window",
            "evidence_quote": "Standard production deployments take place on Tuesdays and Thursdays between 10:00 AM and 2:00 PM EST."
        },
        {
            "question": "What does the CD pipeline roll back to on canary failure?",
            "options": ["Previous stable release artifact via 1-click rollback", "A random old build", "An empty deployment", "Manual server rebuilds"],
            "correct_answer": "Previous stable release artifact via 1-click rollback",
            "learning_objective": "Know rollback target",
            "evidence_quote": "immediately triggers a 1-click rollback to the previous stable release artifact."
        },
    ],
    "product_triage": [
        {
            "question": "What is the RICE formula?",
            "options": ["(Reach × Impact × Confidence) / Effort", "Reach + Impact + Confidence + Effort", "Revenue − Cost", "Random lottery ranking"],
            "correct_answer": "(Reach × Impact × Confidence) / Effort",
            "learning_objective": "Apply the RICE scoring formula",
            "evidence_quote": "prioritized using the RICE framework: (Reach × Impact × Confidence) / Effort."
        },
        {
            "question": "Where do high-RICE initiatives get slotted?",
            "options": ["Quarterly product roadmaps", "Friday deploy queue", "Trash folder", "Personal notebooks"],
            "correct_answer": "Quarterly product roadmaps",
            "learning_objective": "Know roadmap slotting for top initiatives",
            "evidence_quote": "High-RICE initiatives are slotted into quarterly product roadmaps."
        },
        {
            "question": "Where are customer feature requests aggregated?",
            "options": ["Productboard, from Zendesk, Gong, and sales calls", "Spreadsheet on a laptop", "Napkins", "Nowhere"],
            "correct_answer": "Productboard, from Zendesk, Gong, and sales calls",
            "learning_objective": "Know feedback aggregation pipeline",
            "evidence_quote": "Customer feature requests from Zendesk, Gong, and sales calls are aggregated in Productboard."
        },
        {
            "question": "How often are aggregated requests reviewed with engineering leads?",
            "options": ["Bi-weekly", "Yearly", "Never", "Every 5 years"],
            "correct_answer": "Bi-weekly",
            "learning_objective": "Know feedback review cadence",
            "evidence_quote": "reviewed bi-weekly with engineering leads."
        },
        {
            "question": "Which item is REQUIRED in every Jira bug ticket?",
            "options": ["Step-by-step reproduction steps", "Author's favorite color", "Lunch order", "Horoscope"],
            "correct_answer": "Step-by-step reproduction steps",
            "learning_objective": "Know bug ticket required fields",
            "evidence_quote": "Every bug ticket must include: summary, reproduction steps, expected/actual behavior, environment details, Sentry trace or screenshot."
        },
        {
            "question": "Which trace evidence belongs in a bug ticket?",
            "options": ["Sentry error trace or screenshot", "Movie quotes", "Memes", "Blank attachments"],
            "correct_answer": "Sentry error trace or screenshot",
            "learning_objective": "Know diagnostic evidence standards",
            "evidence_quote": "Sentry error trace or screenshot."
        },
        {
            "question": "What Fibonacci values size user stories?",
            "options": ["1, 2, 3, 5, 8", "10, 20, 30", "100, 200", "Any even number"],
            "correct_answer": "1, 2, 3, 5, 8",
            "learning_objective": "Know story-point scale",
            "evidence_quote": "User stories must be sized in Fibonacci story points (1, 2, 3, 5, 8)."
        },
        {
            "question": "What must happen to stories larger than 8 points?",
            "options": ["Broken down into smaller stories", "Auto-approved", "Assigned to interns only", "Closed as wontfix"],
            "correct_answer": "Broken down into smaller stories",
            "learning_objective": "Enforce story splitting rule",
            "evidence_quote": "Stories larger than 8 points must be broken down."
        },
        {
            "question": "How often do PMs and eng leads triage incoming tickets?",
            "options": ["Daily", "Monthly", "Once a decade", "Never"],
            "correct_answer": "Daily",
            "learning_objective": "Know triage cadence",
            "evidence_quote": "triage incoming tickets daily."
        },
        {
            "question": "How are P0 blockers handled?",
            "options": ["Assigned immediately to current sprint", "Backlogged for next quarter", "Ignored", "Deleted"],
            "correct_answer": "Assigned immediately to current sprint",
            "learning_objective": "Know P0 handling rule",
            "evidence_quote": "Blockers (P0) are assigned immediately to current sprint."
        },
        {
            "question": "How are P1 bugs scheduled?",
            "options": ["Within 24 hours", "Within 24 months", "Sometime eventually", "Never scheduled"],
            "correct_answer": "Within 24 hours",
            "learning_objective": "Know P1 scheduling SLA",
            "evidence_quote": "P1 bugs are scheduled within 24 hours."
        },
        {
            "question": "In RICE, what does a higher Effort do to priority?",
            "options": ["Lowers it (Effort is the denominator)", "Raises it", "Nothing at all", "Deletes the feature"],
            "correct_answer": "Lowers it (Effort is the denominator)",
            "learning_objective": "Interpret Effort in RICE",
            "evidence_quote": "(Reach × Impact × Confidence) / Effort."
        },
        {
            "question": "What does the 'C' in RICE stand for?",
            "options": ["Confidence", "Cost", "Calendar", "Coffee"],
            "correct_answer": "Confidence",
            "learning_objective": "Recall RICE components",
            "evidence_quote": "RICE framework: (Reach × Impact × Confidence) / Effort."
        },
        {
            "question": "A ticket lacks environment details. Is it complete?",
            "options": ["No — environment/browser details are required", "Yes, ship it", "Only on Fridays", "Depends on mood"],
            "correct_answer": "No — environment/browser details are required",
            "learning_objective": "Enforce ticket completeness",
            "evidence_quote": "Environment/Browser details."
        },
        {
            "question": "Who reviews aggregated feedback with engineering leads?",
            "options": ["Product team bi-weekly", "Nobody", "External auditors only", "Customers directly in prod"],
            "correct_answer": "Product team bi-weekly",
            "learning_objective": "Know review participants",
            "evidence_quote": "reviewed bi-weekly with engineering leads."
        },
        {
            "question": "What sources feed Productboard aggregation?",
            "options": ["Zendesk, Gong, and sales calls", "Dreams and guesses", "Competitor press releases", "Random tweets"],
            "correct_answer": "Zendesk, Gong, and sales calls",
            "learning_objective": "Know feedback sources",
            "evidence_quote": "from Zendesk, Gong, and sales calls are aggregated in Productboard."
        },
        {
            "question": "An epic spans 6 sprints. Is it correctly scoped?",
            "options": ["No — epics max out at 2 sprints (4 weeks)", "Yes, epics are unlimited", "Only if labeled 'epic'", "Scope does not matter"],
            "correct_answer": "No — epics max out at 2 sprints (4 weeks)",
            "learning_objective": "Enforce epic sizing boundary",
            "evidence_quote": "Epics must be scoped to complete within a maximum of 2 agile sprints (4 weeks)."
        },
        {
            "question": "Which behavior pair is required in a bug ticket?",
            "options": ["Expected behavior and actual behavior", "Favorite behavior and lucky behavior", "No behavior needed", "Behavior of competitors"],
            "correct_answer": "Expected behavior and actual behavior",
            "learning_objective": "Know behavior documentation rule",
            "evidence_quote": "Expected behavior, Actual behavior."
        },
    ],
    "sales_playbook": [
        {
            "question": "What does the first 'M' in MEDDIC stand for?",
            "options": ["Metrics", "Money", "Meetings", "Magic"],
            "correct_answer": "Metrics",
            "learning_objective": "Recall MEDDIC components",
            "evidence_quote": "MEDDIC: Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, and Champion."
        },
        {
            "question": "Who is the Economic Buyer?",
            "options": ["The person with budget authority to purchase", "The office manager ordering snacks", "A competitor's CEO", "The intern cohort"],
            "correct_answer": "The person with budget authority to purchase",
            "learning_objective": "Distinguish Economic Buyer role",
            "evidence_quote": "Economic Buyer."
        },
        {
            "question": "What is the Champion's role in MEDDIC?",
            "options": ["Internal advocate selling Nexora inside the account", "External auditor", "Lowest-price seeker", "Contract blocker"],
            "correct_answer": "Internal advocate selling Nexora inside the account",
            "learning_objective": "Understand Champion function",
            "evidence_quote": "Champion."
        },
        {
            "question": "What engineering metric anchors Nexora's value proposition?",
            "options": ["60% reduction in engineering ramp-up time", "10x coffee consumption", "Zero meetings forever", "Free laptops for everyone"],
            "correct_answer": "60% reduction in engineering ramp-up time",
            "learning_objective": "Quote the headline value metric",
            "evidence_quote": "reducing engineering ramp-up time by 60%."
        },
        {
            "question": "Which three pillars form the value proposition?",
            "options": ["Developer productivity, compliance governance, AI-assisted onboarding", "Free food, games, travel", "Lowest price, no support, no docs", "Hardware resale"],
            "correct_answer": "Developer productivity, compliance governance, AI-assisted onboarding",
            "learning_objective": "Recite value proposition pillars",
            "evidence_quote": "unified developer productivity, automated compliance governance, and AI-assisted onboarding."
        },
        {
            "question": "Who approves discounts up to 10%?",
            "options": ["Account Executives", "The customer", "Nobody", "The intern"],
            "correct_answer": "Account Executives",
            "learning_objective": "Know AE discount authority",
            "evidence_quote": "Discounts up to 10% can be approved by Account Executives."
        },
        {
            "question": "Who must sign off discounts of 11-20%?",
            "options": ["Sales Director", "Account Executive alone", "Engineering intern", "No approval needed"],
            "correct_answer": "Sales Director",
            "learning_objective": "Know director approval band",
            "evidence_quote": "11-20% requires Sales Director sign-off."
        },
        {
            "question": "A deal needs a 15% discount. Whose approval is required?",
            "options": ["Sales Director", "Account Executive self-approval", "CFO only", "No one"],
            "correct_answer": "Sales Director",
            "learning_objective": "Apply discount matrix to a 15% case",
            "evidence_quote": "11-20% requires Sales Director sign-off."
        },
        {
            "question": "A deal needs a 25% discount. Whose approval is required?",
            "options": ["VP of Sales and CFO", "Account Executive alone", "Sales Engineer", "No approval"],
            "correct_answer": "VP of Sales and CFO",
            "learning_objective": "Apply discount matrix above 20%",
            "evidence_quote": "discounts exceeding 20% require VP of Sales and CFO approval."
        },
        {
            "question": "What does 'Identify Pain' mean in MEDDIC?",
            "options": ["Uncover the customer's business problem Nexora solves", "Complain about competitors", "List office grievances", "Ignore customer needs"],
            "correct_answer": "Uncover the customer's business problem Nexora solves",
            "learning_objective": "Interpret Identify Pain",
            "evidence_quote": "Identify Pain."
        },
        {
            "question": "What is the difference between Decision Criteria and Decision Process?",
            "options": ["Criteria = what they evaluate; Process = how they decide and who is involved", "They are identical", "Neither matters", "Both mean discount size"],
            "correct_answer": "Criteria = what they evaluate; Process = how they decide and who is involved",
            "learning_objective": "Distinguish Criteria vs Process",
            "evidence_quote": "Decision Criteria, Decision Process."
        },
        {
            "question": "Why must reps qualify with MEDDIC instead of cold-call scripts?",
            "options": ["Enterprise deals require structured qualification of buyer, pain, and process", "Scripts are faster", "MEDDIC is optional", "Cold calls close themselves"],
            "correct_answer": "Enterprise deals require structured qualification of buyer, pain, and process",
            "learning_objective": "Justify structured qualification",
            "evidence_quote": "Sales reps qualify enterprise opportunities using MEDDIC."
        },
        {
            "question": "A rep offers 8% without approval. Is this compliant?",
            "options": ["Yes — within AE authority up to 10%", "No — all discounts need CFO sign-off", "Only on Tuesdays", "Only for new logos"],
            "correct_answer": "Yes — within AE authority up to 10%",
            "learning_objective": "Validate AE-band discount",
            "evidence_quote": "Discounts up to 10% can be approved by Account Executives."
        },
        {
            "question": "What does Metrics quantify in a MEDDIC deal?",
            "options": ["Measurable business outcome the customer gains", "Rep's step count", "Office square footage", "Slide count"],
            "correct_answer": "Measurable business outcome the customer gains",
            "learning_objective": "Interpret Metrics in MEDDIC",
            "evidence_quote": "Metrics."
        },
        {
            "question": "Which approval pairs govern the top discount band?",
            "options": ["VP of Sales plus CFO", "Two interns", "Customer plus vendor", "Nobody"],
            "correct_answer": "VP of Sales plus CFO",
            "learning_objective": "Recall top-band approvers",
            "evidence_quote": "VP of Sales and CFO approval."
        },
        {
            "question": "What target buyer does the playbook address?",
            "options": ["Enterprise teams", "Individual hobbyists", "K-12 students", "Retirees"],
            "correct_answer": "Enterprise teams",
            "learning_objective": "Know target buyer segment",
            "evidence_quote": "Sales reps qualify enterprise opportunities."
        },
        {
            "question": "Which framework is standard for Nexora sellers?",
            "options": ["MEDDIC", "Cold Calling script", "Ouija board", "Coin flip"],
            "correct_answer": "MEDDIC",
            "learning_objective": "Name the standard framework",
            "evidence_quote": "qualify enterprise opportunities using MEDDIC."
        },
        {
            "question": "A champion goes quiet mid-deal. What is the MEDDIC risk?",
            "options": ["Loss of internal advocacy needed to advance Decision Process", "No impact at all", "Automatic discount approval", "Faster close"],
            "correct_answer": "Loss of internal advocacy needed to advance Decision Process",
            "learning_objective": "Assess champion risk",
            "evidence_quote": "Champion."
        },
    ],
}


def get_topic_bank(topic_key: str):
    """Full static bank for a topic key (base bank merged in by caller)."""
    return list(BANK_EXTRA.get(topic_key, []))
