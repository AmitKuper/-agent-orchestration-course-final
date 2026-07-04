# Plan — Report and Email Component

> **Document type:** Engineering / implementation plan  
> **Related PRD:** `PRD_email_report.md`

---

## 1. Module Layout

```text
backend/app/reports/
  generator.py
  schemas.py
  validators.py
  storage.py
  exporters.py
  tests/
backend/app/email/
  sender.py
  providers.py
  templates.py
  delivery_log.py
  tests/
```

---

## 2. Report Generation Flow

```text
Match completed
  -> ReportService.generate_match_report(match_id)
  -> validate JSON schema
  -> store report artifact
  -> expose through /api/reports
  -> optionally send email if enabled
```

---

## 3. Email Flow

```text
Report artifact
  -> EmailService.load_config
  -> EmailProvider.send
  -> DeliveryLog.record_success_or_failure
```

Use environment/config for all email settings. Do not commit secrets or actual recipient values.

---

## 4. JSON Schema Files

```text
schemas/reports/internal_match_report.schema.json
schemas/reports/intergroup_match_report.schema.json
schemas/reports/technical_invalid_report.schema.json
```

---

## 5. Provider Abstraction

Define interface:

```python
class EmailProvider:
    def send_report(self, recipient: str, subject: str, report_json: dict) -> DeliveryResult:
        ...
```

MVP provider can be a dry-run file writer. Real provider can be added later.

---

## 6. Tests

Required tests:

- completed match report schema validation;
- inter-group report schema validation;
- no explicit email address scan in docs/config;
- email disabled mode;
- dry-run delivery mode;
- provider failure does not alter game result;
- API report download flow.
