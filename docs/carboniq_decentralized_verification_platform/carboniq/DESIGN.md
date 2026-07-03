---
name: EcoLens CarbonIQ
colors:
  surface: '#0c150f'
  surface-dim: '#0c150f'
  surface-bright: '#323c34'
  surface-container-lowest: '#07100a'
  surface-container-low: '#141e17'
  surface-container: '#18221b'
  surface-container-high: '#232c25'
  surface-container-highest: '#2d3730'
  on-surface: '#dae5da'
  on-surface-variant: '#b9cbbc'
  inverse-surface: '#dae5da'
  inverse-on-surface: '#29332b'
  outline: '#849587'
  outline-variant: '#3b4a3f'
  surface-tint: '#00e38b'
  primary: '#f4fff3'
  on-primary: '#00391f'
  primary-container: '#00ff9d'
  on-primary-container: '#007143'
  inverse-primary: '#006d40'
  secondary: '#a6e6ff'
  on-secondary: '#003543'
  secondary-container: '#14d1ff'
  on-secondary-container: '#00566b'
  tertiary: '#fffaff'
  on-tertiary: '#3b2f00'
  tertiary-container: '#ffdd65'
  on-tertiary-container: '#766000'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#56ffa8'
  primary-fixed-dim: '#00e38b'
  on-primary-fixed: '#002110'
  on-primary-fixed-variant: '#00522f'
  secondary-fixed: '#b7eaff'
  secondary-fixed-dim: '#4cd6ff'
  on-secondary-fixed: '#001f28'
  on-secondary-fixed-variant: '#004e60'
  tertiary-fixed: '#ffe17a'
  tertiary-fixed-dim: '#e4c44f'
  on-tertiary-fixed: '#231b00'
  on-tertiary-fixed-variant: '#554500'
  background: '#0c150f'
  on-background: '#dae5da'
  surface-variant: '#2d3730'
  surface-glass: rgba(6, 44, 34, 0.6)
  active-glow: rgba(0, 255, 157, 0.15)
  border-low-opacity: rgba(255, 255, 255, 0.1)
  background-deep: '#0C150F'
  text-on-surface: '#DAE5DA'
  text-muted: '#B9CBBC'
  error-accent: '#FFB4AB'
typography:
  headline-xl:
    fontFamily: Geist
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-desktop: 64px
  margin-mobile: 16px
  container-max: 1280px
---

## Brand & Style
EcoLens is a high-precision engineering dashboard designed for sustainability officers and systems engineers. The brand personality is **Technical, Translucent, and Optimistic**. 

The design style is a sophisticated **Cyber-Glassmorphism**. It blends the structural precision of a technical dashboard with the ethereal quality of glassmorphism. It uses deep, dark green "Obsidian" surfaces as a base, contrasted by high-vibrancy "Neon Mint" accents. The emotional goal is to make complex ESG data feel tangible and under control, evoking a sense of "Clean-Tech Futurism" through backdrop blurs, subtle glow effects, and crisp typography.

## Colors
The palette is rooted in a **Dark Fidelity** scheme. 
- **Primary (#00FF9D):** Used for critical data visualizations, success states, and primary actions. It should often be accompanied by a subtle outer glow.
- **Secondary (#00D1FF):** Used for secondary data streams and auxiliary interactive elements.
- **Surface Strategy:** The UI does not use solid blacks. Instead, it uses a deep "Forest Black" (#0C150F). Layers are built using semi-transparent glass containers (`rgba(6, 44, 34, 0.6)`) to allow background depth to bleed through.
- **Status Colors:** Use high-saturation variants for "Live" indicators and error states to ensure they pop against the dark, desaturated background.

## Typography
The system uses a dual-font approach to balance technical precision with readability.
- **Geist** is the "Technical Driver." It is used for all headlines, labels, and numerical data to provide a modern, mono-spaced feel without the legibility issues of a true monospace font.
- **Inter** is the "System Utility." It is used for all long-form body text and interface descriptions to ensure high readability at small sizes.
- **Styling Note:** Labels should frequently use uppercase with increased letter spacing (5%) to denote metadata or category headers.

## Layout & Spacing
The layout follows a **Hybrid Fixed-Fluid Grid** model.
- **Sidebar:** A fixed 256px (w-64) sidebar handles primary navigation.
- **Main Content:** A fluid area that centers its content within a `1280px` max-width container.
- **Grid:** A 12-column system is used for dashboard widgets. Common spans are 4-columns for circular gauges and 8-columns for wide-format charts.
- **Rhythm:** A base unit of `4px` governs all spacing. Margins are generous (`64px` on desktop) to allow the "glass" cards enough room to feel distinct from the background.

## Elevation & Depth
Depth is created through **Luminance and Blur**, not traditional black shadows.
- **Level 0 (Background):** Deepest Forest Black (#0C150F).
- **Level 1 (Navigation/Top Bar):** `backdrop-blur-md` with 40% opacity surfaces. Use a subtle `1px` white border at 5% opacity to define edges.
- **Level 2 (Cards):** The "Glass Card" effect. Use `backdrop-blur-xl`, a slightly greener tint (`rgba(6, 44, 34, 0.6)`), and a `1px` border at 10% opacity.
- **Level 3 (Interactions/Active States):** Elements at this level emit light. Use "Active Glow" box shadows: `0 0 20px rgba(0, 255, 157, 0.15)`.

## Shapes
The shape language is **Structured but Approachable**. 
- Standard components (Buttons, Cards, Inputs) use a `0.5rem` (8px) base radius.
- Larger sections and dashboard widgets scale up to `0.75rem` (12px).
- Search bars and timeframe toggles utilize "Full" roundedness (Pill-shape) to distinguish them as high-frequency utility tools.
- Icons should use the "Material Symbols Outlined" set with a weight of 400 for a consistent, light-weight technical feel.

## Components
- **Buttons:** 
  - *Primary:* Solid Neon Mint background with dark Forest Black text. High-boldness labels.
  - *Secondary:* Ghost style with 10% white borders and subtle hover transitions to mint borders.
- **Cards (Glass-Card):** Must include `backdrop-filter: blur(16px)` and a thin, low-opacity border. Padding is strictly `32px` (p-8) for dashboard widgets.
- **Inputs:** Dark backgrounds (`black/20`) with pill-shaped borders. Focus states should transition the border color to Primary Mint.
- **Toggles:** Use a "Segmented Control" style. Active segments take the Primary Mint background with dark text, while inactive segments remain transparent with muted text.
- **Data Viz:** 
  - Charts use "Animate Dash" stroke effects for a "building" visual on load.
  - Sparklines should include a vertical gradient fill from Primary Mint (30% opacity) to Transparent.
- **Badges:** Use "Glow" filters (drop-shadow) for verified or high-status badges to make them appear self-illuminated.