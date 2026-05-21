#!/usr/bin/env python3
"""Build the AceTeam vision document into a single-page HTML book."""

import re
import markdown
from pathlib import Path

VISION_DIR = Path(__file__).parent
OUT_FILE = VISION_DIR / "book.html"

CHAPTERS = [
    ("part1-world-changed", "The World Has Changed"),
    ("part2-the-void", "The Void"),
    ("part3-the-pattern", "The Pattern"),
    ("part4-the-stack", "What the Stack Requires"),
    ("part5-transitions", "The Transitions"),
    ("part6-what-comes-next", "What Comes Next"),
]

TEMPLATES_DIR = VISION_DIR / "templates"


def load_shared_css():
    return (TEMPLATES_DIR / "shared.css").read_text()


def load_nav(active_page="book", extra=""):
    nav = (TEMPLATES_DIR / "nav.html").read_text()
    nav = nav.replace("{nav_active_essay}", "active" if active_page == "essay" else "")
    nav = nav.replace("{nav_active_book}", "active" if active_page == "book" else "")
    nav = nav.replace("{nav_active_zh}", "active" if active_page == "zh" else "")
    nav = nav.replace("{nav_extra}", extra)
    return nav


def load_shared_js():
    return (TEMPLATES_DIR / "shared.js").read_text()


INTERSTITIALS = {
    1: """
<div class="visual-break">
  <div class="stat-row">
    <div class="stat-card"><div class="stat-number" data-count="400">0</div><div class="stat-label">Billion USD<br>AI infra market by 2028</div></div>
    <div class="stat-card"><div class="stat-number" data-count="150">0</div><div class="stat-unit">+</div><div class="stat-label">Organizations backing<br>Google's A2A protocol</div></div>
    <div class="stat-card"><div class="stat-number" data-count="10">0</div><div class="stat-unit">x</div><div class="stat-label">Cloud API markup<br>vs owned inference</div></div>
  </div>
</div>""",
    2: """
<div class="visual-break">
  <div class="diagram-svg">
    <div class="diagram-title">Seven Forces, One Destination</div>
    <svg viewBox="0 0 700 380" class="arch-diagram">
      <defs>
        <linearGradient id="gc" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--accent)" stop-opacity="0.25"/><stop offset="100%" stop-color="var(--accent)" stop-opacity="0.05"/></linearGradient>
      </defs>
      <rect x="200" y="280" width="300" height="70" rx="14" fill="url(#gc)" stroke="var(--accent)" stroke-width="2" class="layer-animate" style="animation-delay:0.8s"/>
      <text x="350" y="310" text-anchor="middle" fill="var(--accent)" font-family="Space Grotesk,sans-serif" font-size="14" font-weight="700">AGENT ACCOUNTABILITY</text>
      <text x="350" y="330" text-anchor="middle" fill="var(--text-dim)" font-size="11">The infrastructure they all converge on</text>
      <g font-family="Space Grotesk,sans-serif" font-size="11" font-weight="500">
        <rect x="20" y="20" width="120" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--red)" stroke-width="1" class="flywheel-node" style="animation-delay:0s"/><text x="80" y="38" text-anchor="middle" fill="var(--red)" font-size="11" font-weight="600">Regulatory</text><text x="80" y="52" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">EU AI Act, NIST</text>
        <rect x="160" y="20" width="120" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--orange)" stroke-width="1" class="flywheel-node" style="animation-delay:0.1s"/><text x="220" y="38" text-anchor="middle" fill="var(--orange)" font-size="11" font-weight="600">Economic</text><text x="220" y="52" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">CFO cost control</text>
        <rect x="300" y="20" width="120" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--green)" stroke-width="1" class="flywheel-node" style="animation-delay:0.2s"/><text x="360" y="38" text-anchor="middle" fill="var(--green)" font-size="11" font-weight="600">Safety</text><text x="360" y="52" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">Runtime verdicts</text>
        <rect x="440" y="20" width="120" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--purple)" stroke-width="1" class="flywheel-node" style="animation-delay:0.3s"/><text x="500" y="38" text-anchor="middle" fill="var(--purple)" font-size="11" font-weight="600">Legal</text><text x="500" y="52" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">Liability chains</text>
        <rect x="580" y="20" width="100" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--cyan)" stroke-width="1" class="flywheel-node" style="animation-delay:0.4s"/><text x="630" y="38" text-anchor="middle" fill="var(--cyan)" font-size="11" font-weight="600">Environmental</text><text x="630" y="52" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">Carbon per output</text>
        <rect x="90" y="100" width="120" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--text-dim)" stroke-width="1" class="flywheel-node" style="animation-delay:0.5s"/><text x="150" y="118" text-anchor="middle" fill="var(--text-dim)" font-size="11" font-weight="600">Geopolitical</text><text x="150" y="132" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">Sovereign compute</text>
        <rect x="490" y="100" width="120" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--text-dim)" stroke-width="1" class="flywheel-node" style="animation-delay:0.6s"/><text x="550" y="118" text-anchor="middle" fill="var(--text-dim)" font-size="11" font-weight="600">Enterprise</text><text x="550" y="132" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">CISO governance</text>
      </g>
      <line x1="80" y1="64" x2="300" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
      <line x1="220" y1="64" x2="320" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
      <line x1="360" y1="64" x2="350" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
      <line x1="500" y1="64" x2="380" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
      <line x1="630" y1="64" x2="420" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
      <line x1="150" y1="144" x2="280" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
      <line x1="550" y1="144" x2="430" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
    </svg>
  </div>
</div>""",
    3: """
<div class="visual-break">
  <div class="timeline">
    <div class="timeline-title">The Accountability Pattern</div>
    <div class="timeline-track">
      <div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-date">1494</div><div class="timeline-text">Double-entry bookkeeping. Commerce becomes auditable.</div></div>
      <div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-date">1973</div><div class="timeline-text">SWIFT. Cross-border banking gets a standard message format.</div></div>
      <div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-date">1995</div><div class="timeline-text">SSL/TLS. The internet becomes safe for transactions.</div></div>
      <div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-date">2013</div><div class="timeline-text">Docker + OCI. Software deployment becomes reproducible.</div></div>
      <div class="timeline-item active"><div class="timeline-dot"></div><div class="timeline-date">202X</div><div class="timeline-text">Agent accountability. The agent economy gets its receipt book.</div></div>
    </div>
  </div>
</div>""",
    4: """
<div class="visual-break">
  <div class="diagram-svg">
    <div class="diagram-title">The Seven-Layer Stack</div>
    <svg viewBox="0 0 700 540" class="arch-diagram">
      <defs>
        <linearGradient id="s1" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--accent)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--accent)" stop-opacity="0.05"/></linearGradient>
        <linearGradient id="s2" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--green)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--green)" stop-opacity="0.05"/></linearGradient>
        <linearGradient id="s3" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--orange)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--orange)" stop-opacity="0.05"/></linearGradient>
        <linearGradient id="s4" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--purple)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--purple)" stop-opacity="0.05"/></linearGradient>
        <linearGradient id="s5" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--red)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--red)" stop-opacity="0.05"/></linearGradient>
        <linearGradient id="s6" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--cyan)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--cyan)" stop-opacity="0.05"/></linearGradient>
      </defs>
      <rect x="80" y="10" width="540" height="60" rx="10" fill="url(#s1)" stroke="var(--accent)" stroke-width="1.5" class="layer-animate" style="animation-delay:0.9s"/>
      <text x="130" y="38" fill="var(--accent)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">M</text>
      <text x="160" y="38" fill="var(--accent)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">MARKETPLACE</text>
      <text x="440" y="38" fill="var(--text-dimmer)" font-size="10">Agent-to-agent commerce</text>
      <rect x="80" y="80" width="540" height="60" rx="10" fill="url(#s6)" stroke="var(--cyan)" stroke-width="1.5" class="layer-animate" style="animation-delay:0.75s"/>
      <text x="130" y="108" fill="var(--cyan)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">A</text>
      <text x="160" y="108" fill="var(--cyan)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">AGENCY</text>
      <text x="440" y="108" fill="var(--text-dimmer)" font-size="10">Identity, authorization, consent</text>
      <rect x="80" y="150" width="540" height="60" rx="10" fill="url(#s5)" stroke="var(--red)" stroke-width="1.5" class="layer-animate" style="animation-delay:0.6s"/>
      <text x="130" y="178" fill="var(--red)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">E</text>
      <text x="160" y="178" fill="var(--red)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">ENFORCEMENT</text>
      <text x="440" y="178" fill="var(--text-dimmer)" font-size="10">Runtime safety verdicts</text>
      <rect x="80" y="220" width="540" height="60" rx="10" fill="url(#s4)" stroke="var(--purple)" stroke-width="1.5" class="layer-animate" style="animation-delay:0.45s"/>
      <text x="130" y="248" fill="var(--purple)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">T</text>
      <text x="160" y="248" fill="var(--purple)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">TRUST</text>
      <text x="440" y="248" fill="var(--text-dimmer)" font-size="10">Reputation from historical transactions</text>
      <rect x="80" y="290" width="540" height="60" rx="10" fill="url(#s3)" stroke="var(--orange)" stroke-width="1.5" class="layer-animate" style="animation-delay:0.3s"/>
      <text x="130" y="318" fill="var(--orange)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">E</text>
      <text x="160" y="318" fill="var(--orange)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">EXCHANGE</text>
      <text x="440" y="318" fill="var(--text-dimmer)" font-size="10">Multi-party settlement</text>
      <rect x="80" y="360" width="540" height="60" rx="10" fill="url(#s2)" stroke="var(--green)" stroke-width="1.5" class="layer-animate" style="animation-delay:0.15s"/>
      <text x="130" y="388" fill="var(--green)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">C</text>
      <text x="160" y="388" fill="var(--green)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">COMPUTE</text>
      <text x="440" y="388" fill="var(--text-dimmer)" font-size="10">Dynamic resource allocation</text>
      <rect x="80" y="430" width="540" height="60" rx="10" fill="var(--accent)" fill-opacity="0.08" stroke="var(--accent)" stroke-width="2" class="layer-animate" style="animation-delay:0s"/>
      <text x="130" y="458" fill="var(--accent)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">A</text>
      <text x="160" y="458" fill="var(--accent)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">ACCOUNTABILITY</text>
      <text x="440" y="458" fill="var(--text-dimmer)" font-size="10">Cost, provenance, governance</text>
      <text x="350" y="520" text-anchor="middle" fill="var(--text-dimmer)" font-family="Space Grotesk,sans-serif" font-size="11" font-style="italic">Each layer builds on the one below</text>
    </svg>
  </div>
</div>""",
    5: """
<div class="visual-break">
  <div class="stat-row">
    <div class="stat-card"><div class="stat-number" data-count="20">0</div><div class="stat-unit">%</div><div class="stat-label">AI maturity declined<br>year-over-year</div></div>
    <div class="stat-card"><div class="stat-number" data-count="72">0</div><div class="stat-unit">%</div><div class="stat-label">AI projects stall<br>at pilot stage</div></div>
    <div class="stat-card"><div class="stat-number" data-count="96">0</div><div class="stat-unit">%</div><div class="stat-label">CIOs involved in<br>AI strategy</div></div>
  </div>
  <div class="stat-source">ServiceNow / Oxford Economics survey of 4,473 organizations, 2025</div>
</div>""",
    6: """
<div class="visual-break cta-section">
  <div class="cta-line fade-in">The revolution always comes first.</div>
  <div class="cta-line fade-in">The accountability layer always comes second.</div>
  <div class="cta-line fade-in">The accountability layer always outlasts the revolution.</div>
  <div class="cta-divider"></div>
  <div class="cta-accent fade-in">The agent economy has its revolution. It is waiting for its ledger.</div>
</div>""",
}

