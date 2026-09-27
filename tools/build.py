#!/usr/bin/env python3
"""Generates the static HTML pages for the Silvia Vannutelli site. Run: python3 tools/build.py"""
import base64
import hashlib
import math
import os
import random
import re
from html import escape
from urllib.parse import urlparse

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EMAIL = "silvia.vannutelli@northwestern.edu"
X_URL = "https://x.com/silviavannutell"
CV_URL = "https://www.dropbox.com/scl/fi/ll2bxqbce6hzrvaxrr8pe/2026_Apr_CV_Vannutelli.pdf?rlkey=vmk7w52mnqz9h2t9owc80xp1f&st=h7l1grf5&dl=0"

NAV = [
    ("index.html", "Home"),
    ("research.html", "Research"),
    ("teaching.html", "Teaching"),
    ("women-in-economics.html", "Women in Economics"),
    ("cv.html", "CV"),
]


BOOT = (
    "(function(d){if(window.top!==window.self){d.classList.add('is-framed');return;}"
    "d.classList.add('js');try{if(sessionStorage.getItem('sv-intro'))d.classList.add('no-intro');"
    "else sessionStorage.setItem('sv-intro','1');}catch(e){}})(document.documentElement);"
)
BOOT_HASH = base64.b64encode(hashlib.sha256(BOOT.encode("utf-8")).digest()).decode("ascii")
CSP = (
    "default-src 'self'; "
    f"script-src 'self' 'sha256-{BOOT_HASH}'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'none'; "
    "frame-src 'none'; "
    "worker-src 'none'"
)


def safe_href(href):
    href = (href or "").strip()
    lowered = href.lower()
    if lowered.startswith(("javascript:", "data:", "vbscript:", "file:")):
        raise SystemExit("refusing unsafe URL")
    parsed = urlparse(href)
    if parsed.scheme == "":
        if href.startswith("//") or "\\" in href:
            raise SystemExit("refusing protocol-relative URL")
        return href
    if parsed.scheme in ("https", "http", "mailto"):
        return href
    raise SystemExit("refusing URL scheme " + parsed.scheme)


def icon(name, cls="icon"):
    if not re.fullmatch(r"i-[a-z0-9-]+", name or ""):
        raise SystemExit("refusing icon name")
    return f'<svg class="{cls}" aria-hidden="true"><use href="assets/img/icons.svg#{name}"/></svg>'


def ext(href, text, cls="link"):
    href = safe_href(href)
    return f'<a class="{cls}" href="{escape(href)}" target="_blank" rel="noopener noreferrer">{text}</a>'


def chip(href, text, ic="i-arrow"):
    href = safe_href(href)
    return f'<a class="chip" href="{escape(href)}" target="_blank" rel="noopener noreferrer">{text}{icon(ic)}</a>'


def brand():
    return (
        '<a class="brand" href="index.html" aria-label="Silvia Vannutelli, home">'
        '<span class="brand-mark" aria-hidden="true"><span></span><span>SV</span></span>'
        '<span class="brand-text"><span class="brand-name">Silvia Vannutelli</span>'
        '<span class="brand-role">Economist · Northwestern University</span></span></a>'
    )


def nav_list(active):
    items = []
    for i, (href, label) in enumerate(NAV, 1):
        cur = ' aria-current="page"' if href == active else ""
        items.append(
            f'<li><a href="{href}"{cur}><span class="num">0{i}</span><span class="label">{label}</span></a></li>'
        )
    return '<ul class="nav">' + "".join(items) + "</ul>"


def actions():
    return (
        '<div class="rail-actions">'
        f'<button type="button" class="btn" data-contact aria-haspopup="dialog">{icon("i-mail")}Contact</button>'
        f'<a class="btn btn-ghost" href="{escape(safe_href(CV_URL))}" target="_blank" rel="noopener noreferrer">{icon("i-download")}Download CV</a>'
        "</div>"
    )


def contact_dialog():
    return f"""
<dialog class="contact-dialog" id="contact" aria-labelledby="contact-title">
  <div class="cd-head">
    <button type="button" class="icon-btn cd-close" data-contact-close aria-label="Close contact window">{icon("i-close")}</button>
    <span class="tag tag-sky">Get in touch</span>
    <h2 id="contact-title">Contact</h2>
    <p class="is-placeholder">[How to reach me.]</p>
  </div>
  <div class="cd-body">
    <div class="cd-email">
      {icon("i-mail")}
      <a href="{escape(safe_href('mailto:' + EMAIL))}">{EMAIL}</a>
      <button type="button" class="icon-btn" data-copy="{EMAIL}" aria-label="Copy email address">{icon("i-copy")}</button>
    </div>
    <div class="cd-addresses">
      <address class="cd-address is-current">
        <span class="tag">Current · 2026–27</span>
        <strong>Hoover Institution</strong>
        Hoover Memorial Building<br>Office 337, 434 Galvez Mall<br>Stanford, CA 94305
        <br>{chip("https://www.google.com/maps/search/?api=1&query=Hoover+Memorial+Building+434+Galvez+Mall+Stanford+CA+94305", "Map", "i-pin")}
      </address>
      <address class="cd-address">
        <span class="tag">Northwestern</span>
        <strong>Kellogg Global Hub</strong>
        Office 3431<br>2211 Campus Drive<br>Evanston, IL 60208
        <br>{chip("https://www.google.com/maps/search/?api=1&query=Kellogg+Global+Hub+2211+Campus+Dr+Evanston+IL+60208", "Map", "i-pin")}
      </address>
    </div>
    <div class="cd-social">
      <a class="btn btn-sm btn-flare" href="{escape(safe_href('mailto:' + EMAIL))}">{icon("i-mail")}Send an email</a>
      <a class="btn btn-sm btn-ghost" href="{escape(safe_href(X_URL))}" target="_blank" rel="noopener noreferrer">{icon("i-x")}@silviavannutell</a>
    </div>
  </div>
</dialog>"""


def footer():
    return f"""
<footer class="footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h2 class="is-placeholder">[Footer heading]</h2>
        <p class="is-placeholder">[Footer note.]</p>
      </div>
      <button type="button" class="btn btn-flare" data-contact aria-haspopup="dialog">{icon("i-mail")}Get in touch</button>
    </div>
    <div class="footer-small">
      <span>© <span data-year>2026</span> Silvia Vannutelli</span>
      <span>made by Charlie Fisman</span>
    </div>
  </div>
</footer>"""


def page(filename, title, description, body, active=None):
    active = active or filename
    full_title = "Silvia Vannutelli" if title is None else f"{title} · Silvia Vannutelli"
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(full_title)}</title>
<meta name="description" content="{escape(description)}">
<meta name="theme-color" content="#1D5BD6">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta property="og:title" content="{escape(full_title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:type" content="website">
<meta property="og:image" content="assets/img/headshot.jpg">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/css/style.css">
<script>{BOOT}</script>
<script src="assets/js/site.js" defer></script>
</head>
<body>
<a class="skip-link" href="#content">Skip to content</a>
<div class="shell">
  <aside class="rail" aria-label="Site">
    {brand()}
    <nav aria-label="Primary">{nav_list(active)}</nav>
    {actions()}
    <div class="rail-foot"><p>Assistant Professor of Economics<br>Northwestern University</p></div>
  </aside>

  <header class="topbar">
    {brand()}
    <div class="topbar-actions">
      <button type="button" class="btn btn-sm" data-contact aria-haspopup="dialog">{icon("i-mail")}<span class="btn-label">Contact</span></button>
      <button type="button" class="icon-btn" data-menu-toggle aria-expanded="false" aria-controls="menu-sheet" aria-label="Menu">{icon("i-menu")}</button>
    </div>
  </header>
  <div class="sheet" id="menu-sheet">
    <nav aria-label="Primary (mobile)">{nav_list(active)}</nav>
    {actions()}
  </div>

  <main class="main" id="content">
{body}
{footer()}
  </main>
