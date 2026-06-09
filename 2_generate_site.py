import json, os

def load_json(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else {}
    with open(path, encoding='utf-8') as f:
        return json.load(f)

mcq_raw = load_json('mcq_final.json')
img_map = load_json('q_images_map.json')
open_qs = load_json('open_qs.json', [])

# keep questions with >=2 options
mcq = {k: v for k, v in mcq_raw.items() if len(v['options']) >= 2}
total_mcq = len(mcq)
total_oe  = len(open_qs)

mcq_js = json.dumps(mcq, ensure_ascii=False)
img_js = json.dumps(img_map, ensure_ascii=False)
oe_js  = json.dumps(open_qs, ensure_ascii=False)

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Comprehensive Algorithms Revision — Dr. Mahmoud Wahdan</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{{
  --bg:#0f172a;--sf:#1e293b;--sf2:#263045;--br:#334155;
  --ac:#6366f1;--ac2:#818cf8;--tx:#e2e8f0;--mu:#94a3b8;
  --ok:#22c55e;--er:#ef4444;--wn:#f59e0b;--r:10px;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--tx);font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh}}

/* ── NAV ── */
.nav{{background:var(--sf);border-bottom:1px solid var(--br);display:flex;align-items:center;gap:4px;padding:0 16px;position:sticky;top:0;z-index:200;flex-wrap:wrap}}
.nav-branding{{padding:12px 12px 12px 0;border-right:1px solid var(--br);margin-right:4px}}
.nav h1{{font-size:.95rem;font-weight:700;color:var(--ac2);white-space:nowrap}}
.nav p{{font-size:.65rem;color:var(--mu);margin-top:1px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px}}
.tab{{padding:12px 14px;border-bottom:3px solid transparent;cursor:pointer;font-size:.85rem;font-weight:500;color:var(--mu);background:none;border-top:none;border-left:none;border-right:none;transition:all .2s;white-space:nowrap}}
.tab.on{{color:var(--ac2);border-bottom-color:var(--ac2)}}
.tab:hover{{color:var(--tx)}}
#tmr{{margin-left:auto;font-size:.95rem;font-weight:700;color:var(--wn);background:rgba(245,158,11,.1);padding:5px 12px;border-radius:7px;border:1px solid var(--wn)}}
#tmr.urg{{color:var(--er);border-color:var(--er);animation:pulse .8s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.5}}}}

/* ── PROGRESS ── */
#pw{{height:3px;background:var(--br)}}
#pb{{height:3px;background:var(--ac);transition:width .3s;width:0%}}
#pt{{font-size:.73rem;color:var(--mu);padding:4px 18px}}

/* ── PAGES ── */
.pg{{display:none;padding:18px;max-width:940px;margin:0 auto}}
.pg.on{{display:block}}

/* ── MCQ TOOLBAR ── */
.tb{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:16px}}
.srch{{background:var(--sf);border:1px solid var(--br);border-radius:8px;padding:7px 13px;color:var(--tx);font-size:.85rem;width:200px;outline:none}}
.srch:focus{{border-color:var(--ac)}}
.fb{{background:var(--sf);border:1px solid var(--br);border-radius:7px;padding:6px 13px;color:var(--mu);font-size:.8rem;cursor:pointer;transition:all .2s}}
.fb.on{{background:var(--ac);color:#fff;border-color:var(--ac)}}
#qct{{color:var(--mu);font-size:.8rem}}
.sub-all{{margin-left:auto;background:var(--ac);color:#fff;border:none;border-radius:8px;padding:7px 16px;font-size:.85rem;font-weight:600;cursor:pointer}}
.sub-all:hover{{opacity:.85}}

/* ── Q CARD ── */
.qc{{background:var(--sf);border:1px solid var(--br);border-radius:var(--r);padding:16px 18px;margin-bottom:12px;transition:border-color .2s}}
.qc.ans{{border-color:rgba(99,102,241,.45)}}
.qc.ck-ok{{border-color:var(--ok)}}
.qc.ck-bad{{border-color:var(--er)}}
.qh{{display:flex;gap:9px;align-items:flex-start;margin-bottom:10px}}
.qbadge{{background:var(--sf2);border:1px solid var(--br);border-radius:6px;padding:2px 8px;font-size:.7rem;font-weight:700;color:var(--mu);white-space:nowrap;flex-shrink:0}}
.qtxt{{font-size:.93rem;font-weight:500;line-height:1.55}}
.qimg{{max-width:100%;border-radius:7px;margin:8px 0;border:1px solid var(--br);display:block}}
.opts{{display:grid;gap:6px;margin-top:8px}}
.opt{{background:var(--sf2);border:1px solid var(--br);border-radius:7px;padding:8px 13px;text-align:left;cursor:pointer;color:var(--tx);font-size:.87rem;display:flex;align-items:center;gap:9px;transition:all .18s}}
.opt:hover:not(:disabled){{background:rgba(99,102,241,.11);border-color:var(--ac)}}
.opt.sel{{background:rgba(99,102,241,.16);border-color:var(--ac2)}}
.opt.ok{{background:rgba(34,197,94,.1)!important;border-color:var(--ok)!important;color:var(--ok)}}
.opt.bad{{background:rgba(239,68,68,.07)!important;border-color:var(--er)!important;color:var(--er)}}
.opt:disabled{{cursor:default}}
.ol{{font-weight:700;width:18px;flex-shrink:0;opacity:.6}}

/* ── QUESTION FOOTER ── */
.qfoot{{display:flex;align-items:center;gap:10px;margin-top:10px;flex-wrap:wrap}}
.chk-btn{{background:var(--sf2);border:1px solid var(--br);border-radius:7px;padding:5px 13px;color:var(--ac2);font-size:.78rem;font-weight:600;cursor:pointer;transition:all .18s}}
.chk-btn:hover{{background:rgba(99,102,241,.12);border-color:var(--ac)}}
.chk-btn:disabled{{opacity:.4;cursor:default}}
.res-badge{{font-size:.75rem;font-weight:700;padding:3px 8px;border-radius:5px}}
.res-ok{{background:rgba(34,197,94,.12);color:var(--ok)}}
.res-bad{{background:rgba(239,68,68,.08);color:var(--er)}}

/* ── EXPLANATION ── */
.exp-btn{{background:none;border:none;color:var(--ac2);font-size:.78rem;cursor:pointer;padding:0;display:flex;align-items:center;gap:4px}}
.exp-body{{margin-top:7px;padding:9px 13px;background:rgba(99,102,241,.05);border-left:3px solid var(--ac);border-radius:0 6px 6px 0;font-size:.82rem;color:var(--mu);display:none;line-height:1.6}}
.exp-body.open{{display:block}}

/* ── OPEN-ENDED ── */
.oe-card{{background:var(--sf);border:1px solid var(--br);border-radius:var(--r);padding:16px 18px;margin-bottom:12px}}
.oe-q{{font-size:.93rem;font-weight:500;line-height:1.6;margin-bottom:10px}}
.oe-ta{{width:100%;min-height:80px;background:var(--sf2);border:1px solid var(--br);border-radius:8px;padding:9px 13px;color:var(--tx);font-size:.87rem;resize:vertical;outline:none;font-family:inherit}}
.oe-ta:focus{{border-color:var(--ac)}}

/* ── CHEAT SHEET ── */
.cs-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}}
.cs{{background:var(--sf);border:1px solid var(--br);border-radius:var(--r);padding:16px 18px}}
.cs h3{{font-size:.9rem;font-weight:700;color:var(--ac2);margin-bottom:10px;padding-bottom:7px;border-bottom:1px solid var(--br)}}
.cs table{{width:100%;border-collapse:collapse;font-size:.8rem}}
.cs th{{background:var(--sf2);padding:6px 9px;text-align:left;color:var(--mu);font-weight:600;border:1px solid var(--br)}}
.cs td{{padding:6px 9px;border:1px solid var(--br);vertical-align:top;line-height:1.4}}
.cs td:first-child{{font-weight:600;color:var(--ac2)}}
.cs p,.cs li{{font-size:.83rem;color:var(--mu);line-height:1.65}}
.cs ul{{padding-left:14px}}
code{{background:var(--sf2);padding:1px 5px;border-radius:4px;font-family:monospace;font-size:.79rem;color:var(--ac2)}}

/* ── ANALYTICS ── */
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:11px;margin-bottom:22px}}
.st{{background:var(--sf);border:1px solid var(--br);border-radius:var(--r);padding:14px;text-align:center}}
.sv{{font-size:1.7rem;font-weight:800;color:var(--ac2)}}
.sl{{font-size:.73rem;color:var(--mu);margin-top:3px}}
.chart-box{{background:var(--sf);border:1px solid var(--br);border-radius:var(--r);padding:18px}}

/* ── MODAL ── */
#mod{{position:fixed;inset:0;background:rgba(0,0,0,.75);display:none;align-items:center;justify-content:center;z-index:999}}
#mod.on{{display:flex}}
.mb{{background:var(--sf);border:1px solid var(--br);border-radius:14px;padding:28px;max-width:420px;width:90%;text-align:center}}
.mg{{font-size:3.2rem;font-weight:900;margin:10px 0}}
.ga{{color:var(--ok)}}.gb{{color:#84cc16}}.gc{{color:var(--wn)}}.gd{{color:var(--er)}}
.ms{{font-size:1rem;color:var(--mu);margin-bottom:14px}}
.mbtn{{background:var(--ac);color:#fff;border:none;border-radius:7px;padding:8px 18px;font-size:.85rem;font-weight:600;cursor:pointer;margin:3px}}
.mbtn.s{{background:var(--sf2);color:var(--tx);border:1px solid var(--br)}}

@media(max-width:580px){{
  .nav h1{{display:none}} #tmr{{display:none}}
  .pg{{padding:10px}}
}}
</style>
</head>
<body>

<div class="nav">
  <div class="nav-branding">
    <h1>⚡ Algorithms Revision</h1>
    <p>Dr. Mahmoud Wahdan</p>
  </div>
  <button class="tab on" onclick="go('mcq')">📝 MCQ ({total_mcq})</button>
  <button class="tab" onclick="go('oe')">✍️ Open-Ended ({total_oe})</button>
  <button class="tab" onclick="go('cheat')">📋 Cheat Sheet</button>
  <button class="tab" onclick="go('analytics')">📊 Analytics</button>
  <div id="tmr">45:00</div>
</div>
<div id="pw"><div id="pb"></div></div>
<div id="pt">0 / {total_mcq} answered</div>

<!-- ══ MCQ ══ -->
<div class="pg on" id="pg-mcq">
  <div class="tb">
    <input class="srch" id="srch" placeholder="🔍 Search…" oninput="filt()"/>
    <button class="fb on" onclick="setF('all',this)">All</button>
    <button class="fb" onclick="setF('un',this)">Unanswered</button>
    <button class="fb" onclick="setF('done',this)">Answered</button>
    <span id="qct"></span>
    <button class="sub-all" onclick="submitAll()">Submit All &amp; Grade</button>
  </div>
  <div id="qlist"></div>
</div>

<!-- ══ OPEN-ENDED ══ -->
<div class="pg" id="pg-oe">
  <h2 style="margin-bottom:5px;font-size:1.1rem">Open-Ended / Short Answer</h2>
  <p style="color:var(--mu);font-size:.83rem;margin-bottom:18px">From the revision sheet — write your answers for self-review.</p>
  <div id="oelist"></div>
</div>

<!-- ══ CHEAT SHEET ══ -->
<div class="pg" id="pg-cheat">
  <h2 style="margin-bottom:18px;font-size:1.1rem">📋 Algorithm Cheat Sheet</h2>
  <div class="cs-grid">

    <div class="cs">
      <h3>Asymptotic Notations</h3>
      <table>
        <tr><th>Notation</th><th>Meaning</th><th>Case</th></tr>
        <tr><td><code>O(f(n))</code></td><td>Upper bound</td><td>Worst</td></tr>
        <tr><td><code>Ω(f(n))</code></td><td>Lower bound</td><td>Best</td></tr>
        <tr><td><code>Θ(f(n))</code></td><td>Tight bound</td><td>Both</td></tr>
        <tr><td><code>o(f(n))</code></td><td>Strict upper</td><td>&lt; f(n)</td></tr>
      </table>
    </div>

    <div class="cs">
      <h3>Sorting Algorithms</h3>
      <table>
        <tr><th>Algorithm</th><th>Best</th><th>Avg</th><th>Worst</th><th>Space</th><th>Stable</th></tr>
        <tr><td>Bubble</td><td>O(n)</td><td>O(n²)</td><td>O(n²)</td><td>O(1)</td><td>✅</td></tr>
        <tr><td>Selection</td><td>O(n²)</td><td>O(n²)</td><td>O(n²)</td><td>O(1)</td><td>❌</td></tr>
        <tr><td>Insertion</td><td>O(n)</td><td>O(n²)</td><td>O(n²)</td><td>O(1)</td><td>✅</td></tr>
        <tr><td>Merge</td><td>O(n log n)</td><td>O(n log n)</td><td>O(n log n)</td><td>O(n)</td><td>✅</td></tr>
        <tr><td>Quick</td><td>O(n log n)</td><td>O(n log n)</td><td>O(n²)</td><td>O(log n)</td><td>❌</td></tr>
        <tr><td>Heap</td><td>O(n log n)</td><td>O(n log n)</td><td>O(n log n)</td><td>O(1)</td><td>❌</td></tr>
        <tr><td>Counting</td><td>O(n+k)</td><td>O(n+k)</td><td>O(n+k)</td><td>O(k)</td><td>✅</td></tr>
      </table>
    </div>

    <div class="cs">
      <h3>Searching</h3>
      <table>
        <tr><th>Algorithm</th><th>Best</th><th>Avg</th><th>Worst</th><th>Requires</th></tr>
        <tr><td>Linear</td><td>O(1)</td><td>O(n)</td><td>O(n)</td><td>—</td></tr>
        <tr><td>Binary</td><td>O(1)</td><td>O(log n)</td><td>O(log n)</td><td>Sorted</td></tr>
        <tr><td>Hashing</td><td>O(1)</td><td>O(1)</td><td>O(n)</td><td>Hash fn</td></tr>
      </table>
    </div>

    <div class="cs">
      <h3>Tree &amp; Graph Operations</h3>
      <table>
        <tr><th>Structure</th><th>Search</th><th>Insert</th><th>Delete</th></tr>
        <tr><td>BST avg</td><td>O(log n)</td><td>O(log n)</td><td>O(log n)</td></tr>
        <tr><td>BST worst</td><td>O(n)</td><td>O(n)</td><td>O(n)</td></tr>
        <tr><td>AVL Tree</td><td>O(log n)</td><td>O(log n)</td><td>O(log n)</td></tr>
        <tr><td>Heap</td><td>O(n)</td><td>O(log n)</td><td>O(log n)</td></tr>
        <tr><td>BFS/DFS (list)</td><td colspan="3">O(V+E)</td></tr>
        <tr><td>BFS/DFS (matrix)</td><td colspan="3">O(V²)</td></tr>
      </table>
    </div>

    <div class="cs">
      <h3>AVL Tree Rotations</h3>
      <table>
        <tr><th>Case</th><th>Imbalance</th><th>Fix</th></tr>
        <tr><td>LL</td><td>Left-Left heavy</td><td>Single Right Rotate</td></tr>
        <tr><td>RR</td><td>Right-Right heavy</td><td>Single Left Rotate</td></tr>
        <tr><td>LR</td><td>Left-Right heavy</td><td>Left then Right Rotate</td></tr>
        <tr><td>RL</td><td>Right-Left heavy</td><td>Right then Left Rotate</td></tr>
      </table>
      <p style="margin-top:8px">Balance Factor = height(L) − height(R). Must be −1, 0, or +1.</p>
    </div>

    <div class="cs">
      <h3>Tree Traversals</h3>
      <table>
        <tr><th>Order</th><th>Pattern</th><th>Use case</th></tr>
        <tr><td>Inorder</td><td>L → Root → R</td><td>Sorted output from BST</td></tr>
        <tr><td>Preorder</td><td>Root → L → R</td><td>Copy tree, prefix expr</td></tr>
        <tr><td>Postorder</td><td>L → R → Root</td><td>Delete tree, postfix</td></tr>
        <tr><td>Level-order</td><td>BFS row by row</td><td>Shortest path (unweighted)</td></tr>
      </table>
    </div>

    <div class="cs">
      <h3>Heap (Array)</h3>
      <ul>
        <li>Parent of i: <code>⌊(i−1)/2⌋</code></li>
        <li>Left child of i: <code>2i+1</code></li>
        <li>Right child of i: <code>2i+2</code></li>
        <li>Leaves: indices <code>⌊n/2⌋</code> to <code>n−1</code></li>
        <li>Height: <code>⌊log₂ n⌋</code></li>
        <li>Build-Heap: <code>O(n)</code></li>
        <li>Max-Heap: parent ≥ children</li>
        <li>Min-Heap: parent ≤ children</li>
      </ul>
    </div>

    <div class="cs">
      <h3>Hashing</h3>
      <table>
        <tr><th>Concept</th><th>Formula / Detail</th></tr>
        <tr><td>Load factor α</td><td>n / m</td></tr>
        <tr><td>Division</td><td>h(k) = k mod m</td></tr>
        <tr><td>Multiplication</td><td>h(k) = ⌊m·(kA mod 1)⌋, A≈0.618</td></tr>
        <tr><td>Separate chaining</td><td>Linked list per bucket</td></tr>
        <tr><td>Linear probing</td><td>(h(k)+i) mod m</td></tr>
        <tr><td>Quadratic probing</td><td>(h(k)+c₁i+c₂i²) mod m</td></tr>
        <tr><td>Double hashing</td><td>(h₁(k)+i·h₂(k)) mod m</td></tr>
      </table>
    </div>

    <div class="cs">
      <h3>D&amp;C Recurrences</h3>
      <table>
        <tr><th>Algorithm</th><th>Recurrence</th><th>Result</th></tr>
        <tr><td>Merge Sort</td><td>2T(n/2)+O(n)</td><td>O(n log n)</td></tr>
        <tr><td>Quick Sort avg</td><td>2T(n/2)+O(n)</td><td>O(n log n)</td></tr>
        <tr><td>Binary Search</td><td>T(n/2)+O(1)</td><td>O(log n)</td></tr>
        <tr><td>Closest Pair</td><td>2T(n/2)+O(n log n)</td><td>O(n log n)</td></tr>
      </table>
      <p style="margin-top:8px">Master Theorem: T(n)=aT(n/b)+f(n)</p>
    </div>

    <div class="cs">
      <h3>BFS vs DFS</h3>
      <table>
        <tr><th>Property</th><th>BFS</th><th>DFS</th></tr>
        <tr><td>Data structure</td><td>Queue</td><td>Stack / Recursion</td></tr>
        <tr><td>Time</td><td>O(V+E)</td><td>O(V+E)</td></tr>
        <tr><td>Space</td><td>O(V)</td><td>O(V)</td></tr>
        <tr><td>Shortest path</td><td>✅ unweighted</td><td>❌</td></tr>
        <tr><td>Topological sort</td><td>✅ Kahn's</td><td>✅ finish time</td></tr>
        <tr><td>Tree traversal</td><td>Level-order</td><td>Pre/In/Post</td></tr>
      </table>
    </div>

    <div class="cs">
      <h3>Design Paradigms</h3>
      <table>
        <tr><th>Paradigm</th><th>Idea</th><th>Examples</th></tr>
        <tr><td>Brute Force</td><td>Try all</td><td>Closest pair O(n²)</td></tr>
        <tr><td>D&amp;C</td><td>Divide → Solve → Combine</td><td>Merge Sort, Binary Search</td></tr>
        <tr><td>Transform &amp; Conquer</td><td>Simplify instance</td><td>Presorting, AVL, Heaps</td></tr>
        <tr><td>Greedy</td><td>Locally optimal</td><td>Fractional Knapsack</td></tr>
        <tr><td>Dynamic Prog.</td><td>Memoize subproblems</td><td>0/1 Knapsack</td></tr>
        <tr><td>Backtracking</td><td>Build &amp; prune</td><td>N-Queens</td></tr>
      </table>
    </div>

    <div class="cs">
      <h3>Complexity Classes</h3>
      <table>
        <tr><th>Class</th><th>Name</th><th>Example</th></tr>
        <tr><td><code>O(1)</code></td><td>Constant</td><td>Array access</td></tr>
        <tr><td><code>O(log n)</code></td><td>Logarithmic</td><td>Binary search</td></tr>
        <tr><td><code>O(n)</code></td><td>Linear</td><td>Linear search</td></tr>
        <tr><td><code>O(n log n)</code></td><td>Linearithmic</td><td>Merge sort</td></tr>
        <tr><td><code>O(n²)</code></td><td>Quadratic</td><td>Bubble sort</td></tr>
        <tr><td><code>O(2ⁿ)</code></td><td>Exponential</td><td>Subset enumeration</td></tr>
      </table>
    </div>

  </div>
</div>

<!-- ══ ANALYTICS ══ -->
<div class="pg" id="pg-analytics">
  <h2 style="margin-bottom:16px;font-size:1.1rem">📊 Score Analytics</h2>
  <div class="stats" id="stats"></div>
  <div class="chart-box">
    <h3 style="margin-bottom:12px;font-size:.88rem;color:var(--mu)">Score by 50-question block</h3>
    <canvas id="ac" height="110"></canvas>
  </div>
</div>

<!-- ══ MODAL ══ -->
<div id="mod">
  <div class="mb">
    <div style="font-size:1rem;font-weight:700">Exam Complete!</div>
    <div class="mg" id="mg"></div>
    <div class="ms" id="ms"></div>
    <div id="mbr" style="font-size:.8rem;color:var(--mu);margin-bottom:14px;line-height:1.8"></div>
    <button class="mbtn" onclick="closeMod();go('analytics')">View Analytics</button>
    <button class="mbtn s" onclick="closeMod()">Close</button>
  </div>
</div>

<script>
const MCQ  = {mcq_js};
const IMGS = {img_js};
const OE   = {oe_js};
const KEYS = Object.keys(MCQ).map(Number).sort((a,b)=>a-b);
const TOT  = KEYS.length;

const answers   = {{}};     // qnum -> chosen idx
const checked   = {{}};     // qnum -> true (per-question submitted)
let   allDone   = false;
let   curFilter = 'all';
let   chartInst = null;
let   timerSecs = 45*60;

// ── TABS ──────────────────────────────────────────────────────────
function go(name) {{
  ['mcq','oe','cheat','analytics'].forEach((n,i) => {{
    document.getElementById('pg-'+n).classList.toggle('on', n===name);
    document.querySelectorAll('.tab')[i].classList.toggle('on', n===name);
  }});
  if(name==='analytics') drawAnalytics();
}}

// ── BUILD MCQ ─────────────────────────────────────────────────────
function buildMCQ() {{
  const L = document.getElementById('qlist');
  KEYS.forEach(qn => {{
    const q = MCQ[qn];
    const card = document.createElement('div');
    card.className = 'qc'; card.id = 'qc-'+qn;

    const imgs = (IMGS[qn]||[]).map(src=>
      `<img class="qimg" src="${{src}}" alt="Q${{qn}} figure" loading="lazy"/>`).join('');

    const opts = q.options.map((o,i)=>
      `<button class="opt" id="op-${{qn}}-${{i}}" onclick="pick(${{qn}},${{i}})">
        <span class="ol">${{'ABCD'[i]}}</span><span>${{esc(o)}}</span>
      </button>`).join('');

    const expHtml = q.explanation
      ? `<button class="exp-btn" onclick="togExp(${{qn}})">▶ Show Explanation</button>
         <div class="exp-body" id="ex-${{qn}}">${{esc(q.explanation)}}</div>`
      : '';

    card.innerHTML = `
      <div class="qh">
        <span class="qbadge">Q${{qn}}</span>
        <span class="qtxt">${{esc(q.text)}}</span>
      </div>
      ${{imgs}}
      <div class="opts">${{opts}}</div>
      <div class="qfoot">
        <button class="chk-btn" id="ckb-${{qn}}" onclick="checkOne(${{qn}})" disabled>Check Answer</button>
        <span id="cr-${{qn}}"></span>
        ${{expHtml}}
      </div>
    `;
    L.appendChild(card);
  }});
  document.getElementById('qct').textContent = TOT + ' questions';
}}

function esc(s) {{
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

// ── PICK ─────────────────────────────────────────────────────────
function pick(qn, oi) {{
  if(allDone || checked[qn]) return;
  answers[qn] = oi;
  for(let k=0; k<4; k++) {{
    const b=document.getElementById(`op-${{qn}}-${{k}}`);
    if(b) b.classList.toggle('sel',k===oi);
  }}
  document.getElementById('qc-'+qn).classList.add('ans');
  document.getElementById('ckb-'+qn).disabled = false;
  updateProg();
}}

// ── CHECK ONE ─────────────────────────────────────────────────────
function checkOne(qn) {{
  if(checked[qn] || allDone) return;
  checked[qn] = true;
  const q = MCQ[qn];
  const ans = q.answer;
  const chosen = answers[qn];
  const correct = (chosen === ans && ans >= 0);

  for(let k=0; k<q.options.length; k++) {{
    const b=document.getElementById(`op-${{qn}}-${{k}}`);
    if(!b) continue;
    b.disabled = true;
    if(k===ans && ans>=0) b.classList.add('ok');
    else if(k===chosen) b.classList.add('bad');
  }}

  const card = document.getElementById('qc-'+qn);
  card.classList.remove('ans');
  card.classList.add(correct ? 'ck-ok' : 'ck-bad');

  const badge = document.getElementById('cr-'+qn);
  badge.innerHTML = correct
    ? `<span class="res-badge res-ok">✓ Correct</span>`
    : `<span class="res-badge res-bad">✗ Wrong${{ans>=0?' — '+('ABCD'[ans]):''}}</span>`;

  const ckb = document.getElementById('ckb-'+qn);
  if(ckb) ckb.disabled = true;

  // Auto-show explanation
  const exp = document.getElementById('ex-'+qn);
  const ebtn = exp ? exp.previousElementSibling : null;
  if(exp) {{ exp.classList.add('open'); if(ebtn) ebtn.textContent='▼ Hide Explanation'; }}
}}

// ── SUBMIT ALL ────────────────────────────────────────────────────
function submitAll() {{
  if(allDone) {{ showModal(); return; }}
  allDone = true;
  KEYS.forEach(qn => {{ if(!checked[qn]) checkOne(qn); }});
  clearInterval(timerInt);
  showModal();
}}

function showModal() {{
  const c = KEYS.filter(qn => answers[qn]===MCQ[qn].answer && MCQ[qn].answer>=0).length;
  const pct = Math.round(c/TOT*100);
  const g = pct>=90?'A':pct>=80?'B':pct>=70?'C':'D';
  document.getElementById('mg').innerHTML = `<span class="g${{g.toLowerCase()}}">${{g}}</span>`;
  document.getElementById('ms').textContent = `${{c}} / ${{TOT}} (${{pct}}%)`;
  let br='';
  for(let s=0;s<TOT;s+=50){{
    const bl=KEYS.slice(s,s+50);
    const bc=bl.filter(q=>answers[q]===MCQ[q].answer&&MCQ[q].answer>=0).length;
    br+=`Q${{KEYS[s]}}–Q${{KEYS[Math.min(s+49,TOT-1)]}}: ${{bc}}/${{bl.length}}<br>`;
  }}
  document.getElementById('mbr').innerHTML=br;
  document.getElementById('mod').classList.add('on');
}}
function closeMod(){{document.getElementById('mod').classList.remove('on');}}

// ── TOGGLE EXPLANATION ────────────────────────────────────────────
function togExp(qn) {{
  const el=document.getElementById('ex-'+qn);
  const btn=el?el.previousElementSibling:null;
  if(!el)return;
  const open=el.classList.toggle('open');
  if(btn) btn.textContent=(open?'▼ Hide':'▶ Show')+' Explanation';
}}

// ── FILTER / SEARCH ───────────────────────────────────────────────
function setF(f,btn) {{
  curFilter=f;
  document.querySelectorAll('.fb').forEach(b=>b.classList.remove('on'));
  btn.classList.add('on');
  filt();
}}
function filt() {{
  const s=document.getElementById('srch').value.toLowerCase();
  let v=0;
  KEYS.forEach(qn=>{{
    const q=MCQ[qn];
    const c=document.getElementById('qc-'+qn);
    if(!c)return;
    const isDone=answers[qn]!==undefined;
    const fok=curFilter==='all'||(curFilter==='done'&&isDone)||(curFilter==='un'&&!isDone);
    const sok=!s||q.text.toLowerCase().includes(s)||q.options.some(o=>o.toLowerCase().includes(s));
    c.style.display=(fok&&sok)?'':'none';
    if(fok&&sok)v++;
  }});
  document.getElementById('qct').textContent=v+' questions shown';
}}

// ── PROGRESS ─────────────────────────────────────────────────────
function updateProg() {{
  const n=Object.keys(answers).length;
  document.getElementById('pb').style.width=(n/TOT*100)+'%';
  document.getElementById('pt').textContent=n+' / '+TOT+' answered';
}}

// ── BUILD OE ─────────────────────────────────────────────────────
function buildOE() {{
  const L=document.getElementById('oelist');
  OE.forEach(q=>{{
    const c=document.createElement('div');
    c.className='oe-card';
    const imgs = (IMGS['oe_'+q.num]||[]).map(src=>
      `<img class="qimg" src="${{src}}" alt="OE Q${{q.num}} figure" loading="lazy"/>`).join('');
    c.innerHTML=`<div class="qh"><span class="qbadge">Q${{q.num}}</span><div class="oe-q">${{esc(q.text)}}</div></div>
    ${{imgs}}
    <textarea class="oe-ta" rows="3" placeholder="Write your answer…"></textarea>`;
    L.appendChild(c);
  }});
}}

// ── ANALYTICS ────────────────────────────────────────────────────
function drawAnalytics() {{
  const a=Object.keys(answers).length;
  const c=KEYS.filter(qn=>answers[qn]===MCQ[qn].answer&&MCQ[qn].answer>=0).length;
  const pct=a?Math.round(c/a*100):0;
  document.getElementById('stats').innerHTML=`
    <div class="st"><div class="sv">${{a}}</div><div class="sl">Answered</div></div>
    <div class="st"><div class="sv">${{c}}</div><div class="sl">Correct</div></div>
    <div class="st"><div class="sv">${{a-c}}</div><div class="sl">Incorrect</div></div>
    <div class="st"><div class="sv">${{pct}}%</div><div class="sl">Accuracy</div></div>
    <div class="st"><div class="sv">${{TOT-a}}</div><div class="sl">Remaining</div></div>`;
  const labels=[],data=[],colors=[];
  for(let s=0;s<TOT;s+=50){{
    const bl=KEYS.slice(s,s+50);
    const ba=bl.filter(q=>answers[q]!==undefined).length;
    const bc=bl.filter(q=>answers[q]===MCQ[q].answer&&MCQ[q].answer>=0).length;
    const bp=ba?Math.round(bc/ba*100):0;
    labels.push(`Q${{KEYS[s]}}–${{KEYS[Math.min(s+49,TOT-1)]}}`);
    data.push(bp); colors.push(bp>=70?'#22c55e':bp>=50?'#f59e0b':'#ef4444');
  }}
  if(chartInst)chartInst.destroy();
  chartInst=new Chart(document.getElementById('ac').getContext('2d'),{{
    type:'bar',
    data:{{labels,datasets:[{{label:'Score %',data,backgroundColor:colors,borderRadius:5}}]}},
    options:{{responsive:true,plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.parsed.y+'%'}}}}}},
      scales:{{y:{{min:0,max:100,ticks:{{color:'#94a3b8',callback:v=>v+'%'}},grid:{{color:'rgba(148,163,184,.1)'}}}},
               x:{{ticks:{{color:'#94a3b8'}},grid:{{display:false}}}}}}}}
  }});
}}

// ── TIMER ────────────────────────────────────────────────────────
let timerInt=setInterval(()=>{{
  timerSecs--;
  const m=String(Math.floor(timerSecs/60)).padStart(2,'0');
  const s=String(timerSecs%60).padStart(2,'0');
  const el=document.getElementById('tmr');
  el.textContent=m+':'+s;
  if(timerSecs<=300)el.classList.add('urg');
  if(timerSecs<=0){{clearInterval(timerInt);el.textContent='00:00';}}
}},1000);

// ── INIT ─────────────────────────────────────────────────────────
buildMCQ();
buildOE();
</script>
</body>
</html>"""

out = 'index.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(HTML)
print(f"Written: {out} ({len(HTML)//1024} KB)")
print(f"MCQ: {total_mcq} | Open-ended: {total_oe}")
