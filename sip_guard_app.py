"""
SIP Guard — concept prototype of a predictive AutoPay-failure defence inside a mutual-fund app.

Run:  pip install "streamlit>=1.39"  &&  streamlit run sip_guard_app.py

NextLeap PM capstone prototype. Not affiliated with or endorsed by Groww. The investor, portfolio, fund names,
NAVs, returns, model weights and backtest figures are all illustrative. Evidence figures (680 public reviews,
₹295–885 bounce charges) come from the SIP Discovery Engine and public bank-charge reporting.
"""
from __future__ import annotations

import html
import re

import streamlit as st

st.set_page_config(page_title="SIP Guard · Concept prototype", page_icon="🛡️", layout="wide")

# ----------------------------------------------------------------------------------------------------------------
# Design tokens
# ----------------------------------------------------------------------------------------------------------------
MINT, MINT_DK, NAVY, WHITE, CANVAS, BORDER, CORAL = "#00D09C", "#00B386", "#0F172A", "#FFFFFF", "#F8FAFC", "#ECEFF2", "#EF4444"
INK, BODY, META = "#0F172A", "#44475B", "#7C7E8C"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, .stApp, .stApp *:not([data-testid="stIconMaterial"]):not(.material-symbols-rounded) {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }}
.stApp {{ background: {CANVAS}; }}
#MainMenu, footer {{ visibility: hidden; }}
[data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stToolbar"] {{ display: none; }}
.block-container {{ padding-top: 0.8rem; padding-bottom: 2rem; max-width: 1240px; }}

/* nav */
.nav {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; background: {WHITE};
  border: 1px solid {BORDER}; border-radius: 14px; padding: 10px 18px; }}
.nav .l {{ display: flex; align-items: center; gap: 22px; min-width: 0; }}
.brand {{ display: flex; align-items: center; gap: 8px; font-weight: 700; color: {INK}; font-size: 16px; white-space: nowrap; }}
.brand i {{ width: 26px; height: 26px; border-radius: 50%; background: {MINT}; display: inline-block; }}
.tabs {{ display: flex; gap: 18px; font-size: 14px; font-weight: 500; color: {META}; white-space: nowrap; }}
.tabs .on {{ color: {INK}; font-weight: 600; border-bottom: 2px solid {MINT}; padding-bottom: 3px; }}
.nav .r {{ display: flex; align-items: center; gap: 16px; }}
.ico {{ position: relative; display: inline-flex; color: {INK}; }}
.dot {{ position: absolute; top: -1px; right: -1px; width: 8px; height: 8px; background: {CORAL}; border-radius: 50%;
  border: 2px solid {WHITE}; }}
.avatar {{ width: 32px; height: 32px; border-radius: 50%; background: #E6FAF5; color: #00805F; font-weight: 700;
  display: inline-flex; align-items: center; justify-content: center; font-size: 14px; }}
@media (max-width: 760px) {{ .tabs {{ display: none; }} }}

/* greeting + summary */
.hi h2 {{ margin: 18px 0 2px 0; color: {INK}; font-size: 24px; font-weight: 700; letter-spacing: -0.01em; }}
.hi p {{ margin: 0; color: {BODY}; font-size: 14px; }}
.sum {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); background: {WHITE}; border: 1px solid {BORDER};
  border-radius: 16px; margin: 14px 0 18px 0; box-shadow: 0 1px 3px rgba(0,0,0,.04); }}
