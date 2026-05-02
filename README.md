# Kids Games — a tiny PWA for the iPad

A small offline collection of ad-free minigames you can install on your kids'
iPads as if it were a native app. No App Store, no developer account, no ads,
no tracking, no network calls after the first load.

## What's inside

```
kids-games/
├── index.html              # Launcher — the "app" home screen
├── manifest.webmanifest    # PWA manifest (installable metadata)
├── sw.js                   # Service worker (offline cache)
├── styles.css              # Shared styles
├── icons/                  # 180/192/512 PNG icons (one set per game)
├── generate_icons.py       # Re-run with PIL to regenerate icons
└── games/
    ├── memory.html         # Memory Match (flip pairs)
    ├── target.html         # Tap the Target (reflexes, 30s)
    └── sequence.html       # Color Sequence (Simon-style)
```

Each game is one self-contained HTML file. Add a new game by dropping a new
`games/<name>.html` and adding a tile in `index.html` plus an entry in
`sw.js` (the `CORE_ASSETS` list) so it works offline.

## Try it locally

From the `kids-games/` folder:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000> on your laptop. To test on the iPad on the
same Wi-Fi: find your laptop's LAN IP (e.g. `192.168.1.42`) and visit
`http://192.168.1.42:8000` in Safari on the iPad.

> Service workers require **HTTPS** or `localhost`. Over LAN HTTP the games
> still work, but offline caching and "Add to Home Screen" behave best once
> you deploy to a real HTTPS host (next section).

## Deploy (free, HTTPS, takes ~5 minutes)

The simplest path: **GitHub Pages**.

1. Create a new GitHub repo (e.g. `kids-games`).
2. From this folder:
   ```bash
   git init
   git add .
   git commit -m "initial games"
   git branch -M main
   git remote add origin git@github.com:YOURNAME/kids-games.git
   git push -u origin main
   ```
3. On GitHub: **Settings → Pages → Source: `main` / root**. Save.
4. Wait ~1 minute. Your site is live at
   `https://YOURNAME.github.io/kids-games/`.

Alternatives: Netlify drop, Cloudflare Pages, Vercel — all free, all HTTPS.

## Install on the iPad

1. Open the deployed URL in **Safari** (not Chrome — only Safari can install
   PWAs to the home screen on iPadOS).
2. Tap the **Share** button → **Add to Home Screen**.
3. Confirm. A "Games" icon appears on the home screen.
4. Tapping it launches fullscreen, no Safari chrome, works offline after the
   first load.

To pin individual games as their own home-screen icons (one icon per game),
open each game's URL directly (e.g. `.../games/memory.html`) and Add to Home
Screen from there. Each has its own apple-touch-icon and title.

## Updating

Bump `CACHE_VERSION` in `sw.js` whenever you change cached files. Old iPads
will pick up the new version next time they have network.

## Adding more games

1. Copy one of the files in `games/` as a template.
2. Update `<title>`, theme color, apple-touch-icon, and the in-page header.
3. Add a tile in `index.html`.
4. Add the file to `CORE_ASSETS` in `sw.js` and bump `CACHE_VERSION`.
5. (Optional) Add a row to `GAMES` in `generate_icons.py` and re-run it to
   produce a fresh icon set:
   ```bash
   python3 generate_icons.py
   ```

## Notes / limitations

- iPad Safari PWAs do not get push notifications, GameCenter, or full
  background audio. Fine for offline minigames; not a full native runtime.
- The included icons are colored rounded squares with a circle (the emoji
  font path didn't render on this machine). Drop in nicer PNGs anytime —
  same filenames, same sizes.
- Everything is plain HTML/CSS/JS, no build step, no dependencies.
