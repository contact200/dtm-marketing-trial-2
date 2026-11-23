# DateTheMoment / TRIAL SOCIAL STUDIO

## Send trial reels to your existing Telegram bot (no new secrets)

**[Run DTM Trial 2 → Existing Make / Telegram](https://github.com/contact200/datethemoment-motion/actions/workflows/dtm-trial-2-to-make.yml)** in your existing `datethemoment-motion` repository. Click **Run workflow**, choose a concept or `auto`, and the main GitHub workflow checks out this trial generator, renders the video, and sends its MP4 + matching caption straight to your **existing Make review webhook**. Make performs Supabase upload and Telegram notification exactly as it does for the main DateTheMoment and Kosówka review videos.

This project stays the creative source; the main repository owns the **Monday/Wednesday/Friday delivery schedule** and the existing Make webhook secret. No trial Supabase keys, new buckets, or duplicated Telegram settings are needed.

The workflow in **this trial repository is preview-only** if you just want to download the MP4. It does not attempt delivery or require credentials. Both the main and preview workflows pass the GitHub run number to rotate visual concepts across runs.

Creative direction: Kosówka-level visual simplicity, **not** Kosówka pacing or scenery. This is fast, bold, white-first DateTheMoment marketing: sports photos becoming weeks of content, captions from a PDF schedule, scheduling and posting all within a background automation.

**Outputs:** 13-second 9:16 MP4, custom rhythmic sound effects, JPEG cover, English caption with hashtags, and JSON metadata. **7 different graphic concepts × 4 unique copy variants = 28 combinations.** Main-repo GitHub run number selects the next concept, so consecutive runs no longer repeat the same scene family. This is a finite deterministic rotation, not an AI-powered infinite-concept engine.

**Colors:** spacious white, black lettering, royal blue highlights. Only occasionally teal or orange; never green. **Four quick, legible story beats instead of slow ambient fades**. No mountains, ski footage, winter imagery, fake people, faces or hands. Approved sports photos can optionally replace graphic diagram backdrops.

## First reel (works on iPad)

To download a preview only, open [this repo's GitHub Actions](https://github.com/contact200/dtm-marketing-trial-2/actions) → **DTM Trial 2 · Preview Only** → **Run workflow**. For Telegram use the main-repository workflow linked above. The preview artifact contains: `reel.mp4`, `cover.jpg`, `caption.txt`, `payload.json`.

Scheduled generation and Make delivery happen in the **main repo's new workflow**, Monday, Wednesday and Friday at 15:00 UTC (9 AM Chicago in winter, 10 AM in summer). Artifacts are drafts for review. **No auto-posting occurs.**

## 7 visual concepts
| ID | Visual mechanism |
|---|---|
| `calendar_fills` | Content calendar rapidly fills with scheduled photo posts |
| `one_match_months` | One sports gallery expands into weeks of posts |
| `club_voice` | PDF schedule becomes team-specific captions |
| `time_saved` | Repetitive marketing tasks become background jobs |
| `media_pipeline` | PHOTOS → CAPTIONS → SCHEDULE → POST |
| `quiet_cadence` | Background publishing rhythm keeps the calendar active |
| `moments_live_on` | Match moments transform into an ongoing social feed |

All seven mechanisms are visually distinct: calendar-grid population, gallery multiplication, PDF-to-caption conversion, task-list completion, a four-stage publishing pipeline, weekly publishing rhythm, and gallery-to-feed transfer. The branding and typography are consistent. **None are travel, mountain or lodging ads.**

## Approved photo mode

No photos required; default is abstract motion graphics. To use approved real photos, add images in `assets/photos/` and register them in `config/photos.json`:
```json
{"photos":[{"file":"assets/photos/approved-match-01.jpg","approved":true,"name":"match-01"}]}
```
You may also specify an **owner-controlled HTTPS URL** with `url`, `approved` and `name` fields. The workflow imports photos before rendering. `full_bleed_photo` requires at least one approved image. Auto mode uses full bleed for photo-centric concepts once such images exist; all other concepts remain motion graphics.

## Existing Make + Supabase + Telegram wiring

**This trial does not upload media to Supabase by itself.** Instead, the main repo's [DTM Trial 2 → Existing Make / Telegram](https://github.com/contact200/datethemoment-motion/actions/workflows/dtm-trial-2-to-make.yml) job sends the rendered MP4 and caption as `multipart/form-data` to the **already-working** `MAKE_MOTION_REVIEW_WEBHOOK_URL`. The receiver's existing Supabase Upload File module creates the public HTTPS video URL and its Telegram module sends a review notification.

Make receives `video`, `concept_id`, `creative_angle`, `creative_hook`, `on_screen_text`, `social_caption`, `visual_mode`, `render_run_id`, `status=READY_FOR_REVIEW`, and `video_url=pending_make_upload` (compatibility field until Make creates the real public URL). These values match the currently operational main workflow's form schema.

Video delivery is for **review only**; do not connect the review receiver directly to an Instagram publishing module.

## Local test
Python 3.12 + FFmpeg:
```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/render.py --concept calendar_fills --visual-mode motion_graphic --output outputs/test
python scripts/render.py --concept club_voice --no-video --size 720x1280 --output outputs/preview
```

The main `datethemoment-motion` repository now contains one additional isolated wrapper workflow; its existing publishing workflows are unchanged.

**You live the moment. DateTheMoment makes sure it doesn't disappear.**
