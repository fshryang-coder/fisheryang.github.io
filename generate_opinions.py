# -*- coding: utf-8 -*-
"""Generate Opinion list page + 5 article detail pages from extracted txt."""
import os, re, html

TXT_DIR = r"C:\Users\Ifyou\AppData\Local\Temp\articles_txt"
ROOT = r"C:\Users\Ifyou\OneDrive\桌面\PhD Application\Personal Website\academic-website-materials"
OPS_DIR = os.path.join(ROOT, "opinions")
os.makedirs(OPS_DIR, exist_ok=True)

# filename, slug, title, date, date_sort
ARTICLES = [
    ("pboc_Yifei_Yang.txt", "pboc", "How PBOC Combats China's Structural Recession", "May 2026", "2026-05"),
    ("ai_human_capital_Yifei_Yang.txt", "ai-human-capital", "Possible Macroeconomic Consequences of AI in China: A Human Capital Perspective", "April 2025", "2025-04"),
    ("korea_election_Yifei_Yang.txt", "korea-election", "The 2024 South Korean Parliamentary Election and the Constraints on President Yoon Suk-yeol's Governance", "April 2024", "2024-04"),
    ("ev_Yifei_Yang.txt", "ev", "Cross-Industry Competition in China's Smart Mobility Sector: Smartphone Makers, Automakers, and the Rise of AI", "March 2024", "2024-03"),
    ("israel_Yifei_Yang.txt", "israel", "Netanyahu's Wartime Survival: Security Politics and the Constraints of the Gaza Conflict", "January 2024", "2024-01"),
]

PBOC_H1 = {"Background", "Analysis", "Policy Options", "Recommendations", "Conclusion"}

def esc(s):
    return html.escape(s, quote=False)

def parse(txt):
    lines = [l.rstrip() for l in txt.split("\n")]
    subtitle = ""
    for l in lines[:5]:
        if l.strip().startswith("（") or l.strip().startswith("("):
            subtitle = l.strip().strip("（）()")
            break
    abstract = ""
    kw = ""
    body_start = 0
    for i, l in enumerate(lines):
        if l.strip() == "Abstract":
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].strip().lower().startswith("key words"):
                if lines[j].strip():
                    buf.append(lines[j].strip())
                j += 1
            abstract = " ".join(buf)
            if j < len(lines):
                kw_line = lines[j].strip()
                kw = kw_line.split(":",1)[-1].strip() if ":" in kw_line else ""
            body_start = j + 1
            break
    ref_start = len(lines)
    for i, l in enumerate(lines):
        if l.strip() == "References":
            ref_start = i
            break
    blocks = []
    for l in lines[body_start:ref_start]:
        s = l.strip()
        if not s:
            continue
        if re.match(r"^\[\d+\]", s):
            continue
        is_fig = bool(re.match(r"^Figure\s*\d+\s*$", s, re.I))
        is_heading = (not is_fig
                      and len(s) < 120
                      and not re.search(r"[。.!?\"”\)]$", s)
                      and not s.startswith("[")
                      and len(s.split()) <= 25)
        blocks.append({
            "type": ("figure_marker" if is_fig else ("h" if is_heading else "p")),
            "text": s
        })
    ref_text = " ".join(l.strip() for l in lines[ref_start+1:] if l.strip())
    refs = re.split(r"(?=\[\d+\])", ref_text)
    refs = [r.strip() for r in refs if r.strip() and re.match(r"^\[\d+\]", r.strip())]
    return {"subtitle": subtitle, "abstract": abstract, "keywords": kw,
            "blocks": blocks, "refs": refs}

def postprocess(blocks, slug):
    """Refine block levels (h1/h2/p) and insert figures / formula boxes."""
    out = []
    i = 0
    n = len(blocks)
    while i < n:
        b = blocks[i]
        # ---- PBOC: figure marker ----
        if slug == "pboc" and b["type"] == "figure_marker":
            m = re.match(r"^Figure\s*(\d+)", b["text"], re.I)
            fn = int(m.group(1)) if m else 0
            # caption: look at next block: if heading-type or short and no ending punct, use as caption
            caption = ""
            used_next = False
            if i + 1 < n:
                nb = blocks[i + 1]
                t = nb["text"].strip()
                if nb["type"] == "h" or (len(t) < 80 and not re.search(r"[。.!?\"”\)]$", t) and len(t.split()) <= 12):
                    caption = t
                    used_next = True
            out.append({"type": "figure", "num": fn, "caption": caption})
            i += 2 if used_next else 1
            continue
        # ---- Heading level assign ----
        if b["type"] == "h":
            t = b["text"].strip()
            level = "h2"
            if slug == "pboc" and t in PBOC_H1:
                level = "h1"
            if slug == "ai-human-capital" and t in ("Introduction", "Theoretical Framework: AI in the Growth Model",
                                                    "AI as a Consequence of China's Development",
                                                    "AI's Role in Human Capital Development", "Conclusion", "References"):
                level = "h1"
            if slug == "israel" and t in ("'安全的和平'", '"一国方案"与哈马斯', "加沙冲突将何去何从？"):
                level = "h1"
            if slug == "korea-election" and t in ('"支持率降到1%也要亲日"', '第一夫人"失踪"数月',
                                                  '"禁止携带大葱进入投票站"', "总理请辞，尹锡悦或面临弹劾？"):
                level = "h1"
            if slug == "ev" and t in ("门缝开启：一块屏幕引起的故事", "一场事关汽车控制权的斗争",
                                      "新能源与人工智能的头部之争", "谁是未来的头号玩家？"):
                level = "h1"
            out.append({"type": "heading", "level": level, "text": t})
            i += 1
            continue
        # ---- Default ----
        out.append({"type": b["type"], "text": b["text"]})
        i += 1

    # ---- AI article: insert formula box after 'expressed as:' paragraph ----
    if slug == "ai-human-capital":
        out2 = []
        formula_inserted = False
        for idx, bl in enumerate(out):
            out2.append(bl)
            if not formula_inserted and bl["type"] == "p" and "adapted production function is expressed as" in bl["text"]:
                # insert formula box right after this paragraph
                out2.append({"type": "formula_box"})
                formula_inserted = True
        out = out2
    return out

