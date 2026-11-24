# SentiAI Enterprise UI/UX Platform Specification

## 1. Overview & Vision
The SentiAI Enterprise Suite elevates sentiment analysis from a simple isolated polarity classifier into an end-to-end customer experience & brand intelligence platform. It is designed for Product Managers, Customer Success VPs, Support Leads, and Brand Strategists.

---

## 2. Core Functional Modules

### Module 1: Realtime Intelligence & Aspect-Based Sentiment Analysis (ABSA)
- **Multi-Dimensional Aspect Decomposition:**
  Automatically detects and extracts feedback impacting five operational departments:
  - 🚀 **Product & Capabilities:** Features, stability, algorithms, workflows.
  - 🎧 **Customer Support:** Responsiveness, empathy, resolution speed.
  - 💳 **Pricing & Billing:** Renewal costs, invoice errors, subscription value.
  - ⚡ **Performance & UX:** Latency, crashing, mobile responsiveness, smoothness.
  - 🚚 **Fulfillment & Logistics:** Delivery timeliness, packaging integrity.
- **Urgency & Churn Triage Banner:**
  - Automated detection of churn threats (*"canceling my subscription"*, *"switching to competitor"*).
  - Triage levels: `Critical`, `High`, `Attention`, `Standard`, `Low`.
  - Intent classification: `Bug Report`, `Feature Request`, `Billing Dispute`, `Churn Threat`, `Brand Advocacy`.
  - Actionable recommendation for operational routing.

### Module 2: Batch & CSV Data Ingestion Hub
- **Enterprise-Scale File Upload:**
  - Drag-and-drop CSV / TXT file parser.
  - Automatic vectorized batch processing via `POST /api/v1/predict/batch`.
- **Pre-Bundled Benchmark Datasets:**
  - *SaaS Feedback & Churn Risk* (10 rows).
  - *Airline Flight Delay Tweets* (10 rows).
  - *Consumer Electronics Launch* (10 rows).
- **Interactive Data Grid:**
  - Real-time search across feedback text.
  - Polarity filtering (`All`, `Positive`, `Negative`, `Neutral`).
  - 1-Click **"Export Enriched CSV"** with sentiment, confidence, urgency, and aspect tags.
  - Direct **"Open Copilot →"** integration for any table row.

### Module 3: SentiAI Copilot & Resolution Drafter
- **Conversational Intelligence:**
  - Interactive Q&A chat drawer powered by `POST /api/v1/enterprise/copilot/chat`.
  - Real-time queries: *"What should we do first?"*, *"Why was this classified negative?"*, *"Draft an apology email"*.
- **1-Click Pre-Drafted Customer Responses:**
  - **Empathetic:** Warm, apologetic, de-escalating.
  - **Solution-Oriented:** Direct, actionable, SLA-focused.
  - **Executive Brief:** 2-sentence bottom-line summary for leadership.
- **Key Strategic Drivers:**
  - Synthesized bullet-point takeaways on customer retention risks.

### Module 4: A/B Benchmark & Competitive Compare
- **Side-by-Side Comparison Engine:**
  - Evaluates two pieces of feedback, product versions, or competitor brands.
  - Computes net sentiment differential:
    $$\Delta = (\text{Score}_A \times \text{Conf}_A) - (\text{Score}_B \times \text{Conf}_B)$$
  - Displays competitive winner trophy, delta percentage, and comparative aspect breakdowns.
- **Built-in Presets:**
  - Platform v2.0 (New) vs Legacy v1.0 (Old).
  - Customer Support Experience vs Delivery Logistics.
  - Brand A vs Brand B.

---

## 3. Design System & Accessibility
- **Color Palette:**
  - Background: Deep Obsidian `#07070b` & `#0a0a0f`.
  - Accent / Positive: Emerald Neon `#00F5A0`.
  - Negative: Coral Red `#f87171`.
  - Neutral / Warning: Solar Amber `#facc15`.
  - Informational: Cyan Blue `#60a5fa`.
- **Typography:**
  - Clean system sans-serif with monospace accents for confidence scores and model versioning.
- **Accessibility:**
  - WCAG 2.1 AA compliant.
  - Accessible tablist navigation, high contrast text ratios, and screen-reader aria live regions.
