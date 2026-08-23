# Actually Worth It

Static editorial starter for [actuallyworthit.com](https://actuallyworthit.com). Deploy on **Cloudflare Pages** as a plain HTML site (no build step).

## Deploy (Cloudflare Pages)

1. Connect the GitHub repo or upload this folder.
2. Build command: leave empty.
3. Output directory: `/` (project root).
4. After the first deploy, add a custom domain `actuallyworthit.com`.

## Affiliate links

Buttons use `href="#"` and `data-asin="..."`. When you have an Amazon Associates ID, replace `#` with tagged `https://www.amazon.com/dp/ASIN?tag=YOURTAG-20` (or your preferred short-link pattern).

## Editorial rules used here

- No invented prices, star ratings, or customer quotes.
- Copy is labeled sourced draft where we did not hands-on test.
- FTC-style disclosure is in the footer and on every review.

## Local preview

Any static server works, e.g. `npx serve .` or `python3 -m http.server 8080`.