.sum > div {{ padding: 14px 18px; border-right: 1px solid {BORDER}; min-width: 0; }}
.sum > div:last-child {{ border-right: 0; }}
.sum .k {{ font-size: 12.5px; color: {META}; }}
.sum .v {{ font-size: 20px; font-weight: 700; color: {INK}; margin-top: 2px; letter-spacing: -0.01em; }}
.up {{ color: #00A57D; }} .down {{ color: {CORAL}; }}
@media (max-width: 760px) {{ .sum {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .sum > div:nth-child(2) {{ border-right: 0; }} .sum > div:nth-child(-n+2) {{ border-bottom: 1px solid {BORDER}; }} }}

/* cards */
.card {{ background: {WHITE}; border: 1px solid {BORDER}; border-radius: 16px; padding: 16px 18px; margin-bottom: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,.04), 0 2px 6px -1px rgba(0,0,0,.02); }}
.card h3 {{ margin: 0 0 2px 0; font-size: 16px; color: {INK}; font-weight: 700; }}
.sub {{ font-size: 12.5px; color: {META}; line-height: 1.5; }}
.pill {{ display: inline-flex; align-items: center; gap: 4px; border-radius: 9999px; padding: 3px 9px; font-size: 11.5px;
  font-weight: 600; white-space: nowrap; }}
.p-mint {{ color: #00805F; background: #E6FAF5; }} .p-coral {{ color: #C62828; background: #FEE2E2; }}
.p-amber {{ color: #B45309; background: #FEF3C7; }} .p-grey {{ color: {BODY}; background: #F1F5F9; }}
.p-blue {{ color: #1D4ED8; background: #DBEAFE; }}

/* fund rows */
.fund {{ display: grid; grid-template-columns: minmax(0, 1.7fr) 96px minmax(0, 0.9fr) minmax(0, 0.9fr); gap: 12px;
  align-items: center; padding: 14px 0; border-top: 1px solid {BORDER}; }}
.fund:first-of-type {{ border-top: 0; }}
.fund .nm {{ font-size: 14.5px; font-weight: 600; color: {INK}; }}
.fund .tags {{ font-size: 12px; color: {META}; margin-top: 3px; }}
.fund .num {{ font-size: 14px; font-weight: 600; color: {INK}; text-align: right; }}
.fund .lab {{ font-size: 11.5px; color: {META}; text-align: right; }}
@media (max-width: 640px) {{ .fund {{ grid-template-columns: minmax(0, 1fr) 80px; }} .fund .hide-sm {{ display: none; }} }}

/* alert */
.alert {{ border: 1px solid #FECACA; background: #FFF5F5; border-radius: 14px; padding: 14px 16px; }}
.alert .t {{ font-size: 15px; font-weight: 700; color: #B91C1C; }}
.alert .b {{ font-size: 13.5px; color: {INK}; margin-top: 6px; line-height: 1.55; }}
.ok {{ border: 1px solid #A7F3D0; background: #ECFDF5; border-radius: 14px; padding: 14px 16px; font-size: 13.5px;
  color: #065F46; line-height: 1.55; }}
.info {{ border: 1px solid {BORDER}; background: {CANVAS}; border-radius: 14px; padding: 14px 16px; font-size: 13.5px;
  color: {INK}; line-height: 1.55; }}
.fail {{ border: 1px solid #FECACA; background: #FEE2E2; border-radius: 14px; padding: 14px 16px; font-size: 13.5px;
  color: #7F1D1D; line-height: 1.55; }}
.debit {{ display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 12px; }}
.debit .amt {{ font-size: 22px; font-weight: 700; color: {INK}; }}

/* tracker */
.track {{ display: flex; align-items: center; gap: 0; margin: 14px 0 4px 0; }}
.track .s {{ display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 0 0 auto; font-size: 12px;
  font-weight: 600; color: {META}; }}
.track .c {{ width: 22px; height: 22px; border-radius: 50%; border: 2px solid #CBD5E1; background: {WHITE};
  display: inline-flex; align-items: center; justify-content: center; font-size: 12px; color: {WHITE}; }}
.track .s.done .c {{ background: {MINT}; border-color: {MINT}; }} .track .s.done {{ color: {INK}; }}
.track .s.bad .c {{ background: {CORAL}; border-color: {CORAL}; }} .track .s.bad {{ color: #B91C1C; }}
.track .ln {{ flex: 1 1 auto; height: 2px; background: #E2E8F0; margin: 0 6px 18px 6px; }}
.track .ln.done {{ background: {MINT}; }}

/* buttons */
.stButton button {{ border-radius: 8px; font-weight: 600; min-height: 44px; transition: all .2s cubic-bezier(.4,0,.2,1); }}
.stButton button[kind="primary"] {{ background: {MINT}; border: 0; color: {WHITE}; }}
.stButton button[kind="primary"]:hover {{ background: {MINT_DK}; color: {WHITE}; }}
.stButton button[kind="secondary"] {{ background: {WHITE}; border: 1px solid #E2E8F0; color: {BODY}; }}
.stButton button[kind="secondary"]:hover {{ border-color: {MINT}; color: #00805F; background: #F6FFFC; }}

/* upcoming-debit card (keyed container, so real buttons sit inside it) */
.st-key-debit_card {{ background: {WHITE}; border: 1px solid {BORDER}; border-radius: 16px; padding: 16px 18px;
  margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,.04), 0 2px 6px -1px rgba(0,0,0,.02); }}

/* evaluator panel */
.st-key-evaluator {{ background: {WHITE}; border: 1px dashed #94A3B8; border-radius: 16px; padding: 14px 16px; }}
.tele {{ display: grid; grid-template-columns: minmax(0, 1fr) 64px; gap: 8px; padding: 8px 0; border-bottom: 1px solid #F1F5F9;
  font-size: 13px; color: {INK}; align-items: center; }}
.tele .bar {{ grid-column: 1 / -1; height: 6px; background: #F1F5F9; border-radius: 9999px; position: relative; margin-top: -2px; }}
.tele .bar span {{ position: absolute; left: 0; top: 0; bottom: 0; border-radius: 9999px; background: {CORAL}; }}
.tele .v {{ text-align: right; font-weight: 600; }}
.prob {{ display: flex; align-items: baseline; gap: 10px; margin: 12px 0 4px 0; }}
.prob b {{ font-size: 32px; color: {INK}; letter-spacing: -0.02em; }}
.gate {{ display: flex; justify-content: space-between; gap: 10px; padding: 9px 0; border-bottom: 1px solid #F1F5F9; }}
.gate .t {{ font-size: 13px; font-weight: 600; color: {INK}; }} .gate .d {{ font-size: 12px; color: {META}; margin-top: 2px; }}
.note {{ font-size: 11.5px; color: {META}; border-top: 1px solid {BORDER}; padding-top: 10px; margin-top: 20px; }}
</style>
""", unsafe_allow_html=True)

esc = lambda x: html.escape(str(x), quote=True)  # noqa: E731


def keyed(key: str):
    try:
        return st.container(key=key)
    except TypeError:  # Streamlit < 1.39
        return st.container()


def inr(x: float) -> str:
    """Indian digit grouping: 124380 -> 1,24,380."""
    s = f"{abs(int(round(x))):d}"
    head, tail = s[:-3], s[-3:]
    while len(head) > 2:
        tail = head[-2:] + "," + tail
        head = head[:-2]
    out = (head + "," + tail) if head else tail
    return ("-" if x < 0 else "") + "₹" + out


def sparkline(points: list[float], w: int = 96, h: int = 34) -> str:
    lo, hi = min(points), max(points)
    xs = [i * w / (len(points) - 1) for i in range(len(points))]
    ys = [h - 3 - (p - lo) / (hi - lo or 1) * (h - 6) for p in points]
    path = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(zip(xs, ys)))
    area = path + f" L{w},{h} L0,{h} Z"
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true">'
            f'<path d="{area}" fill="{MINT}" fill-opacity="0.12"/><path d="{path}" fill="none" stroke="{MINT}" '
            f'stroke-width="2" stroke-linejoin="round"/></svg>')


# ----------------------------------------------------------------------------------------------------------------
# Illustrative account (fictional numbers; the 5 Nov debits are what SIP Guard protects)
# ----------------------------------------------------------------------------------------------------------------
USER = "Ritu"
BANK = "HDFC Bank ••4821"
DEBIT_DATE, NEXT_DATE = "5 Nov", "5 Dec"
FUNDS = [
    {"name": "Hybrid Equity Fund", "tags": "Medium risk · Hybrid · Large Cap", "sip": 2500, "ret3y": 16.32,
     "series": [10, 10.4, 10.2, 10.9, 11.3, 11.1, 11.8, 12.4, 12.2, 12.9, 13.5, 13.9]},
    {"name": "Nifty 50 Index Fund", "tags": "Very high risk · Equity · Index", "sip": 1500, "ret3y": 13.85,
     "series": [10, 10.6, 10.1, 10.8, 11.6, 11.2, 12.0, 11.7, 12.6, 13.1, 12.8, 13.6]},
    {"name": "Flexi Cap Fund", "tags": "Very high risk · Equity · Flexi Cap", "sip": 1000, "ret3y": 18.04,
     "series": [10, 10.3, 10.9, 10.7, 11.5, 12.1, 11.8, 12.7, 13.4, 13.0, 14.1, 14.6]},
]
DUE = sum(f["sip"] for f in FUNDS)
INVESTED, CURRENT = 108000, 124380
DAY_PCT = 0.55

# Evaluator scenarios: the model's output for this account. Contributions are shown on a simple additive
# probability scale so evaluators can read them; a production model would be a calibrated classifier.
SCENARIOS = {
    "high": {"label": "High risk (87%)", "factors": [
        ("Historical failure rate on this mandate", 34), ("3 SIPs stacked on the same date", 22),
        ("Salary usually credited after the debit date", 19), ("Start-of-month clearing pattern", 12)]},
    "unsure": {"label": "Inconclusive (54%)", "factors": [
        ("Historical failure rate on this mandate", 18), ("3 SIPs stacked on the same date", 22),
        ("Salary usually credited after the debit date", 0), ("Start-of-month clearing pattern", 14)]},
    "low": {"label": "Low risk (9%)", "factors": [
        ("Historical failure rate on this mandate", 3), ("3 SIPs stacked on the same date", 6),
        ("Salary usually credited after the debit date", 0), ("Start-of-month clearing pattern", 0)]},
}
ALERT_AT, FALLBACK_AT = 70, 40   # ≥70: T-3 SIP Guard alert · 40–69: inconclusive → standard T-1 reminder · <40: silent

# Pre-approved copy. The app only fills slots; nothing is generated at runtime.
TEMPLATES = {
    "alert_t": {"ok": True, "text": "⚡ SIP Guard Alert: Auto-debit at high risk of bounce"},
    "alert_b": {"ok": True, "text": "Your upcoming {amt} debit on {date} ({n} SIPs, {bank} mandate) may fail: in recent "
                                    "months your balance was low around this date. Avoid a ₹295–₹885 bank bounce "
                                    "charge per SIP."},
    "fallback": {"ok": True, "text": "Reminder: {amt} will be debited from {bank} on {date}. Please keep enough "
                                     "balance."},
    "o_pay": {"ok": True, "text": "⚡ Skip & Pay via UPI Now"},
    "o_skip": {"ok": True, "text": "⏸️ Skip This Month Safely"},
    "o_shift": {"ok": True, "text": "📅 Shift SIP Date to 8th"},
    "o_keep": {"ok": True, "text": "✅ Keep Debit (I'll maintain balance)"},
    "recovery": {"ok": True, "text": "Your {date} debit didn't go through. We will not retry it automatically, so your "
                                     "bank won't charge you twice."},
    "rogue": {"ok": False, "text": "Markets are rallying! Don't miss out: top up your best fund now for guaranteed "
                                   "returns."},
}
ADVICE = re.compile(r"\b(guarantee\w*|best fund|recommend\w*|buy|sell|don'?t miss|rally\w*|top up your|"
                    r"switch to|outperform\w*)\b", re.I)


def t(key: str, **kw) -> str:
    return TEMPLATES[key]["text"].format(**kw)


# ----------------------------------------------------------------------------------------------------------------
# State
# ----------------------------------------------------------------------------------------------------------------
ss = st.session_state
ss.setdefault("choice", None)        # skip_pay | skip | shift | keep
ss.setdefault("t0", None)            # None | not_presented | success | failed
ss.setdefault("paid_after", False)
ss.setdefault("balance_added", False)
ss.setdefault("flag_on", True)
ss.setdefault("eval_mode", False)
ss.setdefault("scenario", "high")
ss.setdefault("rogue", False)


def reset() -> None:
    ss.choice, ss.t0, ss.paid_after, ss.balance_added = None, None, False, False


def choose(c: str) -> None:
    ss.choice = c
    st.toast({"skip_pay": f"{inr(DUE)} paid via UPI · {DEBIT_DATE} debit won't be presented ✅",
              "skip": f"November instalments skipped · no bank charge · SIPs stay active ⏸️",
              "shift": "From December, your SIPs debit on the 8th 📅",
              "keep": f"Debit kept · we'll remind you on 4 Nov ✅"}[c])


def simulate_debit_day() -> None:
    if ss.choice in ("skip_pay", "skip"):
        ss.t0 = "not_presented"
    elif ss.choice == "keep" and ss.balance_added:
        ss.t0 = "success"
    else:
        ss.t0 = "failed" if ss.scenario == "high" else "success"


def pay_after_failure() -> None:
    ss.paid_after = True
    st.toast(f"{inr(DUE)} paid via UPI · units at the NAV of the payment date ✅")


# ----------------------------------------------------------------------------------------------------------------
# Model output + gates (computed first: they decide what the investor is allowed to see)
# ----------------------------------------------------------------------------------------------------------------
sc = SCENARIOS[ss.scenario]
prob = sum(v for _, v in sc["factors"])
band = "high" if prob >= ALERT_AT else ("unsure" if prob >= FALLBACK_AT else "low")

shown = []
if ss.flag_on and band == "high" and ss.t0 is None and not ss.choice:
    shown += ["alert_t", "alert_b", "o_pay", "o_skip", "o_shift", "o_keep"]
    if ss.rogue:
        shown.append("rogue")
if ss.flag_on and ss.t0 == "failed":
    shown.append("recovery")
on_screen = " ".join(TEMPLATES[k]["text"] for k in shown)
unapproved = [k for k in shown if not TEMPLATES[k]["ok"]]
advice_hits = sorted({m.group(0) for m in ADVICE.finditer(on_screen)})
gates = [
    ("Gate 1 · Precision check (≥ 60%)", True, "64.2% of alerts were real failures on a simulated 12-month backtest."),
    ("Gate 2 · Non-advisory guardrail", not advice_hits,
     "0 fund recommendations or market claims on screen." if not advice_hits
     else "Blocked: " + ", ".join(f"“{h}”" for h in advice_hits)),
    ("Gate 3 · Template compliance", not unapproved,
     "100% pre-approved copy; slots only, no free text." if not unapproved
     else f"Blocked: {len(unapproved)} unapproved message(s)."),
    ("Gate 4 · Safe fallback", True,
     "Inconclusive score: showing the standard T-1 reminder instead." if band == "unsure"
     else "Scores of 40–69% fall back to the standard T-1 reminder."),
]
gates_ok = all(ok for _, ok, _ in gates)
guard_on = ss.flag_on and band == "high" and gates_ok

# ----------------------------------------------------------------------------------------------------------------
# Top nav + greeting
# ----------------------------------------------------------------------------------------------------------------
SEARCH = ('<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5" fill="none" '
          'stroke="currentColor" stroke-width="2"/><path d="M16 16l4.5 4.5" stroke="currentColor" stroke-width="2" '
          'stroke-linecap="round"/></svg>')
BELL = ('<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 16V11a6 6 0 1 1 12 0v5l1.5 2h-15z'
        'M10 20a2 2 0 0 0 4 0" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>')
st.markdown(
    f'<div class="nav"><div class="l"><span class="brand"><i></i>Invest</span>'
    f'<span class="tabs"><span>Stocks</span><span class="on">Mutual Funds</span><span>SIPs</span><span>UPI</span></span>'
    f'</div><div class="r"><span class="ico">{SEARCH}</span><span class="ico">{BELL}'
    f'{"<span class=dot></span>" if guard_on and not ss.choice else ""}</span>'
    f'<span class="avatar">{USER[0]}</span></div></div>', unsafe_allow_html=True)

g_l, g_r = st.columns([3, 1.3], vertical_alignment="bottom")
with g_l:
    st.markdown(f'<div class="hi"><h2>Hi, {USER} 👋</h2><p>Here is your SIP portfolio and upcoming scheduled debits.'
                f'</p></div>', unsafe_allow_html=True)
with g_r:
    st.toggle("🔍 View AI Eval-Gate & Model Telemetry (Evaluator Mode)", key="eval_mode")

gain = CURRENT - INVESTED
st.markdown(
    f'<div class="sum"><div><div class="k">Total invested</div><div class="v">{inr(INVESTED)}</div></div>'
    f'<div><div class="k">Current value</div><div class="v">{inr(CURRENT)}</div></div>'
    f'<div><div class="k">1-day returns</div><div class="v up">+{inr(CURRENT * DAY_PCT / 100)} '
    f'<span style="font-size:14px">(+{DAY_PCT:.2f}%)</span></div></div>'
    f'<div><div class="k">Total returns</div><div class="v up">+{inr(gain)} '
    f'<span style="font-size:14px">(+{gain / INVESTED * 100:.2f}%)</span></div></div></div>',
    unsafe_allow_html=True)

main, side = st.columns([1.65, 1], gap="large")

# ----------------------------------------------------------------------------------------------------------------
# Upcoming debit + SIP Guard
# ----------------------------------------------------------------------------------------------------------------
def tracker(stages: list[tuple[str, str]]) -> str:
    """stages = [(label, 'done'|'bad'|'')]."""
    out = []
    for i, (label, s) in enumerate(stages):
        if i:
            out.append(f'<span class="ln {"done" if s in ("done", "bad") else ""}"></span>')
        mark = "✓" if s == "done" else ("!" if s == "bad" else "")
        out.append(f'<span class="s {s}"><span class="c">{mark}</span>{esc(label)}</span>')
    return '<div class="track">' + "".join(out) + "</div>"


@st.dialog("Pay this month's SIPs via UPI")
def upi_dialog() -> None:
    st.markdown(f'<div class="sub">This month\'s {DEBIT_DATE} auto-debit is skipped, so it is never presented to '
                f'{BANK}. You pay {inr(DUE)} now from any UPI app or bank account.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info" style="margin:12px 0"><b>{inr(DUE)}</b> · {len(FUNDS)} SIPs · units at the NAV '
                'of the payment date</div>', unsafe_allow_html=True)
    if st.button(f"Pay {inr(DUE)} via UPI", type="primary", use_container_width=True):
        choose("skip_pay")
        st.rerun()


with main:
    with keyed("debit_card"):
        st.markdown('<h3 style="margin:0;font-size:16px;color:#0F172A">Upcoming debit</h3>', unsafe_allow_html=True)
        pill = ('<span class="pill p-coral">High bounce risk</span>' if guard_on and not ss.choice and ss.t0 is None
                else '<span class="pill p-mint">Guard protected</span>' if ss.choice and ss.t0 is None and ss.flag_on
                else '<span class="pill p-grey">Scheduled</span>' if ss.t0 is None
                else '<span class="pill p-coral">Debit failed</span>' if ss.t0 == "failed" and not ss.paid_after
                else '<span class="pill p-mint">Done</span>')
        st.markdown(f'<div class="debit"><div><div class="amt">{inr(DUE)}</div><div class="sub">{len(FUNDS)} SIPs · '
                    f'{DEBIT_DATE} · AutoPay mandate on {BANK}</div></div>{pill}</div>', unsafe_allow_html=True)

        # ---- before debit day ----
        if ss.t0 is None:
            if guard_on and not ss.choice:
                st.markdown(f'<div class="alert"><div class="t">{esc(t("alert_t"))}</div><div class="b">'
                            f'{esc(t("alert_b", amt=inr(DUE), date=DEBIT_DATE, n=len(FUNDS), bank=BANK))}</div></div>',
                            unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(t("o_pay"), type="primary", use_container_width=True, key="o_pay"):
                        upi_dialog()
                    st.button(t("o_shift"), use_container_width=True, key="o_shift", on_click=choose, args=("shift",))
                with c2:
                    st.button(t("o_skip"), use_container_width=True, key="o_skip", on_click=choose, args=("skip",))
                    st.button(t("o_keep"), use_container_width=True, key="o_keep", on_click=choose, args=("keep",))
                st.markdown('<div class="sub">Skip and Pay are penalty-free because the debit is never presented to '
                            'your bank. Cancel stays available in SIP settings.</div>', unsafe_allow_html=True)
                st.markdown(tracker([("Notified", "done"), ("Scheduled", ""), ("Guard Protected", "")]),
                            unsafe_allow_html=True)
            elif ss.choice and ss.flag_on:
                msg = {"skip_pay": f"<b>Paid {inr(DUE)} via UPI.</b> The {DEBIT_DATE} auto-debit won't be presented "
                                   f"to your bank, so there's no duplicate debit and no bounce charge.",
                       "skip": f"<b>Skipped for November.</b> The {DEBIT_DATE} debit won't be presented to your bank: "
                               f"no bounce charge. Your SIPs stay active; next debit {NEXT_DATE}.",
                       "shift": f"<b>Date moved.</b> From December your SIPs debit on the 8th, after salary credit. "
                                f"The {DEBIT_DATE} debit is still scheduled; we'll remind you on 4 Nov.",
                       "keep": f"<b>Debit kept.</b> We'll remind you on 4 Nov (T-1) to keep {inr(DUE)} in "
                               f"{BANK}."}[ss.choice]
                st.markdown(f'<div class="ok">{msg}</div>', unsafe_allow_html=True)
                if ss.choice in ("shift", "keep"):
                    ss.balance_added = st.checkbox(f"I've added {inr(DUE)} to my bank account",
                                                   value=ss.balance_added, key="bal_chk")
                st.markdown(tracker([("Notified", "done"), ("Scheduled", "done"), ("Guard Protected", "done")]),
                            unsafe_allow_html=True)
            elif ss.flag_on and band == "unsure":
                st.markdown(f'<div class="info">🔔 {esc(t("fallback", amt=inr(DUE), bank=BANK, date=DEBIT_DATE))}'
                            '</div>', unsafe_allow_html=True)
            elif ss.flag_on and band == "high" and not gates_ok:
                st.markdown(f'<div class="info">🔔 {esc(t("fallback", amt=inr(DUE), bank=BANK, date=DEBIT_DATE))}'
                            '<div class="sub" style="margin-top:6px">An eval gate failed, so SIP Guard fell back to '
                            'the standard reminder.</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="info">Auto-debit scheduled for {DEBIT_DATE}. No action needed.</div>',
                            unsafe_allow_html=True)
            st.button(f"⏩ Simulate debit day ({DEBIT_DATE})", use_container_width=True, on_click=simulate_debit_day,
                      key="sim_t0")

        # ---- debit day ----
        else:
            if ss.t0 == "not_presented":
                st.markdown(f'<div class="ok">✓ No debit presented to {BANK} on {DEBIT_DATE}. '
                            + (f"{inr(DUE)} invested via UPI." if ss.choice == "skip_pay" else
                               f"Instalments skipped; next debit {NEXT_DATE}.")
                            + ' No bounce charge.</div>', unsafe_allow_html=True)
                st.markdown(tracker([("Notified", "done"), ("Scheduled", "done"), ("Guard Protected", "done")]),
                            unsafe_allow_html=True)
            elif ss.t0 == "success" or ss.paid_after:
                st.markdown(f'<div class="ok">✓ {inr(DUE)} '
                            + ("paid via UPI after the failed debit." if ss.paid_after else f"debited from {BANK}.")
                            + ' Units are being allotted.</div>', unsafe_allow_html=True)
                st.markdown(tracker([("Scheduled", "done"), ("Debited", "done"), ("Units allotted", "done")]),
                            unsafe_allow_html=True)
            elif not ss.flag_on or not gates_ok:
                st.markdown('<div class="fail"><b>SIP instalment failed.</b> Status: Failed.</div>'
                            '<div class="sub" style="margin-top:6px">Without SIP Guard: no warning beforehand and '
                            'no explanation after. Your bank may charge ₹295–885 per SIP, and three misses in a row '
                            'cancel a SIP.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="fail">{esc(t("recovery", date=DEBIT_DATE))}</div>', unsafe_allow_html=True)
                st.button(f"Pay {inr(DUE)} via UPI to invest this month", type="primary", use_container_width=True,
                          on_click=pay_after_failure, key="pay_after")
                with st.expander("Why did this happen?"):
                    st.write("Insufficient balance in your bank account when the debit was processed.")
                st.markdown(tracker([("Scheduled", "done"), ("Debit failed", "bad"), ("No auto-retry", "done")]),
                            unsafe_allow_html=True)
            st.button("↺ Replay from T-3", use_container_width=True, on_click=reset, key="replay")

    # ---- SIP list ----
    rows = []
    for f in FUNDS:
        rows.append(
            f'<div class="fund"><div><div class="nm">{esc(f["name"])}</div><div class="tags">{esc(f["tags"])}</div>'
            f'</div><div>{sparkline(f["series"])}</div>'
            f'<div class="hide-sm"><div class="num up">{f["ret3y"]:.2f}%</div><div class="lab">3Y annualised</div></div>'
            f'<div><div class="num">{inr(f["sip"])}</div><div class="lab">SIP · '
            f'{DEBIT_DATE if ss.choice not in ("shift",) else "5 Nov, then 8th"}</div></div></div>')
    st.markdown(f'<div class="card"><h3>Your SIPs</h3><div class="sub">{len(FUNDS)} active · '
                f'{inr(DUE)} per month</div>{"".join(rows)}</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------------------------------------------
# Side: mandate card, or the evaluator panel
# ----------------------------------------------------------------------------------------------------------------
with side:
    if not ss.eval_mode:
        st.markdown(
            f'<div class="card"><h3>AutoPay mandate</h3><div class="sub">{BANK} · active</div>'
            f'<div style="margin-top:10px;font-size:13.5px;color:{BODY};line-height:1.7">'
            f'Max per debit: ₹10,000<br>SIPs on this mandate: {len(FUNDS)}<br>Next debit: {DEBIT_DATE}</div></div>'
            f'<div class="card"><h3>🛡️ SIP Guard</h3><div class="sub">Checks every upcoming debit three days early. '
            f'If one looks likely to fail, you get one alert and a one-tap fix before your bank can charge you. '
            f'It never suggests funds or amounts.</div><div style="margin-top:10px">'
            f'<span class="pill {"p-mint" if ss.flag_on else "p-grey"}">{"On" if ss.flag_on else "Off"}</span>'
            f'</div></div>', unsafe_allow_html=True)
    else:
        with keyed("evaluator"):
            st.markdown('<h3 style="margin:0;font-size:16px">Evaluator mode</h3><div class="sub">Why this is '
                        'AI-native and fails safe. All model figures are simulated.</div>', unsafe_allow_html=True)
            st.toggle("Feature flag: SIP Guard enabled", key="flag_on")
            st.radio("Model output for this account", list(SCENARIOS), key="scenario", horizontal=True,
                     format_func=lambda k: SCENARIOS[k]["label"], on_change=reset)

            tele = "".join(f'<div class="tele"><span>{esc(n)}</span><span class="v">+{v}%</span>'
                           f'<div class="bar"><span style="width:{v / 40 * 100:.0f}%"></span></div></div>'
                           for n, v in sc["factors"])
            verdict = ("p-coral", "HIGH RISK · T-3 alert") if band == "high" else (
                ("p-amber", "INCONCLUSIVE · T-1 reminder") if band == "unsure" else ("p-mint", "LOW RISK · silent"))
            st.markdown(f'<div style="margin-top:6px"><div class="sub" style="font-weight:600;color:{INK}">Feature '
                        f'input telemetry</div>{tele}<div class="prob"><b>{prob}%</b><span class="sub">total failure '
                        f'probability</span></div><span class="pill {verdict[0]}">{verdict[1]}</span>'
                        f'<div class="sub" style="margin-top:6px">Thresholds: ≥ {ALERT_AT}% alert · '
                        f'{FALLBACK_AT}–{ALERT_AT - 1}% standard reminder · below {FALLBACK_AT}% silent.</div></div>',
                        unsafe_allow_html=True)

            gate_html = "".join(f'<div class="gate"><div><div class="t">{esc(n)}</div><div class="d">{esc(d)}</div>'
                                f'</div><span class="pill {"p-mint" if ok else "p-coral"}">{"PASSED" if ok else "FAILED"}'
                                f'</span></div>' for n, ok, d in gates)
            st.markdown(f'<div style="margin-top:14px"><div class="sub" style="font-weight:600;color:{INK}">Eval '
                        f'gates</div>{gate_html}</div>', unsafe_allow_html=True)
            st.toggle("Demo: inject an unapproved marketing message", key="rogue")
            st.markdown('<div class="sub" style="margin-top:8px">Data: the mandate\'s own debit history; bank balance '
                        'only with Account Aggregator consent; never SMS. Built for DPDP notice and purpose limits and '
                        'SEBI\'s expected AI rules on accountability, oversight and kill switches.</div>',
                        unsafe_allow_html=True)

st.markdown('<div class="note">Concept prototype for a NextLeap product-management capstone. Not affiliated with '
            'or endorsed by Groww. The investor, portfolio, fund names, NAVs, returns and model figures are '
            'illustrative. Bank bounce charges: ₹250–750 + 18% GST per failed debit, per public reporting.</div>',
            unsafe_allow_html=True)
