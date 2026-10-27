# Outreach Operations — Design System

Version: 1.0  
Source of truth: `frontend/index.html` and `frontend/styles.css`.

## Direction

The product is a dark operations workspace for Connect, acceptance tracking, recipient preparation, and messaging. Its visual language is inspired by Stripe and Stripi: deep navy ink, electric indigo actions, restrained elevation, compact data surfaces, and typography that gives the interface room to breathe.

The dashboard is a product surface, not a marketing landing page. Use atmospheric color only as a subtle top-level glow; never let decoration compete with a user action or a status signal.

Primary UX goals:

- Make the next safe action obvious.
- Keep Connect → Acceptance → Messages visible as one workflow; recipient preparation is automatic.
- Make status, errors, quotas, and disabled states scannable without opening a detail view.
- Preserve context while filtering, paging, opening drawers, or reviewing a prepared batch.
- Work comfortably with keyboard, touch, and narrow screens.

## Tokens

### Color

```css
:root {
  --bg: #07111f;
  --bg-soft: #0b1728;
  --panel: #101d30;
  --panel-raised: #14253b;
  --panel-hover: #182b45;
  --border: #20334b;
  --border-strong: #304966;
  --text: #f6f9fc;
  --muted: #a7b7ca;
  --faint: #72859d;
  --accent: #635bff;
  --accent-hover: #817cff;
  --accent-press: #5148d8;
  --accent-soft: rgba(99, 91, 255, .16);
  --green: #2dd4bf;
  --green-soft: rgba(45, 212, 191, .13);
  --amber: #f5b94c;
  --amber-soft: rgba(245, 185, 76, .14);
  --red: #f4778b;
  --red-soft: rgba(244, 119, 139, .14);
  --blue: #66a8ff;
  --blue-soft: rgba(102, 168, 255, .14);
}
```

Color meaning is functional: indigo means action or focus, green means healthy or complete, amber means pending or limited, red means blocked or failed, and blue is informational. Neutral panels must remain neutral.

### Typography

Use Inter as the available substitute for Sohne:

```css
font-family: Inter, ui-sans-serif, system-ui, -apple-system,
  BlinkMacSystemFont, "Segoe UI", sans-serif;
font-feature-settings: "ss01" 1;
```

| Role | Size | Weight | Line height | Tracking |
| --- | ---: | ---: | ---: | ---: |
| Page title | 26–34px | 400 | 1.1 | -0.025em |
| Section title | 20–24px | 400 | 1.2 | -0.02em |
| Body | 15px | 400 | 1.4 | 0 |
| Button | 14px | 400 | 1 | 0 |
| Caption | 13px | 400 | 1.4 | -0.02em |
| Eyebrow / table header | 10–11px | 700 | 1.15 | 0.08em |

Use `font-feature-settings: "tnum" 1` for counts, quotas, percentages, dates, and table values. Display text can be light and editorial, but operational controls must remain readable at normal weight.

### Shape and spacing

The base spacing unit is 8px: 2, 4, 8, 12, 16, 24, 32, and 64px. Use 24px panel padding on desktop and 18px on compact mobile surfaces.

| Token | Value | Use |
| --- | ---: | --- |
| Radius md | 8px | Inputs, compact controls |
| Radius lg | 12px | Panels and cards |
| Radius xl | 16px | Shell-level surfaces |
| Pill | 9999px | Buttons, filters, status tags |

## Layout architecture

Desktop uses a fixed 248px navigation rail and a fluid content area. The topbar stays visible while the user scrolls and contains page context, system state, and the refresh action. Main content should use a comfortable maximum width and avoid stretching dense tables across unreadable line lengths.

The Outreach area is one workspace with three process tabs and a Replies inbox:

1. **Connect** — enter URLs, review targets, start a Connect job, and monitor progress.
2. **Acceptance** — queue and inspect acceptance checks and history.
3. **Messages** — one list of accepted recipients and automatically prepared message batches. Ready, Queued, Sending, Completed and Failed are row status badges, not tabs. Users review a draft and queue it for sending; there is no manual Prepare step. Weeks always follow the original Connect batch, never the check/accept/prepare date.
4. **Replies** — review and respond to captured incoming conversations.

Historical data uses a week-first index across Acceptance, Recipients, and Messages. The default view shows dated week cards with lightweight totals; selecting a week reveals only the Connect Jobs, accepted profiles, or message batches belonging to that week. Batch-level filters remain available after a week is selected, but a default dropdown must never be the primary navigation for historical data.

