"""
🛡️ Groww SIP Guard: AI-Powered AutoPay Failure Defense — interactive prototype.

Run:  pip install "streamlit>=1.39"  &&  streamlit run sip_guard_app.py

Everything below is a SIMULATION for a product prototype. Investor profiles, model weights, backtest and
fairness figures are illustrative, not Groww data. Evidence numbers in the header come from the Groww SIP
Discovery Engine (680 public reviews) and public bank-charge reporting.
"""
from __future__ import annotations

import html
import math
import re

import streamlit as st

st.set_page_config(page_title="Groww SIP Guard · Prototype", page_icon="🛡️", layout="wide")

# ---------------------------------------------------------------------------------------------------------------
# Design tokens + CSS
# ---------------------------------------------------------------------------------------------------------------
MINT, NAVY, SLATE, RED, CANVAS = "#00D09C", "#0F172A", "#475569", "#EF4444", "#F8FAFC"

st.markdown(f"""
<style>
.stApp {{ background: {CANVAS}; }}
.block-container {{ padding-top: 1.4rem; max-width: 1380px; }}
.sg-hero h1 {{ color: {NAVY}; font-size: 1.75rem; margin: 0; letter-spacing: -0.01em; }}
.sg-hero p {{ color: {SLATE}; margin: 4px 0 0 0; font-size: 0.95rem; }}
.sg-tag {{ display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
          color: #00805F; background: #ECFDF5; border-radius: 12px; padding: 3px 10px; margin-bottom: 6px; }}
.sg-sim {{ display: inline-block; font-size: 11px; font-weight: 700; color: #92400E; background: #FEF3C7;
          border-radius: 12px; padding: 3px 10px; margin-left: 6px; }}
.sg-strip {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 14px 0 18px 0; }}
.sg-stat {{ background: #fff; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 14px;
           box-shadow: 0 1px 3px rgba(15,23,42,.04); }}
.sg-stat b {{ display: block; color: {NAVY}; font-size: 1.35rem; line-height: 1.2; }}
.sg-stat span {{ color: {SLATE}; font-size: 12px; }}
@media (max-width: 900px) {{ .sg-strip {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}

.sg-card {{ background: #fff; border: 1px solid #E2E8F0; border-radius: 14px; padding: 14px 16px;
           box-shadow: 0 1px 3px rgba(15,23,42,.04), 0 4px 12px rgba(15,23,42,.02); margin-bottom: 12px; }}
.sg-card h4 {{ margin: 0 0 6px 0; color: {NAVY}; font-size: 1rem; }}
.sg-muted {{ color: {SLATE}; font-size: 12.5px; line-height: 1.45; }}
.sg-pill {{ display: inline-block; font-size: 11px; font-weight: 700; border-radius: 12px; padding: 2px 9px; white-space: nowrap; }}
.sg-pill.ok {{ color: #027A48; background: #ECFDF3; }}
.sg-pill.bad {{ color: #B42318; background: #FEE2E2; }}
.sg-pill.warn {{ color: #92400E; background: #FEF3C7; }}
.sg-pill.info {{ color: #1D4ED8; background: #DBEAFE; }}
.sg-pill.mute {{ color: {SLATE}; background: #F1F5F9; }}

/* Phone frame: the keyed container becomes the device, so real Streamlit buttons live inside it */
.st-key-phone {{ max-width: 420px; margin: 0 auto; border-radius: 28px; box-shadow: 0 12px 36px rgba(0,0,0,0.1);
                border: 4px solid #1E293B; background: #FFFFFF; padding: 14px 16px 18px 16px; }}
.st-key-phone [data-testid="stVerticalBlock"] {{ gap: 0.6rem; }}
.ph-status {{ display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; color: {NAVY};
             padding: 0 4px 8px 4px; border-bottom: 1px solid #F1F5F9; }}
.ph-title {{ font-size: 15px; font-weight: 700; color: {NAVY}; margin: 2px 0 0 0; }}
.ph-sip {{ border: 1px solid #E2E8F0; border-radius: 12px; padding: 10px 12px; display: flex;
          justify-content: space-between; align-items: center; gap: 8px; }}
.ph-sip .nm {{ font-size: 13px; font-weight: 600; color: {NAVY}; }}
.ph-sip .sb {{ font-size: 11.5px; color: {SLATE}; }}
.ph-alert {{ border: 1px solid #FCD34D; background: #FFFBEB; border-left: 4px solid #F59E0B; border-radius: 12px;
            padding: 10px 12px; font-size: 13px; color: {NAVY}; line-height: 1.45; }}
.ph-alert small {{ display: block; color: #92400E; margin-top: 4px; font-size: 12px; }}
.ph-ok {{ border: 1px solid #A7F3D0; background: #ECFDF5; border-left: 4px solid {MINT}; border-radius: 12px;
         padding: 10px 12px; font-size: 13px; color: #065F46; line-height: 1.45; }}
.ph-fail {{ border: 1px solid #FECACA; background: #FEF2F2; border-left: 4px solid {RED}; border-radius: 12px;
           padding: 10px 12px; font-size: 13px; color: #7F1D1D; line-height: 1.45; }}
.ph-neutral {{ border: 1px solid #E2E8F0; background: #F8FAFC; border-radius: 12px; padding: 10px 12px;
              font-size: 13px; color: {NAVY}; line-height: 1.45; }}
.ph-tl {{ font-size: 12.5px; color: {NAVY}; line-height: 1.9; }}
.ph-tl .d {{ color: {MINT}; font-weight: 700; }} .ph-tl .x {{ color: {RED}; font-weight: 700; }} .ph-tl .o {{ color: #94A3B8; }}
.st-key-phone .stButton button {{ border-radius: 999px; font-weight: 700; }}
.st-key-phone .stButton button[kind="primary"] {{ background: {MINT}; border-color: {MINT}; color: #fff; }}

.sg-steps {{ display: flex; gap: 6px; justify-content: center; margin: 0 0 10px 0; flex-wrap: wrap; }}
.sg-step {{ font-size: 11.5px; font-weight: 700; border-radius: 12px; padding: 3px 10px; background: #F1F5F9; color: {SLATE}; }}
.sg-step.on {{ background: {MINT}; color: #fff; }}

.sg-factor {{ display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr) 52px; gap: 8px; align-items: center;
             font-size: 12.5px; color: {NAVY}; padding: 5px 0; border-bottom: 1px solid #F1F5F9; }}
.sg-bar {{ position: relative; height: 8px; background: #F1F5F9; border-radius: 999px; }}
.sg-bar span {{ position: absolute; top: 0; bottom: 0; border-radius: 999px; }}
.sg-risk {{ display: flex; align-items: baseline; gap: 10px; margin-top: 10px; }}
.sg-risk b {{ font-size: 2rem; color: {NAVY}; line-height: 1; }}
.sg-gate {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; padding: 8px 0;
           border-bottom: 1px solid #F1F5F9; }}
.sg-gate .t {{ font-size: 13px; font-weight: 600; color: {NAVY}; }}
.sg-gate .d {{ font-size: 12px; color: {SLATE}; }}
.sg-persona {{ font-size: 12.5px; color: {SLATE}; line-height: 1.5; }}
.sg-persona b {{ color: {NAVY}; }}
.st-key-persona_pick label p {{ font-weight: 600; }}
</style>
""", unsafe_allow_html=True)