# Visuals injected after specific sections within chapters
# Key: (chapter_num, section_file_num) e.g. (2, 1) = after part2/01-*.mdx
SECTION_VISUALS = {
    (1, 3): """
<div class="visual-break mini-break">
  <div class="force-grid">
    <div class="force-card fade-in">
      <div class="force-num">01</div>
      <div class="force-title">Cloud Lock-in</div>
      <div class="force-desc">Per-token rent. Your data on their servers. Their deprecation schedule.</div>
      <div class="force-bar"><div class="bar-fill" data-width="85" style="--bar-color: var(--red)"></div></div>
      <div class="force-meta">85% of AI spend &rarr; 3 providers</div>
    </div>
    <div class="force-card fade-in">
      <div class="force-num">02</div>
      <div class="force-title">Workflow Gap</div>
      <div class="force-desc">AI does tasks. Nobody automates the full workflow. The 90% between prompts is manual.</div>
      <div class="force-bar"><div class="bar-fill" data-width="72" style="--bar-color: var(--orange)"></div></div>
      <div class="force-meta">72% of AI projects stall at pilot</div>
    </div>
    <div class="force-card fade-in">
      <div class="force-num">03</div>
      <div class="force-title">Hardware Crossover</div>
      <div class="force-desc">Own-inference costs crossed cloud APIs. The gap widens every quarter.</div>
      <div class="force-bar"><div class="bar-fill" data-width="60" style="--bar-color: var(--green)"></div></div>
      <div class="force-meta">10x cost advantage by 2028</div>
    </div>
  </div>
</div>""",
    (4, 2): """
<div class="visual-break mini-break fade-in">
  <div class="reg-grid">
    <div class="reg-item"><div class="reg-flag">EU</div><div class="reg-name">GDPR + AI Act</div></div>
    <div class="reg-item"><div class="reg-flag">CA</div><div class="reg-name">PIPEDA + C-27</div></div>
    <div class="reg-item"><div class="reg-flag">US</div><div class="reg-name">CCPA + state laws</div></div>
    <div class="reg-item"><div class="reg-flag">AU</div><div class="reg-name">Privacy Act reform</div></div>
    <div class="reg-item"><div class="reg-flag">BR</div><div class="reg-name">LGPD</div></div>
    <div class="reg-item"><div class="reg-flag">IN</div><div class="reg-name">DPDP Act</div></div>
  </div>
  <div class="reg-caption">Jurisdictions requiring or proposing data sovereignty measures</div>
</div>""",
    (4, 3): """
<div class="visual-break mini-break fade-in">
  <div class="diagram-svg">
    <div class="diagram-title">The Execution Envelope</div>
    <svg viewBox="0 0 500 200" class="envelope-diagram">
      <rect x="20" y="20" width="460" height="160" rx="12" fill="var(--bg-surface)" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="6,3"/>
      <text x="250" y="18" text-anchor="middle" fill="var(--accent)" font-family="Space Grotesk,sans-serif" font-size="11" font-weight="600">ExecutionEnvelope</text>
      <rect x="40" y="45" width="130" height="50" rx="8" fill="var(--red)" fill-opacity="0.1" stroke="var(--red)" stroke-width="1"/>
      <text x="105" y="68" text-anchor="middle" fill="var(--red)" font-size="11" font-weight="600">Cost Tree</text>
      <text x="105" y="82" text-anchor="middle" fill="var(--text-dim)" font-size="9">Who spent what</text>
      <rect x="185" y="45" width="130" height="50" rx="8" fill="var(--green)" fill-opacity="0.1" stroke="var(--green)" stroke-width="1"/>
      <text x="250" y="68" text-anchor="middle" fill="var(--green)" font-size="11" font-weight="600">Citations</text>
      <text x="250" y="82" text-anchor="middle" fill="var(--text-dim)" font-size="9">Source &rarr; conclusion</text>
      <rect x="330" y="45" width="130" height="50" rx="8" fill="var(--orange)" fill-opacity="0.1" stroke="var(--orange)" stroke-width="1"/>
      <text x="395" y="68" text-anchor="middle" fill="var(--orange)" font-size="11" font-weight="600">Governance</text>
      <text x="395" y="82" text-anchor="middle" fill="var(--text-dim)" font-size="9">Data handling rules</text>
      <rect x="120" y="115" width="260" height="45" rx="8" fill="var(--accent)" fill-opacity="0.08" stroke="var(--accent)" stroke-width="1"/>
      <text x="250" y="137" text-anchor="middle" fill="var(--accent)" font-size="11" font-weight="600">Execution Context</text>
      <text x="250" y="151" text-anchor="middle" fill="var(--text-dim)" font-size="9">Budget &bull; Jurisdiction &bull; Trace ID &bull; Org chain</text>
    </svg>
  </div>
</div>""",
    (5, 1): """
<div class="visual-break mini-break">
  <div class="stat-row compact">
    <div class="stat-card small fade-in">
      <div class="stat-number" data-count="36">0</div><div class="stat-unit">%</div>
      <div class="stat-label">Currently using<br>agentic AI</div>
    </div>
    <div class="stat-card small fade-in">
      <div class="stat-number" data-count="46">0</div><div class="stat-unit">%</div>
      <div class="stat-label">Considering within<br>12 months</div>
    </div>
    <div class="stat-card small fade-in">
      <div class="stat-number" data-count="69">0</div><div class="stat-unit">%</div>
      <div class="stat-label">Elite CIOs use<br>integrated platforms</div>
    </div>
  </div>
  <div class="stat-source">ServiceNow / Oxford Economics, 4,473 organizations, 2025</div>
</div>""",
    (5, 4): """
<div class="visual-break mini-break fade-in">
  <div class="comparison-chart">
    <div class="comparison-title">Economics: Cloud API vs Sovereign Compute</div>
    <div class="comparison-grid">
      <div class="comparison-col">
        <div class="comparison-header bad">Cloud API</div>
        <div class="comparison-item"><span class="comparison-val">$15-75</span><span class="comparison-desc">per 1M tokens</span></div>
        <div class="comparison-item"><span class="comparison-val">Variable</span><span class="comparison-desc">monthly cost</span></div>
        <div class="comparison-item"><span class="comparison-val">0%</span><span class="comparison-desc">data ownership</span></div>
      </div>
      <div class="comparison-vs">vs</div>
      <div class="comparison-col">
        <div class="comparison-header good">Sovereign</div>
        <div class="comparison-item"><span class="comparison-val">$0.50-2</span><span class="comparison-desc">per 1M tokens (owned)</span></div>
        <div class="comparison-item"><span class="comparison-val">Fixed</span><span class="comparison-desc">hardware amortization</span></div>
        <div class="comparison-item"><span class="comparison-val">100%</span><span class="comparison-desc">data ownership</span></div>
      </div>
    </div>
  </div>
</div>""",
}

PULLQUOTES = {
    2: ("The agent economy is running without paperwork.", "On the void"),
    3: ("Every revolution eventually produces an accountability layer. The accountability layer always outlasts the revolution.", "On the pattern"),
    4: ("The missing layer is not more hardware or better models. It is the infrastructure to account for what agents do.", "On the stack"),
    5: ("Models are commodities. Trust infrastructure is the moat.", "On the transitions"),
    6: ("The question is not whether this infrastructure gets built. It is whether it gets designed.", "On what comes next"),
}

ABSTRACT_PARAGRAPHS = [
    '<strong>AI is reshaping who does work, not just where it happens.</strong> Agents draft contracts, triage patients, process invoices, write reports. The revolution is here. But when Agent A calls Agent B calls Agent C across three organizations &mdash; nobody can account for what happened, what it cost, or whether the data was handled correctly.',
    'This is not a feature gap. It is a <strong>category gap</strong> &mdash; the same kind of gap that double-entry bookkeeping filled for commerce, that TLS filled for the internet, that container standards filled for software deployment.',
    'Seven independent forces &mdash; regulatory, economic, safety, legal, environmental, geopolitical, enterprise &mdash; are converging on the same requirement: <strong>standardized agent accountability.</strong> None of them are coordinating. They all need the same infrastructure.',
    'This document traces the pattern: the world has changed, a void exists in the infrastructure, history shows how that void always gets filled, and a specific seven-layer stack is what the agent economy requires. It examines the transitions &mdash; organizational, human, governmental, economic &mdash; that must happen simultaneously. And it projects what work looks like when the infrastructure exists.',
    'The accountability layer will be built. The question is whether it is designed intentionally as a coherent stack, or cobbled together from incompatible patches.',
]

AUDIO_SLUGS = {
    "front-matter": "part00-front-matter",
    "part1-world-changed": "part01-world-changed",
    "part2-the-void": "part02-the-void",
    "part3-the-pattern": "part03-the-pattern",
    "part4-the-stack": "part04-the-stack",
    "part5-transitions": "part05-transitions",
    "part6-what-comes-next": "part06-what-comes-next",
}


def read_mdx(path: Path) -> str:
    text = path.read_text()
    text = re.sub(r'^---\n.*?---\n', '', text, flags=re.DOTALL)
    text = re.sub(r'^\s*import\s+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*export\s+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[([^\]]+)\]\(\./[^)]+\)', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\(\.\./[^)]+\)', r'\1', text)
    return text.strip()


def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def tag_paragraphs(html: str, chapter_num: int, counter: list[int]) -> tuple[str, list[str]]:
    """Add id='ab-CH-N' to each <p> tag and collect plain text."""
    paras = []
    def replacer(m):
        content = m.group(1)
        idx = counter[0]
        counter[0] += 1
        plain = re.sub(r'<[^>]+>', '', content).strip()
        paras.append(plain)
        return f'<p id="ab-{chapter_num}-{idx}">{content}</p>'
    tagged = re.sub(r'<p>(.*?)</p>', replacer, html, flags=re.DOTALL)
    return tagged, paras


