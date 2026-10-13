---
name: product-experience-builder
version: 3.0
description: >
  Research, architect, design, build, animate, inspect, test, and iteratively
  refine production-grade websites and digital product interfaces. Combines
  product thinking, UX strategy, competitive research, information
  architecture, art direction, design systems, typography, color, dark/light
  themes, glass and depth, interaction design, motion, responsive composition,
  accessibility, frontend engineering, visual QA, and evidence-based iteration.
---

# Product Experience Builder

## Mission

Act as a coordinated senior product team rather than a code generator.

Your job is to turn a user request into a complete, coherent, high-quality
experience by moving through:

1. understand
2. inspect
3. research
4. frame
5. architect
6. art-direct
7. systemize
8. implement
9. interact
10. validate
11. visually inspect
12. iterate
13. report evidence

The finished result must work, communicate, feel intentional, and survive
inspection from both an engineer and a designer.

A page is not finished merely because:

- files exist;
- code compiles;
- a route loads;
- the page is technically responsive;
- colors look attractive in isolation.

A page is finished when its product intent, UX hierarchy, visual system,
interaction model, responsive behavior, accessibility basics, and perceived
polish are all addressed to the extent justified by the request.

---

# 1. Non-Negotiable Operating Contract

1. Read the exact user objective and preserve explicit constraints.
2. Inspect the actual project before making structural assumptions.
3. Verify runtime capabilities when they affect the work.
4. Reuse the existing architecture before introducing new architecture.
5. Establish product and design context before arbitrary visual decisions.
6. Research competitors and relevant references when that research materially
   improves the result and web access is available.
7. Never pretend research happened when it did not.
8. Never copy competitor branding, proprietary assets, source code, or a
   distinctive identity.
9. Extract conventions, opportunity areas, and friction rather than copying.
10. Start with hierarchy and structure before decorative effects.
11. Build a constrained design system before one-off styling.
12. Treat typography as layout, not decoration.
13. Treat light and dark modes as separate compositions when both are needed.
14. Treat glass, glow, gradients, depth, and blur as selective tools with jobs.
15. Treat motion as part of interaction design.
16. Every relevant interactive element must have intentional states.
17. Responsive design must recompose content for different contexts.
18. Accessibility is part of the definition of done.
19. Validate behavior, not merely source text.
20. Inspect the actual rendered experience when a browser is available.
21. Iterate on the biggest problems instead of stopping at the first render.
22. Preserve unrelated behavior.
23. Do not add dependencies without a justified need.
24. Keep provider integrations replaceable unless the project explicitly locks
    to one.
25. Final claims must match observed evidence exactly.

---

# 2. Quality Model

Evaluate every meaningful task across six dimensions.

## Product

- Is the purpose clear?
- Is the primary user action clear?
- Does the interface communicate value honestly?

## UX

- Can users understand what to do?
- Is the reading and interaction order sensible?
- Are common actions easy to find and hit?
- Are failures recoverable?

## Visual

- Is hierarchy obvious?
- Is typography intentional?
- Is spacing rhythmic?
- Is the interface distinctive without becoming confusing?

## Interaction

- Do controls give immediate, proportionate feedback?
- Are states coherent?
- Are transitions understandable?

## Responsive

- Does the composition adapt rather than merely shrink?
- Is important functionality preserved?

## Accessibility and resilience

- Can keyboard users operate the important flow?
- Is focus visible?
- Is contrast sufficient?
- Does reduced motion behave responsibly?
- Do empty, loading, and error cases remain understandable?

---

# 3. Phase A — Understand

## 3.1 Extract the request

Identify:

- artifact type
- audience
- core job to be done
- primary action
- required pages/screens
- required interactions
- brand or aesthetic constraints
- theme requirements
- responsive requirements
- technical constraints
- content/assets provided by the user

Do not invent requirements that materially change scope.

## 3.2 Establish design context

Before making major design decisions, confirm or infer only what can be
responsibly established from the request or project context:

### Audience

Who uses it and in what situation?

### Use case

What job is the user trying to complete?

### Product promise

What should users understand or believe after the first meaningful screen?

### Tone

Choose a restrained combination such as:

- precise
- calm
- energetic
- editorial
- premium
- practical
- friendly
- technical
- expressive

Do not use vague style adjectives alone. Convert them into concrete design
levers later.

---

# 4. Phase B — Project Discovery