</div>
{contact_dialog()}
</body>
</html>
"""
    if "fonts.googleapis.com" in html or "fonts.gstatic.com" in html:
        raise SystemExit("third-party font host left in " + filename)
    for match in re.finditer(r'''(?:href|src)\s*=\s*["']([^"']+)''', html):
        safe_href(match.group(1).replace("&amp;", "&"))
    scripts = re.findall(r"<script\b([^>]*)>(.*?)</script>", html, re.S)
    for attrs, body in scripts:
        if "src=" in attrs:
            if "assets/js/site.js" not in attrs:
                raise SystemExit("unexpected script in " + filename)
        elif body != BOOT:
            raise SystemExit("unexpected inline script in " + filename)
    if re.search(r"\sstyle\s*=", html):
        raise SystemExit("inline style attribute in " + filename)
    with open(os.path.join(OUT, filename), "w", encoding="utf-8") as f:
        f.write(html)


# ---------------------------------------------------------------- data

def co(names):
    return ", ".join(f'<span class="co">{escape(n)}</span>' for n in names)


PUBLICATIONS = [
    dict(
        id="procurement",
        year="Forthcoming",
        title="Rules, Discretion, and Corruption in Procurement: Evidence from Italian Government Contracting",
        href="https://www.dropbox.com/scl/fi/rm4pazbr1q9bvx9muw6jx/criminal_procurement_JPEMicroFinalSubmitted_v2.pdf?rlkey=m45rbdbra9cwlou7653mn4hrd&st=czyyl55o&dl=0",
        coauthors=["Francesco Decarolis", "Raymond Fisman", "Paolo Pinotti"],
        venue="Journal of Political Economy: Microeconomics",
        links=[
            ("Paper", "https://www.dropbox.com/scl/fi/rm4pazbr1q9bvx9muw6jx/criminal_procurement_JPEMicroFinalSubmitted_v2.pdf?rlkey=m45rbdbra9cwlou7653mn4hrd&st=czyyl55o&dl=0", "i-file"),
            ("Online Appendix", "https://www.dropbox.com/scl/fi/ffq3my3gzf40pamxol63g/criminal_procurement_JPEMicroFinalSubmitted.pdf?rlkey=0mbp9evvm56ogxps2f8fe362j&st=et793avt&dl=0", "i-file"),
        ],
        abstract="The benefits of bureaucratic discretion depend on the extent to which it is used for public benefit versus exploited for private gain. We study the relationship between discretion and corruption in Italian government procurement auctions, using a confidential database of firms and procurement officials investigated for corruption by Italian enforcement authorities. Based on a regression discontinuity design around thresholds for discretion, we find that, overall, a large increase in the use of discretionary procedures in the 2000s led to a minimal increase in auctions won by investigated firms. To understand this ‘non-result,’ we further investigate the attributes of “corrupted” auctions. We show that discretionary procedure auctions are associated with corruption only when conducted with fewer than the formally required number of bidders; similarly, discretionary criteria (“scoring rule” rather than first price) auctions are won more often by investigated firms. We further show that these “corruptible” discretionary auctions are chosen more often by officials who are themselves investigated for corruption, but less often in procurement administrations in which at least one official is investigated for corruption. These findings fit with a framework in which more discretion leads to greater efficiency as well as more opportunities for theft, and a central monitor manages this trade-off by limiting discretion for high-corruption procedures and locales. Additional results based on two standard tools for curbing corruption – turnover and subcontracting limits – corroborate this interpretation. Overall, our results imply that discretion is under-utilized, given the high potential benefits as compared to the modest increment in corruption.",
    ),
    dict(
        id="unemployment-assistance",
        year="2023",
        title="Bringing Them In or Pushing Them Out? The Labor Market Effects of Pro-cyclical Unemployment Assistance Changes",
        href="https://www.nber.org/papers/w30301",
        coauthors=["Gerard Domènech-Arumí"],
        venue="Review of Economics and Statistics",
        links=[("NBER WP 30301", "https://www.nber.org/papers/w30301", "i-arrow")],
        abstract="We exploit an unanticipated labor market reform to estimate the effects of pro-cyclical changes in long-term unemployment assistance (UA). In July 2012, Spain raised the minimum age to receive unlimited-duration UA from 52 to 55. Using a difference-in-differences design, we document that shorter benefits caused (i) shorter non-employment duration, especially among younger workers; (ii) higher labor force exit and other programs' take-up, especially among older workers; (iii) lower wages upon re-employment. The reform induced moderate government savings. Our results highlight the importance of considering the interplay with labor market conditions when designing long-term benefit schedules that affect workers close to retirement.",
    ),
    dict(
        id="distributional-preferences-americans",
        year="2023",
        title="The Distributional Preferences of Americans, 2013–2016",
        href="https://eml.berkeley.edu/~kariv/FJKV_I.pdf",
        coauthors=["Raymond Fisman", "Pamela Jakiela", "Shachar Kariv"],
        venue="Experimental Economics",
        links=[("Paper", "https://eml.berkeley.edu/~kariv/FJKV_I.pdf", "i-file")],
        abstract="We study the distributional preferences of Americans during 2013-2016, a period of significant social and economic upheaval. We decompose preferences into two qualitatively different tradeoffs — fairness versus self-interest, and equality versus efficiency — and measure both at the individual level in a large and diverse sample. The population-level distributions of preferences remain remarkably stable overall, and individual-level preferences in 2013 are highly predictive of those in 2016. Subjects that experienced an increase in household income became more self-interested, and those who voted for Democratic presidential candidates in both 2012 and 2016 became more equality-oriented.",
    ),
    dict(
        id="gender-corruption",
        year="2022",
        title="Gender and Bureaucratic Corruption: Evidence from Two Countries",
        href="https://www.nber.org/papers/w28397",
        coauthors=["Francesco Decarolis", "Raymond Fisman", "Paolo Pinotti", "Yongxiang Wang"],
        venue="Journal of Law, Economics, and Organization",
        links=[
            ("NBER WP 28397", "https://www.nber.org/papers/w28397", "i-arrow"),
            ("Journal version", "https://doi.org/10.1093/jleo/ewab041", "i-arrow"),
        ],
        abstract="We examine the correlation between gender and bureaucratic corruption using two distinct datasets, one from Italy and a second from China. In each case, we find that women are far less likely to be investigated for corruption than men. In our Italian data, female procurement officials are 34 percent less likely than men to be investigated for corruption by enforcement authorities; in China, female prefectural leaders are as much as 75 percent less likely to be arrested for corruption than men. While these represent correlations (rather than definitive causal effects), both are very robust relationships, which survive the inclusion of fine-grained individual and geographic controls.",
    ),
    dict(
        id="larger-groups",
        year="2020",
        title="Distributional Preferences in Larger Groups: Keeping up with the Joneses and Keeping Track of the Tails",
        href="https://www.dropbox.com/s/pa57i39wuo165co/local_comp_JEEAformatting.pdf?dl=0",
        coauthors=["Raymond Fisman", "Ilyana Kuziemko"],
        venue="Journal of the European Economic Association",
        links=[("Paper", "https://www.dropbox.com/s/pa57i39wuo165co/local_comp_JEEAformatting.pdf?dl=0", "i-file")],
        abstract="We study distributional preferences in “large” groups. While most prior experiments have focused on exploring attitudes toward inequality in two- or three-person groups, we field a series of experiments via Mechanical Turk in which subjects choose between two income distributions, each with seven (or nine) individuals, with hypothetical incomes that aim to approximate the actual distribution of income in the U.S. Our setting thus provides a more direct comparison to the redistributive choices faced by society. Consistent with standard maximin (Rawlsian) preferences, subjects select distributions in which the bottom individual’s income is higher (but show little regard for lower incomes above the bottom ranking). In contrast to standard models, however, we find that subjects select distributions that lower the top individual’s income, but not other high incomes. Finally, we provide tentative evidence of “locally competitive” preferences—in most experimental sessions, subjects select distributions that lower the income of the individual directly above them, while the income of the individual two positions above has little effect on subjects’ decisions. Our findings suggest that theories of inequality aversion should be enriched to account for individuals’ aversion to “topmost” and “local” disadvantageous inequality.",
    ),
]

WORKING = [
    dict(
        id="ambiguous-attribution",
        status=("sub", "Submitted"),
        title="Ambiguous Attribution: Theory and Evidence",
        href="https://www.nber.org/papers/w35550",
        coauthors=["Ricardo Alonso", "Monica Martinez-Bravo", "Gerard Padró i Miquel", "Carlos Sanz"],
        venue="NBER Working Paper 35550",
        links=[("NBER WP 35550", "https://www.nber.org/papers/w35550", "i-arrow")],
        abstract="Clarity of responsibility is an essential element of political accountability. We develop a rational model of Bayesian updating in the presence of ambiguous attribution and we test its predictions using an original survey. We show that respondents’ partisanship, assessment of public healthcare quality, and beliefs over which layer of government is responsible for healthcare are correlated as predicted: good-assessment voters attribute responsibility to the layer governed by their preferred party, while bad-assessment voters blame the layer governed by the party they dislike. These partisan patterns of credit and blame, often interpreted as evidence of motivated reasoning or partisan bias, can thus arise from rational Bayesian updating under attribution ambiguity. No such partisan patterns exist where the same party is in charge of regional and central government. A survey experiment in which we inform subjects of the official quality of healthcare has them update in the predicted, partisan, direction. Model and empirical results show that partisan priors are extremely hard to dislodge when attribution is ambiguous.",
    ),
    dict(
        id="lapdogs-watchdogs",
        status=("rr", "R&R · JPE"),
        title="From Lapdogs to Watchdogs: Selecting Monitors in Multi-Layered Organizations",
        href="https://www.nber.org/papers/w30644",
        coauthors=[],
        venue="Revised and Resubmitted, <em>Journal of Political Economy</em> · NBER WP 30644",
        links=[("NBER WP 30644", "https://www.nber.org/papers/w30644", "i-arrow")],
        abstract="A central challenge in public finance is how to design oversight institutions that align local governments' incentives with national fiscal objectives. While monitoring can mitigate agency problems, it may itself be rendered ineffective if monitors are corruptible. In this paper, I evaluate the consequences of changes in the design of monitoring institutions for organizational performance. I exploit the staggered introduction of a reform that removed the control of municipal auditors’ appointments from local politicians and introduced a random assignment mechanism. I obtain four main findings. First, random matching severs auditors-mayors connections. Second, treated municipalities significantly and persistently improve their net surpluses and debt repayments, in line with national government objectives. Third, the fiscal improvement results from a sizeable increase in tax capacity. Fourth, treatment effects are significantly larger where the risk of auditor capture was highest before the reform, but also increasing in auditors' expertise—suggesting the potential presence of a bias-information trade-off. Overall, the results highlight the value of monitors’ independence and illustrate how changes in organizational design can substantially improve governance.",
    ),
    dict(
        id="revolving-door",
        status=("sub", "Submitted"),
        title="Revolving Door Laws and Political Selection",
        href="https://www.dropbox.com/scl/fi/brwsp2avm7kqlvnnmsabi/Revolving_Door_AERSubmit.pdf?rlkey=0f4ir31joz1f3z0jvl9wl653l&dl=0",
        coauthors=["Raymond Fisman", "Jetson Leder-Luis", "Catherine O’Donnell"],
        venue="NBER Working Paper 33626",
        links=[
            ("Paper", "https://www.dropbox.com/scl/fi/brwsp2avm7kqlvnnmsabi/Revolving_Door_AERSubmit.pdf?rlkey=0f4ir31joz1f3z0jvl9wl653l&dl=0", "i-file"),
            ("NBER WP 33626", "https://www.nber.org/papers/w33626", "i-arrow"),
        ],
        abstract="Revolving door laws restrict public officials from representing private interests before government after leaving office. While these laws mitigate potential conflicts of interest, they also may affect the pool of candidates for public positions by lowering the financial benefits of holding office. We study the consequences of revolving door laws for political selection in U.S. state legislatures, exploiting the staggered roll-out of laws across states over time. We find that fewer new candidates enter politics in treated states and that incumbent legislators are less likely to leave office, leading to an increase in uncontested elections. The decline in entry is particularly strong for independent and more moderate candidates, which may increase polarization. We provide a model of politician career incentives to interpret the results.",
    ),
    dict(
        id="stimulus-transfers",
        status=("sub", "Submitted"),
        title="The Political Economy of Stimulus Transfers",
        href="https://www.dropbox.com/scl/fi/97t0c82ba7vr9jo8q8l0y/80euro_june42025.pdf?rlkey=g8iqcop7pc5etvg5ytkq1bwnw&dl=0",
        coauthors=[],
        venue="Working paper",
        links=[("Paper", "https://www.dropbox.com/scl/fi/97t0c82ba7vr9jo8q8l0y/80euro_june42025.pdf?rlkey=g8iqcop7pc5etvg5ytkq1bwnw&dl=0", "i-file")],
        abstract="Stimulus payments are one of the most common policy tools during economic downturns. To maximize effectiveness, transfers should target liquidity-constrained individuals, yet they often end up benefiting the middle class. I argue that political incentives might explain this puzzle. I study one of the largest stimulus tax credits in history, that targeted median earners and excluded the lowest-income groups. The transfer modestly boosted consumption but significantly increased the incumbent’s vote share by 0.18 pp per 1 pp rise in recipients. Electoral rewards persist up to five years post-policy introduction. I then document stronger responses in localities with relatively richer beneficiaries, suggesting that electoral incentives may prompt politicians to prioritize middle-income, electorally responsive groups over the poorer, more consumption-responsive ones. Finally, I document significant punishment of the incumbent among individuals who lose access to the transfer, which help explain politicians’ reluctance to repeal stimulus tax cuts, despite their substantial costs. Overall, these findings demonstrate the importance of considering political incentives to understand the design of major taxes and transfers.",
    ),
    dict(
        id="government-audits",
        status=("rr", "R&R · JLEO"),
        title="Government Audits",
        href="https://www.nber.org/papers/w30975",
        coauthors=["Martina Cuneo", "Jetson Leder-Luis"],
        venue="Revised and Resubmitted, <em>Journal of Law, Economics, and Organization</em> · NBER WP 30975",
        links=[("NBER WP 30975", "https://www.nber.org/papers/w30975", "i-arrow")],
        abstract="Audits are a classic mechanism to ensure accountability in the management of public funds. While commonly used, audits are costly and do not always produce valuable results. In this paper, we use theory and empirics to examine the effectiveness of internal government audits as a function of state capacity. In our model, the value of audits depends on both the underlying presence of abuse and on the government's ability to enforce punishments, making auditing most effective in middling state-capacity environments. Consistent with this theory, we survey all the existing credibly causal studies and show that government audits have positive effects mostly in middle-state-capacity environments like Brazil. Finally, we present novel empirical evidence on the effectiveness of audits for local governments in the US, a high-capacity and low-impropriety environment. Using a previously unexplored threshold in federal audit rules and a dynamic regression discontinuity design, we find no marginal effects of audits on any fiscal outcomes of local governments, a result that is in line with the predictions of our model. Overall, our findings suggest that countries like the US might benefit from relaxing audit requirements and reducing their regulatory burden.",
    ),
    dict(
        id="back-to-black",
        status=("rr", "R&R · JHR"),
        title="Back to Black? The Impact of Regularizing Migrant Workers",
        href="https://www.dropbox.com/scl/fi/jcfgsk04utidgqgmboh4f/DPMNV_2023_v5.pdf?rlkey=bx2pvbb7x2auixcx8cikqfbb0&dl=0",
        coauthors=["Edoardo Di Porto", "Enrica Maria Martino", "Paolo Naticchioni"],
        venue="Revised and Resubmitted, <em>Journal of Human Resources</em>",
        links=[("Paper", "https://www.dropbox.com/scl/fi/jcfgsk04utidgqgmboh4f/DPMNV_2023_v5.pdf?rlkey=bx2pvbb7x2auixcx8cikqfbb0&dl=0", "i-file")],
        abstract="Using unique matched employer-employee data on the universe of workers in Italy, we evaluate one of the world's largest amnesties that regularized over 700,000 undocumented migrants. We employ a difference-in-differences design, comparing firms that regularized at least one migrant to a control group of eligible firms that applied for the regularization process but did not complete it. We document four sets of results. First, the policy has a positive and sizeable impact on firm-level employment in the short run, which only partially fades out in the long run. Second, average firm-level wages experience a small and persistent decrease. Third, at the firm-level, the consequences of the regularization are mainly borne by incumbent migrants, with more limited impact on natives. At the individual level, although the regularization induces changes in the composition of employment, it does not affect native workers' careers in the subsequent years. Fourth, we document a sizeable hysteresis effect of the regularization: 73.5% of newly regularized migrants are still employed in the formal Italian labor market after 4 years, well beyond the expiration of their temporary work permit.",
    ),
    dict(
        id="eu-enlargement",
        status=("rr", "R&R · EJ"),
        title="Immigrants’ Legal Status and Firms: Evidence from the 2007 EU Enlargement",
        href="https://www.nber.org/papers/w35493",
        coauthors=["Vittoria Dicandia"],
        venue="Revised and Resubmitted, <em>Economic Journal</em> · NBER WP 35493",
        links=[("NBER WP 35493", "https://www.nber.org/papers/w35493", "i-arrow")],
        note='This project is made possible thanks to the ' + ext("https://www.inps.it/it/it/dati-e-bilanci/attivit--di-ricerca/programma-visitinps-scholars.html", "VisitINPS Scholars") + ' program, granting access to the universe of Italian Social Security data.',
        abstract="We study how firms and workers adjust when previously restricted migrants gain full and portable work rights in a labor market with substantial informality. We exploit the 2007 EU accession of Bulgaria and Romania, which granted unrestricted work rights to Italy's largest migrant group. Using matched employer–employee administrative data and an IV-DID design, we find that firms suddenly and persistently shift employment composition toward EU07 workers, compressing the native employment share without reducing native hiring or increasing separations. We don't detect any significant change in wages for either natives or EU07 workers. For migrants, this null effect reflects offsetting compositional shifts as newly observed and incumbent EU07 workers enter the formal workforce with different wage trajectories. Consistent with a shift in bargaining power toward workers, EU07 migrants experienced significant gains in job mobility and job security. Overall, the evidence suggests that removing legal restrictions reshaped firms’ personnel choices and altered migrants’ employment relationships, improving their outside options, bargaining position, and access to more secure jobs.",
    ),
]

WIP = [
    dict(title="The Value of Information for Regulatory Enforcement", coauthors=["Elliott Ash", "Maddalena Ronchi", "Elena Stella"], topic="[Topic]", motif="dots"),
    dict(title="Improving Governance through Citizen Feedback Technologies: Evidence from Pakistan", coauthors=["Sultan Mehmood", "Shaheen Naseer"], topic="[Topic]", motif="ripples"),
    dict(title="The Political Economy of Environmental Policy", coauthors=["Reka Juhasz"], topic="[Topic]", motif="waves"),
    dict(title="Managing Tax Collection", coauthors=["Simone Paci", "Giacomo Marcolin"], topic="[Topic]", motif="bars"),
    dict(title="Outsourcing Government in the U.S.", coauthors=["Guo Xu", "Charles Hanzel"], topic="[Topic]", motif="nested"),
    dict(title="Managers and the Organization of Remote Work", coauthors=["Erika Deserranno", "Maria De Paola"], topic="[Topic]", motif="network"),
    dict(title="Pay, Stability and Quality in the U.S. Childcare Sector", coauthors=["Anna Weber", "Sara Downing"], topic="[Topic]", motif="blocks",
         note="This project is supported by a grant from the Alfred P. Sloan Foundation."),
]


# ---------------------------------------------------------------- motifs

PALETTE = ["#1D5BD6", "#143F9E", "#BFD7F7", "#8FB6F0", "#FF5A3C"]


def motif_svg(kind, seed):
    rnd = random.Random(seed)
    W, H = 600, 150
    parts = []
    if kind == "dots":
        for gx in range(0, W + 1, 24):
            for gy in range(12, H, 24):
                r = 2.4
                fill = "#BFD7F7"
                roll = rnd.random()
                if roll > .93:
                    fill, r = "#1D5BD6", 5
                elif roll > .985:
                    fill, r = "#FF5A3C", 5
                parts.append(f'<circle cx="{gx}" cy="{gy}" r="{r}" fill="{fill}"/>')
        parts.append('<circle cx="444" cy="60" r="6" fill="#FF5A3C"/>')
    elif kind == "ripples":
        for cx, cy, n, col in [(140, 120, 7, "#1D5BD6"), (430, 30, 6, "#8FB6F0")]:
            for i in range(1, n + 1):
                parts.append(f'<circle cx="{cx}" cy="{cy}" r="{i*22}" fill="none" stroke="{col}" stroke-opacity="{1 - i/(n+2):.2f}" stroke-width="2"/>')
        parts.append('<rect x="300" y="62" width="70" height="30" rx="15" fill="#FF5A3C"/>')
        parts.append('<rect x="382" y="96" width="110" height="30" rx="15" fill="#1D5BD6"/>')
    elif kind == "waves":
        for i in range(9):
            y0 = 20 + i * 15
            d = f"M0 {y0}"
            for x in range(0, W + 1, 20):
                y = y0 + math.sin((x / 90) + i * .55) * 10
                d += f" L{x} {y:.1f}"
            col = "#FF5A3C" if i == 4 else ("#1D5BD6" if i % 2 else "#8FB6F0")
            parts.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="round"/>')
    elif kind == "bars":
        x = 20
        h = 26
        while x < W - 20:
            h = max(14, min(128, h + rnd.randint(-8, 16)))
            col = "#1D5BD6" if rnd.random() > .3 else "#8FB6F0"
            parts.append(f'<rect x="{x}" y="{H - h}" width="16" height="{h}" rx="4" fill="{col}"/>')
            x += 24
        parts.append(f'<rect x="{x - 24}" y="{H - h}" width="16" height="{h}" rx="4" fill="#FF5A3C"/>')
    elif kind == "nested":
        for k, (cx, cy) in enumerate([(120, 75), (300, 75), (480, 75)]):
            for i in range(4):
                s = 110 - i * 26
                col = ["#143F9E", "#1D5BD6", "#8FB6F0", "#BFD7F7"][i]
                if k == 2 and i == 3:
                    col = "#FF5A3C"
                parts.append(f'<rect x="{cx - s/2 + k*6*i}" y="{cy - s/2}" width="{s}" height="{s}" rx="10" fill="none" stroke="{col}" stroke-width="2.4"/>')
        parts.append('<path d="M175 75 H245 M355 75 H425" stroke="#1D5BD6" stroke-width="2.4" stroke-dasharray="4 6"/>')
    elif kind == "network":
        pts = [(rnd.randint(30, W - 30), rnd.randint(20, H - 20)) for _ in range(16)]
        for i, (x1, y1) in enumerate(pts):
            for x2, y2 in pts[i + 1:]:
                if math.hypot(x2 - x1, y2 - y1) < 150:
                    parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#BFD7F7" stroke-width="1.6"/>')
        for i, (x, y) in enumerate(pts):
            col = "#FF5A3C" if i == 3 else ("#1D5BD6" if i % 3 else "#143F9E")
            parts.append(f'<rect x="{x-7}" y="{y-7}" width="14" height="14" rx="4" fill="{col}"/>')
    elif kind == "blocks":
        x = 24
        while x < W - 40:
            stack = rnd.randint(1, 4)
            for j in range(stack):
                col = rnd.choice(["#1D5BD6", "#8FB6F0", "#BFD7F7", "#143F9E"])
                parts.append(f'<rect x="{x}" y="{H - 30 - j*30}" width="34" height="26" rx="6" fill="{col}"/>')
            x += 40
        parts.append(f'<rect x="{x - 40}" y="{H - 30}" width="34" height="26" rx="6" fill="#FF5A3C"/>')
    return (
        f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">'
        + "".join(parts)
        + "</svg>"
    )


# ---------------------------------------------------------------- pages

def wip_window():
    tabs, panels = [], []
    for i, w in enumerate(WIP):
        n = f"{i+1:02d}"
        sel = "true" if i == 0 else "false"
        tabs.append(
            f'<li role="presentation"><button type="button" class="wip-tab" role="tab" id="wip-tab-{i}" '
            f'aria-controls="wip-panel-{i}" aria-selected="{sel}" tabindex="{0 if i == 0 else -1}">'
            f'<span class="n">{n}</span><span class="t">{escape(w["title"])}</span><span class="bar"><i></i></span></button></li>'
        )
        note = f'<p class="wip-note">{escape(w["note"])}</p>' if w.get("note") else ""
        hidden = "" if i == 0 else " hidden"
        panels.append(
            f'<div class="wip-panel" role="tabpanel" id="wip-panel-{i}" aria-labelledby="wip-tab-{i}"{hidden}>'
            f'<div class="wip-art">{motif_svg(w["motif"], i + 7)}</div>'
            f'<div class="wip-meta"><span class="pill pill-wip">In progress</span><span class="tag is-placeholder">{escape(w["topic"])}</span></div>'
            f'<h3>{escape(w["title"])}</h3>'
            f'<p class="wip-with">with <span>{escape(", ".join(w["coauthors"][:-1]) + (" and " if len(w["coauthors"]) > 1 else "") + w["coauthors"][-1])}</span></p>'
            f"{note}</div>"
        )
    return f"""