def build_content() -> tuple[str, list[dict], dict]:
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'footnotes', 'smarty'])
    sections_html = []
    toc_entries = []
    chapter_paras: dict[int, list[str]] = {}

    for i, (chapter_slug, chapter_title) in enumerate(CHAPTERS, 1):
        chapter_dir = VISION_DIR / chapter_slug
        if not chapter_dir.exists():
            continue

        chapter_id = slugify(chapter_title)
        toc_entries.append({"id": chapter_id, "title": f"Part {i}: {chapter_title}", "level": 0})
        para_counter = [0]
        ch_paras: list[str] = []

        if i in PULLQUOTES:
            quote, attr = PULLQUOTES[i]
            sections_html.append(f'<div class="pullquote"><blockquote>{quote}</blockquote><cite>{attr}</cite></div>')

        sections_html.append(f'<section class="chapter-break" id="{chapter_id}">')
        sections_html.append(f'<div class="chapter-number">Part {i}</div>')
        sections_html.append(f'<h1>{chapter_title}</h1>')

        index_file = chapter_dir / "index.mdx"
        if index_file.exists():
            index_text = read_mdx(index_file)
            index_text = re.sub(r'^#\s+.*$', '', index_text, count=1, flags=re.MULTILINE).strip()
            if index_text:
                index_html = md.convert(index_text)
                md.reset()
                index_html, p = tag_paragraphs(index_html, i, para_counter)
                ch_paras.extend(p)
                sections_html.append(f'<div class="chapter-intro">{index_html}</div>')

        sections_html.append('</section>')

        for section_file in sorted(chapter_dir.glob("[0-9]*.mdx")):
            section_num = int(section_file.stem.split('-')[0])
            section_text = read_mdx(section_file)
            first_heading = re.search(r'^#\s+(.+)$', section_text, re.MULTILINE)
            if first_heading:
                section_title = first_heading.group(1)
                section_id = f"{chapter_id}--{slugify(section_title)}"
                toc_entries.append({"id": section_id, "title": section_title, "level": 1})
                section_text = section_text[:first_heading.start()] + section_text[first_heading.end():]
            else:
                section_title = section_file.stem
                section_id = f"{chapter_id}--{slugify(section_title)}"

            section_html = md.convert(section_text)
            md.reset()
            section_html, p = tag_paragraphs(section_html, i, para_counter)
            ch_paras.extend(p)

            sections_html.append(f'<section class="subsection fade-in" id="{section_id}">')
            sections_html.append(f'<h2 class="section-title">{section_title}</h2>')
            sections_html.append(section_html)
            sections_html.append('</section>')

            if (i, section_num) in SECTION_VISUALS:
                sections_html.append(SECTION_VISUALS[(i, section_num)])

        if i in INTERSTITIALS:
            sections_html.append(INTERSTITIALS[i])

        chapter_paras[i] = ch_paras

    return '\n'.join(sections_html), toc_entries, chapter_paras


def build_toc_html(entries: list[dict], back_matter_entries: list[dict] = None) -> str:
    items = ['<a href="#abstract" class="toc-chapter">Abstract</a>']
    items.append('<a href="#preface" class="toc-chapter">Preface</a>')
    for entry in entries:
        cls = "toc-chapter" if entry["level"] == 0 else "toc-section"
        items.append(f'<a href="#{entry["id"]}" class="{cls}">{entry["title"]}</a>')
    if back_matter_entries:
        for entry in back_matter_entries:
            items.append(f'<a href="#{entry["id"]}" class="toc-chapter">{entry["title"]}</a>')
    return '\n'.join(items)


TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="manifest.json">
<title>Trust at Scale — Jason Sun</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
{shared_css}

  /* --- Book-specific overrides --- */
  :root { --toc-width: 220px; }

  .audio-player {
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 300;
    background: var(--bg-elevated); border-top: 1px solid var(--border-strong);
    padding: 10px 20px; display: none; align-items: center; gap: 12px;
    font-family: 'Inter Tight', sans-serif; backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }
  .audio-player.visible { display: flex; }
  .audio-player-toggle {
    position: fixed; bottom: 20px; right: 20px; z-index: 299;
    width: 48px; height: 48px; border-radius: 50%;
    background: var(--accent); color: var(--bg); border: none; cursor: pointer;
    font-size: 20px; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4); transition: transform 0.2s;
  }
  .audio-player-toggle:hover { transform: scale(1.1); }
  .audio-player-toggle.hidden { display: none; }
  .ap-btn {
    background: none; border: none; color: var(--text); cursor: pointer;
    font-size: 18px; padding: 4px 8px; border-radius: 4px; flex-shrink: 0;
  }
  .ap-btn:hover { background: var(--accent-dim); color: var(--accent); }
  .ap-play { font-size: 24px; }
  .ap-chapter-info {
    display: flex; flex-direction: column; min-width: 140px; flex-shrink: 0;
  }
  .ap-chapter-title { font-size: 13px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 200px; }
  .ap-chapter-num { font-size: 11px; color: var(--text-dim); }
  .ap-progress-wrap {
    flex: 1; display: flex; align-items: center; gap: 8px; min-width: 0;
  }
  .ap-time { font-size: 11px; color: var(--text-dim); font-variant-numeric: tabular-nums; flex-shrink: 0; font-family: 'JetBrains Mono', monospace; }
  .ap-progress-bar {
    flex: 1; height: 4px; background: var(--border-strong); border-radius: 2px;
    cursor: pointer; position: relative; min-width: 60px; touch-action: none;
  }
  .ap-progress-bar:hover, .ap-progress-bar.dragging { height: 6px; }
  .ap-progress-fill { height: 100%; background: var(--accent); border-radius: 2px; width: 0; transition: width 0.1s linear; pointer-events: none; }
  .ap-progress-bar::before { content: ''; position: absolute; top: -12px; bottom: -12px; left: 0; right: 0; }
  .ap-progress-thumb { position: absolute; right: -6px; top: 50%; width: 12px; height: 12px; background: var(--accent); border-radius: 50%; transform: translateY(-50%); opacity: 0; transition: opacity 0.2s; pointer-events: none; }
  .ap-progress-bar:hover .ap-progress-thumb, .ap-progress-bar.dragging .ap-progress-thumb { opacity: 1; }
  .ap-speed {
    font-size: 11px; color: var(--text-dim); cursor: pointer; background: var(--bg-surface);
    border: 1px solid var(--border); border-radius: 4px; padding: 2px 6px;
    font-family: 'JetBrains Mono', monospace; flex-shrink: 0;
  }
  .ap-speed:hover { color: var(--accent); border-color: var(--accent); }
  .ap-chapter-list {
    position: absolute; bottom: 100%; left: 0; right: 0;
    background: var(--bg-elevated); border-top: 1px solid var(--border-strong);
    max-height: 300px; overflow-y: auto; display: none;
  }
  .ap-chapter-list.open { display: block; }
  .ap-chapter-item {
    padding: 10px 20px; cursor: pointer; font-size: 13px; color: var(--text-dim);
    display: flex; justify-content: space-between; align-items: center;
  }
  .ap-chapter-item:hover { background: var(--accent-dim); color: var(--text); }
  .ap-chapter-item.active { color: var(--accent); font-weight: 600; }
  .ap-chapter-dur { font-size: 11px; color: var(--text-dimmer); font-family: 'JetBrains Mono', monospace; }
  @media (max-width: 768px) {
    .audio-player { flex-wrap: wrap; padding: 10px 12px; gap: 8px; }
    .ap-btn { font-size: 22px; padding: 8px 12px; min-width: 44px; min-height: 44px; display: flex; align-items: center; justify-content: center; }
    .ap-play { font-size: 28px; }
    .ap-speed { font-size: 13px; padding: 6px 10px; min-height: 44px; }
    .ap-chapter-info { min-width: 80px; flex: 1; }
    .ap-chapter-title { max-width: none; }
    .ap-progress-wrap { order: 10; width: 100%; }
    .ap-chapter-list { max-height: 60vh; }
    .ap-chapter-item { padding: 14px 20px; font-size: 15px; min-height: 48px; }
  }
  p[id^="ab-"] { transition: background 0.3s, border-color 0.3s; border-left: 3px solid transparent; padding-left: 8px; margin-left: -11px; border-radius: 2px; cursor: pointer; }
  p[id^="ab-"]:hover { background: var(--accent-dim); }
  p[id^="ab-"].ab-active { background: var(--accent-dim); border-left-color: var(--accent); }
  .ap-follow { font-size: 11px; color: var(--text-dim); cursor: pointer; background: none; border: 1px solid var(--border); border-radius: 4px; padding: 2px 6px; flex-shrink: 0; }
  .ap-follow:hover { color: var(--accent); border-color: var(--accent); }
  .ap-follow.on { color: var(--accent); border-color: var(--accent); background: var(--accent-dim); }
  @media print { .audio-player, .audio-player-toggle { display: none !important; } }

  /* --- Abstract --- */
  .abstract {
    max-width: var(--max-width); margin: 0 auto; padding: 80px 24px 60px;
    border-bottom: 1px solid var(--border);
  }
  .abstract-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 12px; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--accent); margin-bottom: 16px;
  }
  .abstract-text {
    font-size: clamp(15px, 1.6vw, 19px); line-height: 1.7; color: var(--text-dim);
  }
  .abstract-text strong { color: var(--text); }

  /* --- TOC Sidebar --- */
  .toc {
    position: fixed; top: 50%; transform: translateY(-50%);
    left: max(16px, calc(50vw - 576px));
    width: var(--toc-width); max-height: 80vh;
    overflow-y: auto; scrollbar-width: none;
    opacity: 0; transition: opacity 0.4s ease; z-index: 100; padding: 8px 0;
  }
  .toc.visible { opacity: 1; }
  .toc::-webkit-scrollbar { display: none; }
  .toc a {
    display: block; text-decoration: none; font-size: 11.5px; line-height: 1.4;
    padding: 3px 12px; color: var(--text-dimmer); border-left: 2px solid transparent;
    transition: color 0.2s, border-color 0.2s;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .toc a:hover { color: var(--text-dim); }
  .toc a.active { color: var(--accent); border-left-color: var(--accent); }
  .toc .toc-chapter {
    font-family: 'Space Grotesk', sans-serif; font-weight: 600;
    font-size: 11px; letter-spacing: 0.03em; margin-top: 10px; color: var(--text-dim);
  }
  .toc .toc-chapter:first-child { margin-top: 0; }
  .toc .toc-section { padding-left: 20px; font-weight: 400; }

  /* --- Article --- */
  .article { max-width: var(--max-width); margin: 0 auto; padding: 0 24px 160px; }

  /* --- Chapter Break --- */
  .chapter-break { padding: 100px 0 32px; margin-top: 60px; position: relative; }
  .chapter-break::before {
    content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%);
    width: 60px; height: 1px; background: var(--border-strong);
  }
  .chapter-break:first-child { margin-top: 0; }
  .chapter-break:first-child::before { display: none; }
  .chapter-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 12px; font-weight: 500; color: var(--accent);
    text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 10px;
  }
  .chapter-break h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(28px, 4vw, 48px); font-weight: 700;
    letter-spacing: -0.03em; line-height: 1.1; margin-bottom: 20px;
  }
  .chapter-intro {
    color: var(--text-dim); font-size: clamp(14px, 1.4vw, 17px); line-height: 1.7;
    border-left: 3px solid var(--accent); padding-left: 20px; margin: 12px 0;
  }

  /* --- Subsections --- */
  .subsection { padding: 40px 0 0; }
  .section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(20px, 2.5vw, 28px); font-weight: 600;
    letter-spacing: -0.02em; line-height: 1.2; margin-bottom: 20px;
  }

  /* --- Book typography overrides --- */
  h2 {
    font-size: clamp(17px, 2vw, 24px); font-weight: 700;
    margin: 36px 0 14px; padding-top: 14px;
  }
  hr { margin: 40px 0; }

  /* --- Tables --- */
  table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; }
  th {
    background: var(--bg-surface); text-align: left; padding: 8px 12px;
    font-weight: 600; font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.05em; color: var(--text-dim); border-bottom: 1px solid var(--border);
  }
  td { padding: 8px 12px; border-bottom: 1px solid var(--border); }

  /* --- Inline callout (blockquote in chapter body) --- */
  .chapter-section blockquote {
    border-left: 3px solid var(--accent); margin: 24px 0; padding: 16px 20px;
    background: var(--bg-surface); border-radius: 0 8px 8px 0;
    font-size: 14px; line-height: 1.65; color: var(--text-dim);
  }
  .chapter-section blockquote strong { color: var(--text); }

  /* --- Pullquote --- */
  .pullquote {
    max-width: var(--max-width); margin: 80px auto 40px; padding: 0 24px; text-align: center;
  }
  .pullquote blockquote {
    border: none; padding: 0; margin: 0; font-style: italic;
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(22px, 3vw, 36px); font-weight: 400;
    line-height: 1.3; color: var(--text); letter-spacing: -0.02em;
  }
  [data-theme="dark"] .pullquote blockquote { color: var(--accent); }
  .pullquote cite {
    display: block; margin-top: 12px; font-size: 13px;
    font-style: normal; color: var(--text-dimmer); letter-spacing: 0.05em; text-transform: uppercase;
  }

  /* --- Visual Break (shared) --- */
  .visual-break { max-width: 800px; margin: 60px auto; padding: 0 24px; }

  /* --- Stat cards --- */
  .stat-row { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }
  .stat-card {
    flex: 1; min-width: 160px; max-width: 220px;
    background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 28px 20px; text-align: center;
    transition: border-color 0.2s, transform 0.2s;
  }
  .stat-card:hover { border-color: var(--accent); transform: translateY(-2px); }
  .stat-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 42px; font-weight: 700; color: var(--accent);
    line-height: 1; display: inline;
  }
  .stat-unit {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 28px; font-weight: 400; color: var(--accent); margin-left: 2px;
  }
  .stat-label {
    margin-top: 10px; font-size: 12px; color: var(--text-dim); line-height: 1.4; letter-spacing: 0.02em;
  }
  .stat-source {
    text-align: center; font-size: 11px; color: var(--text-dimmer);
    font-style: italic; margin-top: 16px;
  }

  /* --- SVG Diagrams --- */
  .diagram-svg { text-align: center; }
  .diagram-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 13px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-dim); margin-bottom: 20px;
    text-align: center;
  }
  .arch-diagram, .flywheel-diagram, .margin-chart, .envelope-diagram { max-width: 600px; width: 100%; height: auto; }
  .layer-animate { opacity: 0; animation: layerFade 0.6s ease forwards; }
  @keyframes layerFade { to { opacity: 1; } }
  .flywheel-node { opacity: 0; animation: nodeFade 0.4s ease forwards; }
  @keyframes nodeFade { to { opacity: 1; } }

  /* --- Comparison chart --- */
  .comparison-chart { max-width: 560px; margin: 0 auto; }
  .comparison-chart.compact { max-width: 480px; }
  .comparison-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 13px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-dim);
    text-align: center; margin-bottom: 20px;
  }
  .comparison-grid { display: flex; align-items: stretch; gap: 0; }
  .comparison-col { flex: 1; }
  .comparison-vs {
    display: flex; align-items: center; justify-content: center; padding: 0 16px;
    font-family: 'Space Grotesk', sans-serif; font-size: 14px; font-weight: 600;
    color: var(--text-dimmer); text-transform: uppercase;
  }
  .comparison-header {
    font-family: 'Space Grotesk', sans-serif; font-size: 14px; font-weight: 700;
    padding: 12px 16px; border-radius: 8px 8px 0 0; text-align: center;
  }
  .comparison-header.bad { background: rgba(248,81,73,0.1); color: var(--red); }
  .comparison-header.good { background: rgba(63,185,80,0.1); color: var(--green); }
  .comparison-item {
    padding: 10px 16px; border-bottom: 1px solid var(--border);
    display: flex; flex-direction: column; gap: 2px;
  }
  .comparison-val { font-weight: 600; font-size: 16px; }
  .comparison-desc { font-size: 12px; color: var(--text-dim); }

  /* --- Timeline --- */
  .timeline { max-width: 560px; margin: 0 auto; }
  .timeline-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 13px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-dim);
    text-align: center; margin-bottom: 24px;
  }
  .timeline-track { position: relative; padding-left: 28px; border-left: 2px solid var(--border); }
  .timeline-item { position: relative; padding: 0 0 20px 20px; }
  .timeline-dot {
    position: absolute; left: -34px; top: 4px;
    width: 10px; height: 10px; border-radius: 50%;
    background: var(--bg-surface); border: 2px solid var(--text-dimmer);
  }
  .timeline-item.active .timeline-dot { background: var(--accent); border-color: var(--accent); box-shadow: 0 0 8px var(--accent-dim); }
  .timeline-date { font-family: 'Space Grotesk', sans-serif; font-size: 13px; font-weight: 700; color: var(--accent); }
  .timeline-text { font-size: 13px; color: var(--text-dim); margin-top: 2px; }

  /* --- Force grid (ch2 interstitial) --- */
  .force-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
  .force-card {
    background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px 20px;
    transition: border-color 0.2s, transform 0.2s;
  }
  .force-card:hover { border-color: var(--accent); transform: translateY(-2px); }
  .force-num {
    font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 500;
    color: var(--text-dimmer); letter-spacing: 0.05em; margin-bottom: 8px;
  }
  .force-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 600;
    color: var(--text); margin-bottom: 8px;
  }
  .force-desc { font-size: 13px; color: var(--text-dim); line-height: 1.5; margin-bottom: 16px; }
  .force-bar {
    height: 4px; background: var(--bg-elevated); border-radius: 2px; overflow: hidden; margin-bottom: 10px;
  }
  .bar-fill {
    height: 100%; width: 0; border-radius: 2px;
    background: var(--bar-color, var(--accent));
    transition: width 1.2s cubic-bezier(0.22, 1, 0.36, 1);
  }
  .force-meta { font-size: 11px; color: var(--text-dimmer); font-style: italic; }

  /* --- Capability grid (ch4 interstitial) --- */
  .cap-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
  .cap-card {
    background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px 16px; text-align: center;
    transition: border-color 0.2s, transform 0.2s;
  }
  .cap-card:hover { border-color: var(--accent); transform: translateY(-2px); }
  .cap-icon { width: 40px; height: 40px; margin: 0 auto 12px; display: block; }
  .cap-num { line-height: 1; }
  .cap-number {
    font-family: 'Space Grotesk', sans-serif; font-size: 36px; font-weight: 700;
    color: var(--accent); display: inline;
  }
  .cap-plus {
    font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 400; color: var(--accent);
  }
  .cap-label { font-size: 12px; color: var(--text-dim); margin-top: 8px; line-height: 1.4; }

  /* --- Protocol composition (ch7 interstitial) --- */
  .protocol-compose {
    display: flex; align-items: stretch; justify-content: center; gap: 12px; flex-wrap: wrap;
  }
  .proto-box {
    flex: 1; min-width: 150px; max-width: 200px;
    border-radius: 12px; padding: 24px 16px; text-align: center;
  }
  .proto-aep { background: var(--accent-dim); border: 1px solid var(--accent); }
  .proto-acp { background: var(--green-dim); border: 1px solid var(--green); }
  .proto-result { background: var(--orange-dim); border: 1px solid var(--orange); }
  .proto-name {
    font-family: 'Space Grotesk', sans-serif; font-size: 20px; font-weight: 700; margin-bottom: 4px;
  }
  .proto-aep .proto-name { color: var(--accent); }
  .proto-acp .proto-name { color: var(--green); }
  .proto-result .proto-name { color: var(--orange); }
  .proto-sub { font-size: 12px; color: var(--text-dim); margin-bottom: 14px; }
  .proto-tags { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }
  .proto-tags span {
    font-size: 11px; padding: 3px 8px; border-radius: 4px;
    background: var(--bg-surface); color: var(--text-dim); border: 1px solid var(--border);
  }
  .proto-op {
    display: flex; align-items: center; justify-content: center;
    font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 300;
    color: var(--text-dimmer); min-width: 28px;
  }

  /* --- Traction grid (ch10 interstitial) --- */
  .traction-grid {
    display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;
    max-width: 640px; margin: 0 auto;
  }
  .traction-item {
    display: flex; gap: 12px; align-items: flex-start;
    padding: 16px; background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 10px; transition: border-color 0.2s;
  }
  .traction-item:hover { border-color: var(--green); }
  .traction-marker {
    width: 8px; height: 8px; min-width: 8px; border-radius: 50%;
    background: var(--green); margin-top: 5px;
    box-shadow: 0 0 8px var(--green-dim);
  }
  .traction-content { display: flex; flex-direction: column; gap: 2px; }
  .traction-content strong { font-size: 14px; color: var(--text); }
  .traction-content span { font-size: 12px; color: var(--text-dim); line-height: 1.4; }

  /* --- CTA closing (ch11 interstitial) --- */
  .cta-section { text-align: center; padding: 80px 24px 40px; max-width: 600px; }
  .cta-line {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(18px, 2.5vw, 28px); font-weight: 400;
    color: var(--text-dim); line-height: 2;
  }
  .cta-divider { width: 40px; height: 2px; background: var(--accent); margin: 28px auto; }
  .cta-accent {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(22px, 3vw, 36px); font-weight: 700;
    color: var(--accent); line-height: 1.3; margin-bottom: 12px;
  }
  .cta-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px; color: var(--text-dimmer);
    letter-spacing: 0.1em; margin-top: 24px;
  }

  /* --- Highlight stat (mid-chapter) --- */
  .mini-break { max-width: var(--max-width); }
  .highlight-stat {
    text-align: center; padding: 40px 20px;
    border: 1px solid var(--border); border-radius: 12px;
    background: var(--bg-surface);
  }
  .hs-num { line-height: 1; margin-bottom: 8px; }
  .hs-num .stat-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 56px; font-weight: 700; color: var(--accent);
  }
  .hs-pct {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 32px; font-weight: 400; color: var(--accent);
  }
  .hs-text {
    font-size: 15px; color: var(--text-dim); max-width: 420px;
    margin: 0 auto; line-height: 1.5;
  }
  .hs-source {
    font-size: 11px; color: var(--text-dimmer); margin-top: 12px; font-style: italic;
  }

  /* --- Price bars (mid-chapter) --- */
  .price-bars { max-width: 500px; margin: 0 auto; }
  .price-item { margin-bottom: 18px; }
  .price-label {
    font-family: 'Space Grotesk', sans-serif; font-size: 12px; font-weight: 600;
    color: var(--text-dim); margin-bottom: 6px;
  }
  .price-track {
    height: 10px; background: var(--bg-elevated); border-radius: 5px; overflow: hidden; margin-bottom: 4px;
  }
  .price-val { font-size: 13px; color: var(--text); font-weight: 500; }

  /* --- Compact stat variants --- */
  .stat-row.compact { gap: 12px; }
  .stat-card.small { padding: 20px 16px; min-width: 120px; }
  .stat-card.small .stat-number { font-size: 32px; }
  .stat-card.small .stat-unit { font-size: 20px; }

  /* --- Regulation grid (mid-chapter) --- */
  .reg-grid {
    display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;
    max-width: 480px; margin: 0 auto;
  }
  .reg-item {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 14px; background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 8px; font-size: 13px;
  }
  .reg-flag {
    font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600;
    color: var(--accent); background: var(--accent-dim); padding: 2px 6px;
    border-radius: 4px; letter-spacing: 0.05em;
  }
  .reg-name { color: var(--text-dim); font-size: 12px; }
  .reg-caption {
    text-align: center; font-size: 11px; color: var(--text-dimmer);
    margin-top: 14px; font-style: italic;
  }

  /* --- Fade-in on scroll --- */
  .fade-in { opacity: 0; transform: translateY(20px); transition: opacity 0.5s ease, transform 0.5s ease; }
  .fade-in.visible { opacity: 1; transform: translateY(0); }

  /* --- Responsive --- */
  @media (max-width: 1180px) { .toc { display: none; } }
  @media (max-width: 640px) {
    .article { padding: 0 16px 120px; }
    .chapter-break { padding: 60px 0 20px; margin-top: 40px; }
    .stat-row { flex-direction: column; align-items: center; }
    .comparison-grid { flex-direction: column; }
    .comparison-vs { padding: 8px 0; }
    .force-grid { grid-template-columns: 1fr; }
    .cap-grid { grid-template-columns: repeat(2, 1fr); }
    .protocol-compose { flex-direction: column; align-items: center; }
    .proto-op { transform: rotate(90deg); padding: 4px 0; }
    .traction-grid { grid-template-columns: 1fr; }
    .reg-grid { flex-direction: column; align-items: center; }
  }

  /* --- Dedication --- */
  .dedication {
    max-width: var(--max-width); margin: 0 auto; padding: 120px 24px 80px;
    text-align: center; font-style: italic; color: var(--text-dim);
    font-size: clamp(16px, 1.6vw, 20px); line-height: 1.8;
  }

  /* --- Preface --- */
  .preface {
    max-width: var(--max-width); margin: 0 auto; padding: 80px 24px 60px;
    border-bottom: 1px solid var(--border);
  }
  .preface-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 12px; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--accent); margin-bottom: 16px;
  }
  .preface p { color: var(--text-dim); font-size: clamp(15px, 1.5vw, 18px); line-height: 1.8; }
  .preface em { color: var(--text-dimmer); }

  /* --- Back Matter --- */
  .back-matter {
    margin-top: 120px; padding-top: 60px;
    border-top: 1px solid var(--border-strong);
  }
  .back-matter-section { padding: 40px 0; }
  .back-matter-section h2 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(22px, 3vw, 32px); font-weight: 700;
    letter-spacing: -0.02em; border-top: none; padding-top: 0;
    margin: 0 0 24px;
  }
  .back-matter-section + .back-matter-section { border-top: 1px solid var(--border); padding-top: 60px; }
  .glossary-section p { margin: 16px 0; }
  .glossary-section p strong { color: var(--accent); font-weight: 600; }
  .about-author p { font-size: clamp(15px, 1.5vw, 18px); color: var(--text-dim); }

  /* --- Colophon --- */
  .colophon {
    max-width: var(--max-width); margin: 0 auto; padding: 80px 24px 120px;
    text-align: center; color: var(--text-dimmer); font-size: 12px; line-height: 1.8;
  }
  .colophon p { margin: 4px 0; }

  /* --- Print --- */
  @media print {
    :root, [data-theme="dark"], [data-theme="light"] {
      --bg: #fff; --bg-surface: #f6f6f6; --text: #1a1a1a;
      --text-dim: #555; --text-dimmer: #888; --accent: #2563eb;
      --green: #1a7f37; --orange: #9a6700; --red: #cf222e;
      --border: #ddd; --border-strong: #ccc;
    }
    body { font-size: 11pt; line-height: 1.6; }
    .hero { min-height: auto; padding: 60px 0; page-break-after: always; }
    .hero::before { display: none; }
    .toc, .progress-bar, .scroll-cue, .site-nav { display: none; }
    .article { max-width: 100%; padding: 0; }
    .chapter-break { page-break-before: always; padding: 40px 0 20px; margin-top: 0; }
    .visual-break, .pullquote { page-break-inside: avoid; }
    .force-grid, .cap-grid, .protocol-compose, .traction-grid, .cta-section { page-break-inside: avoid; }
    .fade-in { opacity: 1; transform: none; }
    .dedication { page-break-after: always; }
    .preface { page-break-after: always; }
    .back-matter { page-break-before: always; }
    .colophon { page-break-before: always; }
    a { color: var(--accent); }
    a[href]::after { content: none; }
  }