def keyed(key: str):
    """st.container(key=...) gives a .st-key-<key> CSS hook (Streamlit >= 1.39); plain container otherwise."""
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


esc = lambda x: html.escape(str(x), quote=True)  # noqa: E731

# ---------------------------------------------------------------------------------------------------------------
# Simulated investors (illustrative profiles grounded in review themes)
# ---------------------------------------------------------------------------------------------------------------
PERSONAS = {
    "priya": {
        "label": "Priya · salary delay",
        "who": "Priya, 27 · salaried analyst",
        "story": "Three ₹2,000 SIPs all debit on the 5th. Her salary usually lands on the 1st but slipped to the 7th "
                 "this month.",
        "sips": [("Flexi Cap Fund", 2000), ("Nifty 50 Index Fund", 2000), ("Mid Cap Fund", 2000)],
        "debit_date": "5 Nov", "bank": "Private bank", "charge": 590,
        "features": {"past_failures": 2, "sips_same_date": 3, "salary_after_debit": 1, "festive": 0, "psu_bank": 0},
        "aa": None,                      # no Account Aggregator consent
        "truly_short": True,             # what actually happens on debit day if nothing changes
    },
    "rahul": {
        "label": "Rahul · festive cash crunch",
        "who": "Rahul, 29 · salaried, first-time investor",
        "story": "Diwali spending drained his account. He wants one month of relief without breaking his SIP.",
        "sips": [("Large Cap Fund", 2000)],
        "debit_date": "5 Nov", "bank": "PSU bank", "charge": 295,
        "features": {"past_failures": 1, "sips_same_date": 1, "salary_after_debit": 0, "festive": 1, "psu_bank": 1},
        "aa": {"balance": 600},          # consented AA balance in ₹
        "truly_short": True,
    },
    "aman": {
        "label": "Aman · healthy balance (control)",
        "who": "Aman, 32 · salaried, steady saver",
        "story": "Plenty of balance and a clean debit history. SIP Guard should stay silent.",
        "sips": [("ELSS Tax Saver Fund", 2000), ("Index Fund", 2000)],
        "debit_date": "5 Nov", "bank": "Private bank", "charge": 590,
        "features": {"past_failures": 0, "sips_same_date": 2, "salary_after_debit": 0, "festive": 1, "psu_bank": 0},
        "aa": {"balance": 48000},
        "truly_short": False,
    },
}

