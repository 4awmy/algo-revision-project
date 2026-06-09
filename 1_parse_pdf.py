import fitz, re, json, os

PDF = 'general Revision Sheet.pdf'
if not os.path.exists(PDF):
    print(f"Error: {PDF} not found.")
    exit(1)

doc = fitz.open(PDF)

# ── helpers ───────────────────────────────────────────────────────
def get_lines(page):
    """Return list of (full_text, spans) where spans = [(text, is_bold)]."""
    result = []
    try:
        blocks = page.get_text("dict")["blocks"]
    except:
        return []
    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            spans = [(s["text"], bool(s["flags"] & 16)) for s in line["spans"] if s["text"].strip()]
            full  = "".join(s["text"] for s in line["spans"]).strip()
            if full:
                result.append((full, spans))
    return result

def opt_bold_from_spans(spans, opt_text):
    """Check whether opt_text (stripped) appears in a bold span."""
    for span_text, is_bold in spans:
        if is_bold and any(word in span_text for word in opt_text.split()[:2]):
            return True
    return False

def split_inline(line_text, spans):
    """Split inline options and detect bold."""
    all_opts = list(re.finditer(r'([a-d])\s*[).]\s*(.*?)(?=\s{2,}[a-d]\s*[).]|$)', line_text, re.IGNORECASE))
    result = []
    for m in all_opts:
        letter = m.group(1).lower()
        text   = m.group(2).strip()
        bold   = opt_bold_from_spans(spans, text)
        result.append((letter, text, bold))
    return result

q_pat   = re.compile(r'^(\d{1,3})\.\s+(.+)')
opt_pat = re.compile(r'^([a-d])\s*[).]\s*(.*)', re.IGNORECASE)
exp_pat = re.compile(r'^[Ee]xplan\w*\s*:?\s*(.*)')

questions = {}
seen_qs   = set()

cur_num  = None
cur_text = []
cur_opts = []   # (text, is_bold)
cur_exp  = []
in_q     = False
in_exp   = False

def save():
    global cur_num, cur_text, cur_opts, cur_exp, in_q, in_exp
    if cur_num and cur_text and cur_num not in questions:
        ans = -1
        for i, (ot, ob) in enumerate(cur_opts):
            if ob:
                ans = i
                break
        questions[cur_num] = {
            'text':        ' '.join(cur_text).strip(),
            'options':     [ot for ot, _ in cur_opts],
            'answer':      ans,
            'explanation': ' '.join(cur_exp).strip()
        }
    cur_num = None; cur_text = []; cur_opts = []; cur_exp = []
    in_q = False; in_exp = False

# ── MCQs (Pages 0 to 125) ──────────────────────────────────────────
for pi in range(126):
    for raw_line, spans in get_lines(doc[pi]):
        if re.match(r'^\d{1,3}$', raw_line): continue
        if 'Revision Sheet' in raw_line or 'Wahdan' in raw_line: continue

        # ── New question ──
        qm = q_pat.match(raw_line)
        if qm:
            qn = int(qm.group(1))
            # Sequence check: only accept if it's a new number and reasonably sequential or we're starting
            is_new_q = qn not in seen_qs and (cur_num is None or qn > cur_num or qn == cur_num + 1)
            
            if 1 <= qn <= 266 and is_new_q:
                save()
                seen_qs.add(qn)
                cur_num  = qn
                cur_text = [qm.group(2)]
                in_q     = True
                continue
            elif 1 <= qn <= 266 and qn in seen_qs and qn != cur_num:
                # Likely a duplicate or false positive, skip as question number
                pass
            elif qn == cur_num:
                # Already processing this one
                continue

        if cur_num is None: continue

        em = exp_pat.match(raw_line)
        if em:
            in_exp = True; in_q = False
            rest = em.group(1); 
            if rest: cur_exp.append(rest)
            continue

        if in_exp:
            cur_exp.append(raw_line)
            continue

        om = opt_pat.match(raw_line)
        if om:
            in_q = False
            inline = split_inline(raw_line, spans)
            if len(inline) > 1:
                for letter, text, bold in inline: cur_opts.append((text, bold))
            else:
                line_bold = any(b for _, b in spans)
                cur_opts.append((om.group(2).strip(), line_bold))
            continue

        if in_q: cur_text.append(raw_line)
        elif cur_opts:
            last_t, last_b = cur_opts[-1]
            line_bold = any(b for _, b in spans)
            cur_opts[-1] = (last_t + ' ' + raw_line, last_b or line_bold)

save()

# ── Open-Ended (Page 126 to End) ─────────────────────────────────────
open_qs = []
oe_num = 1
for pi in range(126, len(doc)):
    page_text = doc[pi].get_text().split('\n')
    for line in page_text:
        line = line.strip()
        if not line or line.isdigit(): continue
        if 'Revision Sheet' in line or 'Wahdan' in line: continue
        if line.lower() == 'answer': continue
        
        # Check if it looks like a question (ends with ? or starts with number)
        if line.endswith('?') or re.match(r'^\d+\.', line):
            text = re.sub(r'^\d+\.\s*', '', line)
            open_qs.append({'num': oe_num, 'text': text})
            oe_num += 1

# ── Save ──────────────────────────────────────────────────────────
with open('mcq_final.json', 'w', encoding='utf-8') as f:
    json.dump({str(k): v for k, v in sorted(questions.items())}, f, ensure_ascii=False)

with open('open_qs.json', 'w', encoding='utf-8') as f:
    json.dump(open_qs, f, ensure_ascii=False)

# Ensure images map exists (even if empty)
if not os.path.exists('q_images_map.json'):
    with open('q_images_map.json', 'w', encoding='utf-8') as f:
        json.dump({}, f)

print(f"MCQs: {len(questions)} | Open-Ended: {len(open_qs)}")
print("Saved mcq_final.json and open_qs.json")