<div class="wip reveal" data-wip>
  <ul class="wip-list" role="tablist" aria-label="Selected work in progress" aria-orientation="vertical">
    {''.join(tabs)}
  </ul>
  <div class="wip-stage">
    {''.join(panels)}
    <div class="wip-controls">
      <span class="wip-count" aria-live="polite">Project <b data-wip-current>1</b> of {len(WIP)}</span>
      <div class="wip-buttons">
        <button type="button" class="icon-btn prev" data-wip-prev aria-label="Previous project">{icon("i-right")}</button>
        <button type="button" class="icon-btn" data-wip-toggle aria-pressed="false" aria-label="Pause rotation">{icon("i-pause")}</button>
        <button type="button" class="icon-btn" data-wip-next aria-label="Next project">{icon("i-right")}</button>
      </div>
    </div>
  </div>
</div>"""


FIELD_GLYPHS = {
    "pe": '<svg class="field-glyph" viewBox="0 0 44 44" aria-hidden="true"><rect x="4" y="22" width="8" height="18" rx="2" fill="#BFD7F7"/><rect x="18" y="12" width="8" height="28" rx="2" fill="#1D5BD6"/><rect x="32" y="4" width="8" height="36" rx="2" fill="#143F9E"/></svg>',
    "pub": '<svg class="field-glyph" viewBox="0 0 44 44" aria-hidden="true"><circle cx="22" cy="22" r="18" fill="#BFD7F7"/><path d="M22 4a18 18 0 0 1 18 18H22z" fill="#1D5BD6"/><path d="M22 22h18a18 18 0 0 1-5.3 12.7z" fill="#143F9E"/></svg>',
    "org": '<svg class="field-glyph" viewBox="0 0 44 44" aria-hidden="true"><rect x="16" y="3" width="12" height="10" rx="2" fill="#143F9E"/><rect x="3" y="31" width="12" height="10" rx="2" fill="#BFD7F7"/><rect x="16" y="31" width="12" height="10" rx="2" fill="#1D5BD6"/><rect x="29" y="31" width="12" height="10" rx="2" fill="#BFD7F7"/><path d="M22 13v9M9 31v-5h26v5M22 22v9" stroke="#1D5BD6" stroke-width="2" fill="none"/></svg>',
}


def build_home():
    cards = []
    for i, p in enumerate(PUBLICATIONS[:3]):
        cards.append(
            f'<a class="paper-card reveal" data-delay="{i+1}" href="research.html#{p["id"]}">'
            f'<span class="venue">{escape(p["venue"])} · {escape(p["year"])}</span>'
            f'<h3>{escape(p["title"])}</h3>'
            f'<span class="go">Read more {icon("i-arrow", "icon")}</span></a>'
        )
    body = f"""