# Transparent logistic model (illustrative weights)
INTERCEPT = -3.2
WEIGHTS = {
    "past_failures": (0.9, "Failed debits in the last 6 cycles", "per failure"),
    "sips_same_date": (0.45, "Other SIPs debiting the same day", "per extra SIP"),
    "salary_after_debit": (1.6, "Salary credit slipped past the debit date", "inferred from past debit timing"),
    "festive": (0.6, "Festive-season spending window", "calendar signal"),
    "psu_bank": (0.3, "Bank clearing pattern (PSU vs private)", "bank-level rate"),
}
ALERT_THRESHOLD = 0.5


def score(p: dict, overrides: dict | None = None) -> tuple[float, list[tuple[str, float, str]]]:
    """Returns (failure probability, [(factor label, contribution to log-odds, note)])."""
    f = dict(p["features"], **(overrides or {}))
    parts = []
    for key, (w, label, note) in WEIGHTS.items():
        x = f[key] - 1 if key == "sips_same_date" else f[key]
        parts.append((label, w * x, note))
    aa = p.get("aa")
    if aa is not None:
        due = sum(a for _, a in p["sips"])
        ratio = aa["balance"] / max(due, 1)
        aa_term = 2.2 if ratio < 1 else (-1.5 if ratio >= 3 else 0.0)
        parts.append(("Balance vs amount due (Account Aggregator, opt-in)", aa_term,
                      f"₹{aa['balance']:,} vs ₹{due:,} due"))
    z = INTERCEPT + sum(c for _, c, _ in parts)
    return 1 / (1 + math.exp(-z)), parts


# ---------------------------------------------------------------------------------------------------------------
# Compliance-approved templates: the only text the phone ever shows. Slots are filled; nothing is generated.
# ---------------------------------------------------------------------------------------------------------------
TEMPLATES = {
    "alert": {"approved": True,
              "text": "⚡ Heads-up: your {what} on {date} {verb} at high risk of failing."},
    "alert_charge": {"approved": True,
                     "text": "If a debit fails, your bank may charge ₹295–885 per SIP. Sort it now, penalty-free."},
    "opt_skip_pay": {"approved": True, "text": "Skip this month & pay via UPI now"},
    "opt_skip_pay_sub": {"approved": True, "text": "Invest this month from another bank account. No bank debit."},
    "opt_skip": {"approved": True, "text": "Skip this month safely"},
    "opt_skip_sub": {"approved": True,
                     "text": "This month's debit won't be presented to your bank, so no bounce charge. "
                             "Your SIP stays active."},
    "opt_shift": {"approved": True, "text": "Shift future SIP date to the 8th"},
    "opt_shift_sub": {"approved": True, "text": "From December, debits run after your salary lands. "
                                                "This month's debit still runs on {date}."},
    "opt_keep": {"approved": True, "text": "Keep debit as-is"},
    "opt_keep_sub": {"approved": True, "text": "I'll add funds before {date}."},
    "recovery": {"approved": True,
                 "text": "Debit didn't go through. We will NOT retry automatically, so you won't get charged twice "
                         "by your bank."},
    "recovery_why": {"approved": True, "text": "Insufficient balance at the time of bank clearing."},
    "unapproved_demo": {"approved": False,
                        "text": "Markets are rallying! Don't miss out — top up your best fund now for guaranteed returns."},
}
BANNED = re.compile(r"\b(guarantee\w*|best fund|recommend\w*|buy|sell|don'?t miss|hurry|last chance|rally\w*|"
                    r"returns? will|outperform\w*)\b", re.I)
