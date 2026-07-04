# PRD — Report and Email Component

> **Document type:** Product Requirements Document  
> **Scope:** Requirements for generating match reports and optionally sending them by email.

---

## 1. Purpose

The Report and Email component generates machine-readable reports for completed matches and optionally sends them to a configured recipient.

No explicit email address may be hard-coded in documentation, code, tests, or committed configuration.

---

## 2. Report Requirements

The system must generate reports for:

- internal/local matches;
- human-vs-server games;
- inter-group MCP matches;
- technical-invalid or aborted matches, when useful for audit.

Reports must be machine-readable JSON.

---

## 3. Report Content

A completed match report must include:

- report type;
- rules version;
- local server identity;
- opponent identity;
- match ID;
- mode;
- start/end timestamps;
- timezone;
- final score;
- result from local server perspective;
- sub-game summaries;
- role schedule;
- configuration used;
- technical-invalid attempts, if any;
- replay/event-log references;
- mutual agreement flag for inter-group reports, if applicable.

---

## 4. Email Requirements

If email sending is enabled, the system must:

- read recipient destination from environment or secure config;
- never hard-code recipient addresses;
- support disabling email entirely;
- attach or include the JSON report according to configured mode;
- log delivery status;
- handle delivery failure without corrupting game history.

Required configuration names:

```text
REPORT_EMAIL_ENABLED
REPORT_RECIPIENT_EMAIL
REPORT_SENDER_ID
REPORT_PROVIDER
```

---

## 5. Privacy and Security

Reports must not include:

- API keys;
- auth tokens;
- private debug logs;
- raw LLM prompts unless explicitly enabled for internal debugging;
- hidden live-state data for incomplete games;
- hard-coded email addresses.

---

## 6. REST API Requirements

The system must expose report operations through `/api`:

```http
GET  /api/reports
GET  /api/reports/{report_id}
GET  /api/reports/{report_id}/download
POST /api/reports/{report_id}/send-email
GET  /api/reports/{report_id}/delivery-status
```

---

## 7. Acceptance Criteria

The component is acceptable when:

- every completed match can produce a valid JSON report;
- reports contain no hard-coded recipient address;
- email can be disabled through config;
- email delivery status is recorded;
- failed email delivery does not change game result;
- reports can be downloaded through the REST API;
- automated tests validate report schema.