<section class="hero">
  <div class="wrap">
    <div class="hero-grid">
      <div>
        <span class="tag">Assistant Professor of Economics · Northwestern University</span>
        <h1><span class="line"><span>Silvia</span></span><span class="line"><span class="accent">Vannutelli</span></span></h1>
        <p class="hero-statement is-placeholder">[Bio here. Two or three sentences.]</p>
        <div class="hero-actions">
          <a class="btn" href="research.html">Explore research {icon("i-right")}</a>
          <a class="btn btn-ghost" href="cv.html">View CV {icon("i-right")}</a>
        </div>
        <ul class="affils" aria-label="Affiliations">
          <li><strong>NBER</strong> Faculty Research Fellow</li>
          <li><strong>CEPR</strong> Faculty Affiliate</li>
          <li><strong>Stigler Center</strong>, Chicago Booth · Senior Affiliate Fellow</li>
        </ul>
      </div>
      <div>
        <div class="portrait">
          <span class="layer layer-1" aria-hidden="true"></span>
          <span class="layer layer-2" aria-hidden="true"></span>
          <img src="assets/img/headshot.jpg" width="415" height="517" alt="Portrait of Silvia Vannutelli">
          <div class="portrait-badge">
            <span class="tag">2026–27</span>
            <strong>Glenn Campbell and Rita Ricardo-Campbell National Fellow</strong> at the Hoover Institution, Stanford
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head reveal">
      <div>
        <span class="tag">What I work on</span>
        <h2 class="is-placeholder">[Section heading]</h2>
        <p class="section-note is-placeholder">[One or two sentences on this section.]</p>
      </div>
    </div>
    <div class="fields">
      <article class="field reveal" data-delay="1">{FIELD_GLYPHS["pe"]}<h3>Political Economy</h3><p class="is-placeholder">[Short description.]</p></article>
      <article class="field reveal" data-delay="2">{FIELD_GLYPHS["pub"]}<h3>Public Economics</h3><p class="is-placeholder">[Short description.]</p></article>
      <article class="field reveal" data-delay="3">{FIELD_GLYPHS["org"]}<h3>Organizational Economics</h3><p class="is-placeholder">[Short description.]</p></article>
    </div>
  </div>