FUND_ADVICE = re.compile(r"\b(top up your|switch to|invest more in|this fund will)\b", re.I)


def tpl(key: str, **slots) -> str:
    return TEMPLATES[key]["text"].format(**slots)


def gate_checks(shown_keys: list[str]) -> list[dict]:
    """The four eval gates. Gates 1–2 read the (simulated) backtest; gates 3–4 scan the exact templates on screen."""
    backtest_precision = 0.64
    bank_precision = {"Private bank A": 0.66, "Private bank B": 0.63, "PSU bank A": 0.61, "PSU bank B": 0.60,
                      "Small finance bank": 0.62}
    avg = sum(bank_precision.values()) / len(bank_precision)
    worst_gap = max(abs(v - avg) for v in bank_precision.values()) * 100
    unapproved = [k for k in shown_keys if not TEMPLATES[k]["approved"]]
    texts = " ".join(TEMPLATES[k]["text"] for k in shown_keys)
    advice_hits = sorted({m.group(0) for m in BANNED.finditer(texts)} | {m.group(0) for m in FUND_ADVICE.finditer(texts)})
    return [
        {"name": "Precision backtest gate (≥ 60%)", "ok": backtest_precision >= 0.60,
         "detail": f"{backtest_precision:.0%} of past alerts were real failures (simulated 12-month backtest)."},
        {"name": "Fairness across banks gate", "ok": worst_gap <= 10,
         "detail": f"Largest gap from average precision: {worst_gap:.1f} points across {len(bank_precision)} "
                   "bank groups (limit 10)."},
        {"name": "Compliance template gate", "ok": not unapproved,
         "detail": ("All on-screen messages are pre-approved templates; slots only, no free text."
                    if not unapproved else f"Blocked: {len(unapproved)} unapproved message(s) on screen.")},
        {"name": "Non-advisory guardrail", "ok": not advice_hits,
         "detail": ("Scan found 0 fund recommendations or market advice."
                    if not advice_hits else "Blocked: found " + ", ".join(f"“{h}”" for h in advice_hits) + ".")},
    ]


# ---------------------------------------------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------------------------------------------
def state(pid: str) -> dict:
    s = st.session_state.setdefault("sg_state", {})
    return s.setdefault(pid, {"stage": "home", "choice": None, "funds_added": False, "t0": None, "paid": False})


def reset(pid: str) -> None:
    st.session_state.setdefault("sg_state", {})[pid] = {"stage": "home", "choice": None, "funds_added": False,
                                                       "t0": None, "paid": False}


st.session_state.setdefault("flag_on", True)
st.session_state.setdefault("demo_unapproved", False)

# ---------------------------------------------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------------------------------------------
st.markdown(
    '<div class="sg-hero"><span class="sg-tag">Prototype · Eval-gated AI</span>'
    '<span class="sg-sim">Simulated data</span>'
    '<h1>🛡️ Groww SIP Guard: AI-Powered AutoPay Failure Defense</h1>'
    '<p>Predict a failing SIP debit three days early, fix it in one tap, and never retry into a second bank charge.</p>'
    '</div>'
    '<div class="sg-strip">'
    '<div class="sg-stat"><b>680</b><span>public reviews analysed (≈481 unique)</span></div>'
    '<div class="sg-stat"><b>35%</b><span>of themed reviews: Bank &amp; Auto-Debit Friction, the #1 driver</span></div>'
    '<div class="sg-stat"><b>&gt;5 : 1</b><span>operational friction vs complaints about returns</span></div>'
    '<div class="sg-stat"><b>₹295–885</b><span>bank charge per failed SIP debit (₹250–750 + GST)</span></div>'
    '</div>', unsafe_allow_html=True)