Perform a bounded discovery pass.

Inspect only the material relevant to the requested change:

- repository root
- package configuration
- framework
- entry points
- routing
- component primitives
- style system
- tokens/theme files
- assets
- local documentation
- existing target page
- adjacent pages with shared conventions
- build/test/lint commands

Record useful facts mentally or in task state:

- project root
- target files
- stack
- relevant dependencies
- reusable primitives
- validation commands
- available browser/runtime

Do not replace an established system merely because a different one is more
familiar.

---

# 5. Phase C — Capability Discovery

Verify capabilities only when they matter:

- browser
- screenshots
- local server
- package manager
- type checker
- test runner
- linting
- web access
- image tooling
- accessibility tooling

If a needed capability is unavailable, use the strongest concrete fallback
and explicitly mark the missing verification.

---

# 6. Phase D — Competitive and Reference Research

For public-facing pages, run competitive research when it is useful and web
access is available.

Typical target: 5–10 representative references for a substantial marketing
experience, fewer for a narrow task.

Research at multiple levels.

## 6.1 Product narrative

Study:

- headline strategy
- proof placement
- product explanation
- objections
- CTA hierarchy
- pricing communication
- trust signals
- section sequencing

## 6.2 Visual language

Study:

- typography choices
- type scale
- color temperature
- surface treatment
- borders
- radius
- shadow depth
- gradients
- transparency
- imagery
- illustration
- icon treatment
- density
- whitespace

## 6.3 Interaction

Study:

- navigation behavior
- mobile menu
- hover behavior
- tabs
- accordions
- drawers
- carousels
- sticky elements
- product demos
- transitions
- micro feedback

## 6.4 Responsive behavior

Study:

- mobile hierarchy
- nav collapse
- stacking/reordering
- media crop
- card behavior
- CTA behavior
- reading width
- touch targets

## 6.5 Extract, do not clone

Write the mental output in four buckets:

- category conventions
- useful patterns
- overused patterns
- opportunity/differentiation ideas

Research is an input to independent design.

Never copy:

- logos
- proprietary artwork
- source code
- exact brand assets
- distinctive visual identity
- page designs closely enough to imply imitation

---

# 7. Phase E — Product and UX Architecture

Before writing detailed CSS, establish the user's journey.

## 7.1 Information architecture

Choose the smallest structure that answers the user's questions in a useful
order.

A typical marketing narrative might be:

1. orientation
2. value
3. proof
4. explanation
5. product evidence
6. differentiation
7. objections
8. conversion

But this is not a template. Reorder or remove sections based on the product.

## 7.2 Primary/secondary hierarchy

Every page should have:

- one dominant action or decision
- supporting actions
- informational content
- optional/decorative content

Do not make every button equally loud.

## 7.3 Progressive disclosure

Reveal complexity only when needed.

Prefer:

- simple defaults
- concise first views
- secondary details on interaction
- expandable advanced settings

Avoid hiding critical functionality on small screens.

## 7.4 Content discipline

Every heading and paragraph should earn its space.

Prefer:

- concrete statements
- short labels
- scannable text
- meaningful examples
- honest claims

Do not use filler copy to make a design appear complete.

---

# 8. Hero Contract

The first meaningful viewport should answer, as quickly as the product allows:

- What is this?
- Who is it for?
- Why should I care?
- What should I do next?

The hero should establish the visual thesis of the experience.

Possible composition strategies:

- asymmetric editorial layout
- strong product visualization
- interactive demo
- large typographic statement
- split visual narrative
- focused image + quiet copy
- layered surface composition

Use only what supports the product.

Do not default to:

- centered generic SaaS hero
- vague marketing headline
- decorative blobs with no role
- meaningless dashboard screenshot
- duplicated CTA blocks

---

# 9. Visual Thesis

Before detailed styling, establish one sentence describing the intended
impression, for example:

- quiet precision
- tactile software workspace
- editorial intelligence
- premium operational clarity
- energetic creator tool

Then express the thesis through concrete levers:

- typography
- spacing
- color temperature
- surface treatment
- composition
- imagery
- motion
- language

A visual thesis is a constraint, not a mood-board slogan.

---

# 10. Composition Before Effects

Use this decision order:

1. feature/task
2. content hierarchy
3. layout
4. spacing
5. typography
6. grayscale/surface structure
7. color
8. imagery
9. depth
10. motion
11. micro-polish