</section>

<section class="section" id="work-in-progress">
  <div class="wrap">
    <div class="section-head reveal">
      <div>
        <span class="tag">Selected work in progress</span>
        <h2 class="is-placeholder">[Work in progress heading]</h2>
        <p class="section-note is-placeholder">[One sentence introducing current projects.]</p>
      </div>
      <a class="btn btn-ghost btn-sm" href="research.html#in-progress">All research {icon("i-right")}</a>
    </div>
    {wip_window()}
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head reveal">
      <div>
        <span class="tag">Recent publications</span>
        <h2 class="is-placeholder">[Recent publications heading]</h2>
      </div>
      <a class="btn btn-ghost btn-sm" href="research.html#publications">All publications {icon("i-right")}</a>
    </div>
    <div class="paper-cards">{''.join(cards)}</div>
  </div>
</section>
"""
    page("index.html", None, "Silvia Vannutelli, Assistant Professor of Economics, Northwestern University.", body)


def paper_item(p, kind):
    abs_id = f"abs-{p['id']}"
    if kind == "pub":
        pill = "Accepted" if p["year"] == "Forthcoming" else "Published"
        side = f'<span class="paper-year">{escape(p["year"])}</span><span class="pill pill-pub">{pill}</span>'
        venue = f'<p class="paper-venue"><em>{escape(p["venue"])}</em></p>'
    else:
        cls, label = p["status"]
        side = f'<span class="pill pill-{cls}">{escape(label)}</span>'
        venue = f'<p class="paper-venue">{p["venue"]}</p>'
    authors = f'<p class="paper-authors">with {co(p["coauthors"])}</p>' if p["coauthors"] else '<p class="paper-authors">Single-authored</p>'
    links = "".join(chip(h, escape(t), ic) for t, h, ic in p["links"])
    note = f'<p class="paper-note">{p["note"]}</p>' if p.get("note") else ""
    return f"""
