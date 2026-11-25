"""Gera fotos ilustrativas (texturas) para as pedras que ainda não têm foto real.

Uso: python3 tools/gerar_texturas.py
Cria data/stones/fotos/<id>.jpg e marca no JSON da pedra "image" e "illustrative": true.
Quando chegar a foto real, basta trocar o arquivo pelo painel: o selo "Imagem ilustrativa" some
ao remover "illustrative" do JSON (o painel faz isso ao salvar uma foto nova? Não: remova à mão
ou desmarque o campo "Imagem ilustrativa" no painel).
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import zoom, gaussian_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 1800


def noise(rng, scale, octaves=5, persist=.5):
    """Ruído fractal suave (value noise) em [0,1]."""
    out = np.zeros((H, W)); amp = 1; tot = 0
    for o in range(octaves):
        gh, gw = max(2, int(H / scale * 2 ** o)), max(2, int(W / scale * 2 ** o))
        g = rng.random((gh + 1, gw + 1))
        z = zoom(g, (H / gh, W / gw), order=3)[:H, :W]
        out += z * amp; tot += amp; amp *= persist
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-9)


def hexrgb(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def mix(a, b, t):
    return a * (1 - t[..., None]) + b * t[..., None]


def marble(rng, base, base2, veins, scale=1800):
    """Mármore/lâmina: veios em cristas de ruído fractal (ridged noise)."""
    cloud = noise(rng, scale * .7, 4)
    img = mix(hexrgb(base), hexrgb(base2), cloud * .7)
    for col, strength, power, sc in veins:
        n = noise(rng, scale * sc * 1.4, 6, .55)
        n2 = noise(rng, scale * sc * .8, 5, .5)
        v = 1 - np.abs((n * .65 + n2 * .35) - .5) * 2
        v = np.clip(v, 0, 1) ** power
        img = mix(img, hexrgb(col), v * strength)
    img += ((noise(rng, 40, 2) - .5) * 8)[..., None]
    return img


def speckle(rng, base, grains, blur=.6):
    """Granito: grãos de cores sobre fundo."""
    img = np.tile(hexrgb(base), (H, W, 1)) + ((noise(rng, 200, 4) - .5) * 30)[..., None]
    for col, frac, size in grains:
        m = noise(rng, size, 2, .45)
        thr = np.quantile(m, 1 - frac)
        mask = gaussian_filter((m > thr).astype(float), min(blur, .5))
        img = mix(img, hexrgb(col), np.clip(mask, 0, 1))
    return img


def quartz(rng, base, flecks=None, glitter=0.0, var=10):
    img = np.tile(hexrgb(base), (H, W, 1)) + ((noise(rng, 260, 4) - .5) * var)[..., None]
    if flecks:
        for col, frac in flecks:
            r = rng.random((H, W)); m = gaussian_filter((r < frac).astype(float), .7) * 4
            img = mix(img, hexrgb(col), np.clip(m, 0, 1))
    if glitter:
        r = rng.random((H, W)); g = gaussian_filter((r < glitter).astype(float), .5) * 6
        img = img + np.clip(g, 0, 1)[..., None] * 170
    return img


def light(img):
    """Iluminação suave de showroom (canto superior mais claro)."""
    yy, xx = np.mgrid[0:H, 0:W]
    g = 1.06 - .12 * ((xx / W) * .4 + (yy / H) * .6)
    return img * g[..., None]


S = {
    # ArtechLâminas
    "calacatta-gold-laminas": lambda r: marble(r, "#f5f2ec", "#ebe6de", [("#b48f55", .85, 60, .9), ("#9a958e", .6, 90, .5)]),
    "carrara": lambda r: marble(r, "#eceeef", "#dde0e3", [("#8b929a", .75, 40, .5), ("#a7adb3", .5, 14, .25)]),
    "arabescato-vagli": lambda r: marble(r, "#f1f0ee", "#e3e1de", [("#5f5c59", .9, 10, .6), ("#8f8c88", .7, 30, .3)]),
    "branco-white": lambda r: marble(r, "#f7f7f5", "#efefec", [("#d6d5d1", .45, 70, .6)]),
    "nero-marquina": lambda r: marble(r, "#141414", "#1f1f1f", [("#ebe8e2", .9, 70, .7), ("#bcb8b1", .5, 25, .35)]),
    "laurent-black": lambda r: marble(r, "#1c1815", "#2a2420", [("#c8a066", .85, 35, .6), ("#e3ddd0", .6, 80, .4)]),
    "dark-tormenta": lambda r: marble(r, "#252728", "#3a3d3f", [("#dcdedf", .8, 8, .9), ("#8c9193", .6, 20, .5)]),
    "sahara-noir": lambda r: marble(r, "#121212", "#1b1a19", [("#cfa65c", .9, 55, .6), ("#efebe3", .6, 90, .45)]),
    "basalt-black": lambda r: speckle(r, "#26272a", [("#3a3b3f", .3, 20), ("#18191b", .25, 15)], 1.2),
    "cemento-grigio": lambda r: speckle(r, "#8f8d89", [("#a3a19c", .35, 60), ("#7d7b77", .3, 45), ("#b4b1ab", .08, 9)], 1.8),
    "pietra-light-grey": lambda r: marble(r, "#bebdb9", "#aaa9a5", [("#dcdad5", .6, 30, .3), ("#97958f", .45, 40, .25)]),
    "silver-grey-laminas": lambda r: marble(r, "#a7a9ab", "#8f9193", [("#e4e5e5", .75, 30, .5), ("#6c6f71", .5, 40, .35)]),
    # ArtechQuartzo
    "amarelo-quartzo": lambda r: quartz(r, "#e3b23c", [("#f3d27c", .02), ("#b9861e", .015)]),
    "amarelo-stellar": lambda r: quartz(r, "#d9a52e", [("#f0cd6e", .01)], glitter=.0016),
    "azul-stellar": lambda r: quartz(r, "#1d3f73", [("#2e5a98", .01)], glitter=.0018),
    "branco-stellar": lambda r: quartz(r, "#efefec", [("#dcdcd8", .01)], glitter=.0014),
    "cinza-stellar": lambda r: quartz(r, "#6f7174", [("#86888b", .01)], glitter=.0016),
    "preto-stellar": lambda r: quartz(r, "#121212", [("#232323", .01)], glitter=.0018),
    "vermelho-stellar": lambda r: quartz(r, "#9b1c1f", [("#b83236", .01)], glitter=.0016),
    "verde-quartzo": lambda r: quartz(r, "#3f7d4e", [("#5c9a6a", .02), ("#2b5e38", .015)]),
    "terracota": lambda r: quartz(r, "#b5562f", [("#cc714b", .02), ("#8e3e1f", .015)]),
    "liso-bege": lambda r: quartz(r, "#d9c7a8", [("#e6d8bf", .015), ("#c4ae8b", .012)], var=8),
    "super-white": lambda r: quartz(r, "#f8f8f6", [("#ececea", .008)], var=5),
    "silver-grey-quartzo": lambda r: quartz(r, "#a9abad", [("#c4c6c8", .02), ("#8b8d8f", .02)]),
    "calacatta-quartzo": lambda r: marble(r, "#f6f5f2", "#edece8", [("#8d8d8b", .7, 70, .8)]),
    "calacatta-gold-quartzo": lambda r: marble(r, "#f7f4ef", "#eee9e2", [("#c19c62", .8, 70, .85), ("#a7a39d", .45, 100, .5)]),
    # ArtechNano
    "artechnano-branco": lambda r: quartz(r, "#fbfbfa", None, var=3),
    # Pedras naturais
    "corumbazinho": lambda r: speckle(r, "#cfc6b8", [("#8a8178", .22, 13), ("#2d2a28", .08, 6), ("#e8e1d4", .25, 15)]),
    "dallas": lambda r: speckle(r, "#b9aea3", [("#3b3633", .14, 7), ("#d9d0c4", .28, 13), ("#7b6f66", .2, 10)]),
    "itaunas": lambda r: speckle(r, "#e5ddcf", [("#c8b9a2", .3, 17), ("#5d564f", .07, 6), ("#9a8a76", .15, 11)]),
    "ornamental": lambda r: speckle(r, "#c7b38f", [("#8b6f4c", .22, 13), ("#2f2925", .1, 7), ("#e4d7bf", .2, 16)]),
    "preto-sao-gabriel": lambda r: speckle(r, "#151516", [("#2c2c2e", .3, 9), ("#4a4a4c", .06, 5)], .8),
    "verde-perola": lambda r: speckle(r, "#1f2a25", [("#3f5c52", .25, 15), ("#6d8a80", .1, 8), ("#0f1512", .2, 10)]),
    "verde-ubatuba": lambda r: speckle(r, "#1c241e", [("#3d4a3c", .22, 9), ("#5d6b4e", .08, 5), ("#0d110e", .25, 8)], .8),
    "marmore-griggio": lambda r: marble(r, "#9c9894", "#8a8682", [("#d6d2cc", .65, 25, .4), ("#6a6662", .5, 35, .3)]),
    "marmore-pinta-verde": lambda r: speckle(r, "#3c5a43", [("#d9d6cc", .12, 11), ("#22362a", .3, 15), ("#7d9a80", .15, 9)]),
}


def main():
    folder = os.path.join(ROOT, "data", "stones")
    only = set(sys.argv[1:])
    for i, (sid, fn) in enumerate(sorted(S.items())):
        if only and sid not in only: continue
        p = os.path.join(folder, sid + ".json")
        d = json.load(open(p, encoding="utf-8"))
        if d.get("image") and not d.get("illustrative") and not only: continue  # já tem foto real
        rng = np.random.default_rng(1000 + i)
        img = light(fn(rng))
        im = Image.fromarray(np.clip(img, 0, 255).astype("uint8")).filter(ImageFilter.UnsharpMask(1.2, 40, 2))
        out = sid + ".jpg"
        im.save(os.path.join(folder, "fotos", out), quality=86, optimize=True)
        d["image"] = out; d["illustrative"] = True
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2); f.write("\n")
        print("ok", sid)


if __name__ == "__main__":
    main()