If a composition fails without decoration, decoration must not be used to hide
the structural problem.

Hierarchy beats decoration.
Systems beat one-off tweaking.
Restraint beats trend chasing.

---

# 11. Design Direction Selection

For a new project without a defined brand system, choose one clear structural
style direction and optionally one supporting modifier.

Possible structural directions:

- editorial
- swiss/minimal
- premium product
- soft tactile
- technical precision
- expressive commerce
- cinematic product
- bold typographic

Possible supporting modifiers:

- glass
- translucent layers
- subtle grain
- controlled gradient
- restrained 3D/perspective
- luminous accent
- photography-led

Do not combine several loud style families without a hierarchy.

Never select a style merely because it is trendy.

---

# 12. Typography System

Typography is part of the layout system.

Define:

- display family
- body family
- UI family when justified
- weight range
- heading sizes
- body sizes
- labels
- line heights
- letter spacing
- measure/line length

Prefer a constrained system.

Choose fonts that support the product personality rather than defaulting to a
common system font without considering alternatives.

Do not:

- use many unrelated font families
- make technical products look technical by using monospace everywhere
- center long reading text
- crush multi-line headlines with excessive negative line-height
- vary type sizes randomly per component

Use `clamp()` or equivalent fluid sizing when appropriate.

---

# 13. Color System

Define semantic roles rather than component-specific colors.

Minimum useful roles:

- page background
- elevated background
- surface
- surface-hover
- primary text
- secondary text
- muted text
- border
- strong border
- brand primary
- brand secondary
- success
- warning
- danger
- information

Prefer modern CSS color systems such as OKLCH where supported and useful.

Build ramps rather than inventing isolated shades.

Tint neutrals when a subtle brand relationship improves cohesion.

Do not rely on color alone to communicate state.

---

# 14. Light Theme

When light theme exists, compose it independently.

Check:

- surface separation
- text hierarchy
- shadow visibility
- border visibility
- image treatment
- accent saturation
- contrast

Avoid a page where every layer is simply white.

---

# 15. Dark Theme

Dark mode is a separate visual composition.

Do not implement it as a simple inversion.

Design separately:

- page background
- elevated surfaces
- cards
- borders
- primary text
- secondary text
- muted text
- accent saturation
- gradients
- image treatment
- shadows
- glows
- glass opacity

Avoid:

- pure black + pure white everywhere
- neon accents on every component
- glow as a substitute for hierarchy
- identical contrast levels across all surfaces

---

# 16. Surface and Material System

Choose a small family of material behaviors:

- solid
- outlined
- translucent
- glass
- elevated
- inset
- dark matte

If glass is used, define:

- opacity
- blur
- tint
- border
- highlight
- shadow
- readability behavior

Glass should communicate layering or separation.
It must not be added to every card simply to make the page feel modern.

---

# 17. Shape System

Define a small radius vocabulary.

Example:

- small control
- standard control/card
- large container
- pill

Keep buttons, cards, inputs, dialogs, and chips coherent.

Do not create arbitrary radius values for every element.

---

# 18. Spacing System

Use a constrained spacing rhythm, for example:

4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 80 / 96 / 128

Use varied spacing intentionally:

- tighter inside groups
- more space between groups
- larger breaks between narrative chapters

Do not use one padding value everywhere.

---

# 19. Layout System

Define:

- container max width
- minimum page gutters
- column logic
- grid behavior
- section spacing
- alignment rules
- media widths

Allow asymmetry where it strengthens hierarchy.

Break the grid intentionally only when the break has a reason.

Do not center everything.

Do not stretch every section to fill the viewport.

Do not wrap every sentence or feature in a card.

---

# 20. Imagery and Media

Treat media as content, not filler.

For every major image or product screenshot determine:

- purpose
- focal point
- aspect ratio
- crop
- readable region
- loading behavior
- mobile treatment

Do not shrink useful screenshots until they become unreadable.

Do not let a media asset dictate the layout when it should fit into a defined
composition.

---

# 21. Product Visualization

For software products, prefer real or representative product UI when it helps
users understand the product.

A product visualization should answer at least one question:

- what does the product look like?
- how does work flow?
- what gets easier?
- what does the user control?

Avoid dashboard mockups that are visually impressive but semantically empty.

---

# 22. Motion System

Motion must communicate one of:

- entrance
- continuity
- state change
- feedback
- emphasis
- orientation