Keep actions close to the data they affect. Destructive actions require a deliberate confirmation surface. Long-running actions show an immediate pending state, progress, and an actionable error when they fail.

### Responsive behavior

- ≥ 1200px: fixed rail, full workflow controls, multi-column panels.
- 768–1199px: compact rail/content spacing; panels can collapse to two columns.
- < 860px: navigation becomes a sticky horizontal grid; the main content uses the full width.
- < 560px: two-column navigation, stacked toolbars, full-width buttons and fields.

Every interactive target is at least 40px high; mobile controls should reach 44px where space permits. Tables may scroll horizontally, but their primary status and action must remain visible.

## Components

### Primary action

Use one filled indigo pill for the main action in a region:

- background `var(--accent)`;
- hover `var(--accent-hover)`;
- pressed `var(--accent-press)`;
- white text;
- 40px minimum height, 16px horizontal padding;
- pill radius.

Secondary actions use a dark surface with a border. Destructive actions use red only when the action can cause loss or stop a running operation.

### Panels and cards

Panels use `var(--panel)`, a 1px `var(--border)` border, 12px radius, and restrained shadow. Use `var(--panel-raised)` only for a drawer, modal, or active detail hierarchy. Hover should change the border or surface slightly, never add a strong glow.

### Inputs and filters

Inputs use `var(--bg-soft)` with a `var(--border-strong)` border, 8px radius, and 40px minimum height. Focus uses a 2px indigo outline with a 2px offset. Labels sit above fields and use caption or eyebrow styles. Preserve entered values when a request fails.

Dropdowns use the custom trigger-and-menu pattern from the Recipients week picker: a bordered button with a label and chevron opens a matching anchored menu of selectable rows. Do not use native select controls for workflow filters. Match the trigger shape, spacing, surfaces, hover, selected, and focus states to the week picker.

### Workflow tabs

The four Outreach process tabs use a segmented pill container. The active tab is filled indigo with white text. Inactive tabs are transparent or neutral and must retain a clear hover and focus state. The active process panel is the only visible panel.

### Status

Status should be expressed redundantly through text, color, and where useful an icon. Never use color alone. Keep words short and consistent: `queued`, `processing`, `completed`, `failed`, `accepted`, `pending`, `unknown`, and `not sent`.

### Tables and lists

Use compact rows with strong first-column identity, muted secondary metadata, and tabular numerics. For historical operational data, show a week index before the table and progressively disclose the rows after a week is selected. Keep filters above the revealed table, show result counts, provide an empty state that explains the next action, and keep pagination controls adjacent to the count.

### Drawers and modals

Use a drawer for contextual analysis such as Acceptance Insights or Rate Limits. Use a modal only for confirmation, message composition, or a focused session operation. Every overlay needs an accessible title, close button, Escape support, and a visible focus style.

## Interaction principles

- Disable only the action currently in flight; keep safe navigation available.
- Poll or refresh only while a relevant job is pending or processing.
- Show last-updated timestamps for operational data.
- Keep the original Connect Job ID attached to every acceptance, recipient, and message batch.
- Never hide an error behind a generic spinner.
- Use confirmation language that names the exact scope and consequence.
- Respect reduced-motion preferences.

## Do and don't

### Do

- Use indigo sparingly for action and focus.
- Use subtle navy depth and thin borders to establish hierarchy.
- Apply tabular figures to operational numbers.
- Keep the four-step Outreach workflow visually continuous.
- Prefer progressive disclosure through drawers and expandable rows.
- Test keyboard focus, empty states, loading states, failure states, and mobile widths.

### Don't

- Don't use bright white canvases or large marketing gradients inside the operational workspace.
- Don't use a rainbow of status colors or decorative accent colors.
- Don't turn every button into a filled CTA.
- Don't use rounded rectangles with inconsistent radii; controls are pills and panels are 8–12px cards.
- Don't remove context when changing tabs, filters, or pages.
- Don't alter the Outreach data flow while changing presentation.

## Verification checklist

Before shipping a visual change:

1. Check Connect, Acceptance, Recipients, and Messages with real and empty data.
2. Verify that loading, disabled, failed, and success states remain distinguishable.
3. Test at 1440px, 1024px, 768px, and 390px widths.
4. Navigate using keyboard only and confirm visible focus.
5. Run `node --check frontend/app.js` and a Python compile check for backend changes.