<li class="paper reveal" id="{p['id']}">
  <div class="paper-side">{side}</div>
  <div>
    <h3 class="paper-title"><a href="{escape(safe_href(p['href']))}" target="_blank" rel="noopener noreferrer">{escape(p['title'])}</a></h3>
    {authors}
    {venue}
    <div class="paper-actions">
      {links}
      <button type="button" class="abs-toggle" data-expand aria-expanded="false" aria-controls="{abs_id}" data-open-label="Hide abstract">{icon("i-plus")}<span class="lbl">Abstract</span></button>
    </div>
    {note}
    <div class="abstract" id="{abs_id}" aria-hidden="true"><div><p>{escape(p['abstract'])}</p></div></div>
  </div>
</li>"""


def build_research():
    pubs = "".join(paper_item(p, "pub") for p in PUBLICATIONS)
    wps = "".join(paper_item(p, "wp") for p in WORKING)
    wip_cards = "".join(
        f'<li class="wip-card reveal"><span class="pill pill-wip is-placeholder">{escape(w["topic"])}</span><h3>{escape(w["title"])}</h3>'
        f'<p>with <span>{escape(", ".join(w["coauthors"]))}</span></p>'
        + (f'<p>{escape(w["note"])}</p>' if w.get("note") else "")
        + "</li>"
        for w in WIP
    )
    body = f"""
<header class="page-head">
  <div class="wrap">
    <span class="tag">02 · Research</span>
    <h1>Research</h1>
    <p class="lede is-placeholder">[One or two sentences about the research page.]</p>
  </div>
</header>

<div class="filters" data-filters>
  <div class="wrap">
    <div class="seg" role="group" aria-label="Filter research">
      <button type="button" data-filter="all" aria-pressed="true">All <span class="count">{len(PUBLICATIONS) + len(WORKING) + len(WIP)}</span></button>
      <button type="button" data-filter="publications" aria-pressed="false">Publications <span class="count">{len(PUBLICATIONS)}</span></button>
      <button type="button" data-filter="working-papers" aria-pressed="false">Working papers <span class="count">{len(WORKING)}</span></button>
      <button type="button" data-filter="in-progress" aria-pressed="false">In progress <span class="count">{len(WIP)}</span></button>
    </div>
  </div>
</div>

<div class="wrap">
  <section class="group" id="publications" data-group="publications" aria-labelledby="h-pubs">
    <div class="group-title"><h2 id="h-pubs">Publications</h2><span class="tag">{len(PUBLICATIONS)} papers</span></div>
    <ul class="papers">{pubs}</ul>
  </section>

  <section class="group" id="working-papers" data-group="working-papers" aria-labelledby="h-wps">
    <div class="group-title"><h2 id="h-wps">Working papers</h2><span class="tag">{len(WORKING)} papers</span></div>
    <ul class="papers">{wps}</ul>
  </section>

  <section class="group group-last" id="in-progress" data-group="in-progress" aria-labelledby="h-wip">
    <div class="group-title"><h2 id="h-wip">Selected work in progress</h2><span class="tag">{len(WIP)} projects</span></div>
    <ul class="wip-grid">{wip_cards}</ul>
  </section>
</div>
"""
    page("research.html", "Research", "Research by Silvia Vannutelli.", body)


def build_teaching():
    courses = [
        dict(id="governing-better", code="Masters", inst="Sciences Po · School of Public Affairs", title="Governing Better: A Political Economy of the State",
             summary="[Short course description.]",
             full=[
                 "This is a course about how to improve the functioning of government by understanding the interplay between politics, policy, and public administration. It explores the deep organizational and institutional challenges that shape how democracies work — or fail to. From how we elect politicians to how we recruit bureaucrats, from the design of federal systems to the execution of public procurement, the course investigates why good policies so often fall short and what can be done about it.",
                 "Drawing on political economy theory and real-world examples, the course helps students develop a practical understanding of how states function — and malfunction — in the face of political constraints, bureaucratic complexity, and fiscal limits. We examine foundational models such as the median voter theorem and citizen-candidate framework, as well as more applied challenges like digital governance, AI in the public sector, and policy learning.",
                 "The course is interactive and applied. Students engage with key academic concepts and test them against contemporary public sector problems. They learn to use key methodological tools, such as the Smart Policy Design and Implementation (SPDI) Framework. Guest lectures from policymakers and practitioners offer first-hand perspectives. Through group presentations and a final project simulating stakeholder persuasion, students are encouraged to think like reformers — crafting policy proposals that are both politically feasible and administratively sound.",
             ]),
        dict(id="econ-436", code="ECON 436", inst="Northwestern · Graduate", title="Graduate Public Economics",
             summary="[Short course description.]",
             full=[
                 "This course aims at giving a broad overview of some of the most important topics in public finance, with a focus on recent research as well as areas that have been underlooked for a while and could be revived. We will start with a general overview of the role of government in the economy, and think about modern methods to compare the welfare impacts of different policy interventions. We will then move to think about how governments finance themselves through taxation, covering issues related to how should tax systems be designed, how individuals and firms respond to taxation and who bears the cost of tax changes, and how tax evasion affects the optimal design of taxes and transfers and how can governments fight tax evasion.",
                 "We will then think about the structure of governments, explore issues of local public finance, analyze why some policies in many countries are carried out by local governments, and how to design and evaluate place-based interventions. In the second half of the course, we will think more about government spending, exploring mostly issues related to the economics of education. We will also think about problems related to the assessment of public goods and public service provision, such as the difficulty of measuring the performance and quality of public goods. Finally, we will devote time thinking about the personnel economics of the public sector, meaning the role played by the quality of individuals who work as public sector workers and how to attract and retain talent in the public sector.",
             ]),
        dict(id="econ-337", code="ECON 337", inst="Northwestern · Undergraduate", title="Economics of State and Local Governments",
             summary="[Short course description.]",
             full=[
                 "State and local governments play an essential role in citizens’ day-to-day life, as they decide and deliver key public goods and services, such as education, transportation, health and welfare. This course uses applied tools of microeconomics and simple data analysis to acquaint students with various aspects of the subnational government sector, including expenditure, financing, and policy issues.",
                 "We start by reviewing under what situation government provision is desirable. We then study how levels of state goods and services are determined, and what are the main sources of revenues through which these expenditures are financed, including taxes and transfers from higher levels of government. Students will also learn the importance of political considerations and the role of state and local politics in influencing local government decisions. The course will end with policy analysis and applications. The main focus is going to be on the United States but we are also going to explore examples and issues faced by local governments around the world.",
             ]),
        dict(id="icpsr", code="ICPSR 2020", inst="Summer Program · Online", title="Modern Difference-in-Differences Designs",
             summary="[Short course description.]",
             full=[
                 "This is an intensive summer course offered online through the " + ext("https://www.icpsr.umich.edu/sites/icpsr/sumprog", "ICPSR Summer Program") + "; the main instructor was John Poe. I attended the entire course, taught some of the sessions and provided virtual office hours and live assistance in answering questions. I also prepared some of the teaching materials.",
             ],
             links=[("ICPSR Summer Program", "https://www.icpsr.umich.edu/sites/icpsr/sumprog", "i-arrow")]),
    ]
    items = []
    for c in courses:
        did = f"desc-{c['id']}"
        paras = "".join(f"<p>{t if c['id'] == 'icpsr' else escape(t)}</p>" for t in c["full"])
        links = "".join(chip(h, escape(t), ic) for t, h, ic in c.get("links", []))
        items.append(f"""
<article class="course reveal" id="{c['id']}">
  <div class="course-side">
    <span class="course-code">{escape(c['code'])}</span>
    <span class="course-inst">{escape(c['inst'])}</span>
  </div>
  <div>
    <h3>{escape(c['title'])}</h3>
    <p class="summary is-placeholder">{escape(c['summary'])}</p>
    <div class="paper-actions">
      {links}
      <button type="button" class="abs-toggle" data-expand aria-expanded="false" aria-controls="{did}" data-open-label="Hide description">{icon("i-plus")}<span class="lbl">Full description</span></button>
    </div>
    <div class="abstract" id="{did}" aria-hidden="true"><div>{paras}</div></div>
  </div>
</article>""")
    body = f"""
<header class="page-head">
  <div class="wrap">
    <span class="tag">03 · Teaching</span>
    <h1>Teaching</h1>
    <p class="lede is-placeholder">[One or two sentences about teaching.]</p>
  </div>
