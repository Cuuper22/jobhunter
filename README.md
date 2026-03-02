# jobhunter

An AI job application system that scrapes, scores, and drafts — but won't submit without your say-so, and won't lie about your credentials.

## Why

I needed a job. I also needed to not manually apply to 200 listings a week.

So I built a system where AI agents scrape job boards, score each opportunity against my actual background, generate cover letters, and pre-fill application forms. The system runs every 3 hours on Cloud Run. It's found 1,976 jobs, scored 247 of them, and drafted 52 applications.

It has submitted zero.

Not because the automation is broken — the `/apply` endpoint exists, the Playwright form filler works, the ATS detection handles Greenhouse, Lever, and Workday. The system *can* submit. It doesn't, because the architecture requires a human to review every application and click "Approve" before anything goes out.

The more interesting constraint is honesty. The system prompts contain an explicit rule: "The candidate does NOT have a completed degree. Do NOT say 'Bachelor's degree.'" The AI could write more impressive cover letters by fabricating credentials. It's told not to. This is a real tension — the optimizer wants to maximize callbacks, the constraint says be truthful.

Half the scored jobs cluster at exactly 50 on the 0-100 scale. The scoring threshold is 40. Which means the model's uncertainty generates work for the human reviewer. The AI hedges, and I have to decide.

This is a small-scale version of the alignment problem: an autonomous agent optimizing for an objective while constrained by values, with a human in the loop who has the final say. It also found me some good leads.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Cloud Scheduler                            │
│                   (cron: every 3 hours)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ POST /scrape-and-score
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                         │
│                                                                 │
│  /jobs          — list scraped jobs                             │
│  /applications  — list applications + approval workflow         │
│  /scrape-and-score — trigger full pipeline                      │
│  /controls      — pause / resume / emergency-stop               │
│                                                                 │
│  Auth: Bearer token from Secret Manager                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                Agent Browser (FastAPI + Playwright)              │
│                                                                 │
│  Scraper ──► Scorer ──► Cover Letter ──► Form Filler            │
│  (jobspy)    (Gemini)   (Gemini)         (Playwright)           │
│                                                                 │
│  Each module has independent retry logic (5s, 10s, 20s)         │
│  Honesty constraints enforced at the prompt level               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐
│    Firestore     │  │  Cloud Storage   │  │     Dashboard      │
│  (jobs, apps,    │  │  (resume, context │  │  (Next.js + React) │
│   task queue)    │  │   documents)     │  │  Review & approve  │
└──────────────────┘  └──────────────────┘  └────────────────────┘
```

Three services on Cloud Run. Firestore is the shared state. The dashboard polls every 30 seconds and shows pending applications for human review.

## The Safety Mechanisms

This is the part I care about most.

**Human-in-the-loop approval.** Every application goes through a review queue. The dashboard shows the job, the generated cover letter, and pre-filled form fields. Nothing submits until a human clicks "Approve." The `/apply` endpoint checks `application.status == APPROVED` and rejects anything else with a 400.

**Honesty constraints in system prompts.** Three separate AI modules (scorer, cover letter, form QA) each contain explicit instructions about what the system must not fabricate:

```
# From cover_letter.py
"The candidate does NOT have a completed degree. He has 76 credits
from Minerva University. Do NOT say 'Bachelor's degree' — say
'coursework in AI and Physics at Minerva University' or similar
honest framing."

# From job_scorer.py
"No completed degree (76 credits) — penalize roles requiring
BS/MS but not fatally"

