# EditorialMotionV1 — standalone
11-second, 9:16 Remotion TSX rendition of the provided editorial motion reference. This folder is independent of the Python trial generator, other concepts and repo preferences.

Its six-scene storyboard is in `src/EditorialMotionV1.tsx`. Source photos are taken from DateTheMoment's existing online portfolio, listed in `photo-sources.json`. The Node fetch script downloads them into this folder's local `public/photos/` for deterministic rendering. The original source component is kept intact.

To render locally: `npm install && node scripts/fetch-photos.mjs && npm run render`

Telegram review uses a separate, push-triggered transport workflow in `contact200/datethemoment-motion`, which only borrows the existing Make/Telegram webhook secret and does not inherit that repo's creative settings or scheduled workflows.
