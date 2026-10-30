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
├── styles.css              # Shared look: top bar, buttons, pickers, dialogs
├── kit.js                  # Shared helpers: best scores, end-of-game dialog, confetti
├── icons/                  # 180/192/512 PNG icons (one set per game)
├── generate_icons.py       # Re-run with PIL to regenerate icons
├── tools/trivoca_kids_words.py  # Kid word lists + hints; rebuilds Trivoca's word data
└── games/
    ├── memory.html         # Memory Match (flip pairs)
    ├── target.html         # Tap the Target (reflexes, 30s)
    ├── sequence.html       # Color Sequence (Simon-style)
    ├── trivoca.html        # Trivoca Kids (word guess with hints — PT-BR, ES-LA, EN-US; 4 or 5 letters)
    └── imposter.html       # Imposter (pass-the-iPad party game)
```

Each game is one HTML file that uses the shared `styles.css` and `kit.js`.
Add a new game by dropping a new `games/<name>.html` and adding a tile in
`index.html` plus an entry in `sw.js` (the `CORE_ASSETS` list) so it works
offline.

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

The app loads fresh files whenever the iPad is online and falls back to the
saved copy offline, so updates show up on the next launch. Bump
`CACHE_VERSION` in `sw.js` when you add or rename files so the offline copy
is rebuilt.

## Adding more games

1. Copy `games/memory.html` as a template (top bar, stats, `Kit.dialog`,
   `Kit.record` for best scores).
2. Update `<title>`, the `--game` / `--game-2` colors on `<body>`,
   apple-touch-icon, and the top bar.
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
- Icons are drawn by `generate_icons.py` with the system emoji font
  (Apple Color Emoji or Noto Color Emoji); without one it falls back to a
  plain circle.
- Best scores and the Imposter roster are saved on each iPad (localStorage).
- Everything is plain HTML/CSS/JS, no build step, no dependencies.
  (Imposter loads two web fonts when online and falls back to built-in ones.)

## Trivoca Kids word lists

The answer words, with the category shown by the first 💡 hint (the emoji
is kept in the list but not shown — it gave the word away),
live in `tools/trivoca_kids_words.py`. To add or change words, edit the list
for that language (`word emoji category`, one per line, written with its
accents), then rebuild the data inside `games/trivoca.html`:

```bash
pip install wordfreq
python3 tools/trivoca_kids_words.py
```

Bump `CACHE_VERSION` in `sw.js` afterwards so the iPads pick it up.