left, mid, right = st.columns([1.0, 1.25, 1.35], gap="large")

# ---------------------------------------------------------------------------------------------------------------
# Left: scenario switcher
# ---------------------------------------------------------------------------------------------------------------
with left:
    st.markdown('<div class="sg-card"><h4>1 · Pick an investor</h4>'
                '<div class="sg-muted">Each profile replays a pattern from the review data.</div></div>',
                unsafe_allow_html=True)
    with keyed("persona_pick"):
        pid = st.radio("Investor", list(PERSONAS), format_func=lambda k: PERSONAS[k]["label"],
                       key="persona", label_visibility="collapsed")
    P = PERSONAS[pid]
    S = state(pid)
    total_due = sum(a for _, a in P["sips"])
    st.markdown(
        f'<div class="sg-card sg-persona"><b>{esc(P["who"])}</b><br>{esc(P["story"])}<br><br>'
        f'<b>SIPs:</b> {len(P["sips"])} × ₹{P["sips"][0][1]:,} on {P["debit_date"]} (₹{total_due:,})<br>'
        f'<b>Bank:</b> {esc(P["bank"])} · ₹{P["charge"]:,} per failed debit incl. GST<br>'
        f'<b>If every debit bounces:</b> ₹{P["charge"] * len(P["sips"]):,} in charges<br>'
        f'<b>Balance data:</b> {"Account Aggregator consent given" if P["aa"] else "not shared (Groww data only)"}'
        f'</div>', unsafe_allow_html=True)
    st.button("↺ Reset this investor", on_click=reset, args=(pid,), use_container_width=True)
    with st.expander("What's real vs simulated"):
        st.markdown("- **Real:** the evidence strip (Discovery Engine, public bank-charge reporting), Groww's 2-day "
                    "skip cut-off, the no-retry rule.\n- **Simulated:** investors, model weights, backtest and "
                    "fairness figures. A pilot would replace them with Groww's debit logs.")

# ---------------------------------------------------------------------------------------------------------------
# Risk + gates (computed before drawing the phone, because they decide what the phone may show)
# ---------------------------------------------------------------------------------------------------------------
overrides = st.session_state.get(f"whatif_{pid}", {})
prob, parts = score(P, overrides)
high_risk = prob >= ALERT_THRESHOLD
flag_on = st.session_state["flag_on"]

shown = ["alert", "alert_charge"] if (flag_on and high_risk) else []
if flag_on and high_risk and st.session_state["demo_unapproved"]:
    shown.append("unapproved_demo")
if S["stage"] == "sheet":
    shown += ["opt_skip_pay", "opt_skip_pay_sub", "opt_skip", "opt_skip_sub", "opt_shift", "opt_shift_sub",
              "opt_keep", "opt_keep_sub"]
if S["t0"] == "failed" and flag_on:
    shown += ["recovery", "recovery_why"]
gates = gate_checks(shown)
gates_ok = all(g["ok"] for g in gates)
guard_active = flag_on and high_risk and gates_ok  # fail-safe: any failed gate suppresses SIP Guard's messages


def plural(n: int, one: str, many: str) -> str:
    return one if n == 1 else many


def debit_outcome() -> str:
    """What the bank does on debit day for this investor, given the choice they made."""
    c = S["choice"]
    if c in ("skip_pay", "skip"):
        return "not_presented"
    if c == "keep" and S["funds_added"]:
        return "success"
    return "failed" if P["truly_short"] else "success"


def go(stage: str) -> None:
    S["stage"] = stage


def choose(choice: str) -> None:
    S["choice"], S["stage"] = choice, "resolved"
    msgs = {"skip_pay": "Skipped this month · UPI payment received ✅", "skip": "This month skipped · no bank charge ✅",
            "shift": "Future debits move to the 8th from December 📅", "keep": "Got it · keep the debit as-is 👍"}
    st.toast(msgs[choice])


def run_debit_day() -> None:
    S["t0"] = debit_outcome()
    S["stage"] = "t0"


def pay_upi() -> None:
    S["paid"] = True
    st.toast(f"₹{total_due:,} paid via UPI · units will be allotted at the applicable NAV ✅")


