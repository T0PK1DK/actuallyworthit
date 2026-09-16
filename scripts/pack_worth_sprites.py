#!/usr/bin/env python3
"""Build img/worth/sprites from the live role PNGs (same line-blob art)."""
from pathlib import Path
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
WORTH = ROOT / "img" / "worth"
SPRITES = WORTH / "sprites"
THRESH = 90


def load(name: str) -> Image.Image:
    return Image.open(WORTH / name).convert("RGB")


def arr(im: Image.Image) -> np.ndarray:
    return np.array(im)


def dark_mask(a: np.ndarray, thresh: int = THRESH) -> np.ndarray:
    return a.mean(axis=2) < thresh


def flood(open_mask: np.ndarray, seed_yx: tuple[int, int]) -> np.ndarray:
    h, w = open_mask.shape
    vis = np.zeros_like(open_mask, dtype=bool)
    q = deque([seed_yx])
    vis[seed_yx] = True
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not vis[ny, nx] and open_mask[ny, nx]:
                vis[ny, nx] = True
                q.append((ny, nx))
    return vis


def dilate(mask: np.ndarray, size: int = 21) -> np.ndarray:
    if size % 2 == 0:
        size += 1
    im = Image.fromarray((mask.astype(np.uint8) * 255))
    return np.array(im.filter(ImageFilter.MaxFilter(size=size))) > 127


def body_parts(im: Image.Image):
    a = arr(im)
    dark = dark_mask(a)
    seed = None
    for y in range(360, 500):
        if not dark[y, 360]:
            seed = (y, 360)
            break
    if seed is None:
        seed = (400, 360)
    interior = flood(~dark, seed)
    body = dilate(interior, 21)
    outside = dark & ~body
    return a, dark, interior, body, outside


def ink_region(a: np.ndarray, binary: np.ndarray, grow: int = 5) -> np.ndarray:
    return dilate(binary, grow) & (a.mean(axis=2) < 245)


def whiteout(a: np.ndarray, mask: np.ndarray) -> None:
    a[mask] = 255


def stamp(dst: np.ndarray, src: np.ndarray, mask: np.ndarray, dy: int = 0, dx: int = 0) -> None:
    if dy == 0 and dx == 0:
        dst[mask] = src[mask]
        return
    ys, xs = np.where(mask)
    ny, nx = ys + dy, xs + dx
    keep = (ny >= 0) & (ny < dst.shape[0]) & (nx >= 0) & (nx < dst.shape[1])
    dst[ny[keep], nx[keep]] = src[ys[keep], xs[keep]]


def save(a: np.ndarray, name: str) -> None:
    SPRITES.mkdir(parents=True, exist_ok=True)
    Image.fromarray(a).save(SPRITES / name, optimize=True)


def copy_role(src: str, dest: str) -> None:
    Image.open(WORTH / src).convert("RGB").save(SPRITES / dest, optimize=True)


def side(mask: np.ndarray, which: str, y_max: int = 540) -> np.ndarray:
    out = mask.copy()
    out[y_max:, :] = False
    if which == "L":
        out[:, 360:] = False
    else:
        out[:, :360] = False
    return out


def main() -> None:
    SPRITES.mkdir(parents=True, exist_ok=True)
    blush_im = load("worth-it-conditional.png")
    shrug_im = load("shrug-depends.png")

    copy_role("neutral-gutter.png", "worth-neutral.png")
    copy_role("thinker-tradeoffs.png", "worth-thinking.png")
    copy_role("shrug-depends.png", "worth-shrug.png")
    copy_role("worth-it-conditional.png", "worth-happy.png")
    copy_role("judge-skeptical.png", "worth-grumpy.png")
    copy_role("unimpressed-skip.png", "worth-smug.png")
    blush_im.resize((1440, 1440), Image.Resampling.LANCZOS).save(
        SPRITES / "worth-blush-smile.png", optimize=True
    )

    blush_a, _, _, blush_body, blush_out = body_parts(blush_im)
    shrug_a, _, _, _, shrug_out = body_parts(shrug_im)

    # Wave: blush body + left hanging arm + shrug's raised right arm.
    wave = blush_a.copy()
    whiteout(wave, ink_region(blush_a, side(blush_out, "R"), grow=11))
    raised = side(shrug_out, "R")
    raised[400:, :] = False  # keep the up-stroke, drop the side stub
    raised_ink = ink_region(shrug_a, raised, grow=5)
    stamp(wave, shrug_a, raised_ink)
    wave[blush_body] = blush_a[blush_body]
    feet = blush_out.copy()
    feet[:540, :] = False
    left_and_feet = ink_region(blush_a, side(blush_out, "L") | feet, grow=7)
    stamp(wave, blush_a, left_and_feet)
    keep = blush_body | left_and_feet | raised_ink
    stray = (wave.mean(axis=2) < 245) & ~keep
    wave[stray] = 255
    save(wave, "worth-wave.png")
    save(wave, "worth-thumbs-up.png")

    # Jumping: same shrug art, shifted up
    jump = np.full_like(shrug_a, 255)
    stamp(jump, shrug_a, shrug_a.mean(axis=2) < 245, dy=-40)
    save(jump, "worth-jumping.png")

    # Remaining named poses stay on-model copies of live role art
    # (the attached sprite pack was not in this workspace).
    copy_role("thinker-tradeoffs.png", "worth-look-up.png")
    copy_role("worth-it-conditional.png", "worth-hearts.png")
    copy_role("worth-it-conditional.png", "worth-surprised.png")


if __name__ == "__main__":
    main()