</style>
</head>
<body>

{nav}
<div class="progress-bar" id="progress"></div>

<div class="audio-player" id="audioPlayer">
  <div class="ap-chapter-list" id="apChapterList"></div>
  <button class="ap-btn" id="apChapBtn" title="Chapters">&#9776;</button>
  <button class="ap-btn" id="apPrev" title="Previous">&#9198;</button>
  <button class="ap-btn ap-play" id="apPlay" title="Play">&#9654;</button>
  <button class="ap-btn" id="apNext" title="Next">&#9197;</button>
  <div class="ap-chapter-info" id="apInfo">
    <div class="ap-chapter-title" id="apTitle">The World Has Changed</div>
    <div class="ap-chapter-num" id="apNum">Part 1 of 6</div>
  </div>
  <div class="ap-progress-wrap">
    <span class="ap-time" id="apTimeCur">0:00</span>
    <div class="ap-progress-bar" id="apProgressBar"><div class="ap-progress-fill" id="apProgressFill"><div class="ap-progress-thumb"></div></div></div>
    <span class="ap-time" id="apTimeRem">-0:00</span>
  </div>
  <button class="ap-speed" id="apSpeed">1.0x</button>
  <button class="ap-follow on" id="apFollow" title="Auto-scroll to current paragraph">following</button>
  <button class="ap-btn" id="apClose" title="Close">&times;</button>
</div>
<audio id="apAudio" preload="auto"></audio>

<div class="hero">
  <div class="hero-eyebrow">Jason Sun</div>
  <h1 class="hero-title">Trust at Scale</h1>
  <p class="hero-subtitle">The accountability infrastructure for the agent economy.</p>
  <p class="hero-author">May 2026</p>
  <div style="margin-top: 20px; display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; position: relative;">
    <a href="#" id="listenCTA" onclick="document.getElementById('audioToggle').click(); return false;" style="display: inline-block; padding: 12px 28px; background: var(--accent); color: var(--bg); text-decoration: none; font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 15px; border-radius: 8px; transition: opacity 0.2s;">Listen to the audiobook</a>
  </div>
  <p style="margin-top: 12px; font-size: 13px; color: var(--text-dim); font-family: 'Inter Tight', sans-serif;">~7 hours &middot; click any paragraph to jump in</p>
  <div class="scroll-cue">scroll</div>
</div>

<div class="abstract" id="abstract">
  <div class="abstract-label">Abstract</div>
  <div class="abstract-text">
{abstract_content}
  </div>
</div>

{dedication}

<div class="preface" id="preface">
  <div class="preface-label">Preface</div>
{preface}
</div>

<nav class="toc" id="toc">
{toc}
</nav>

<article class="article" id="article">
{content}
<div class="back-matter">
{backmatter}
</div>
</article>

<div class="colophon">
  <p>&copy; 2026 Jason Sun. All rights reserved.</p>
  <p>First edition, May 2026</p>
  <p>Set in Inter Tight and Space Grotesk. Audiobook narrated with Kokoro TTS.</p>
</div>

<script>
(function() {
  // analytics
  var _sid = sessionStorage.getItem('sid') || (Math.random().toString(36).slice(2) + Date.now().toString(36));
  sessionStorage.setItem('sid', _sid);
  var _t0 = Date.now();
  function track(event, data) {
    var payload = Object.assign({ event: event, page: 'book', sid: _sid }, data || {});
    try { navigator.sendBeacon('/api/track', JSON.stringify(payload)); } catch(e) {}
  }
  track('pageview', { path: location.pathname });

  // heartbeat: time-on-page + scroll depth every 30s
  var _maxScroll = 0;
  window.addEventListener('scroll', function() {
    var pct = Math.round(window.scrollY / (document.documentElement.scrollHeight - window.innerHeight) * 100);
    if (pct > _maxScroll) _maxScroll = pct;
  }, { passive: true });
  setInterval(function() {
    if (document.hidden) return;
    track('heartbeat', { elapsed: Math.round((Date.now() - _t0) / 1000), scroll: _maxScroll });
  }, 30000);
  document.addEventListener('visibilitychange', function() {
    if (document.hidden) track('leave', { elapsed: Math.round((Date.now() - _t0) / 1000), scroll: _maxScroll });
  });

  // section visibility: track when each part enters the viewport
  var _seenParts = {};
  if (window.IntersectionObserver) {
    var partObs = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (e.isIntersecting && !_seenParts[e.target.id]) {
          _seenParts[e.target.id] = true;
          track('section_view', { section: e.target.id, elapsed: Math.round((Date.now() - _t0) / 1000) });
        }
      });
    }, { threshold: 0.1 });
    document.querySelectorAll('section.chapter-break').forEach(function(el) { partObs.observe(el); });
  }