</header>

<section class="section">
  <div class="wrap">
    <div class="courses">{''.join(items)}</div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="resource reveal">
      <div>
        <span class="tag">Talk · Methods</span>
        <h3>Recent Advances in DiD Methods</h3>
        <p class="is-placeholder">[Short description of this talk.]</p>
      </div>
      <div class="resource-actions">
        <a class="btn" href="{escape(safe_href('https://www.dropbox.com/s/r9176vxt6yj40dq/zoom_1.mp4?dl=0'))}" target="_blank" rel="noopener noreferrer">{icon("i-play")}Watch lecture</a>
        <a class="btn btn-ghost" href="{escape(safe_href('https://www.dropbox.com/s/ida06skzgj9xp6h/Vannutelli_DID_presentation.pdf?dl=0'))}" target="_blank" rel="noopener noreferrer">{icon("i-file")}Slides</a>
      </div>
    </div>
  </div>
</section>
"""
    page("teaching.html", "Teaching", "Teaching by Silvia Vannutelli.", body)


def build_wie():
    body = f"""
<header class="page-head">
  <div class="wrap">
    <span class="tag">04 · Community</span>
    <h1>Women in Economics</h1>
    <p class="lede is-placeholder">[One or two sentences about this page.]</p>
  </div>
</header>

<section class="section">
  <div class="wrap">
    <ol class="timeline">
      <li class="tl-item reveal">
        <span class="tl-dot" aria-hidden="true"></span>
        <span class="tl-when">Northwestern · Advisor, 2021–present</span>
        <h3>Northwestern Womxn in Economics</h3>
        <div class="tl-card">
          <p>I regularly participate in events organized by {ext("https://economics.northwestern.edu/undergraduate/student-orgs/wie/", "Northwestern Womxn in Economics (WiE)")}, an undergraduate student-led organization seeking to uplift and empower underrepresented genders in economics.</p>
          <p>I held a mini-course about pathways to getting a PhD and the opportunities offered by {ext("https://predoc.org/", "PREDOC")}.</p>
          <div class="paper-actions">{chip("https://www.dropbox.com/s/gpebfmwgt8ga4po/Northwestern-weorg-minicourse.pdf?dl=0", "Mini-course slides", "i-file")}</div>
        </div>
      </li>
      <li class="tl-item reveal">
        <span class="tl-dot" aria-hidden="true"></span>
        <span class="tl-when">During my PhD</span>
        <h3>Seminar Dynamics Collective</h3>
        <div class="tl-card">
          <p>I was part of the Seminar Dynamics Collective, a group of almost 100 economists (mostly graduate students) who volunteered to analyze seminar dynamics and collect and code data for the paper “{ext("https://www.nber.org/papers/w28494", "Gender and the Dynamics of Economics Seminars")}” by Pascaline Dupas, Alicia Sasser Modestino, Muriel Niederle, Justin Wolfers and the Seminar Dynamics Collective.</p>
          <div class="paper-actions">
            {chip("https://www.nber.org/papers/w28494", "NBER paper")}
            {chip("https://www.aeaweb.org/content/file?id=17929", "My CSWEP Newsletter article", "i-file")}
          </div>
        </div>
      </li>
      <li class="tl-item reveal">
        <span class="tl-dot" aria-hidden="true"></span>
        <span class="tl-when">Boston University · Co-Chair, 2017–2019</span>
        <h3>BU Women in Economics (WEOrg)</h3>
        <div class="tl-card">
          <p>I served as Co-Chair of BU WEOrg, a graduate student-led organization dedicated to the advancement of women in all stages of economic research.</p>
          <div class="paper-actions">
            {chip("https://www.bu.edu/econ/students/studentorgs/weorg/", "BU WEOrg website")}
            <a class="chip" href="{escape(safe_href('mailto:weorg@bu.edu'))}">weorg@bu.edu{icon("i-mail")}</a>
          </div>
        </div>
      </li>
      <li class="tl-item reveal">
        <span class="tl-dot" aria-hidden="true"></span>
        <span class="tl-when">Summer 2019 · Organizer</span>
        <h3>WERISE Conference</h3>
        <div class="tl-card">
          <p>We organized {ext("https://questromworld.bu.edu/weorg/", "WERISE")} (Women in Economics: Research, Ideas, Solutions, Executions), a conference bringing together leading scholars for a comprehensive overview of research on the status of women in economics, to reach a deeper understanding of the challenges women face in the profession and to spur ideas for concrete solutions.</p>
          <div class="paper-actions">{chip("https://questromworld.bu.edu/weorg/", "Conference site")}</div>
        </div>
      </li>
    </ol>
  </div>