def topic_tag(kw):
    k = kw.lower()
    tags = []
    if any(x in k for x in ["ai","artificial","monetary","central bank","inflation","macroeconomic"]):
        tags.append("Macroeconomics")
    if any(x in k for x in ["ai","artificial","electric vehicle","technology"]):
        tags.append("AI Development")
    if any(x in k for x in ["political","election","legitimacy","israel","korea","security"]):
        tags.append("Political Economy")
    if not tags:
        tags.append("Commentary")
    return tags

# ============= HTML blocks render =============
def render_blocks(blocks, slug):
    parts = []
    for b in blocks:
        t = b["type"]
        if t == "heading":
            cls = "article-h1" if b["level"] == "h1" else "article-h2"
            parts.append('          <%s class="%s">%s</%s>' % (
                "h2" if b["level"] == "h1" else "h3", cls, esc(b["text"]),
                "h2" if b["level"] == "h1" else "h3"))
        elif t == "figure":
            src = "../articles/figures/figure_%d.png" % b["num"]
            cap = "Figure %d" % b["num"]
            if b["caption"]:
                cap += " &mdash; " + esc(b["caption"])
            parts.append('''          <figure class="article-figure">
            <img src="''' + src + '''" alt="Figure ''' + str(b["num"]) + '''" loading="lazy" />
            <figcaption>''' + cap + '''</figcaption>
          </figure>''')
        elif t == "formula_box":
            parts.append('''          <div class="formula-box">
            <p class="formula-lead">The adapted production function is expressed as:</p>
            <p class="formula-eq">
              <span class="formula-var">Y</span> =
              <span class="formula-var">A</span>&middot;F(K, L,
              <span class="formula-var">Z</span>)
            </p>
            <ul class="formula-where">
              <li><strong><span class="formula-var">A</span> (TFP):</strong> AI acts as a multiplier, boosting productivity across sectors.</li>
              <li><strong><span class="formula-var">Z</span> (Human Capital):</strong> Traditionally reliant on education and foreign knowledge spillovers, now increasingly dependent on domestic AI-driven upskilling.</li>
              <li><strong>K &amp; L:</strong> AI may disrupt traditional labor roles while optimizing capital allocation.</li>
            </ul>
            <p class="formula-foot">Within this framework, AI contributes to economic growth through two primary mechanisms:</p>
            <ul class="formula-mech">
              <li>As a productivity tool &mdash; enhancing TFP (<span class="formula-var">A</span>) across sectors.</li>
              <li>As a developer of human capital &mdash; transforming Human Capital (<span class="formula-var">Z</span>) by improving education and innovation capabilities in a more self-sufficient manner.</li>
            </ul>
          </div>''')
        elif t == "p":
            parts.append('          <p>' + esc(b["text"]) + '</p>')
        else:
            parts.append('          <p>' + esc(b["text"]) + '</p>')
    return "\n".join(parts)

HEAD = '''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — Yang Yifei</title>
  <meta name="description" content="{desc}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet" href="../assets/css/style.css" />
</head>
<body>
  <header class="masthead">
    <div class="masthead-inner">
      <a class="site-title" href="../index.html">Yang Yifei <span class="sep">|</span> 杨逸飞</a>
      <button class="menu-btn" aria-label="Toggle menu">Menu</button>
      <nav class="site-nav">
        <ul>
          <li><a href="../index.html">About</a></li>
          <li><a href="../research.html">Research</a></li>
          <li><a href="../opinion.html" class="active">Opinion</a></li>
          <li><a href="../cv.html">CV</a></li>
        </ul>
      </nav>
    </div>
  </header>
'''