# ---------------------------------------------------------------------------------------------------------------
# Middle: the phone
# ---------------------------------------------------------------------------------------------------------------
with mid:
    stage_names = [("predict", "1 Predict · T-3"), ("protect", "2 Protect"), ("recover", "3 Recover · T+0")]
    active = {"home": "predict", "sheet": "protect", "resolved": "protect", "t0": "recover"}[S["stage"]]
    st.markdown('<div class="sg-steps">' + "".join(
        f'<span class="sg-step{" on" if k == active else ""}">{v}</span>' for k, v in stage_names) + '</div>',
        unsafe_allow_html=True)

    with keyed("phone"):
        st.markdown('<div class="ph-status"><span>9:41</span><span>Groww</span><span>●●● 5G</span></div>'
                    '<div class="ph-title">My SIPs</div>', unsafe_allow_html=True)
        if S["stage"] == "t0" and S["t0"] == "failed" and not S["paid"]:
            sip_pill = '<span class="sg-pill bad">Debit failed</span>'
        elif S["stage"] == "t0" and S["t0"] == "not_presented":
            sip_pill = '<span class="sg-pill mute">Skipped</span>'
        elif guard_active and S["stage"] in ("home", "sheet"):
            sip_pill = '<span class="sg-pill warn">At risk</span>'
        else:
            sip_pill = '<span class="sg-pill ok">Active</span>'
        sip_rows = "".join(
            f'<div class="ph-sip"><div><div class="nm">{esc(n)}</div><div class="sb">₹{a:,} · next debit '
            f'{P["debit_date"]}</div></div>{sip_pill}</div>' for n, a in P["sips"])
        st.markdown(f'<div style="display:flex;flex-direction:column;gap:8px">{sip_rows}</div>',
                    unsafe_allow_html=True)

        n_sips = len(P["sips"])
        what = (f"₹{total_due:,} SIP debit" if n_sips == 1 else f"{n_sips} SIP debits (₹{total_due:,})")
        verb = plural(n_sips, "is", "are")

        # ---- T-3: early warning -------------------------------------------------------------------------------
        if S["stage"] == "home":
            if not flag_on:
                st.markdown('<div class="ph-neutral"><b>SIP Guard is switched off.</b><br>This is today\'s '
                            'experience: no early warning. The investor finds out after the debit fails.</div>',
                            unsafe_allow_html=True)
            elif high_risk and not gates_ok:
                st.markdown('<div class="ph-neutral"><b>Alert suppressed by an eval gate.</b><br>A message failed '
                            'review, so SIP Guard stays silent rather than show it.</div>', unsafe_allow_html=True)
            elif high_risk:
                st.markdown(f'<div class="ph-alert">{esc(tpl("alert", what=what, date=P["debit_date"], verb=verb))}'
                            f'<small>{esc(tpl("alert_charge"))}</small></div>', unsafe_allow_html=True)
                if st.session_state["demo_unapproved"]:
                    st.markdown(f'<div class="ph-fail">{esc(tpl("unapproved_demo"))}</div>', unsafe_allow_html=True)
                st.button("Resolve in 1-Tap", type="primary", use_container_width=True, on_click=go,
                          args=("sheet",), key=f"resolve_{pid}")
            else:
                st.markdown(f'<div class="ph-ok">All set for {P["debit_date"]}. No action needed.</div>',
                            unsafe_allow_html=True)
            st.button(f"⏩ Simulate debit day ({P['debit_date']})", use_container_width=True,
                      on_click=run_debit_day, key=f"t0_home_{pid}")

        # ---- Protect: one-tap fallback sheet -------------------------------------------------------------------
        elif S["stage"] == "sheet":
            st.markdown('<div class="ph-title" style="margin-top:4px">What would you like to do?</div>',
                        unsafe_allow_html=True)
            opts = [("skip_pay", "opt_skip_pay", "opt_skip_pay_sub"), ("skip", "opt_skip", "opt_skip_sub"),
                    ("shift", "opt_shift", "opt_shift_sub"), ("keep", "opt_keep", "opt_keep_sub")]
            for i, (code, t_key, s_key) in enumerate(opts):
                st.button(tpl(t_key), use_container_width=True, type="primary" if i == 0 else "secondary",
                          on_click=choose, args=(code,), key=f"opt_{code}_{pid}")
                st.markdown(f'<div class="sg-muted" style="margin:-6px 4px 4px 4px">'
                            f'{esc(tpl(s_key, date=P["debit_date"]))}</div>', unsafe_allow_html=True)
            st.button("← Back", on_click=go, args=("home",), key=f"back_{pid}")

        # ---- Choice confirmed ----------------------------------------------------------------------------------
        elif S["stage"] == "resolved":
            c = S["choice"]
            if c == "skip_pay":
                st.markdown(f'<div class="ph-ok"><b>Done.</b> This month\'s debit is skipped and ₹{total_due:,} was '
                            'paid by UPI from your other account. No bank debit on '
                            f'{P["debit_date"]}.</div>', unsafe_allow_html=True)
            elif c == "skip":
                st.markdown(f'<div class="ph-ok"><b>Skipped.</b> Your bank won\'t be asked for {P["debit_date"]}\'s '
                            'debit, so there\'s no bounce charge. Your SIP stays active for next month.</div>',
                            unsafe_allow_html=True)
            elif c == "shift":
                st.markdown('<div class="ph-ok"><b>Dates updated.</b> From December, debits run on the 8th. '
                            f'This month\'s debit still runs on {P["debit_date"]}.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ph-neutral"><b>Keeping the debit.</b> Add ₹{total_due:,} to your bank '
                            f'before {P["debit_date"]}.</div>', unsafe_allow_html=True)
                S["funds_added"] = st.checkbox("I've added funds to my bank account", value=S["funds_added"],
                                               key=f"funds_{pid}")
            st.button(f"⏩ Simulate debit day ({P['debit_date']})", type="primary", use_container_width=True,
                      on_click=run_debit_day, key=f"t0_res_{pid}")

        # ---- T+0: debit day ------------------------------------------------------------------------------------
        else:
            out = S["t0"]
            if out == "not_presented":
                st.markdown('<div class="ph-tl"><span class="d">●</span> Notified (T-3)<br><span class="d">●</span> '
                            'Instalment skipped · not presented to bank<br>'
                            + ('<span class="d">●</span> Paid via UPI · units allotted<br>' if S["choice"] == "skip_pay"
                               else '<span class="o">○</span> Next debit 5 Dec<br>')
                            + '</div><div class="ph-ok">No bounce charge this month. SIP active.</div>',
                            unsafe_allow_html=True)
            elif out == "success" or S["paid"]:
                st.markdown('<div class="ph-tl"><span class="d">●</span> Scheduled<br><span class="d">●</span> '
                            + ('Paid via UPI after a failed debit' if S["paid"] else 'Debited from your bank')
                            + '<br><span class="d">●</span> Units allotted</div>'
                            '<div class="ph-ok">This month\'s SIP is invested.</div>', unsafe_allow_html=True)
            elif not flag_on or not gates_ok:
                st.markdown(f'<div class="ph-fail"><b>SIP instalment failed.</b><br>Status: Failed. '
                            f'Your bank may have charged ₹{P["charge"]:,} per failed SIP.</div>'
                            '<div class="sg-muted">Today\'s experience: no warning beforehand, no explanation '
                            'after. Three misses in a row cancel the SIP automatically.</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ph-tl"><span class="d">●</span> Scheduled<br><span class="x">✕</span> '
                            f'Debit failed on {P["debit_date"]}<br><span class="o">○</span> No automatic retry</div>'
                            f'<div class="ph-fail"><b>{esc(tpl("recovery"))}</b></div>', unsafe_allow_html=True)
                st.button(f"Pay ₹{total_due:,} via UPI to invest this month", type="primary",
                          use_container_width=True, on_click=pay_upi, key=f"pay_{pid}")
                with st.expander("Why did this happen?"):
                    st.write(tpl("recovery_why"))
            st.button("↺ Replay from T-3", use_container_width=True, on_click=reset, args=(pid,),
                      key=f"replay_{pid}")