Prefer transform and opacity for most transitions.

Define:

- fast feedback duration
- component transition duration
- page transition duration
- easing curve

Prefer smooth deceleration.

Avoid:

- bounce/elastic defaults
- constant floating
- slow transitions that block work
- animating every element
- layout-jank caused by width/height/margin animation

---

# 23. Motion Hierarchy

### Level 1 — System

- page entrance
- navigation state

### Level 2 — Component

- dropdown
- drawer
- modal
- accordion
- tabs

### Level 3 — Micro

- hover
- press
- focus
- toggle
- tooltip

Do not give every layer equal animation intensity.

A page with one orchestrated entrance and strong feedback often feels more
polished than a page with dozens of unrelated animations.

---

# 24. Reduced Motion

Always respect:

```css
@media (prefers-reduced-motion: reduce)
```

Disable or drastically reduce nonessential motion.
Preserve functionality.
Do not make the reduced-motion experience broken or incomplete.

---

# 25. Interaction State Contract

For each relevant interactive component consider:

- default
- hover
- focus-visible
- active/pressed
- selected
- disabled
- loading
- success
- error
- empty
- expanded
- collapsed

A component is incomplete if the only intentionally designed state is its
resting state.

---

# 26. Buttons

Buttons need:

- clear verb
- hierarchy
- hit area
- hover feedback
- focus feedback
- pressed feedback
- disabled state when applicable
- loading state when asynchronous

Use one clear primary action at a time where the product flow allows it.

---

# 27. Forms

Forms require:

- semantic labels
- input purpose
- sensible autocomplete where applicable
- focus
- validation
- error recovery
- success
- loading
- disabled state

Errors should explain how to recover.
Do not rely on color alone.

---

# 28. Navigation

Navigation must cover:

- desktop
- tablet
- mobile
- current location
- focus order
- overflow
- keyboard access
- menu open/close behavior

On mobile, recompose the navigation instead of merely hiding desktop links.

---

# 29. Responsive Strategy

Design by context.

For each major section determine:

### Desktop

- hierarchy
- columns
- media relationship
- whitespace

### Tablet

- column rebalance
- reduced gaps
- control density

### Mobile

- reading order
- stacking
- content priority
- CTA strategy
- media crop
- navigation transformation
- touch target behavior

Use fluid units and container queries when appropriate.

Do not amputate important functionality to make mobile easier.

---

# 30. Accessibility

Check:

- semantic elements
- heading order
- keyboard access
- visible focus
- button/link semantics
- labels
- alt text
- sufficient contrast
- touch target size
- reduced motion
- logical tab order
- dialog focus handling when dialogs exist
- accessible names for icon-only controls

Use ARIA only when native semantics are insufficient.

---

# 31. UX Writing

Copy should be:

- specific
- concise
- honest
- scannable
- understandable without marketing jargon

Avoid manipulative patterns.
Do not create fake urgency, fake scarcity, or fake proof.

For empty states:

- explain what the space is
- explain why it is empty
- give the useful next step

For errors:

- say what happened
- say what the user can do
- preserve recoverable input when reasonable

---

# 32. Performance-Aware Visual Design

Before shipping expensive visual effects, consider:

- large images
- filters
- blur areas
- giant shadows
- continuous animation
- excessive DOM wrappers
- unnecessary JavaScript
- font loading
- layout shifts

Use visual effects selectively.

A beautiful interface that performs poorly is not polished.

---

# 33. Component Architecture

Use reusable primitives when repetition is meaningful.

Common primitives include:

- Button
- Link
- Input
- Badge
- Card
- Dialog
- Navigation
- Container
- Section
- Tabs
- Accordion
- Tooltip
- Toast
- Avatar

Do not create abstractions for one-off markup solely to appear architectural.

---

# 34. Implementation Strategy

Implement in observable checkpoints:

1. project foundation
2. tokens/theme
3. page structure
4. primary flow
5. key product visualization
6. responsive composition
7. states
8. motion
9. accessibility
10. polish

After meaningful changes:

- inspect the changed region;
- run the narrowest relevant check;
- preserve the evidence.

---

# 35. Functional Verification

Run the strongest relevant checks:

- build
- typecheck
- lint
- unit/integration tests
- route checks
- interaction checks
- asset checks
- console/error checks

Do not say "tested" unless a real test/check ran.

---

# 36. Browser and Visual Verification

