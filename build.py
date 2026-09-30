"""Build CVs: reads data/*.json -> writes dist/<name>.html (+ dist/index.html).
Usage: python build.py
Then open dist/<name>.html in Chrome -> Ctrl+P -> Save as PDF (A4, margins: None, untick headers/footers).
"""

import json
import pathlib
from html import escape as e

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"
CSS = (ROOT / "cv.css").read_text(encoding="utf-8")


def short(url):
    return (url.replace("https://", "").replace("http://", "")
               .replace("www.", "").rstrip("/"))


def ul(items):
    return (
        "<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"
        if items
        else ""
    )


def sec(title, body):
    return f"<section><h2>{e(title)}</h2>{body}</section>" if body else ""


def item(head, period="", sub="", location="", body=""):
    period = f'<span class="meta">{e(period)}</span>' if period else ""
    sub = f'<div class="sub">{e(sub)}</div>' if sub else ""
    location = f'<div class="sub">{e(location)}</div>' if location else ""

    return (
        f'<div class="item">'
        f'<div class="row"><h3>{head}</h3>{period}</div>'
        f'{sub}{location}{body}'
        f'</div>'
    )


def summary(d):
    return f'<p class="summary">{e(d["summary"])}</p>' if d.get("summary") else ""

def experience(d):
    out = ""

    for x in d.get("experience", []):
        head = f"{e(x['role'])} &bull; {e(x['company'])}"

        out += item(
            head,
            x.get("period", ""),
            "",
            x.get("location", ""),
            ul(x.get("bullets"))
        )

    return sec("Work Experience", out)


def projects(d):
    out = ""

    for x in d.get("projects", []):
        link = ""
        if x.get("link"):
            link = f'<a class="meta" href="{e(x["link"])}">{e(short(x["link"]))}</a>'

        tech = f'<div class="sub">{e(x["tech"])}</div>' if x.get("tech") else ""

        out += (
            f'<div class="item">'
            f'<div class="row"><h3>{e(x["name"])}</h3>{link}</div>'
            f'{tech}{ul(x.get("bullets"))}'
            f'</div>'
        )

    return sec("Projects", out)


def education(d):
    out = ""

    for x in d.get("education", []):
        period = f'<span class="meta">{e(x["period"])}</span>' if x.get("period") else ""
        degree = e(x.get("degree", ""))
        location = f'<span class="meta">{e(x["location"])}</span>' if x.get("location") else ""

        out += (
            f'<div class="item">'
            f'<div class="row"><h3>{e(x.get("institution") or x.get("school", ""))}</h3>{period}</div>'
            f'<div class="row"><span class="sub">{degree}</span>{location}</div>'
            f'{ul(x.get("details"))}'
            f'</div>'
        )

    return sec("Education", out)

def skills(d):
    rows = "".join(
        f'<div class="skill"><b>{e(g["label"])}:</b> '
        f'{e(", ".join(g["items"]))}</div>'
        for g in d.get("skills", [])
    )

    return sec("Skills", rows)


def languages(d):
    return sec(
        "Languages",
        ul([
            f"{l['name']} - {l['level']}"
            for l in d.get("languages", [])
        ])
    )


def certifications(d):
    return sec(
        "Licenses & Certifications",
        ul(d.get("certifications"))
    )


RENDERERS = {
    "summary": summary,
    "experience": experience,
    "projects": projects,
    "education": education,
    "skills": skills,
    "languages": languages,
    "certifications": certifications,
}

DEFAULT_ORDER = [
    "summary",
    "experience",
    "projects",
    "education",
    "skills",
    "languages",
    "certifications",
]

def header(d):
    c = d.get("contact", {})
    sep = " &nbsp;|&nbsp; "

    line1 = sep.join(e(c[k]) for k in ("location", "phone", "email") if c.get(k))
    line2 = sep.join(
        f'<a href="{e(l["url"])}">{e(short(l["url"]))}</a>'
        for l in c.get("links", [])
    )

    return (
        f'<header>'
        f'<h1>{e(d["name"])}</h1>'
        f'<div class="title">{e(d.get("title", ""))}</div>'
        f'<div class="contact">{line1}</div>'
        f'<div class="contact">{line2}</div>'
        f'</header>'
    )


def render(d):
    order = d.get("section_order", DEFAULT_ORDER)

    body = "".join(
        RENDERERS[s](d)
        for s in order
    )

    return (
        f'<!doctype html>'
        f'<html lang="en">'
        f'<head>'
        f'<meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{e(d["name"])} - {e(d.get("title", "CV"))}</title>'
        f'<style>{CSS}</style>'
        f'</head>'
        f'<body>'
        f'<main class="page">'
        f'{header(d)}'
        f'{body}'
        f'</main>'
        f'</body>'
        f'</html>'
    )


def main():
    DIST.mkdir(exist_ok=True)

    links = []

    for f in sorted((ROOT / "data").glob("*.json")):
        print(f"Processing: {f}")

        d = json.loads(
            f.read_text(encoding="utf-8")
        )

        output_file = DIST / f"{f.stem}.html"

        output_file.write_text(
            render(d),
            encoding="utf-8"
        )

        links.append(
            f'<li><a href="{f.stem}.html">'
            f'{e(d.get("title", f.stem))}'
            f'</a></li>'
        )

        print(f"built {output_file}")

    (DIST / "index.html").write_text(
        f'<!doctype html>'
        f'<meta charset="utf-8">'
        f'<title>CVs</title>'
        f'<ul>{"".join(links)}</ul>',
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()