# From form_qa.py
"For yes/no questions about degree: the candidate does NOT have
a completed degree"
```

This isn't post-hoc filtering. The constraints live in the system prompts themselves — specification-level truthfulness enforcement.

**Emergency controls.** Three endpoints on the API gateway:
- `POST /pause` — pause the Cloud Tasks queue
- `POST /resume` — resume the queue
- `POST /emergency-stop` — pause AND purge all pending tasks

## How Scoring Works

Gemini 3.1 Pro scores each job 0-100 using a structured rubric:

| Score Range | Meaning |
|-------------|---------|
| 80-100 | Strong fit — skills and experience align well |
| 60-79 | Good fit — most requirements met |
| 40-59 | Moderate fit — some gaps but worth considering |
| 20-39 | Weak fit — significant mismatches |
| 0-19 | Poor fit — wrong domain or level |

The model returns structured JSON: `score`, `reasoning`, `role_summary`, `company_summary`, `strengths`, `gaps`, and `suggestions`.

The scoring threshold is 40. Anything above gets a cover letter generated. In practice, scores cluster heavily around 50 — the model hedges when it's unsure, which creates a fat middle band of "maybe" jobs that require human judgment.

## How Cover Letters Work

Each cover letter follows a rigid 4-paragraph structure:

1. **Hook** (3-4 sentences) — why this company, why this role
2. **Fit & Experience** (5-7 sentences) — relevant background
3. **Projects & Technical Depth** (4-6 sentences) — specific work
4. **Close & Call to Action** (2-3 sentences) — next steps

Word count is enforced at 250-350 words. If the first generation misses the target, the system retries with explicit word count correction. The cover letter module also adapts tone to company culture — startup casual vs. corporate formal.

The honesty constraint means every cover letter says "coursework at Minerva University" instead of "degree from Minerva University." The AI could easily fabricate a more impressive background. It's told not to.

## ATS Form Detection

The form filler detects five applicant tracking systems:

| ATS | Detection | Adapter |
|-----|-----------|---------|
| Greenhouse | URL pattern | Full adapter |
| Lever | URL pattern | Full adapter |
| Workday | URL pattern | Full adapter |
| iCIMS | URL pattern | Detected, generic fill |
| BambooHR | URL pattern | Detected, generic fill |

For Greenhouse, Lever, and Workday, dedicated adapters know the exact form field selectors. For iCIMS and BambooHR, the system falls back to generic field detection. All form filling stops before submission — the submit button is never clicked automatically.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Agent Browser** | Python, FastAPI, Playwright, python-jobspy |
| **AI Engine** | Google Gemini 3.1 Pro Preview |
| **API Gateway** | Python, FastAPI |
| **Dashboard** | Next.js 14, React 18, TypeScript, Tailwind CSS |
| **Database** | Google Cloud Firestore |
| **File Storage** | Google Cloud Storage |
| **Deployment** | Google Cloud Run (3 services) |
| **Scheduling** | Google Cloud Scheduler (cron: `0 */3 * * *`) |
| **Secrets** | Google Secret Manager |
| **Auth** | Bearer token (API gateway), Cloud IAM (service-to-service) |

## Running Locally

```bash
git clone https://github.com/Cuuper22/jobhunter.git
cd jobhunter
cp .env.example .env
# Edit .env with your Gemini API key and applicant details
docker compose up
```

This starts:
- Firestore emulator on port 8181
- Agent Browser on port 8080
- API Gateway on port 8081
- Dashboard on port 3000

You'll need a Gemini API key. Everything else runs locally via Docker.

## Known Issues

**Score clustering.** ~50% of scored jobs land at exactly 50. The Gemini model defaults to the midpoint when uncertain, which makes the 40-point threshold less useful than intended. A calibration pass would help, but I haven't done it.

**Duplicate scraping.** jobspy occasionally returns the same listing under different IDs. The dedup logic catches URL-level duplicates but misses same-job-different-URL cases.

**iCIMS and BambooHR adapters are thin.** Detection works, but form filling falls back to generic field matching. These two ATS platforms have non-standard field naming that would need dedicated adapters.

**Billing disabled.** The Cloud Run services are currently not running (GCP billing paused). The code works — the infrastructure just isn't live. All metrics (1,976 jobs, 247 scored, 52 applications) reflect the last active state.

**Cover letter quality variance.** Some generated letters are genuinely good. Others are formulaic. The 4-paragraph constraint helps consistency but can make letters feel templated. A future version would benefit from few-shot examples per company type.

## License

MIT
