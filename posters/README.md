# 9 November — Allama Iqbal Day Poster

Premium 4:5 editorial poster celebrating **Allama Muhammad Iqbal Day**.

## Deliverables

| File | Size | Use |
| --- | --- | --- |
| `iqbal_day_9nov.png` | 1600 × 2000 | Master file, print / archive |
| `iqbal_day_9nov.jpg` | 1600 × 2000 | High-quality JPEG master (print) |
| `iqbal_day_9nov_1080x1350.png` | 1080 × 1350 | Instagram / Facebook / school pages |
| `iqbal_day_9nov_social.jpg` | 1080 × 1350 | Social-ready JPEG (small file) |

4:5 vertical, exactly the Instagram portrait ratio.

## Composition

- **Allama Iqbal** in his iconic black sherwani and Jinnah-style karakul cap,
  three-quarter profile, gazing toward the sunrise horizon.
- **Badshahi Mosque**, **Minar-e-Pakistan** and the old Lahore skyline emerging
  through golden morning mist.
- **Shaheen falcon** soaring backlit on the right — the symbol of *Khudi*,
  courage and flight.
- A faint, ghosted Nastaliq *خودی* (Khudi) in the open sky; a luminous sweep of
  emerald and white silk as an abstract flag accent.
- Palette: emerald, royal blue, gold/champagne, cream white; cinematic grade,
  volumetric light, bloom, film grain, and a gold editorial hairline frame.

## Typography (all real, shaped text — not AI-rendered letters)

| Element | Face | Text |
| --- | --- | --- |
| Date | Cinzel (500, letterspaced) | `9 NOVEMBER` |
| Title | Cinzel (900) | `IQBAL DAY` |
| Urdu heading | Noto Nastaliq Urdu (600) | `یومِ اقبال` |
| Couplet | Noto Nastaliq Urdu (600) | `خودی کو کر بلند اتنا کہ ہر تقدیر سے پہلے` / `خدا بندے سے خود پوچھے، بتا تیری رضا کیا ہے` |
| Tagline | Cormorant Garamond (400) | `Dream • Believe • Rise` |

The Urdu is shaped with **HarfBuzz** (real Nastaliq joining and ligatures) and
drawn as font outlines, so the calligraphy is orthographically correct and
crisp at any size — no misspellings, no broken joins, no cartoon lettering.

## Rebuilding

```bash
pip install pillow numpy matplotlib uharfbuzz freetype-py fonttools

# 1. artwork plate (text-free cinematic background+portrait)
#    -> posters/plate.png
# 2. instantiate static weights from the variable fonts
#    -> assets/fonts/static/*.ttf
# 3. compose
python posters/poster.py
```

- `posters/typography.py` — HarfBuzz shaping + glyph outline extraction
- `posters/render.py` — vector → raster masks, gradients, glows, grain
- `posters/poster.py` — full art direction, grade, and type lockup

Fonts (SIL Open Font License) live in `assets/fonts/`.

---

## Teacher recruitment ads (Meta)

See `hiring/README.md`. Built by `posters/hiring_ad.py` from
`posters/hiring_plate.png`; outputs 1080×1080 and 1080×1350 with a reserved
logo box (top right) and a phone/email footer bar.
