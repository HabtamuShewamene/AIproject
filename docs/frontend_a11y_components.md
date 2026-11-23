# Frontend Accessibility Component Inventory

## Phase 6 — EvidencePanel Component

**File:** `frontend/components/analysis/EvidencePanel.jsx`  
*(tracked outside git — Next.js app deploys independently)*

### ARIA Implementation Checklist

| Feature | Implementation |
| :--- | :--- |
| Collapsible disclosure | `aria-expanded`, `aria-controls="evidence-panel-body"` on `<button>` |
| Region labels | `aria-label` on every `<section>` and `role="region"` sub-panels |
| Decorative icons | `aria-hidden="true"` on all Lucide icons |
| Sentiment/confidence badges | `aria-label` with full human-readable description |
| Sarcasm status live update | `role="status"`, `aria-live="polite"` |
| Keyword count labels | `aria-label` on count spans (e.g. "3 positive keywords") |
| Focus management | `focus-visible:ring-2 focus-visible:ring-[#00F5A0]` on interactive elements |
| Semantic lists | `dl`/`dt`/`dd` for probability key-value pairs |
| Hidden body | Native `hidden` attribute (not `display:none` via CSS) for `aria-expanded=false` |

### Content-Language Header Contract

The API sets `Content-Language` from the detected language code (e.g. `en`, `am`, `ar`).  
The frontend reads `data.aria.content_language` and updates the `lang` attribute of the results region dynamically.

### Skip Navigation

Frontend shell includes a skip-nav link (`<a href="#results-section">Skip to results</a>`) visible on focus.  
The API sets `aria.focus_target = "#results-section"` on every prediction response to keep the anchor in sync.

### Live Region Policy

All asynchronous prediction updates use `aria-live="polite"` to avoid interrupting screen readers mid-sentence.  
Error states use `role="alert"` for immediate announcement.