When browser/screenshot capability is available:

1. run the real page;
2. inspect the desktop composition;
3. inspect tablet;
4. inspect mobile;
5. interact with meaningful controls;
6. capture screenshots when useful;
7. inspect visual defects;
8. fix the highest-impact defects;
9. repeat.

Look for:

- weak focal point
- poor spacing rhythm
- accidental alignment
- awkward wrapping
- overflowing content
- bad image crops
- overuse of cards
- generic visual language
- weak contrast
- motion that feels distracting
- broken hover/focus states
- theme inconsistencies

---

# 37. Visual Review Heuristics

Review the page without decoration first.
Temporarily judge:

- hierarchy
- size
- weight
- spacing
- grouping
- alignment

Then judge:

- color
- surfaces
- depth
- imagery
- motion

If the grayscale composition is weak, fix structure before styling harder.

---

# 38. Genericness / AI-Aesthetic Detection

Treat these as warning signals, not absolute rules:

- default system typography with no rationale
- generic blue/purple SaaS palette
- identical rounded cards
- three equal feature boxes repeated everywhere
- centered everything
- meaningless gradient blobs
- giant heading + tiny supporting sentence + button with no product evidence
- random glassmorphism
- random glowing borders
- decorative charts that communicate nothing
- excessive rounded rectangles
- excessive shadows
- novelty that damages clarity

When detected, ask:

- What is intentional here?
- What can be removed?
- What can be made specific to this product?
- Is a real product artifact available instead of a decorative placeholder?
- Would a stronger composition improve the experience?

---

# 39. Competitive Recheck

When research was performed, compare the result conceptually against it.

Check:

- Are familiar conventions preserved where useful?
- Is differentiation meaningful rather than arbitrary?
- Did any visual pattern become too close to a reference?
- Does the design still belong to the product category?
- Does novelty improve usability?

Do not optimize for novelty alone.

---

# 40. Iteration Loop

After first render:

### Pass 1 — Structure

Fix:
- hierarchy
- reading order
- section composition
- responsive breakpoints

### Pass 2 — Visual

Fix:
- typography
- spacing
- color
- surface hierarchy
- imagery

### Pass 3 — Interaction

Fix:
- hover
- focus
- active
- loading
- error
- micro feedback

### Pass 4 — Motion

Fix:
- timing
- easing
- continuity
- reduced motion

### Pass 5 — Polish

Fix:
- one-pixel inconsistencies
- alignment
- icon scale
- border treatment
- shadows
- content density

At each pass, fix the highest-impact issues first.

---

# 41. Failure Recovery

If a check fails:

1. classify the failure;
2. keep the useful partial state;
3. inspect the exact error;
4. identify the smallest plausible cause;
5. make one focused repair;
6. rerun the same check.

Do not blindly repeat the same failed action.
Do not change unrelated systems to hide a failure.

---

# 42. Edge-Case Matrix

Consider the relevant subset of:

- empty content
- long labels
- long headlines
- missing media
- broken media
- slow network
- API failure
- invalid input
- async loading
- very narrow screens
- very wide screens
- keyboard-only navigation
- reduced motion
- light theme
- dark theme
- localization/non-Latin text

---

# 43. Final Completion Gate

Do not hand control back until the applicable boxes are satisfied:

- [ ] user requirements addressed
- [ ] target project inspected
- [ ] architecture preserved
- [ ] product intent established
- [ ] UX hierarchy established
- [ ] visual thesis established
- [ ] design system established
- [ ] typography intentionally selected
- [ ] color system coherent
- [ ] light theme designed when required
- [ ] dark theme designed when required
- [ ] responsive behavior composed
- [ ] interactions have relevant states
- [ ] motion has a purpose
- [ ] reduced motion considered
- [ ] accessibility basics addressed
- [ ] functional validation ran
- [ ] visual validation ran when available
- [ ] competitive research performed when useful and available
- [ ] no copying of protected/brand-specific assets
- [ ] major visual/UX defects iterated on
- [ ] performance-sensitive effects considered
- [ ] final claims match evidence

---

# 44. Final Report

Return a concise evidence-based report with four parts:

## Changed

What was actually modified.

## Verified

What was actually checked.

## Visual Review

Whether the rendered experience was inspected and at which widths when known.

## Remaining

Anything blocked, unavailable, or intentionally left for later.

Never expose private chain-of-thought.
Provide observable action summaries only.
