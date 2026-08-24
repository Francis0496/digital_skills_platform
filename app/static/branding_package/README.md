# Digital Skills Platform Branding Package

## Assets
- `logo-full.svg`: primary horizontal logo for light navigation/header surfaces.
- `logo-full-white.svg`: logo for dark navy/purple backgrounds.
- `logo-icon.svg`: compact square icon for favicon, mobile navigation, and small brand placements.
- `logo-full.png`, `logo-full-white.png`, `logo-icon.png`: raster fallbacks.
- `favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`, `favicon-48x48.png`, `favicon-64x64.png`, `favicon-128x128.png`, `favicon-256x256.png`: browser/app icons.
- `brand-tokens.css`: canonical brand colour and radius tokens.
- `brand-guideline-reference.png`: visual direction reference for Codex/design review.

## Brand palette
- Primary Indigo: `#4F46E5`
- Deep Navy: `#0F172A`
- Teal: `#14B8A6`
- Sky: `#0EA5E9`
- Amber: `#F59E0B`
- Success: `#10B981`
- Danger: `#EF4444`
- Text: `#111827`
- Muted: `#64748B`
- Border: `#E2E8F0`
- Surface: `#F8FAFC`

## Codex rules
1. Use `logo-full.svg` in the public navbar on light backgrounds.
2. Use `logo-full-white.svg` on dark backgrounds.
3. Use `logo-icon.svg` or favicon assets for compact contexts.
4. Do not distort, recolour, rotate, or add effects to the logo.
5. Maintain clear space around the logo.
6. Use the supplied palette consistently across Tailwind configuration/components.
7. Prefer SVG in the interface and PNG only where SVG is unsuitable.
8. Do not introduce a second brand palette without approval.

## Suggested Flask placement
Copy this package into `app/static/brand/`. In `base.html`, reference the favicon with `url_for('static', filename='brand/favicon-32x32.png')` and the navbar logo with `url_for('static', filename='brand/logo-full.svg')`.
