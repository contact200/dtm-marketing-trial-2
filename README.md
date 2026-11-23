# DateTheMoment / TRIAL SOCIAL STUDIO

Separate experimental marketing studio for DateTheMoment. Based on the same automation architecture as the Kosówka project, with **new sports-marketing concepts and a DateTheMoment design language**.

**Outputs:** 13-second 9:16 MP4, original soundtrack, JPEG cover, English caption with hashtags, and JSON metadata. **7 distinct visual concepts × 4 copy variants = 28 combinations.** This is a finite deterministic rotation, not an AI-powered never-repeating concept generator.

**Colors:** white, black, royal blue with occasional teal or orange — never green. Motion graphics contain no synthetic people, faces or hands. Approved sports photographs can be used in full-bleed mode.

## First reel (works on iPad)

Open [GitHub Actions](https://github.com/contact200/dtm-marketing-trial-2/actions) → **DateTheMoment Trial Social Studio** → **Run workflow**. Use `concept=auto`, `visual_mode=auto`, `deliver_to_make=false`. Download the completed **dtm-trial-social** artifact: `reel.mp4`, `cover.jpg`, `caption.txt`, `payload.json`.

Scheduled generation happens **Monday, Wednesday and Friday at 15:00 UTC** (9 AM Chicago in winter, 10 AM in summer). Artifacts are drafts for review. **No auto-posting occurs.**

## 7 visual concepts
| ID | Visual mechanism |
|---|---|
| `calendar_fills` | A calendar that fills itself |
| `one_match_months` | One match. More life. |
| `club_voice` | Your club still sounds like your club |
| `time_saved` | Give the hours back |
| `media_pipeline` | From gallery to feed |
| `quiet_cadence` | Stay visible between games |
| `moments_live_on` | The moment continues |

The campaign progression is calendar tiles → one match into many assets → club voice signal → time dial → gallery-to-feed pipeline → day-to-day rhythm → sports-photo frames. They are distinct motion concepts, not re-skinned mountain ads.

## Approved photo mode

No photos required; default is abstract motion graphics. To use approved real photos, add images in `assets/photos/` and register them in `config/photos.json`:
```json
{"photos":[{"file":"assets/photos/approved-match-01.jpg","approved":true,"name":"match-01"}]}
```
You may also specify an **owner-controlled HTTPS URL** with `url`, `approved` and `name` fields. The workflow imports photos before rendering. `full_bleed_photo` requires at least one approved image. Auto mode uses full bleed for photo-centric concepts once such images exist; all other concepts remain motion graphics.

## Optional Make + Supabase approval delivery

The project runs without secrets. For a separate trial approval queue, create a **public Supabase Storage bucket** named `dtm-trial-2-public`. In repo **Settings → Secrets and variables → Actions**, add:
- `DTM_TRIAL_SUPABASE_URL` (secret)
- `DTM_TRIAL_SUPABASE_SERVICE_ROLE_KEY` (secret, do not commit)
- `DTM_TRIAL_MAKE_WEBHOOK_URL` (secret, **new trial webhook**, not the production hook)

Optional repo variables: `DTM_TRIAL_SUPABASE_BUCKET=dtm-trial-2-public`, and `DTM_TRIAL_AUTO_DELIVER_TO_MAKE=true` to send scheduled drafts for approval. **Leave auto delivery off** until the Make scenario accepts drafts safely. Run manually with `deliver_to_make=true` to upload MP4/JPG to the separate public bucket and post a JSON review request containing `video_url`, `cover_url`, `caption`, `campaign_id`, `visual_mode`, `approval_required=true`, and `status=pending_approval`. The public URLs are only real after successful upload. Source photos are never sent to the public bucket. Do not connect this Make webhook directly to an Instagram Publish module.

## Local test
Python 3.12 + FFmpeg:
```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/render.py --concept calendar_fills --visual-mode motion_graphic --output outputs/test
python scripts/render.py --concept club_voice --no-video --size 720x1280 --output outputs/preview
```

Production repo `datethemoment-motion` is unchanged, with no shared secrets or workflow changes.

**You live the moment. DateTheMoment makes sure it doesn't disappear.**
