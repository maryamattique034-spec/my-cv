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
    return sec(
        "Summary",
        f"<p>{e(d['summary'])}</p>"
    ) if d.get("summary") else ""


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
        head = e(x["name"])

        if x.get("tech"):
            head += f' <span class="tech">| {e(x["tech"])}</span>'

        if x.get("link"):
            head += (
                f' <a href="{e(x["link"])}">'
                f'{e(x["link"].replace("https://", ""))}'
                f'</a>'
            )

        out += item(
            head,
            "",
            "",
            "",
            ul(x.get("bullets"))
        )

    return sec("Projects", out)


def education(d):
    out = ""

    for x in d.get("education", []):
        out += item(
            e(x["institution"]),
            x.get("period", ""),
            x.get("degree", ""),
            x.get("location", ""),
            ul(x.get("details"))
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

    parts = [
        e(c[k])
        for k in ("location", "phone", "email")
        if c.get(k)
    ]

    parts += [
        f'<a href="{e(l["url"])}">{e(l["label"])}</a>'
        for l in c.get("links", [])
    ]

    return (
        f'<header>'
        f'<h1>{e(d["name"])}</h1>'
        f'<div class="title">{e(d.get("title", ""))}</div>'
        f'<div class="contact">{" &nbsp;|&nbsp; ".join(parts)}</div>'
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