"""로컬 HTML의 텍스트 구조를 파싱합니다. 수집·로그인·네트워크 코드는 없습니다."""

import re
from bs4 import BeautifulSoup

ZW = "\u200b\ufeff"
BLOCKS = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "pre", "figure", "table"]


def clean(t):
    t = t.translate({ord(c): None for c in ZW})
    t = re.sub(r"[ \t ]+", " ", t)
    return t.strip()


def one_line(t):
    return " ".join(clean(t).split())


def para_text(el):
    for br in el.find_all("br"):
        br.replace_with("\n")
    return "\n".join(clean(x) for x in el.get_text().split("\n")).strip()


def find_words(text, words):
    return [w for w in words if w in text]


def norm_dot(s):
    return s.replace("・", "·").strip()


def parse_naver(html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one(".se-title-text")
    title = one_line(title.get_text()) if title else (soup.find("meta", property="og:title") or {}).get("content", "")
    nick = soup.select_one(".nick") or soup.select_one(".blog_author")
    date_el = soup.select_one(".se_publishDate") or soup.select_one(".blog_date")
    lines, images, videos = [], [], 0
    main = soup.select_one(".se-main-container")
    if main:
        for comp in main.select(":scope > .se-component, :scope > div > .se-component"):
            cls = set(comp.get("class", []))
            if cls & {"se-text", "se-sectionTitle"}:
                for p in comp.select(".se-text-paragraph"):
                    lines.append(para_text(p))
            elif "se-quotation" in cls:
                q = comp.select_one(".se-quote")
                cite = comp.select_one(".se-cite")
                body = para_text(q) if q else para_text(comp)
                cite_t = one_line(cite.get_text()) if cite else ""
                lines.append("> " + body.replace("\n", "\n> ") + (f" — {cite_t}" if cite_t else ""))
            elif cls & {"se-image", "se-imageStrip", "se-imageGroup", "se-imageSlide"}:
                for img in comp.select("img"):
                    src = img.get("data-lazy-src") or img.get("src")
                    if src and not src.startswith("data:") and "/static/" not in src:
                        images.append(src)
                        lines.append(f"[사진 {len(images)}]")
                cap = comp.select_one(".se-caption")
                if cap and one_line(cap.get_text()):
                    lines.append(f"(사진 설명) {one_line(cap.get_text())}")
            elif cls & {"se-placesMap", "se-map"}:
                lines.append("[지도] " + one_line(comp.get_text(" ")))
            elif "se-sticker" in cls:
                continue
            elif "se-oglink" in cls:
                a = comp.select_one("a")
                lines.append("[링크] " + one_line(comp.get_text(" ")) + (f" ({a.get('href')})" if a else ""))
            elif cls & {"se-video", "se-oembed"}:
                videos += 1
                lines.append("[동영상]")
            elif "se-horizontalLine" in cls:
                lines.append("---")
            elif "se-table" in cls:
                for tr in comp.select("tr"):
                    lines.append(" | ".join(one_line(td.get_text(" ")) for td in tr.select("td, th")))
            else:
                t = one_line(comp.get_text(" "))
                if t:
                    lines.append(t)
    else:  # 옛 편집기
        area = soup.select_one("#postViewArea") or soup.select_one(".post-view")
        if area:
            images = [i.get("data-lazy-src") or i.get("src") for i in area.select("img") if i.get("src")]
            lines = para_text(area).split("\n")
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return {"title": title, "author": one_line(nick.get_text()) if nick else "",
            "published_raw": one_line(date_el.get_text()) if date_el else "", "text": text,
            "images": images, "videos": videos}


def has_block_ancestor(el, area):
    for par in el.parents:
        if par is area:
            return False
        if par.name in BLOCKS:
            return True
    return False


def parse_generic(html):
    soup = BeautifulSoup(html, "html.parser")

    def meta(**kw):
        m = soup.find("meta", attrs=kw)
        return m.get("content", "") if m else ""

    title = meta(property="og:title") or (soup.title.get_text() if soup.title else "")
    author = meta(property="og:article:author") or meta(name="by") or meta(property="article:author")
    area = (soup.select_one(".tt_article_useless_p_margin") or soup.select_one(".entry-content")
            or soup.select_one("#article-view") or soup.select_one("article") or soup.body or soup)
    lines, images = [], []
    for el in area.find_all(BLOCKS):
        if has_block_ancestor(el, area):
            continue
        for img in el.select("img"):
            src = img.get("data-src") or img.get("src")
            if src:
                images.append(src)
                lines.append(f"[사진 {len(images)}]")
        if el.name == "table":
            for tr in el.select("tr"):
                lines.append(" | ".join(one_line(td.get_text(" ")) for td in tr.select("td, th")))
            continue
        t = para_text(el)
        if t:
            prefix = {"h1": "# ", "h2": "## ", "h3": "### ", "h4": "#### ", "li": "- ", "blockquote": "> "}.get(el.name, "")
            lines.append(prefix + t)
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return {"title": one_line(title), "author": author, "published_raw": meta(property="article:published_time"),
            "text": text, "images": images, "videos": 0}