</section>
"""
    page("women-in-economics.html", "Women in Economics", "Women in Economics, Silvia Vannutelli.", body)


def rows(items):
    out = []
    for when, what, small in items:
        s = f"<small>{escape(small)}</small>" if small else ""
        out.append(f'<li><span class="when">{escape(when)}</span><span class="what">{what}{s}</span></li>')
    return '<ul class="cv-rows">' + "".join(out) + "</ul>"


def build_cv():
    positions = rows([
        ("2026–27", "<strong>Hoover National Fellow</strong>, Stanford University", ""),
        ("2025–26", "<strong>Visiting Assistant Professor of Economics</strong>, Sciences Po", ""),
        ("2022–", "<strong>Assistant Professor of Economics</strong>, Northwestern University", ""),
        ("2022–", "<strong>Faculty Research Fellow</strong>, National Bureau of Economic Research", ""),
        ("2025–", "<strong>Faculty Research Affiliate</strong>, Centre for Economic Policy Research", ""),
        ("2021–", "<strong>Faculty Fellow</strong>, Institute for Policy Research, Northwestern", ""),
        ("2023–", "<strong>Affiliate Fellow</strong>, Stigler Center, University of Chicago Booth", ""),
        ("2023–", "<strong>External Associated Faculty</strong>, CEMFI", ""),
        ("2021–22", "<strong>College Fellow</strong>, Northwestern University", ""),
    ])
    education = rows([
        ("2021", "<strong>Ph.D., Economics</strong>, Boston University", "Dissertation: Three Essays in Applied Microeconomics · Committee: Raymond Fisman, M. Daniele Paserman, Johannes Schmieder"),
        ("2019–20", "<strong>Visiting PhD Student</strong>, University of Chicago Booth School of Business", ""),
        ("2015", "<strong>M.Sc., European Economy and Business Law</strong>, University of Rome Tor Vergata", "Summa cum laude"),
        ("2013", "<strong>B.S., Political Science</strong>, University of Roma Tre", "Summa cum laude"),
        ("2012–13", "<strong>Visiting Student (Erasmus)</strong>, Université Paris 1 Panthéon-Sorbonne", ""),
    ])
    grants = rows([
        ("2026", "<strong>Alfred P. Sloan Foundation Grant</strong> ($468,000)", ""),
        ("2026", "<strong>IPR Seed Grant</strong> ($7,500)", ""),
        ("2024", "<strong>IPR Seed Grant</strong> ($5,000)", ""),
        ("2023", "<strong>Northwestern Faculty Support Grant</strong> ($40,000)", ""),
        ("2022", "<strong>IPR Seed Grant</strong> ($5,000)", ""),
        ("2020", "<strong>Manuel Abdala Gift Research Grant</strong>, Boston University", ""),
        ("2019, 2020", "<strong>Graduate Research Abroad Fellowship</strong>, Boston University", ""),
        ("2019", "<strong>VisitINPS Fellowship</strong>, Italian Social Security Agency", ""),
        ("2018–19", "<strong>Research Fellowship</strong>, Italian Institute for Public Policy Evaluation (INAPP)", ""),
        ("2018", "<strong>Summer Research Award</strong>, Boston University", ""),
        ("2017", "<strong>Bank of Italy Summer Fellowship</strong>", ""),
        ("2015", "<strong>Dean’s Student Fellowship</strong>, Boston University", ""),
        ("2015", "<strong>INET Summer School Fellowship</strong>", ""),
    ])
    teaching = rows([
        ("2025–26", "<strong>Governing Better: A Political Economy of the State</strong> (Graduate), Sciences Po", ""),
        ("2022–", "<strong>Public Economics</strong> (Graduate), Northwestern University", ""),
        ("2022–", "<strong>Economics of State and Local Governments</strong> (Undergraduate), Northwestern University", ""),
        ("2020", "<strong>Modern Difference-in-Differences Designs</strong>, ICPSR · Teaching Assistant", ""),
        ("2016", "<strong>Economics of the Public Sector</strong> and <strong>Markets and Development Economics</strong>, Boston University · Teaching Fellow", ""),
    ])
    organizing = rows([
        ("2025, 2026", "<strong>CEPR Political Economy Symposium</strong> · Organizer", ""),
        ("2023–2026", "<strong>Barcelona GSE Summer Forum, Public Economics</strong> · Organizer", ""),
        ("2023, 2025", "<strong>European Economic Association Conference</strong> · Program Committee", ""),
        ("2024, 2025", "<strong>Ridge-LACEA Workshop on Public Economics</strong> · Program Committee", ""),
        ("2023", "<strong>Northwestern Interactions Conference</strong> · Organizer", ""),
        ("2022", "<strong>SIOE Conference</strong> · Program Committee; <strong>IIPF Annual Congress</strong> · Scientific Committee", ""),
        ("2019", "<strong>WERISE Conference</strong>, Boston University · Organizer", ""),
    ])
    seminars = rows([
        ("2021–", "<strong>Seminar and Lunch in Health, Labor, Education and Public</strong>, Northwestern", ""),
        ("2024–", "<strong>Seminar in Labor Economics</strong>, Northwestern", ""),
        ("2025–", "<strong>Seminar in Political Economy</strong>, Sciences Po", ""),
        ("2021–", "<strong>Junior and Senior Recruitment</strong>; <strong>Undergraduate Women in Economics Advisor</strong>; <strong>Undergraduate Thesis Advising</strong>, Northwestern", ""),
        ("2017–19", "<strong>Women in Economics (WEOrg)</strong>, Boston University · Co-Chair", ""),
    ])
    students = rows([
        ("PhD", "<strong>Elena Stella</strong>", "NUS Finance"),
        ("PhD", "<strong>Johanna Rayl</strong>", "UC Berkeley (Postdoc)"),
        ("PhD", "<strong>Shaheen Naseer</strong>", "Bilkent University"),
        ("PhD", "<strong>Devis Decet</strong>", "Bocconi University (Postdoc), NHH (Postdoc)"),
        ("PhD", "<strong>Giovanni Pisauro</strong>", "Cornerstone Research"),
        ("PhD", "<strong>Carlo Medici</strong>", "Brown (Postdoc), UCLA (Assistant Professor)"),
        ("PhD", "<strong>Laura Montenbruck</strong>", "Stockholm University"),
        ("PhD", "<strong>Weijia Zhao</strong>", "Marshall Wace"),
        ("Pre-PhD", "<strong>Martina Cuneo</strong>", "PhD student, NYU"),
        ("Pre-PhD", "<strong>Violet Hamlin</strong>", "Research Associate, Chicago Booth"),
    ])
    referee = "American Economic Review, Econometrica, Journal of Political Economy, Quarterly Journal of Economics, Review of Economic Studies, Journal of the European Economic Association, Journal of Political Economy: Microeconomics, AEJ: Applied Economics, AER: Insights, AEJ: Economic Policy, Review of Economics and Statistics, Journal of Labor Economics, Management Science, Journal of Public Economics, Journal of Urban Economics, Journal of Development Economics, Journal of International Economics, Quantitative Economics, National Tax Journal, Journal of Law, Economics and Organization, European Economic Review, Economica, European Journal of Political Economy, Journal of Economic Inequality, Social Science Research"
    referee = referee.replace("Journal of Law, Economics and Organization", "Journal of Law, Economics, and Organization")
    journals = [j.strip() for j in referee.replace("Law, Economics, and", "Law§ Economics§ and").split(",")]
    ref_tags = "".join(f"<li>{escape(j.replace('§', ','))}</li>" for j in journals)

    toc = [("positions", "Positions"), ("education", "Education"), ("fields", "Fields"), ("research", "Research"), ("grants", "Grants & awards"),
           ("teaching", "Teaching"), ("service", "Service"), ("students", "Advising"), ("refereeing", "Refereeing"), ("languages", "Languages")]
    toc_html = "".join(f'<li><a href="#{i}">{escape(t)}</a></li>' for i, t in toc)

    body = f"""
<header class="page-head">
  <div class="wrap">
    <span class="tag">05 · Curriculum Vitae</span>
    <h1>CV</h1>
    <p class="lede is-placeholder">[One sentence about the CV.]</p>
    <div class="cv-bar reveal">
      <div><strong>Full CV (PDF)</strong><span>Updated April 2026</span></div>
      <a class="btn" href="{escape(safe_href(CV_URL))}" target="_blank" rel="noopener noreferrer">{icon("i-download")}Download CV</a>
    </div>
  </div>
</header>

<section class="section">
  <div class="wrap">
    <div class="cv-layout">
      <nav aria-label="CV sections"><ul class="cv-toc">{toc_html}</ul></nav>
      <div>
        <section class="cv-block reveal" id="positions"><h2>Academic positions &amp; affiliations</h2>{positions}</section>
        <section class="cv-block reveal" id="education"><h2>Education</h2>{education}</section>
        <section class="cv-block reveal" id="fields"><h2>Fields</h2>
          <ul class="cv-tags"><li>Political Economy</li><li>Public Economics</li><li>Organizational Economics</li></ul>
        </section>
        <section class="cv-block reveal" id="research"><h2>Research</h2>
          <p class="cv-prose is-placeholder">[Short note pointing to the research page.]</p>
          <div class="paper-actions">
            <a class="chip" href="research.html#publications">Publications{icon("i-right")}</a>
            <a class="chip" href="research.html#working-papers">Working papers{icon("i-right")}</a>
            <a class="chip" href="research.html#in-progress">Work in progress{icon("i-right")}</a>
          </div>
        </section>
        <section class="cv-block reveal" id="grants"><h2>Grants, fellowships &amp; awards</h2>{grants}</section>
        <section class="cv-block reveal" id="teaching"><h2>Teaching</h2>{teaching}</section>
        <section class="cv-block reveal" id="service"><h2>Professional service</h2>
          <p class="cv-sub">Conference organizing</p>{organizing}
          <p class="cv-sub">Seminars &amp; departmental service</p>{seminars}
        </section>
        <section class="cv-block reveal" id="students"><h2>Student advising</h2><p class="cv-prose is-placeholder">[Note about how placements are listed.]</p>{students}</section>
        <section class="cv-block reveal" id="refereeing"><h2>Referee for</h2><ul class="cv-tags">{ref_tags}</ul></section>
        <section class="cv-block reveal" id="languages"><h2>Languages</h2>
          <ul class="cv-tags"><li>Italian · native</li><li>English · fluent</li><li>French · intermediate</li><li>Spanish · beginner</li></ul>
        </section>
      </div>
    </div>
  </div>
</section>
"""
    page("cv.html", "CV", "Curriculum vitae of Silvia Vannutelli.", body)


def build_404():
    body = f"""
<header class="page-head page-head-tall">
  <div class="wrap">
    <span class="tag">404</span>
    <h1>This page has moved or never existed.</h1>
    <p class="lede">Try one of the sections in the menu, or head back to the home page.</p>
    <div class="hero-actions">
      <a class="btn" href="index.html">Go home {icon("i-right")}</a>
      <a class="btn btn-ghost" href="research.html">Browse research {icon("i-right")}</a>
    </div>
  </div>
</header>
"""
    page("404.html", "Page not found", "Page not found.", body, active="")
    # GitHub Pages serves 404.html at any missing path, so relative assets need a root base.
    path = os.path.join(OUT, "404.html")
    with open(path, encoding="utf-8") as f:
        html = f.read()
    html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<base href="/">\n<meta name="robots" content="noindex">', 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    build_home()
    build_research()
    build_teaching()
    build_wie()
    build_cv()
    build_404()
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    print("built")
