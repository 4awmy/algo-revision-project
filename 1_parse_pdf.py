import fitz, re, json, os, base64

PDF = 'general Revision Sheet.pdf'
if not os.path.exists(PDF):
    print(f"Error: {PDF} not found.")
    exit(1)

doc = fitz.open(PDF)

# ── helpers ───────────────────────────────────────────────────────
def get_lines(page):
    """Return list of (full_text, spans, rect) where spans = [(text, is_bold)]."""
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
                line_rect = fitz.Rect(line["bbox"])
                result.append((full, spans, line_rect))
    return result

def opt_bold_from_spans(spans, opt_text):
    for span_text, is_bold in spans:
        if is_bold and any(word in span_text for word in opt_text.split()[:2]):
            return True
    return False

def split_inline(line_text, spans):
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
q_images  = {} # q_num -> [base64_data, ...]
seen_qs   = set()

cur_num  = None
cur_text = []
cur_opts = []
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
    page = doc[pi]
    # Extract images from page using get_images()
    page_images = []
    for img in page.get_images(full=True):
        xref = img[0]
        try:
            pix = doc.extract_image(xref)
            img_data = base64.b64encode(pix["image"]).decode('utf-8')
            page_images.append({'data': f"data:image/{pix['ext']};base64,{img_data}"})
        except:
            continue

    last_q_num = None
    
    for raw_line, spans, line_rect in get_lines(page):
        if re.match(r'^\d{1,3}$', raw_line): continue
        if 'Revision Sheet' in raw_line or 'Wahdan' in raw_line: continue

        qm = q_pat.match(raw_line)
        if qm:
            qn = int(qm.group(1))
            is_new_q = qn not in seen_qs and (cur_num is None or qn > cur_num or qn == cur_num + 1)
            
            if 1 <= qn <= 266 and is_new_q:
                save()
                seen_qs.add(qn)
                cur_num  = qn
                last_q_num = qn
                cur_text = [qm.group(2)]
                in_q     = True
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

    # Simple heuristic: map all images on the page to the last question started on the page
    for img in page_images:
        target_q = cur_num or last_q_num
        if target_q:
            if target_q not in q_images: q_images[target_q] = []
            if img['data'] not in q_images[target_q]:
                q_images[target_q].append(img['data'])

save()

# ── Open-Ended (Page 126 to End) ─────────────────────────────────────
open_qs = []
oe_num = 1
for pi in range(126, len(doc)):
    page = doc[pi]
    # Extract images for open-ended too
    page_images = []
    for img in page.get_images(full=True):
        xref = img[0]
        try:
            pix = doc.extract_image(xref)
            img_data = base64.b64encode(pix["image"]).decode('utf-8')
            page_images.append({'data': f"data:image/{pix['ext']};base64,{img_data}"})
        except:
            continue

    page_text = page.get_text().split('\n')
    last_oe = None
    for line in page_text:
        line = line.strip()
        if not line or line.isdigit(): continue
        if 'Revision Sheet' in line or 'Wahdan' in line: continue
        if line.lower() == 'answer': continue
        if line.endswith('?') or re.match(r'^\d+\.', line):
            text = re.sub(r'^\d+\.\s*', '', line)
            last_oe = oe_num
            open_qs.append({'num': oe_num, 'text': text})
            oe_num += 1

    for img in page_images:
        if last_oe:
            key = f"oe_{last_oe}"
            if key not in q_images: q_images[key] = []
            if img['data'] not in q_images[key]:
                q_images[key].append(img['data'])

# ── Save ──────────────────────────────────────────────────────────
with open('mcq_final.json', 'w', encoding='utf-8') as f:
    json.dump({str(k): v for k, v in sorted(questions.items())}, f, ensure_ascii=False)

with open('open_qs.json', 'w', encoding='utf-8') as f:
    json.dump(open_qs, f, ensure_ascii=False)

with open('q_images_map.json', 'w', encoding='utf-8') as f:
    json.dump({str(k): v for k, v in q_images.items()}, f, ensure_ascii=False)

print(f"MCQs: {len(questions)} | Open-Ended: {len(open_qs)} | Qs with Images: {len(q_images)}")
print("Saved mcq_final.json, open_qs.json, and q_images_map.json")