FOOT = '''  <script src="../assets/js/main.js"></script>
</body>
</html>
'''

def build_detail(slug, title, date, data):
    blocks = postprocess(data["blocks"], slug)
    has_cn = any(u'\u4e00' <= c <= u'\u9fff' for b in blocks if b["type"] == "p" for c in b["text"])
    lang = "zh" if has_cn else "en"
    kw = data["keywords"]
    tags = topic_tag(kw)
    out = []
    out.append(HEAD.format(lang=lang, title=esc(title),
                            desc=esc(data["abstract"][:150])))
    out.append('''  <div class="page page-narrow">
    <main class="content">
      <a class="back-link" href="../opinion.html">← Back to Opinion</a>
      <article class="article">
        <h1 class="article-title">{title}</h1>
        {sub}
        <div class="article-meta">
          <span class="article-date">{date}</span>
          <span class="meta-sep">·</span>
          <span>Yang Yifei</span>
        </div>
        <div class="article-tags">{tags}</div>
        <div class="article-abstract">
          <h2 class="abstract-label">Abstract</h2>
          <p>{abstract}</p>
        </div>
        <div class="article-keywords">
          <strong>Keywords:</strong> {kw}
        </div>
        <div class="article-body">
{blocks}
        </div>
'''.format(title=esc(title),
           sub=('<p class="article-subtitle">'+esc(data["subtitle"])+'</p>') if data["subtitle"] else "",
           date=esc(date), tags="".join('<span class="tag">'+esc(t)+'</span>' for t in tags),
           abstract=esc(data["abstract"]), kw=esc(kw),
           blocks=render_blocks(blocks, slug)))
    if data["refs"]:
        out.append('''        <div class="article-refs">
          <h2 class="article-h1">References</h2>
          <ol class="ref-list">
''')
        for r in data["refs"]:
            out.append('            <li>'+esc(r)+'</li>\n')
        out.append('''          </ol>
        </div>
''')
    out.append('''      </article>
    </main>
  </div>''')
    out.append(FOOT)
    path = os.path.join(OPS_DIR, slug+".html")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    return path, len(blocks), len(data["refs"])

def build_list(arts):
    rows = []
    for fn, slug, title, date, ds in arts:
        with open(os.path.join(TXT_DIR, fn), encoding="utf-8") as f:
            txt = f.read()
        d = parse(txt)
        kw = d["keywords"]
        tags = topic_tag(kw)
        ab = d["abstract"]
        if len(ab) > 280:
            cut = ab[:280]
            cut = cut[:cut.rfind(" ")] + "…"
        else:
            cut = ab
        tags_html = "".join('<span class="tag">'+esc(t)+'</span>' for t in tags)
        rows.append('''        <article class="op-item">
          <div class="op-date">{date}</div>
          <div class="op-main">
            <h2 class="op-title"><a href="opinions/{slug}.html">{title}</a></h2>
            <div class="op-tags">{tags}</div>
            <p class="op-excerpt">{excerpt}</p>
            <a class="op-read" href="opinions/{slug}.html">Read more →</a>
          </div>
        </article>'''.format(date=esc(date), slug=slug, title=esc(title),
                              tags=tags_html, excerpt=esc(cut)))
    body = "\n".join(rows)
    page = HEAD_LIST.format(arts=body)
    with open(os.path.join(ROOT, "opinion.html"), "w", encoding="utf-8") as f:
        f.write(page)

HEAD_LIST = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Opinion — Yang Yifei</title>
  <meta name="description" content="Commentary by Yang Yifei on macroeconomics, AI development, and political economy." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet" href="assets/css/style.css" />
</head>
<body>
  <header class="masthead">
    <div class="masthead-inner">
      <a class="site-title" href="index.html">Yang Yifei <span class="sep">|</span> 杨逸飞</a>
      <button class="menu-btn" aria-label="Toggle menu">Menu</button>
      <nav class="site-nav">
        <ul>
          <li><a href="index.html">About</a></li>
          <li><a href="research.html">Research</a></li>
          <li><a href="opinion.html" class="active">Opinion</a></li>
          <li><a href="cv.html">CV</a></li>
        </ul>
      </nav>
    </div>
  </header>
  <div class="page page-narrow">
    <main class="content">
      <h1 class="page-title">Opinion</h1>
      <p class="page-lead">Commentary on macroeconomics, AI development, and political economy. Articles are listed in reverse chronological order.</p>
      <div class="op-list">
{arts}
      </div>
    </main>
  </div>
  <script src="assets/js/main.js"></script>
</body>
</html>
'''

for fn, slug, title, date, ds in ARTICLES:
    with open(os.path.join(TXT_DIR, fn), encoding="utf-8") as f:
        txt = f.read()
    d = parse(txt)
    p, bn, rn = build_detail(slug, title, date, d)
    print("detail:", p, "| blocks:", bn, "| refs:", rn)

build_list(ARTICLES)
print("list:", os.path.join(ROOT, "opinion.html"))
print("DONE")