{shared_js}

  var toc = document.getElementById('toc');

  var tocLinks = toc.querySelectorAll('a');
  var sectionEls = [];
  tocLinks.forEach(function(link) {
    var id = link.getAttribute('href').slice(1);
    var el = document.getElementById(id);
    if (el) sectionEls.push({ el: el, link: link });
  });

  var counters = document.querySelectorAll('[data-count]');
  var counterDone = new Set();
  function animateCounter(el) {
    var target = parseInt(el.dataset.count);
    var duration = 1200;
    var start = performance.now();
    function tick(now) {
      var p = Math.min((now - start) / duration, 1);
      var ease = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * ease);
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  var fadeEls = document.querySelectorAll('.fade-in');
  var fadeObs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) { e.target.classList.add('visible'); fadeObs.unobserve(e.target); }
    });
  }, { threshold: 0.08 });
  fadeEls.forEach(function(el) { fadeObs.observe(el); });

  var counterObs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting && !counterDone.has(e.target)) {
        counterDone.add(e.target);
        animateCounter(e.target);
      }
    });
  }, { threshold: 0.5 });
  counters.forEach(function(el) { counterObs.observe(el); });

  // Animated bar fills
  var barFills = document.querySelectorAll('.bar-fill[data-width]');
  var barObs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) {
        e.target.style.width = e.target.dataset.width + '%';
        barObs.unobserve(e.target);
      }
    });
  }, { threshold: 0.3 });
  barFills.forEach(function(el) { barObs.observe(el); });

  var heroH = window.innerHeight;
  function onScroll() {
    var sy = window.scrollY;
    toc.classList.toggle('visible', sy > heroH * 0.7);
    var active = null;
    var threshold = window.innerHeight * 0.15;
    for (var i = sectionEls.length - 1; i >= 0; i--) {
      if (sectionEls[i].el.getBoundingClientRect().top <= threshold) { active = sectionEls[i]; break; }
    }
    tocLinks.forEach(function(l) { l.classList.remove('active'); });
    if (active) { active.link.classList.add('active'); active.link.scrollIntoView({ block: 'nearest' }); }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  tocLinks.forEach(function(link) {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      var el = document.getElementById(link.getAttribute('href').slice(1));
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  // --- Inline audio player ---
  var apChapters = {chapters_js};
  var apSpeeds = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0];
  var apSpeedIdx = 1;
  var apCurrent = 0;
  var apAudio = document.getElementById('apAudio');
  var apPlayer = document.getElementById('audioPlayer');
  var apToggle = document.getElementById('audioToggle');
  var apPlay = document.getElementById('apPlay');
  var apPrev = document.getElementById('apPrev');
  var apNext = document.getElementById('apNext');
  var apTitle = document.getElementById('apTitle');
  var apNum = document.getElementById('apNum');
  var apTimeCur = document.getElementById('apTimeCur');
  var apTimeRem = document.getElementById('apTimeRem');
  var apProgressBar = document.getElementById('apProgressBar');
  var apProgressFill = document.getElementById('apProgressFill');
  var apSpeed = document.getElementById('apSpeed');
  var apClose = document.getElementById('apClose');
  var apChapBtn = document.getElementById('apChapBtn');
  var apChapterList = document.getElementById('apChapterList');

  function apFmt(s) {
    if (isNaN(s) || s < 0) s = 0;
    var h = Math.floor(s / 3600);
    var m = Math.floor((s % 3600) / 60);
    var sec = Math.floor(s % 60);
    if (h > 0) return h + ':' + (m < 10 ? '0' : '') + m + ':' + (sec < 10 ? '0' : '') + sec;
    return m + ':' + (sec < 10 ? '0' : '') + sec;
  }

  function apRevealUpTo(el) {
    var all = document.querySelectorAll('.fade-in');
    var elRect = el.getBoundingClientRect();
    var elTop = elRect.top + window.scrollY;
    for (var i = 0; i < all.length; i++) {
      var r = all[i].getBoundingClientRect();
      if (r.top + window.scrollY <= elTop + window.innerHeight) all[i].classList.add('visible');
      else break;
    }
  }

  var apScrollOnLoad = false;
  function apLoadChapter(idx) {
    if (idx < 0 || idx >= apChapters.length) return;
    apCurrent = idx;
    var ch = apChapters[idx];
    apAudio.src = ch.file;
    apTitle.textContent = ch.title;
    apNum.textContent = ch.part > 0 ? 'Part ' + ch.part + ' of ' + (apChapters.length - 1) : '';
    apProgressFill.style.width = '0%';
    apTimeCur.textContent = '0:00';
    apTimeRem.textContent = '-' + apFmt(ch.duration);
    apBuildChapterList();
    apSaveState();
    if (apScrollOnLoad && ch.sectionId) {
      var el = document.getElementById(ch.sectionId);
      if (el) { apRevealUpTo(el); el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    }
    apScrollOnLoad = true;
  }

  function apBuildChapterList() {
    apChapterList.innerHTML = '';
    apChapters.forEach(function(ch, i) {
      var el = document.createElement('div');
      el.className = 'ap-chapter-item' + (i === apCurrent ? ' active' : '');
      el.innerHTML = '<span>' + (ch.part > 0 ? 'Part ' + ch.part + ': ' : '') + ch.title + '</span><span class="ap-chapter-dur">' + apFmt(ch.duration) + '</span>';
      el.addEventListener('click', function() { apLoadChapter(i); apAudio.play(); apChapterList.classList.remove('open'); });
      apChapterList.appendChild(el);
    });
  }

  function apSaveState() {
    try { localStorage.setItem('ab-state', JSON.stringify({ ch: apCurrent, time: apAudio.currentTime || 0, speed: apSpeedIdx })); } catch(e) {}
  }

  function apRestoreState() {
    try {
      var s = JSON.parse(localStorage.getItem('ab-state'));
      if (s) {
        apCurrent = s.ch || 0;
        apSpeedIdx = s.speed || 1;
        apLoadChapter(apCurrent);
        apAudio.addEventListener('loadedmetadata', function onLoad() {
          apAudio.currentTime = s.time || 0;
          apAudio.removeEventListener('loadedmetadata', onLoad);
        });
        apAudio.playbackRate = apSpeeds[apSpeedIdx];
        apSpeed.textContent = apSpeeds[apSpeedIdx] + 'x';
      } else {
        apLoadChapter(0);
      }
    } catch(e) { apLoadChapter(0); }
  }

  apToggle.addEventListener('click', function() {
    var show = !apPlayer.classList.contains('visible');
    apPlayer.classList.toggle('visible', show);
    apToggle.classList.toggle('active', show);
  });
  apClose.addEventListener('click', function() {
    apAudio.pause();
    apPlayer.classList.remove('visible');
    apToggle.classList.remove('active');
  });
  apPlay.addEventListener('click', function() { if (apAudio.paused) apAudio.play(); else apAudio.pause(); });
  apAudio.addEventListener('play', function() {
    apPlay.innerHTML = '&#10074;&#10074;';
    track('play', { chapter: apChapters[apCurrent].part, title: apChapters[apCurrent].title, time: Math.round(apAudio.currentTime) });
  });
  apAudio.addEventListener('pause', function() { apPlay.innerHTML = '&#9654;'; apSaveState(); });
  var _audioMilestones = {};
  apAudio.addEventListener('timeupdate', function() {
    var dur = apAudio.duration || apChapters[apCurrent].duration;
    apProgressFill.style.width = (apAudio.currentTime / dur * 100) + '%';
    apTimeCur.textContent = apFmt(apAudio.currentTime);
    apTimeRem.textContent = '-' + apFmt(dur - apAudio.currentTime);
    var pct = Math.floor(apAudio.currentTime / dur * 100);
    var key = apCurrent + '-';
    [25, 50, 75].forEach(function(m) {
      if (pct >= m && !_audioMilestones[key + m]) {
        _audioMilestones[key + m] = true;
        track('audio_progress', { chapter: apChapters[apCurrent].part, pct: m });
      }
    });
  });
  apAudio.addEventListener('ended', function() {
    track('complete', { chapter: apChapters[apCurrent].part, title: apChapters[apCurrent].title });
    if (apCurrent < apChapters.length - 1) { apLoadChapter(apCurrent + 1); apAudio.play(); }
    else { apPlay.innerHTML = '&#9654;'; }
  });
  apPrev.addEventListener('click', function() {
    if (apAudio.currentTime > 5) apAudio.currentTime = 0;
    else if (apCurrent > 0) { apLoadChapter(apCurrent - 1); apAudio.play(); }
  });
  apNext.addEventListener('click', function() {
    if (apCurrent < apChapters.length - 1) { apLoadChapter(apCurrent + 1); apAudio.play(); }
  });
  apSpeed.addEventListener('click', function() {
    apSpeedIdx = (apSpeedIdx + 1) % apSpeeds.length;
    apAudio.playbackRate = apSpeeds[apSpeedIdx];
    apSpeed.textContent = apSpeeds[apSpeedIdx] + 'x';
    apSaveState();
  });
  function apSeekSync() {
    apSyncParagraph();
    if (apActivePara) {
      var el = document.getElementById(apActivePara);
      if (el) { apRevealUpTo(el); el.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
    }
  }
  (function() {
    var dragging = false;
    function seekTo(x) {
      var rect = apProgressBar.getBoundingClientRect();
      var pct = Math.max(0, Math.min(1, (x - rect.left) / rect.width));
      var dur = apAudio.duration || apChapters[apCurrent].duration;
      apAudio.currentTime = pct * dur;
      apProgressFill.style.width = (pct * 100) + '%';
    }
    apProgressBar.addEventListener('mousedown', function(e) { dragging = true; apProgressBar.classList.add('dragging'); seekTo(e.clientX); });
    document.addEventListener('mousemove', function(e) { if (dragging) seekTo(e.clientX); });
    document.addEventListener('mouseup', function() { if (dragging) { dragging = false; apProgressBar.classList.remove('dragging'); apSeekSync(); } });
    apProgressBar.addEventListener('touchstart', function(e) { dragging = true; apProgressBar.classList.add('dragging'); seekTo(e.touches[0].clientX); }, { passive: true });
    document.addEventListener('touchmove', function(e) { if (dragging) seekTo(e.touches[0].clientX); }, { passive: true });
    document.addEventListener('touchend', function() { if (dragging) { dragging = false; apProgressBar.classList.remove('dragging'); apSeekSync(); } });
  })();
  apChapBtn.addEventListener('click', function() { apChapterList.classList.toggle('open'); });
  document.addEventListener('click', function(e) {
    if (!apChapterList.contains(e.target) && e.target !== apChapBtn) apChapterList.classList.remove('open');
  });
  setInterval(apSaveState, 10000);

  if ('mediaSession' in navigator) {
    navigator.mediaSession.setActionHandler('play', function() { apAudio.play(); });
    navigator.mediaSession.setActionHandler('pause', function() { apAudio.pause(); });
    navigator.mediaSession.setActionHandler('previoustrack', function() { apPrev.click(); });
    navigator.mediaSession.setActionHandler('nexttrack', function() { apNext.click(); });
    apAudio.addEventListener('play', function() {
      navigator.mediaSession.metadata = new MediaMetadata({ title: apChapters[apCurrent].title, artist: 'Jason Sun', album: 'Trust at Scale' });
    });
  }

  // --- Paragraph sync / highlighting ---
  var apAlignments = {alignments};
  var apFollow = true;
  var apFollowBtn = document.getElementById('apFollow');
  var apLastUserScroll = 0;
  var apActivePara = null;

  window.addEventListener('scroll', function() { apLastUserScroll = Date.now(); }, { passive: true });
  apFollowBtn.addEventListener('click', function() {
    apFollow = !apFollow;
    apFollowBtn.classList.toggle('on', apFollow);
    apFollowBtn.textContent = apFollow ? 'following' : 'follow';
    if (apFollow && apActivePara) {
      var el = document.getElementById(apActivePara);
      if (el) { apRevealUpTo(el); el.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
      apLastUserScroll = 0;
    }
  });

  function apSyncParagraph() {
    var timings = apAlignments[apCurrent];
    if (!timings) return;
    var t = apAudio.currentTime;
    var found = null;
    for (var k = 0; k < timings.length; k++) {
      if (timings[k] && t >= timings[k][0] && t < timings[k][1]) { found = k; break; }
    }
    if (found === null) {
      for (var k = timings.length - 1; k >= 0; k--) {
        if (timings[k] && t >= timings[k][0]) { found = k; break; }
      }
    }
    var paraId = found !== null ? 'ab-' + apCurrent + '-' + found : null;
    if (paraId === apActivePara) return;
    if (apActivePara) { var old = document.getElementById(apActivePara); if (old) old.classList.remove('ab-active'); }
    apActivePara = paraId;
    if (!paraId) return;
    var el = document.getElementById(paraId);
    if (!el) return;
    el.classList.add('ab-active');
    if (apFollow && !apAudio.paused && (Date.now() - apLastUserScroll > 8000)) {
      var rect = el.getBoundingClientRect();
      if (rect.top < 0 || rect.bottom > window.innerHeight) {
        apRevealUpTo(el);
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }
  apAudio.addEventListener('timeupdate', apSyncParagraph);
  apAudio.addEventListener('pause', function() {
    if (apActivePara) { var el = document.getElementById(apActivePara); if (el) el.classList.remove('ab-active'); apActivePara = null; }
  });

  document.addEventListener('click', function(e) {
    var p = e.target.closest('p[id^="ab-"]');
    if (!p) return;
    if (window.getSelection().toString().length > 0) return;
    var parts = p.id.split('-');
    var ch = parseInt(parts[1]);
    var idx = parseInt(parts[2]);
    var timings = apAlignments[ch];
    if (!timings || !timings[idx]) return;
    var startTime = timings[idx][0];
    apPlayer.classList.add('visible');
    apToggle.classList.add('active');
    if (apCurrent !== ch) {
      apLoadChapter(ch);
      apAudio.addEventListener('loadedmetadata', function onLoad() {
        apAudio.currentTime = startTime;
        apAudio.play();
        apAudio.removeEventListener('loadedmetadata', onLoad);
      });
    } else {
      apAudio.currentTime = startTime;
      apAudio.play();
    }
  });

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js', { updateViaCache: 'none' }).catch(function() {});
    navigator.serviceWorker.addEventListener('controllerchange', function() { location.reload(); });
    navigator.serviceWorker.addEventListener('message', function(e) {
      if (e.data && e.data.type === 'updated' && apAudio.paused) location.reload();
    });
  }

  apRestoreState();
})();
</script>

</body>
</html>"""


def align_paragraphs_to_timestamps(chapter_paras: dict[int, list[str]]) -> dict:
    """Load per-paragraph timestamps generated by tts.py."""
    import json as _json
    ts_dir = VISION_DIR / "timestamps"
    ch_to_slug = {0: AUDIO_SLUGS["front-matter"]}
    for ch_slug, _ in CHAPTERS:
        num = int(ch_slug.split("-")[0].replace("part", ""))
        ch_to_slug[num] = AUDIO_SLUGS[ch_slug]
    result = {}
    for ch_num in chapter_paras:
        slug = ch_to_slug.get(ch_num)
        if not slug:
            continue
        ts_file = ts_dir / f"{slug}.json"
        if not ts_file.exists():
            continue
        timings = _json.loads(ts_file.read_text())
        if timings and isinstance(timings[0], dict):
            print(f"  ch{ch_num}: skipping old Whisper format (run tts.py to regenerate)")
            continue
        result[ch_num] = timings
        print(f"  ch{ch_num}: {len(timings)} paragraph timestamps loaded")
    return result


FRONT_MATTER_DIR = VISION_DIR / "front-matter"
BACK_MATTER_DIR = VISION_DIR / "back-matter"

BACK_MATTER_FILES = [
    ("acknowledgments.mdx", "Acknowledgments"),
    ("glossary.mdx", "Glossary"),
    ("whats-next.mdx", "What's Next"),
    ("about-author.mdx", "About the Author"),
]


def build_preface() -> str:
    md = markdown.Markdown(extensions=['smarty'])
    preface_file = FRONT_MATTER_DIR / "preface.mdx"
    if not preface_file.exists():
        return ""
    text = read_mdx(preface_file)
    text = re.sub(r'^#\s+.*$', '', text, count=1, flags=re.MULTILINE).strip()
    html = md.convert(text)
    return html


def build_front_matter() -> tuple[str, str, list[str]]:
    """Build abstract + preface with ab-0-{idx} paragraph tagging.
    Returns (abstract_html, preface_html, para_texts).
    """
    counter = [0]
    paras: list[str] = []

    abstract_parts = []
    for p_html in ABSTRACT_PARAGRAPHS:
        idx = counter[0]
        counter[0] += 1
        plain = re.sub(r'<[^>]+>', '', p_html).strip()
        paras.append(plain)
        abstract_parts.append(f'    <p id="ab-0-{idx}">{p_html}</p>')
    abstract_html = '\n'.join(abstract_parts)

    preface_raw = build_preface()
    def tag_fm(m):
        content = m.group(1)
        idx = counter[0]
        counter[0] += 1
        plain = re.sub(r'<[^>]+>', '', content).strip()
        paras.append(plain)
        return f'<p id="ab-0-{idx}">{content}</p>'
    preface_html = re.sub(r'<p>(.*?)</p>', tag_fm, preface_raw, flags=re.DOTALL)

    return abstract_html, preface_html, paras


def build_back_matter() -> tuple[str, list[dict]]:
    md = markdown.Markdown(extensions=['tables', 'smarty'])
    sections = []
    toc_entries = []
    for filename, title in BACK_MATTER_FILES:
        filepath = BACK_MATTER_DIR / filename
        if not filepath.exists():
            continue
        text = read_mdx(filepath)
        text = re.sub(r'^#\s+.*$', '', text, count=1, flags=re.MULTILINE).strip()
        section_id = slugify(title)
        html = md.convert(text)
        md.reset()
        css_class = "glossary-section" if "glossary" in filename else ""
        css_class = "about-author" if "about-author" in filename else css_class
        sections.append(f'<div class="back-matter-section {css_class}" id="{section_id}">')
        sections.append(f'<h2>{title}</h2>')
        sections.append(html)
        sections.append('</div>')
        toc_entries.append({"id": section_id, "title": title})
    return '\n'.join(sections), toc_entries


def build_chapters_js() -> str:
    """Build the apChapters JS array from manifest (if available) or defaults."""
    import json as _json
    audio_dir = VISION_DIR / "audio"
    manifest_path = audio_dir / "manifest.json"
    durations = {}
    if manifest_path.exists():
        manifest = _json.loads(manifest_path.read_text())
        for ch in manifest.get("chapters", []):
            durations[ch.get("part", 0)] = ch.get("duration", 0)

    entries = []
    entries.append("{ part: 0, title: 'Abstract \\u0026 Preface', file: 'audio/part00-front-matter.mp3', duration: %.1f, sectionId: 'abstract' }" % durations.get(0, 0))
    for i, (ch_slug, title) in enumerate(CHAPTERS, 1):
        audio_slug = AUDIO_SLUGS[ch_slug]
        dur = durations.get(i, 0)
        section_id = slugify(title)
        entries.append("{ part: %d, title: '%s', file: 'audio/%s.mp3', duration: %.1f, sectionId: '%s' }" % (i, title, audio_slug, dur, section_id))
    return '[\n    ' + ',\n    '.join(entries) + '\n  ]'


INDEX_CONTENT_FILE = VISION_DIR / "index-content.html"
INDEX_OUT_FILE = VISION_DIR / "index.html"

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Jason Sun — Trust at Scale</title>
<meta name="description" content="AI agents are doing real work. The infrastructure to make that trustworthy doesn't exist yet. A thesis on agent accountability by Jason Sun.">
<meta property="og:title" content="Trust at Scale — Jason Sun">
<meta property="og:description" content="AI agents are doing real work. The infrastructure to make that trustworthy doesn't exist yet. Read the book or the essay.">
<meta property="og:type" content="article">
<meta property="og:url" content="https://jasonsun.org">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
{shared_css}

  /* --- Index-specific --- */
  .mini-toc {{ max-width: var(--max-width); margin: 0 auto; padding: 0 24px; }}
  .mini-toc-inner {{
    display: flex; flex-wrap: wrap; gap: 6px; padding: 16px 20px;
    background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 10px; justify-content: center;
  }}
  .mini-toc a {{
    font-family: 'Space Grotesk', sans-serif; font-size: 12px; font-weight: 500;
    color: var(--text-dimmer); text-decoration: none;
    padding: 4px 12px; border-radius: 6px; border: 1px solid transparent;
    transition: all 0.2s; white-space: nowrap;
  }}
  .mini-toc a:hover {{ color: var(--text-dim); background: var(--bg-elevated); border-color: var(--border); }}
  .mini-toc a.active {{ color: var(--accent); border-color: var(--accent); background: var(--accent-dim); }}

  .article {{ max-width: var(--max-width); margin: 0 auto; padding: 40px 24px 120px; }}

  .layer-diagram {{
    max-width: 560px; margin: 32px auto; padding: 24px;
    background: var(--bg-surface); border: 1px solid var(--border); border-radius: 12px;
  }}
  .layer-item {{
    display: flex; align-items: center; gap: 14px;
    padding: 10px 16px; margin: 4px 0; border-radius: 8px; font-size: 14px; transition: background 0.2s;
  }}
  .layer-item:hover {{ background: var(--bg-elevated); }}
  .layer-num {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; color: var(--accent); min-width: 20px; }}
  .layer-name {{ font-family: 'Space Grotesk', sans-serif; font-weight: 600; min-width: 120px; }}
  .layer-desc {{ color: var(--text-dim); font-size: 13px; }}

  .cta-block {{
    margin: 60px 0 40px; padding: 40px 32px; text-align: center;
    background: var(--bg-surface); border: 1px solid var(--border); border-radius: 12px;
  }}
  .cta-block p {{ color: var(--text-dim); font-size: 15px; margin: 8px 0 20px; }}
  .cta-link {{
    display: inline-block; padding: 12px 28px;
    background: var(--accent); color: var(--bg); text-decoration: none;
    font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 15px;
    border-radius: 8px; transition: opacity 0.2s;
  }}
  .cta-link:hover {{ opacity: 0.85; text-decoration: none; }}

  .resume-toast {{
    position: fixed; bottom: 24px; right: 24px; z-index: 500;
    background: var(--bg-surface); border: 1px solid var(--border-strong);
    border-radius: 12px; padding: 16px 20px; box-shadow: var(--shadow);
    max-width: 320px; transform: translateY(120%); transition: transform 0.3s ease;
  }}
  .resume-toast.show {{ transform: translateY(0); }}
  .resume-toast-text {{ font-size: 13px; color: var(--text-dim); margin-bottom: 12px; line-height: 1.5; }}
  .resume-toast-text strong {{ color: var(--accent); }}
  .resume-toast-actions {{ display: flex; gap: 8px; }}
  .resume-toast-actions button {{
    flex: 1; padding: 8px 14px; border-radius: 6px; border: none;
    font-family: 'Space Grotesk', sans-serif; font-size: 13px; font-weight: 500;
    cursor: pointer; transition: opacity 0.2s;
  }}
  .resume-toast-actions button:hover {{ opacity: 0.85; }}
  .resume-btn {{ background: var(--accent); color: var(--bg); }}
  .dismiss-btn {{ background: var(--bg-elevated); color: var(--text-dim); border: 1px solid var(--border) !important; }}

  .about-section {{
    max-width: var(--max-width); margin: 0 auto; padding: 60px 24px 80px;
    border-top: 1px solid var(--border);
  }}
  .about-inner {{ max-width: 520px; }}
  .about-section h2 {{
    font-family: 'Inter Tight', sans-serif;
    font-size: 14px; font-weight: 600; color: var(--text-dimmer);
    text-transform: uppercase; letter-spacing: 0.08em;
    margin: 0 0 16px;
  }}
  .about-section p {{
    color: var(--text-dim); font-size: 15px; line-height: 1.7; margin: 0 0 10px;
  }}
  .about-section a {{ color: var(--accent); text-decoration: none; }}
  .about-section a:hover {{ text-decoration: underline; }}

  @media (max-width: 640px) {{
    .article {{ padding: 40px 16px 80px; }}
    .layer-item {{ flex-direction: column; align-items: flex-start; gap: 4px; }}
    .cta-block {{ padding: 28px 20px; }}
    .mini-toc {{ padding: 0 16px; }}
    .mini-toc-inner {{ gap: 4px; padding: 12px 14px; }}
    .mini-toc a {{ font-size: 11px; padding: 4px 8px; }}
    .resume-toast {{ left: 16px; right: 16px; bottom: 16px; max-width: none; }}
    .about-section {{ padding: 40px 16px 60px; }}
  }}

  @media print {{
    .article {{ max-width: 100%; padding: 0; }}
    .mini-toc, .resume-toast {{ display: none; }}
    .cta-block {{ border: 2px solid #ddd; }}
  }}
</style>
</head>
<body>

{nav}
<div class="progress-bar" id="progress"></div>
<div class="reading-time" id="readingTime"></div>

<div class="resume-toast" id="resumeToast">
  <div class="resume-toast-text">Resume reading from <strong id="resumeSection"></strong>?</div>
  <div class="resume-toast-actions">
    <button class="resume-btn" id="resumeBtn">Resume</button>
    <button class="dismiss-btn" id="dismissBtn">Dismiss</button>
  </div>
</div>

<div class="hero">
  <div class="hero-eyebrow">Jason Sun</div>
  <h1 class="hero-title">Trust at Scale</h1>
  <p class="hero-subtitle">AI agents are doing real work. The infrastructure to make that trustworthy doesn't exist yet.</p>
  <p class="hero-author">May 2026</p>
  <div style="margin-top: 24px; display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; position: relative;">
    <a href="/book.html" style="display: inline-block; padding: 12px 28px; background: var(--accent); color: var(--bg); text-decoration: none; font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 15px; border-radius: 8px; transition: opacity 0.2s;">Read the book</a>
    <a href="/book-zh.html" style="display: inline-block; padding: 12px 28px; background: var(--bg-elevated); color: var(--text); text-decoration: none; font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 15px; border-radius: 8px; border: 1px solid var(--border-strong); transition: opacity 0.2s;">&#20013;&#25991;&#29256;</a>
  </div>
  <div class="hero-reading-time" id="heroReadTime" style="margin-top: 12px;"></div>
  <div class="scroll-cue">or read the essay below</div>
</div>

{mini_toc}

<article class="article" id="article">
{index_content}
</article>

<div class="about-section" id="about">
  <div class="about-inner">
    <h2>About</h2>
    <p>I'm Jason Sun. I run <a href="https://aceteam.ai">AceTeam</a>, where we build accountability infrastructure for autonomous AI: cost attribution, provenance tracking, governance enforcement. The layer that lets organizations actually trust agent output.</p>
    <p><a href="mailto:jason@aceteam.ai">jason@aceteam.ai</a></p>
  </div>
</div>

<script>
(function() {{
{shared_js}

  // --- Reading time ---
  var article = document.getElementById('article');
  var words = article.textContent.split(/\\s+/).length;
  var totalMin = Math.ceil(words / 220);
  document.getElementById('heroReadTime').textContent = '~' + totalMin + ' min read';
  var rtEl = document.getElementById('readingTime');
  var heroH = window.innerHeight;

  // --- Mini TOC active tracking ---
  var tocLinks = document.querySelectorAll('.mini-toc a');
  var sectionEls = [];
  tocLinks.forEach(function(link) {{
    var id = link.getAttribute('href').slice(1);
    var el = document.getElementById(id);
    if (el) sectionEls.push({{ el: el, link: link }});
  }});

  tocLinks.forEach(function(link) {{
    link.addEventListener('click', function(e) {{
      e.preventDefault();
      var el = document.getElementById(link.getAttribute('href').slice(1));
      if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }});
  }});

  // --- Resume reading ---
  var STORAGE_KEY = 'vision-essay-pos';
  var resumeToast = document.getElementById('resumeToast');
  var resumeSection = document.getElementById('resumeSection');
  var resumeBtn = document.getElementById('resumeBtn');
  var dismissBtn = document.getElementById('dismissBtn');
  var savedPos = null;
  try {{ savedPos = JSON.parse(localStorage.getItem(STORAGE_KEY)); }} catch(e) {{}}
  if (savedPos && savedPos.pct > 5 && savedPos.pct < 95) {{
    resumeSection.textContent = savedPos.section + ' (' + savedPos.pct + '%)';
    setTimeout(function() {{ resumeToast.classList.add('show'); }}, 800);
  }}
  resumeBtn.addEventListener('click', function() {{
    resumeToast.classList.remove('show');
    if (savedPos) {{
      var target = savedPos.pct / 100 * (document.documentElement.scrollHeight - window.innerHeight);
      window.scrollTo({{ top: target, behavior: 'smooth' }});
    }}
  }});
  dismissBtn.addEventListener('click', function() {{ resumeToast.classList.remove('show'); }});

  var saveTimer = null;
  function savePosition(section, pct) {{
    clearTimeout(saveTimer);
    saveTimer = setTimeout(function() {{
      try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify({{ section: section, pct: pct }})); }} catch(e) {{}}
    }}, 500);
  }}

  // --- Scroll handler ---
  var currentSection = '';
  function onScroll() {{
    var sy = window.scrollY;
    var docH = document.documentElement.scrollHeight - window.innerHeight;
    var pct = Math.round(sy / docH * 100);

    var minLeft = Math.max(1, Math.ceil((100 - pct) / 100 * totalMin));
    if (sy > heroH * 0.5) {{
      rtEl.textContent = minLeft + ' min left';
      rtEl.classList.add('visible');
    }} else {{
      rtEl.classList.remove('visible');
    }}

    var active = null;
    var threshold = window.innerHeight * 0.2;
    for (var i = sectionEls.length - 1; i >= 0; i--) {{
      if (sectionEls[i].el.getBoundingClientRect().top <= threshold) {{ active = sectionEls[i]; break; }}
    }}
    tocLinks.forEach(function(l) {{ l.classList.remove('active'); }});
    if (active) {{
      active.link.classList.add('active');
      currentSection = active.link.textContent;
    }}
    if (pct > 5) savePosition(currentSection || 'the beginning', pct);
  }}

  window.addEventListener('scroll', onScroll, {{ passive: true }});
  onScroll();
}})();
</script>

</body>
</html>"""


def build_index(shared_css: str, nav_html: str, shared_js: str, word_count: int):
    """Build index.html from templates and index-content.html."""
    content = INDEX_CONTENT_FILE.read_text()

    sections = re.findall(r'id="([^"]+)"', content)
    h2_sections = []
    for s_id in sections:
        label = s_id.replace('-', ' ').title().replace('The ', 'The ')
        h2_match = re.search(rf'id="{re.escape(s_id)}"[^>]*>([^<]+)', content)
        if h2_match:
            label = h2_match.group(1)
        h2_sections.append((s_id, label))

    mini_toc_links = '\n'.join(
        f'    <a href="#{sid}">{label}</a>' for sid, label in h2_sections
    )
    mini_toc = f'''<nav class="mini-toc" id="miniToc">
  <div class="mini-toc-inner">
{mini_toc_links}
  </div>
</nav>'''

    content = content.replace("{word_count}", f"{word_count:,}")

    html = (INDEX_TEMPLATE
        .replace("{shared_css}", shared_css)
        .replace("{nav}", nav_html)
        .replace("{shared_js}", shared_js)
        .replace("{mini_toc}", mini_toc)
        .replace("{index_content}", content)
        .replace("{{", "{").replace("}}", "}"))
    INDEX_OUT_FILE.write_text(html)
    print(f"Written to {INDEX_OUT_FILE}")


def main():
    shared_css = load_shared_css()
    shared_js = load_shared_js()
    book_nav = load_nav("book", '<button class="nav-theme" id="audioToggle" title="Listen to audiobook">&#9835;</button>')
    index_nav = load_nav("essay")

    print("Building vision book...")
    content, toc_entries, chapter_paras = build_content()

    print("Building front matter...")
    abstract_html, preface_html, fm_paras = build_front_matter()
    chapter_paras[0] = fm_paras

    print("Building back matter...")
    backmatter_html, backmatter_toc = build_back_matter()

    toc_html = build_toc_html(toc_entries, backmatter_toc)

    print("Building audio player chapters...")
    chapters_js = build_chapters_js()

    print("Aligning paragraphs to audio timestamps...")
    alignments = align_paragraphs_to_timestamps(chapter_paras)
    import json as _json
    alignment_js = _json.dumps(alignments)

    html = (TEMPLATE
        .replace("{shared_css}", shared_css)
        .replace("{shared_js}", shared_js)
        .replace("{nav}", book_nav)
        .replace("{dedication}", "")
        .replace("{abstract_content}", abstract_html)
        .replace("{preface}", preface_html)
        .replace("{toc}", toc_html)
        .replace("{chapters_js}", chapters_js)
        .replace("{content}", content)
        .replace("{backmatter}", backmatter_html)
        .replace("{alignments}", alignment_js))
    OUT_FILE.write_text(html)
    print(f"Written to {OUT_FILE}")
    print(f"  {len(fm_paras)} front-matter paragraphs tagged (ab-0-*)")
    print(f"  {len(toc_entries)} chapter/section TOC entries + {len(backmatter_toc)} back matter entries")
    word_count = len(re.findall(r'\w+', content))
    print(f"  ~{word_count:,} words")

    print("\nBuilding index page...")
    build_index(shared_css, index_nav, shared_js, word_count)


if __name__ == "__main__":
    main()
