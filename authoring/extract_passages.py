"""Extract plain-text passages from an Amharic Wikipedia dump (author-side).

Usage: extract_passages.py AMWIKI_PAGES_ARTICLES_XML_BZ2 OUT_JSONL

Each passage: {"pid", "title", "text"}: up to 80 words, cut at sentence ends (።), from the
article's prose. Templates, tables, references, files and categories are removed; links keep
their visible text. Text is kept exactly as Wikipedia writes it (no letter folding)."""
import bz2
import json
import re
import sys
import xml.etree.ElementTree as ET

ETHIOPIC = re.compile(r"[ሀ-፿]")


def strip_templates(t):
    out, depth, i = [], 0, 0
    while i < len(t):
        if t.startswith("{{", i):
            depth += 1; i += 2
        elif t.startswith("}}", i) and depth:
            depth -= 1; i += 2
        else:
            if not depth:
                out.append(t[i])
            i += 1
    return "".join(out)


def clean(wikitext):
    t = strip_templates(wikitext)
    t = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", " ", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"\{\|.*?\|\}", " ", t, flags=re.S)                     # tables
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\[\[(?:[^\]|]*:)[^\]]*\]\]", " ", t)                   # files, categories, interwiki
    t = re.sub(r"\[\[([^\]|]*)\|([^\]]*)\]\]", r"\2", t)
    t = re.sub(r"\[\[([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"\[https?://\S+\s*([^\]]*)\]", r"\1", t)
    t = re.sub(r"'{2,}", "", t)
    paras = []
    for line in t.split("\n"):
        line = line.strip()
        if not line or line.startswith(("=", "*", "#", "|", "!", ":", ";", "{", "}")):
            continue
        line = re.sub(r"\s+", " ", line)
        if len(ETHIOPIC.findall(line)) >= 0.6 * len(re.sub(r"[\s\d\W]", "", line) or "x"):
            paras.append(line)
    return paras


def passages(paras, limit=80):
    out = []
    for p in paras:
        sents = [s.strip() + "።" for s in p.split("።") if s.strip()]
        cur = []
        for s in sents:
            words = s.split()
            if cur and len(cur) + len(words) > limit:
                out.append(" ".join(cur)); cur = []
            cur += words
        if len(cur) >= 12:
            out.append(" ".join(cur))
    return [x for x in out if 12 <= len(x.split()) <= 100]


def main(dump, out_path):
    n = 0
    with open(out_path, "w", encoding="utf-8") as out:
        for _, el in ET.iterparse(bz2.open(dump), events=("end",)):
            if not el.tag.endswith("}page"):
                continue
            if el.find("{*}ns").text == "0":
                title = el.find("{*}title").text
                text = el.find("{*}revision/{*}text").text or ""
                if not text.lstrip().startswith("#"):
                    for k, p in enumerate(passages(clean(text))):
                        out.write(json.dumps({"pid": f"{n:06d}", "title": title, "text": p}, ensure_ascii=False) + "\n")
                        n += 1
            el.clear()
    print("passages", n)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