# ---------------------------------------------------------------------------------------------------------------
# Right: under the hood
# ---------------------------------------------------------------------------------------------------------------
with right:
    st.markdown('<div class="sg-card"><h4>Under the hood · Eval gate</h4><div class="sg-muted">The model decides '
                'only who to warn and when. Anything that moves money needs the investor\'s tap.</div></div>',
                unsafe_allow_html=True)
    st.toggle("Feature flag: SIP Guard enabled", key="flag_on",
              help="Kill switch. Off = today's Groww experience, instantly, for every investor.")

    max_abs = max([abs(c) for _, c, _ in parts] + [0.01])
    rows = []
    for label, c, note in parts:
        width = 50 * abs(c) / max_abs
        bar = (f'<span style="left:50%;width:{width:.0f}%;background:{RED}"></span>' if c > 0 else
               f'<span style="right:50%;width:{width:.0f}%;background:{MINT}"></span>' if c < 0 else "")
        rows.append(f'<div class="sg-factor"><div>{esc(label)}<div class="sg-muted">{esc(note)}</div></div>'
                    f'<div class="sg-bar">{bar}</div><div style="text-align:right">{c:+.2f}</div></div>')
    verdict = ('<span class="sg-pill bad">High risk · alert triggered</span>' if high_risk and guard_active else
               '<span class="sg-pill warn">High risk · alert held back</span>' if high_risk else
               '<span class="sg-pill ok">Low risk · stay silent</span>')
    st.markdown(f'<div class="sg-card"><h4>Live model scoring</h4>'
                f'<div class="sg-muted">Contribution to the failure log-odds (red raises risk, mint lowers it); '
                f'baseline {INTERCEPT:+.1f}.</div>{"".join(rows)}'
                f'<div class="sg-risk"><b>{prob:.0%}</b><span class="sg-muted">failure probability · alert at '
                f'≥ {ALERT_THRESHOLD:.0%}</span></div><div style="margin-top:6px">{verdict}</div></div>',
                unsafe_allow_html=True)

    with st.expander("What-if: change the signals"):
        f0 = P["features"]
        wi = {
            "past_failures": st.slider("Failed debits in last 6 cycles", 0, 6, int(overrides.get("past_failures", f0["past_failures"])),
                                       key=f"wi_pf_{pid}"),
            "sips_same_date": st.slider("SIPs debiting the same day", 1, 6, int(overrides.get("sips_same_date", f0["sips_same_date"])),
                                        key=f"wi_sd_{pid}"),
            "salary_after_debit": int(st.checkbox("Salary credit slipped past the debit date",
                                                  value=bool(overrides.get("salary_after_debit", f0["salary_after_debit"])),
                                                  key=f"wi_sal_{pid}")),
            "festive": int(st.checkbox("Festive-season window", value=bool(overrides.get("festive", f0["festive"])),
                                       key=f"wi_fe_{pid}")),
        }
        if wi != {k: overrides.get(k, f0[k]) for k in wi}:
            st.session_state[f"whatif_{pid}"] = wi
            st.rerun()

    gate_rows = "".join(
        f'<div class="sg-gate"><div><div class="t">{i}. {esc(g["name"])}</div><div class="d">{esc(g["detail"])}</div>'
        f'</div><span class="sg-pill {"ok" if g["ok"] else "bad"}">{"PASSED" if g["ok"] else "FAILED"}</span></div>'
        for i, g in enumerate(gates, 1))
    st.markdown(f'<div class="sg-card"><h4>Automated eval gates</h4>{gate_rows}'
                f'<div class="sg-muted" style="margin-top:8px">'
                f'{"All gates pass: SIP Guard may speak." if gates_ok else "A gate failed: SIP Guard falls back to silence."}'
                f'</div></div>', unsafe_allow_html=True)
    st.toggle("Demo: inject an unapproved marketing message", key="demo_unapproved",
              help="Shows the compliance and non-advisory gates blocking a message and the app failing safe.")

st.markdown('<div class="sg-muted" style="margin-top:18px;border-top:1px solid #E2E8F0;padding-top:10px">'
            'Prototype for a NextLeap PM capstone. Simulated investors and model; not investment advice and not a '
            'Groww product. Evidence: Groww SIP Discovery Engine (680 public reviews); bank charges per public '
            'reporting (₹250–750 + 18% GST per failed debit).</div>', unsafe_allow_html=True)
