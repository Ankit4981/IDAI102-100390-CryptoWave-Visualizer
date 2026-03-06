"""
CryptoWave Visualizer — FA-2 | FinTechLab | Mathematics for AI
UPGRADED VERSION — Real CSV loading, stable/volatile annotations, full deployment ready
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import time
import os

st.set_page_config(page_title="CryptoWave Visualizer", page_icon="₿",
                   layout="wide", initial_sidebar_state="expanded")

if "sidebar_state" not in st.session_state:
    st.session_state["sidebar_state"] = "expanded"

# ── Session state ─────────────────────────────────────────────────────────────
def ss(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

ss("logged_in",     False)
ss("dark",          True)
ss("wave_type",     "Sine Wave")
ss("amplitude",     150)
ss("frequency",     1.5)
ss("drift",         2)
ss("stab",          "Profile")
ss("profile_name",  "Ankit Pradhan")
ss("profile_email", "ankit@cryptowave.ai")
ss("profile_bio",   "Leading the product vision for CryptoWave Visualizer.")
ss("notifications", True)
ss("active_thread", 0)
ss("data_source",   "Simulated")
ss("messages", [
    {"from":"Support Team","time":"10m ago","preview":"Your simulation is ready...",
     "chat":[{"from":"them","text":"Hello! Your simulation is complete. Check Reports."},
             {"from":"me",  "text":"Great! Can I get the CSV too?"},
             {"from":"them","text":"Yes! Use the Download buttons on the Reports page."}]},
    {"from":"Alex Rivera","time":"2h ago","preview":"Check the new parameters","chat":[]},
    {"from":"System Bot", "time":"5h ago","preview":"Weekly report generated",  "chat":[]},
    {"from":"Marketing",  "time":"1d ago","preview":"New features available!",  "chat":[]},
])
ss("reports", [
    {"name":"Q1 Volatility Analysis",  "type":"PDF",   "date":"Mar 01, 2026","status":"COMPLETED"},
    {"name":"Sine Wave Pattern Study",  "type":"CSV",   "date":"Feb 28, 2026","status":"COMPLETED"},
    {"name":"Market Drift Simulation",  "type":"Excel", "date":"Feb 25, 2026","status":"PROCESSING"},
    {"name":"User Engagement Report",   "type":"PDF",   "date":"Feb 20, 2026","status":"COMPLETED"},
])

# ── Theme ─────────────────────────────────────────────────────────────────────
def T():
    if st.session_state.dark:
        return dict(
            bg="#02060f", card="#080f1e", card2="#0c1628",
            border="#162035", text="#eef2ff", sub="#5a7299",
            grid="#0a1525", inp="#060c18", glow="rgba(99,102,241,0.18)"
        )
    return dict(
        bg="#f0f4ff", card="#ffffff", card2="#e8eeff",
        border="#c5d0f0", text="#0f172a", sub="#64748b",
        grid="#f0f4ff", inp="#ffffff", glow="rgba(99,102,241,0.08)"
    )

A=  "#6366f1"; A2= "#818cf8"; A3= "#4f46e5"
GR= "#10b981"; GR2="#34d399"; RD= "#f43f5e"
AM= "#f59e0b"; AM2="#fbbf24"; PU= "#a855f7"
PU2="#c084fc"; CY= "#06b6d4"; CY2="#22d3ee"
PK= "#ec4899"; OR= "#f97316"; TEAL="#14b8a6"
LIME="#84cc16"; VIOL="#7c3aed"

MONTHS=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ══════════════════════════════════════════════════════════════════════════════
#  ★ UPGRADE 1: REAL DATA LOADER
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_real_data():
    """
    Loads real Bitcoin CSV dataset.
    Download from: https://www.kaggle.com/datasets/sudalairajkumar/cryptocurrencypricehistory
    Place 'bitcoin_price.csv' in the same folder as app.py
    Expected columns: Date, Open, High, Low, Close, Volume
    """
    csv_path = "bitcoin_price.csv"
    if not os.path.exists(csv_path):
        return None, "CSV file not found. Using simulated data."

    try:
        # Step 1: Load dataset
        df = pd.read_csv(csv_path)

        # Step 2: Check columns and print shape
        required_cols = {'Date', 'Open', 'High', 'Low', 'Close', 'Volume'}
        if not required_cols.issubset(set(df.columns)):
            # Try alternate column names
            df.columns = [c.strip().title() for c in df.columns]

        # Step 3: Convert Timestamp to proper datetime
        df['Date'] = pd.to_datetime(df['Date'], infer_datetime_format=True)
        df = df.sort_values('Date').reset_index(drop=True)

        # Step 4: Focus on Close Price — rename for clarity
        df.rename(columns={'Close': 'Price'}, inplace=True)

        # Step 5: Handle missing data
        df.dropna(subset=['Price'], inplace=True)
        df[['Open', 'High', 'Low', 'Volume']] = df[['Open', 'High', 'Low', 'Volume']].fillna(method='ffill')

        # Step 6: Subset for simplicity — last 180 days
        df = df.tail(180).reset_index(drop=True)

        # Derived columns
        df['Return']     = df['Price'].pct_change()
        df['RollingStd'] = df['Return'].rolling(14).std() * np.sqrt(252) * 100

        return df, f"✅ Real data loaded! Shape: {df.shape[0]} rows × {df.shape[1]} columns"

    except Exception as e:
        return None, f"Error loading CSV: {e}. Using simulated data."

# ── Chart config ─────────────────────────────────────────────────────────────
def CC(leg=False, h=260):
    t=T()
    return dict(
        paper_bgcolor=t["card"], plot_bgcolor=t["card"],
        font=dict(family="'Outfit','Sora',sans-serif", color=t["sub"], size=11),
        margin=dict(l=50,r=20,t=36,b=36), height=h,
        xaxis=dict(gridcolor=t["grid"], zerolinecolor=t["grid"],
                   tickfont=dict(size=10,color=t["sub"]), linecolor=t["border"]),
        yaxis=dict(gridcolor=t["grid"], zerolinecolor=t["grid"],
                   tickfont=dict(size=10,color=t["sub"]), linecolor=t["border"]),
        hovermode="x unified", showlegend=leg,
        legend=dict(orientation="h",y=1.08,x=0,bgcolor="rgba(0,0,0,0)",
                    font=dict(size=11,color=t["sub"]))
    )

# ── Data generators ───────────────────────────────────────────────────────────
def gen_wave(wt, amp, freq, drift, n=64):
    x=np.linspace(0,4*np.pi,n); np.random.seed(42)
    s={"Sine Wave":amp*np.sin(freq*x),"Cosine Wave":amp*np.cos(freq*x),
       "Random Noise":amp*np.random.randn(n).cumsum()*0.28,
       "Combined":amp*0.65*np.sin(freq*x)+amp*0.35*np.random.randn(n).cumsum()*0.18
       }.get(wt, amp*np.sin(freq*x))
    d=drift*np.arange(n)*0.55
    return pd.DataFrame({
        "label":[MONTHS[min(int(i/(n/12)),11)] for i in range(n)],
        "price":np.clip(500+s+d,5,6000),
        "trend":np.clip(500+d+amp*0.25*np.sin(x*0.5),5,6000)
    })

def gen_btc(wt, amp, freq, drift, days=180):
    np.random.seed(42); x=np.linspace(0,4*np.pi,days)
    s={"Sine Wave":amp*np.sin(freq*x),"Cosine Wave":amp*np.cos(freq*x),
       "Random Noise":amp*np.random.randn(days).cumsum()*0.4,
       "Combined":amp*0.6*np.sin(freq*x)+amp*0.4*np.random.randn(days).cumsum()*0.25
       }.get(wt, amp*np.sin(freq*x))
    close=np.clip(30000+s+drift*np.cumsum(np.ones(days)),5000,200000)
    noise=np.abs(np.random.randn(days))*amp*0.15+100
    op=np.roll(close,1); op[0]=close[0]
    df=pd.DataFrame({
        "Date":pd.date_range(end=pd.Timestamp.today(),periods=days,freq="D"),
        "Open":op.round(2),"High":(close+noise*1.4).round(2),
        "Low":(close-noise*1.4).round(2),"Close":close.round(2),
        "Price":close.round(2),
        "Volume":np.random.randint(5000,80000,days)
    })
    df["Return"]=df["Price"].pct_change()
    df["RollingStd"]=df["Return"].rolling(14).std()*np.sqrt(252)*100
    return df

def H(html): st.markdown(html, unsafe_allow_html=True)

def inject_css():
    t=T()
    H("""<script>
    function keepSidebarOpen() {
        const btn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
        if (btn) btn.style.display = 'none';
    }
    setTimeout(keepSidebarOpen, 300);
    setTimeout(keepSidebarOpen, 800);
    </script>""")
    H(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Sora:wght@400;600;700;800&family=DM+Mono:wght@400;500;600&display=swap');

html,body,[class*="css"]{{font-family:'Outfit',sans-serif!important;background:{t['bg']}!important;color:{t['text']}!important;}}
.main{{background:{t['bg']}!important;}}
.block-container{{padding:1.6rem 2.2rem 1rem!important;max-width:100%!important;}}

.main::before{{content:'';position:fixed;top:0;left:0;right:0;bottom:0;
background:radial-gradient(ellipse 90% 60% at 5% 0%,rgba(99,102,241,0.13) 0%,transparent 50%),
radial-gradient(ellipse 70% 50% at 95% 100%,rgba(168,85,247,0.10) 0%,transparent 50%),
radial-gradient(ellipse 50% 40% at 50% 50%,rgba(6,182,212,0.05) 0%,transparent 55%);
pointer-events:none;z-index:0;}}

.main::after{{content:'';position:fixed;top:0;left:0;right:0;bottom:0;
background-image:radial-gradient(circle,rgba(99,102,241,0.08) 1px,transparent 1px);
background-size:32px 32px;pointer-events:none;z-index:0;opacity:0.5;}}
.block-container{{position:relative;z-index:1;}}

@keyframes floatOrb{{0%,100%{{transform:translate(0,0) scale(1);}}33%{{transform:translate(20px,-15px) scale(1.05);}}66%{{transform:translate(-10px,20px) scale(0.95);}}}}
@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1);box-shadow:0 0 0 0 rgba(16,185,129,0.4);}}50%{{opacity:.7;transform:scale(1.4);box-shadow:0 0 0 6px rgba(16,185,129,0);}}}}
@keyframes fadeInUp{{from{{opacity:0;transform:translateY(12px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes glow{{0%,100%{{box-shadow:0 0 20px rgba(99,102,241,0.2);}}50%{{box-shadow:0 0 40px rgba(99,102,241,0.5),0 0 80px rgba(168,85,247,0.2);}}}}
@keyframes shimmer{{0%{{background-position:-200% center;}}100%{{background-position:200% center;}}}}

section[data-testid="stSidebar"]{{
background:linear-gradient(160deg,{t['card']} 0%,rgba(8,15,30,0.98) 60%,{t['bg']} 100%)!important;
border-right:1px solid {t['border']}!important;
box-shadow:4px 0 40px rgba(0,0,0,0.4),inset -1px 0 0 rgba(99,102,241,0.08)!important;
min-width:240px!important;width:240px!important;
transform:translateX(0)!important;display:block!important;visibility:visible!important;opacity:1!important;
backdrop-filter:blur(20px);}}
section[data-testid="stSidebar"] .block-container{{padding:.8rem!important;}}
button[data-testid="collapsedControl"]{{display:none!important;}}
[data-testid="stSidebarCollapseButton"]{{display:none!important;}}
#MainMenu,footer,header{{visibility:hidden!important;}}
.stDeployButton{{display:none!important;}}

div[data-testid="stRadio"]>div:first-child>label,
div[data-testid="stRadio"] [data-testid="stWidgetLabel"]{{display:none!important;}}
div[data-testid="stRadio"]>div[role="radiogroup"]{{display:flex;flex-direction:column;gap:3px;}}
div[data-testid="stRadio"] label[data-baseweb="radio"]{{
border-radius:12px;padding:11px 14px!important;font-size:13px;font-weight:500;
color:{t['sub']}!important;cursor:pointer;display:flex!important;align-items:center;gap:10px;
transition:all .2s cubic-bezier(.4,0,.2,1);border:1px solid transparent!important;
background:transparent;position:relative;overflow:hidden;width:100%;}}
div[data-testid="stRadio"] label[data-baseweb="radio"]:hover{{color:{t['text']}!important;border-color:{t['border']}!important;transform:translateX(3px);}}
div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"]{{
background:linear-gradient(135deg,rgba(99,102,241,0.25),rgba(168,85,247,0.15))!important;
color:{t['text']}!important;font-weight:700!important;border-color:rgba(99,102,241,0.5)!important;
box-shadow:0 4px 20px rgba(99,102,241,0.25)!important;}}
div[data-testid="stRadio"] label[data-baseweb="radio"]>div:first-child{{display:none!important;}}
div[data-testid="stRadio"] label[data-baseweb="radio"] span{{display:inline!important;visibility:visible!important;opacity:1!important;color:inherit!important;}}

.stButton>button{{
background:linear-gradient(135deg,{A} 0%,{PU} 50%,{A3} 100%)!important;
color:#fff!important;border:none!important;border-radius:14px!important;
font-weight:700!important;font-size:13px!important;padding:11px 20px!important;
transition:all .3s cubic-bezier(.4,0,.2,1)!important;width:100%;
font-family:'Outfit',sans-serif!important;
box-shadow:0 4px 20px rgba(99,102,241,0.35),inset 0 1px 0 rgba(255,255,255,0.1)!important;}}
.stButton>button:hover{{transform:translateY(-2px) scale(1.01)!important;box-shadow:0 12px 32px rgba(99,102,241,0.5)!important;}}

.stTextInput>div>div>input,.stTextArea>div>div>textarea{{
border-radius:12px!important;border:1.5px solid {t['border']}!important;
background:{t['inp']}!important;color:{t['text']}!important;
font-family:'Outfit',sans-serif!important;font-size:13px!important;padding:10px 14px!important;}}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{{
border-color:{A}!important;box-shadow:0 0 0 4px rgba(99,102,241,0.18)!important;}}
.stTextInput label,.stTextArea label,.stSelectbox label,.stSlider label{{
font-size:10px!important;font-weight:700!important;letter-spacing:.1em!important;
color:{t['sub']}!important;text-transform:uppercase!important;}}
.stSelectbox>div>div{{border-radius:12px!important;border:1.5px solid {t['border']}!important;
background:{t['inp']}!important;color:{t['text']}!important;}}

.bthem{{background:linear-gradient(135deg,{t['card2']},{t['card']});color:{t['text']};padding:12px 16px;
border-radius:4px 16px 16px 16px;font-size:13px;max-width:74%;line-height:1.65;
display:inline-block;border:1px solid {t['border']};box-shadow:0 4px 12px rgba(0,0,0,0.1);}}
.bme{{background:linear-gradient(135deg,{A} 0%,{PU} 100%);color:#fff;padding:12px 16px;
border-radius:16px 4px 16px 16px;font-size:13px;max-width:74%;line-height:1.65;
display:inline-block;box-shadow:0 4px 16px rgba(99,102,241,0.35);}}

.dlive{{display:inline-block;width:8px;height:8px;border-radius:50%;
background:{GR};animation:pulse 2s ease-in-out infinite;margin-right:5px;vertical-align:middle;
box-shadow:0 0 0 3px rgba(16,185,129,0.15),0 0 12px rgba(16,185,129,0.3);}}

.cw-card{{background:linear-gradient(145deg,{t['card']},{t['card2']})!important;
border:1px solid {t['border']}!important;border-radius:20px!important;padding:24px!important;
position:relative;overflow:hidden;transition:box-shadow .3s,transform .3s;backdrop-filter:blur(12px);}}
.cw-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;
background:linear-gradient(90deg,transparent,rgba(99,102,241,0.6),rgba(168,85,247,0.4),transparent);}}
.cw-card:hover{{box-shadow:0 20px 60px rgba(0,0,0,0.3),0 0 0 1px rgba(99,102,241,0.15)!important;transform:translateY(-2px);}}

.sc-hdr{{font-size:13px;font-weight:700;color:{t['text']};margin-bottom:16px;
display:flex;align-items:center;gap:8px;font-family:'Sora',sans-serif;letter-spacing:0.01em;}}

hr{{border-color:{t['border']}!important;margin:14px 0!important;}}
::-webkit-scrollbar{{width:4px;height:4px;}}
::-webkit-scrollbar-track{{background:transparent;}}
::-webkit-scrollbar-thumb{{background:linear-gradient(180deg,{A},{PU},{CY});border-radius:99px;}}

.stSlider [role="slider"]{{background:{A}!important;box-shadow:0 0 0 4px rgba(99,102,241,0.25)!important;}}
.stMarkdown,.stPlotlyChart,.stDataFrame{{animation:fadeInUp .3s ease both;}}

.stApp,[data-testid="stAppViewContainer"]{{background:{t['bg']} !important;}}
[data-testid="metric-container"]{{background:{t['card']} !important;color:{t['text']} !important;
border:1px solid {t['border']} !important;border-radius:12px !important;}}
.stDownloadButton>button{{background:linear-gradient(135deg,{t['card']},{t['card2']}) !important;
color:{t['text']} !important;border:1.5px solid {t['border']} !important;}}
.stDownloadButton>button:hover{{border-color:{A} !important;color:{A} !important;}}
input[type="checkbox"]{{accent-color:{A} !important;}}

/* Data source badge */
.ds-badge-real{{background:linear-gradient(135deg,rgba(16,185,129,0.2),rgba(52,211,153,0.1));
color:#34d399;font-size:11px;font-weight:700;padding:5px 14px;border-radius:99px;
border:1px solid rgba(52,211,153,0.35);display:inline-flex;align-items:center;gap:6px;}}
.ds-badge-sim{{background:linear-gradient(135deg,rgba(99,102,241,0.2),rgba(168,85,247,0.1));
color:#818cf8;font-size:11px;font-weight:700;padding:5px 14px;border-radius:99px;
border:1px solid rgba(99,102,241,0.35);display:inline-flex;align-items:center;gap:6px;}}
</style>""")

def ph(title, sub="", badge=None):
    t=T()
    icon_part = title.split(" ")[0]
    text_part = " ".join(title.split(" ")[1:])
    badge_html = ""
    if badge:
        badge_html = f'<div style="margin-left:48px;margin-top:8px;">{badge}</div>'
    H(f'<div style="padding-bottom:20px;border-bottom:1px solid {t["border"]};margin-bottom:28px;position:relative;">'
      f'<div style="position:absolute;bottom:0;left:0;width:60px;height:2px;'
      f'background:linear-gradient(90deg,{A},{PU},{CY});border-radius:99px;"></div>'
      f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">'
      f'<div style="display:flex;align-items:center;justify-content:center;'
      f'width:36px;height:36px;border-radius:10px;font-size:18px;'
      f'background:linear-gradient(135deg,rgba(99,102,241,0.2),rgba(168,85,247,0.1));'
      f'border:1px solid rgba(99,102,241,0.25);">{icon_part}</div>'
      f'<h2 style="font-size:24px;font-weight:800;font-family:\'Sora\',sans-serif;'
      f'background:linear-gradient(135deg,{t["text"]} 0%,{A2} 60%,{PU2} 100%);'
      f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
      f'background-clip:text;margin:0;letter-spacing:-0.02em;">{text_part}</h2>'
      f'</div>'
      + (f'<div style="font-size:12px;color:{t["sub"]};letter-spacing:0.03em;margin-left:48px;">{sub}</div>' if sub else "")
      + badge_html
      + f'</div>')

def ft():
    t=T()
    H(f'<div style="text-align:center;font-family:\'DM Mono\',monospace;font-size:9px;'
      f'color:{t["sub"]};letter-spacing:.18em;padding:24px 0 4px;'
      f'border-top:1px solid {t["border"]};margin-top:36px;">'
      f'<div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:6px;">'
      f'<div style="width:4px;height:4px;border-radius:50%;background:{A};box-shadow:0 0 6px {A};animation:pulse 2s ease-in-out infinite;"></div>'
      f'<span style="background:linear-gradient(90deg,{A2},{PU2});-webkit-background-clip:text;-webkit-text-fill-color:transparent;">CRYPTOWAVE</span>'
      f'<div style="width:4px;height:4px;border-radius:50%;background:{PU};box-shadow:0 0 6px {PU};animation:pulse 2s ease-in-out infinite .5s;"></div>'
      f'</div>'
      f'© 2026 CRYPTOWAVE VISUALIZER · VOLATILITY INTELLIGENCE ENGINE · POWERED BY MATHEMATICS FOR AI'
      f'</div>')

def kpi(label, value, delta, pos=True, grad=None):
    t=T()
    if grad:
        H(f'<div style="background:{grad};border-radius:20px;padding:22px 24px;color:#fff;height:100%;'
          f'box-shadow:0 8px 40px rgba(0,0,0,0.3),inset 0 1px 0 rgba(255,255,255,0.12);'
          f'position:relative;overflow:hidden;">'
          f'<div style="position:absolute;top:-20px;right:-20px;width:80px;height:80px;'
          f'border-radius:50%;background:rgba(255,255,255,0.08);"></div>'
          f'<div style="font-size:10px;letter-spacing:.12em;font-weight:700;opacity:.85;margin-bottom:10px;text-transform:uppercase;position:relative;">{label}</div>'
          f'<div style="font-size:24px;font-weight:800;font-family:\'DM Mono\',monospace;line-height:1.1;margin-bottom:6px;position:relative;">{value}</div>'
          f'<div style="font-size:12px;color:rgba(255,255,255,.75);font-weight:500;position:relative;">{delta}</div></div>')
    else:
        dc=GR2 if pos else RD
        H(f'<div class="cw-card">'
          f'<div style="font-size:10px;letter-spacing:.1em;font-weight:700;color:{t["sub"]};text-transform:uppercase;margin-bottom:10px;">{label}</div>'
          f'<div style="font-size:24px;font-weight:800;font-family:\'DM Mono\',monospace;color:{t["text"]};line-height:1.1;margin-bottom:6px;">{value}</div>'
          f'<div style="font-size:12px;font-weight:600;color:{dc};display:flex;align-items:center;gap:4px;">{delta}</div>'
          f'</div>')

# ══════════════════════════════════════════════════════════════════════════════
#  ★ UPGRADE 2: STABLE vs VOLATILE ANNOTATION HELPER
# ══════════════════════════════════════════════════════════════════════════════
def add_stable_volatile_regions(fig, df, date_col="Date", std_col="RollingStd"):
    """
    Adds colored shaded regions to a Plotly figure marking:
    - Red zones  = Volatile periods (rolling std > median)
    - Green zones = Stable periods  (rolling std <= median)
    """
    rolling_std = df[std_col].fillna(0)
    threshold   = rolling_std.median()
    dates       = df[date_col]

    # --- Volatile zones (above median) ---
    in_volatile = False; start_idx = None
    for i, (date, std) in enumerate(zip(dates, rolling_std)):
        if std > threshold and not in_volatile:
            in_volatile = True; start_idx = date
        elif (std <= threshold or i == len(dates)-1) and in_volatile:
            in_volatile = False
            fig.add_vrect(
                x0=start_idx, x1=date,
                fillcolor="rgba(244,63,94,0.07)",
                layer="below", line_width=0,
                annotation_text="⚡ Volatile",
                annotation_position="top left",
                annotation_font=dict(size=9, color="#f43f5e"),
                annotation_bgcolor="rgba(244,63,94,0.12)",
                annotation_bordercolor="rgba(244,63,94,0.3)",
                annotation_borderwidth=1,
            )

    # --- Stable zones (below median) ---
    in_stable = False; start_idx = None
    for i, (date, std) in enumerate(zip(dates, rolling_std)):
        if std <= threshold and not in_stable and std > 0:
            in_stable = True; start_idx = date
        elif (std > threshold or i == len(dates)-1) and in_stable:
            in_stable = False
            fig.add_vrect(
                x0=start_idx, x1=date,
                fillcolor="rgba(16,185,129,0.05)",
                layer="below", line_width=0,
                annotation_text="🟢 Stable",
                annotation_position="top left",
                annotation_font=dict(size=9, color="#10b981"),
                annotation_bgcolor="rgba(16,185,129,0.1)",
                annotation_bordercolor="rgba(16,185,129,0.25)",
                annotation_borderwidth=1,
            )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════════════════════════════
def login_page():
    import streamlit.components.v1 as components
    st.markdown("""<style>
    section[data-testid="stSidebar"]{display:none!important;}
    header,footer,#MainMenu{display:none!important;}
    .block-container{padding:0!important;max-width:100%!important;}
    .main{background:#030712!important;}
    .login-zone{padding:0 52px;}
    .login-zone .stTextInput>div>div>input{background:rgba(255,255,255,0.04)!important;border:1.5px solid rgba(255,255,255,0.09)!important;border-radius:13px!important;color:#e8f0fe!important;font-size:14px!important;padding:13px 16px!important;font-family:'Outfit',sans-serif!important;}
    .login-zone .stTextInput>div>div>input:focus{border-color:rgba(99,102,241,0.65)!important;background:rgba(99,102,241,0.07)!important;box-shadow:0 0 0 4px rgba(99,102,241,0.12)!important;}
    .login-zone .stTextInput label{font-size:11px!important;font-weight:700!important;letter-spacing:.1em!important;text-transform:uppercase!important;color:#2a4060!important;}
    .login-zone .stButton>button{background:linear-gradient(135deg,#6366f1,#a855f7)!important;border:none!important;border-radius:13px!important;color:#fff!important;font-size:15px!important;font-weight:700!important;font-family:'Sora',sans-serif!important;padding:14px!important;box-shadow:0 8px 28px rgba(99,102,241,0.4)!important;}
    .login-zone .stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 14px 36px rgba(99,102,241,0.55)!important;}
    .social-row .stButton>button{background:rgba(255,255,255,0.04)!important;border:1.5px solid rgba(255,255,255,0.1)!important;border-radius:13px!important;color:#7a8fa8!important;font-size:13px!important;font-weight:600!important;box-shadow:none!important;}
    .login-zone .stCheckbox label{color:#2a4060!important;font-size:13px!important;}
    </style>""", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.25, 0.75])
    with left_col:
        components.html(f"""<!DOCTYPE html><html><head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@700;800&family=DM+Mono:wght@600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{background:#030712;height:100%;overflow:hidden;}}
body::before{{content:'';position:fixed;inset:0;pointer-events:none;
background:radial-gradient(ellipse 80% 70% at 5% 5%,rgba(99,102,241,0.2) 0%,transparent 55%),
radial-gradient(ellipse 60% 50% at 95% 95%,rgba(168,85,247,0.15) 0%,transparent 50%);}}
@keyframes breathe{{0%,100%{{box-shadow:0 0 40px rgba(99,102,241,0.45);}}50%{{box-shadow:0 0 80px rgba(99,102,241,0.8);}}}}
@keyframes floatUp{{0%{{transform:translateY(105%);opacity:0;}}10%{{opacity:.45;}}90%{{opacity:.18;}}100%{{transform:translateY(-5%);opacity:0;}}}}
@keyframes pulse{{0%,100%{{transform:scale(1);}}50%{{transform:scale(1.4);}}}}
.p{{position:fixed;border-radius:50%;background:linear-gradient(135deg,rgba(99,102,241,.5),rgba(168,85,247,.3));animation:floatUp linear infinite;pointer-events:none;}}
.wrap{{padding:52px 56px;display:flex;flex-direction:column;justify-content:space-between;height:100vh;position:relative;z-index:1;}}
.brand{{display:flex;align-items:center;gap:14px;margin-bottom:68px;}}
.logo{{width:50px;height:50px;border-radius:15px;background:linear-gradient(135deg,#6366f1,#a855f7);display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:800;color:#fff;animation:breathe 4s ease-in-out infinite;}}
.bname{{font-size:18px;font-weight:800;color:#e8f0fe;font-family:'Sora',sans-serif;}}
.btag{{font-size:10px;letter-spacing:.2em;font-family:'DM Mono',monospace;font-weight:700;background:linear-gradient(135deg,#818cf8,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
h1{{font-size:52px;font-weight:800;line-height:1.08;font-family:'Sora',sans-serif;color:#e8f0fe;margin-bottom:18px;}}
.grad{{background:linear-gradient(135deg,#818cf8,#c084fc 50%,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
p{{font-size:15px;color:#3a5570;line-height:1.75;max-width:400px;margin-bottom:30px;}}
.pills{{display:flex;flex-wrap:wrap;gap:10px;}}
.pill{{display:flex;align-items:center;gap:7px;padding:8px 16px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:99px;font-size:12px;color:#6a7f98;}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);border-radius:18px;overflow:hidden;margin-bottom:14px;}}
.stat{{padding:20px 22px;text-align:center;border-right:1px solid rgba(255,255,255,.05);}}
.stat:last-child{{border-right:none;}}
.sn{{font-size:24px;font-weight:800;font-family:'DM Mono',monospace;margin-bottom:4px;}}
.sl{{font-size:10px;letter-spacing:.1em;color:#1e3050;font-weight:600;text-transform:uppercase;}}
.live{{display:flex;align-items:center;gap:10px;padding:13px 18px;background:rgba(16,185,129,.05);border:1px solid rgba(16,185,129,.1);border-radius:14px;}}
.dot{{width:8px;height:8px;border-radius:50%;background:#34d399;flex-shrink:0;animation:pulse 2s ease-in-out infinite;}}
.lt{{font-size:11px;font-family:'DM Mono',monospace;color:#1e5040;letter-spacing:.06em;}}
</style></head><body>
<div class="p" style="width:4px;height:4px;left:8%;animation-duration:13s;bottom:0;"></div>
<div class="p" style="width:6px;height:6px;left:22%;animation-duration:17s;animation-delay:2s;bottom:0;"></div>
<div class="p" style="width:3px;height:3px;left:42%;animation-duration:11s;animation-delay:4s;bottom:0;"></div>
<div class="p" style="width:5px;height:5px;left:65%;animation-duration:15s;animation-delay:1.5s;bottom:0;"></div>
<div class="wrap">
  <div>
    <div class="brand"><div class="logo">₿</div><div><div class="bname">CryptoWave</div><div class="btag">VISUALIZER PRO</div></div></div>
    <h1>Decode<br><span class="grad">Market</span><br>Volatility</h1>
    <p>Harness mathematical wave simulations to understand cryptocurrency price patterns, volatility indexes, and market drift in real time.</p>
    <div class="pills">
      <div class="pill">📈 Live Simulation</div><div class="pill">🌊 Wave Patterns</div>
      <div class="pill">⚡ Real-time Analytics</div><div class="pill">🔒 Secure & Private</div>
    </div>
  </div>
  <div>
    <div class="stats">
      <div class="stat"><div class="sn" style="color:#818cf8">21K+</div><div class="sl">Active Users</div></div>
      <div class="stat"><div class="sn" style="color:#34d399">99.9%</div><div class="sl">Uptime</div></div>
      <div class="stat"><div class="sn" style="color:#22d3ee">180D</div><div class="sl">Data Range</div></div>
    </div>
    <div class="live"><div class="dot"></div><div class="lt">ALL SYSTEMS OPERATIONAL · BTC $43,218.50 ▲ 2.4%</div></div>
  </div>
</div></body></html>""", height=680, scrolling=False)

    with right_col:
        st.markdown('<div class="login-zone">', unsafe_allow_html=True)
        st.markdown(f'<div style="height:2px;background:linear-gradient(90deg,transparent,#6366f1,#a855f7,#22d3ee,transparent);border-radius:99px;margin-bottom:40px;"></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="display:inline-flex;align-items:center;gap:7px;padding:5px 13px;background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(168,85,247,0.08));border:1px solid rgba(99,102,241,0.25);border-radius:99px;margin-bottom:18px;"><span style="width:6px;height:6px;border-radius:50%;background:#818cf8;display:inline-block;"></span><span style="font-size:11px;font-weight:700;color:#818cf8;letter-spacing:.12em;font-family:\'DM Mono\',monospace;">SECURE LOGIN</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:34px;font-weight:800;color:#e8f0fe;font-family:\'Sora\',sans-serif;line-height:1.18;margin-bottom:8px;">Welcome<br>back 👋</div><div style="font-size:14px;color:#2a4060;line-height:1.65;margin-bottom:28px;">Sign in to continue your market analysis.</div>', unsafe_allow_html=True)

        st.markdown('<div class="social-row">', unsafe_allow_html=True)
        sc1, sc2 = st.columns(2)
        with sc1:
            if st.button("🔍  Google", use_container_width=True, key="btn_g"):
                st.session_state.logged_in = True; st.rerun()
        with sc2:
            if st.button("🐙  GitHub", use_container_width=True, key="btn_gh"):
                st.session_state.logged_in = True; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin:20px 0;"><div style="flex:1;height:1px;background:rgba(255,255,255,0.06);"></div><span style="font-size:11px;color:#1a3050;font-family:\'DM Mono\',monospace;letter-spacing:.1em;">OR WITH EMAIL</span><div style="flex:1;height:1px;background:rgba(255,255,255,0.06);"></div></div>', unsafe_allow_html=True)

        email    = st.text_input("📧  Email Address", placeholder="you@company.com", key="li_e")
        password = st.text_input("🔑  Password", placeholder="Enter your password", type="password", key="li_p")
        rc1, rc2 = st.columns(2)
        with rc1: st.checkbox("Remember me", key="li_rem")
        with rc2: st.markdown('<div style="text-align:right;padding-top:6px;"><span style="font-size:12px;color:#818cf8;font-weight:600;cursor:pointer;">Forgot password?</span></div>', unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Sign In  →", use_container_width=True, key="btn_login"):
            if not email or not password:
                st.error("⚠️ Please enter your email and password.")
            else:
                with st.spinner("Authenticating…"):
                    time.sleep(0.6)
                st.session_state.logged_in = True
                st.session_state.profile_email = email
                st.rerun()

        st.markdown(f'<div style="text-align:center;font-size:13px;color:#1e3050;margin-top:16px;">Don\'t have an account? &nbsp;<span style="background:linear-gradient(135deg,#818cf8,#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700;cursor:pointer;">Create one free →</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def sidebar():
    t=T()
    with st.sidebar:
        H(f'<div style="display:flex;align-items:center;gap:12px;padding:8px 4px 18px;border-bottom:1px solid {t["border"]};margin-bottom:14px;position:relative;">'
          f'<div style="position:absolute;bottom:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,{A}55,{PU}55,transparent);"></div>'
          f'<div style="width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,{A},{PU});display:flex;align-items:center;justify-content:center;box-shadow:0 4px 16px rgba(99,102,241,0.4);animation:glow 3s ease-in-out infinite;">'
          f'<span style="color:#fff;font-weight:800;font-size:18px;">₿</span></div>'
          f'<div><div style="font-weight:800;font-size:14px;color:{t["text"]};font-family:\'Sora\',sans-serif;">CryptoWave</div>'
          f'<div style="font-size:10px;background:linear-gradient(135deg,{A2},{CY2});-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700;letter-spacing:.08em;">VISUALIZER PRO</div></div></div>')

        pages = ["🏠  Dashboard","📊  Analytics","💹  Trading","📄  Reports",
                 "📨  Messages","📅  Calendar","👥  Users","⚙️  Settings"]
        choice = st.radio("Navigate", pages, label_visibility="collapsed", key="main_nav")
        page = choice.split("  ")[1].strip()

        H(f'<hr style="border-color:{t["border"]};margin:14px 0;">')

        dark_lbl = "☀️  Light Mode" if st.session_state.dark else "🌙  Dark Mode"
        if st.button(dark_lbl, use_container_width=True, key="btn_dark"):
            st.session_state.dark = not st.session_state.dark; st.rerun()
        if st.button("🚪  Logout", use_container_width=True, key="btn_logout"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

        H(f'<div style="margin-top:16px;padding:14px;background:linear-gradient(135deg,{t["card2"]},{t["card"]});border:1px solid {t["border"]};border-radius:14px;display:flex;align-items:center;gap:10px;">'
          f'<div style="width:38px;height:38px;border-radius:50%;flex-shrink:0;background:linear-gradient(135deg,{A},{PU});display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:13px;box-shadow:0 4px 12px rgba(99,102,241,0.35);">AP</div>'
          f'<div style="overflow:hidden;"><div style="font-size:13px;font-weight:600;color:{t["text"]};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-family:\'Sora\',sans-serif;">{st.session_state.profile_name}</div>'
          f'<div style="font-size:11px;color:{t["sub"]};display:flex;align-items:center;gap:4px;"><span class="dlive"></span>Product Manager</div></div></div>')
    return page


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    t=T()

    # Load real data
    real_df, data_msg = load_real_data()
    using_real = real_df is not None

    if using_real:
        badge = f'<span class="ds-badge-real">🟢 Real CSV Data Loaded — {data_msg}</span>'
    else:
        badge = f'<span class="ds-badge-sim">🔵 Simulated Data — {data_msg}</span>'

    ph("🏠 Dashboard", "CryptoWave Simulation Engine — live price pattern modeling", badge=badge)

    # Show data info banner if using real data
    if using_real:
        H(f'<div style="background:linear-gradient(135deg,rgba(16,185,129,0.1),rgba(52,211,153,0.05));'
          f'border:1px solid rgba(52,211,153,0.25);border-radius:14px;padding:14px 18px;'
          f'margin-bottom:20px;display:flex;align-items:center;gap:12px;">'
          f'<span style="font-size:20px;">📂</span>'
          f'<div><div style="font-size:13px;font-weight:700;color:{GR2};margin-bottom:2px;">Real Bitcoin Dataset Loaded Successfully</div>'
          f'<div style="font-size:11px;color:{t["sub"]};">Shape: {real_df.shape[0]} rows × {real_df.shape[1]} columns · '
          f'Date range: {real_df["Date"].iloc[0].strftime("%b %d, %Y")} → {real_df["Date"].iloc[-1].strftime("%b %d, %Y")} · '
          f'Missing values handled with forward fill</div></div></div>')

    c1,c2,c3,c4=st.columns(4)
    for col,(l,v,d,g) in zip([c1,c2,c3,c4],[
        ("TOTAL SALES",    "21,324",       "↑ +2,311 this week",  f"linear-gradient(135deg,{A} 0%,{PU} 100%)"),
        ("TOTAL INCOME",   "₹2,21,324.50", "↑ +42,381 monthly",   f"linear-gradient(135deg,{GR} 0%,{CY} 100%)"),
        ("TOTAL SESSIONS", "16,703",        "↑ +319 today",         f"linear-gradient(135deg,{AM} 0%,{OR} 100%)"),
        ("CONVERSION",     "12.8%",         "↑ +4.2% vs last month",f"linear-gradient(135deg,{RD} 0%,{PK} 100%)"),
    ]):
        with col: kpi(l,v,d,grad=g)

    st.markdown("<br>",unsafe_allow_html=True)

    H(f'<div class="cw-card"><div class="sc-hdr">⚡ Simulation Engine <span style="font-size:11px;font-weight:400;color:{t["sub"]};">— adjust sliders to see live patterns</span></div>')
    s1,s2,s3,s4=st.columns([2.2,1.2,1.2,1.2])
    with s1:
        wave=st.selectbox("Wave Pattern",["Sine Wave","Cosine Wave","Random Noise","Combined"],
                          index=["Sine Wave","Cosine Wave","Random Noise","Combined"].index(st.session_state.wave_type),key="d_wave")
        st.session_state.wave_type=wave
    with s2:
        amp=st.slider("Amplitude",10,500,st.session_state.amplitude,key="d_amp")
        st.session_state.amplitude=amp
    with s3:
        freq=st.slider("Frequency",0.5,5.0,st.session_state.frequency,0.1,key="d_freq")
        st.session_state.frequency=freq
    with s4:
        drift=st.slider("Drift",-20,50,st.session_state.drift,key="d_drift")
        st.session_state.drift=drift

    df_sim=gen_wave(wave,amp,freq,drift)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df_sim["label"],y=df_sim["price"],mode="lines+markers",name="Price",
        line=dict(color=A2,width=2.5),fill="tozeroy",fillcolor="rgba(129,140,248,0.1)",
        marker=dict(size=5,color=A2,line=dict(color=A,width=1.5)),
        hovertemplate="Price: <b>$%{y:.0f}</b><extra></extra>"))
    fig.add_trace(go.Scatter(x=df_sim["label"],y=df_sim["trend"],mode="lines",name="Trend",
        line=dict(color=AM2,width=1.5,dash="dot"),hovertemplate="Trend: $%{y:.0f}<extra></extra>"))
    fig.update_layout(**CC(leg=True,h=260))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    H('</div>')

    st.markdown("<br>",unsafe_allow_html=True)

    # Use REAL data if available, otherwise simulate
    if using_real:
        df_b = real_df.copy()
        df_b["Close"] = df_b["Price"]
        df_b["High"]  = df_b.get("High", df_b["Price"] * 1.02)
        df_b["Low"]   = df_b.get("Low",  df_b["Price"] * 0.98)
    else:
        df_b = gen_btc(wave, amp*100, freq, drift*10)

    ca,cb=st.columns([2.4,1])
    with ca:
        H('<div class="cw-card">')
        data_label = "Real Bitcoin Data" if using_real else "Simulated Data"
        H(f'<div class="sc-hdr">📈 Bitcoin Close Price <span style="color:{t["sub"]};font-weight:400;font-size:11px;">— Last 180 Days ({data_label})</span></div>')
        fig2=go.Figure(go.Scatter(x=df_b["Date"],y=df_b["Price" if "Price" in df_b.columns else "Close"],
            mode="lines",fill="tozeroy",fillcolor="rgba(99,102,241,0.08)",
            line=dict(color=A2,width=2.5),
            hovertemplate="<b>%{x|%b %d}</b> · $%{y:,.0f}<extra></extra>"))
        if "RollingStd" in df_b.columns:
            fig2 = add_stable_volatile_regions(fig2, df_b, date_col="Date", std_col="RollingStd")
        fig2.update_layout(**CC(leg=False,h=240))
        st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})
        H('</div>')
    with cb:
        price_col = "Price" if "Price" in df_b.columns else "Close"
        last=df_b[price_col].iloc[-1]; first=df_b[price_col].iloc[0]
        pct=(last-first)/first*100
        vol=df_b["RollingStd"].mean() if "RollingStd" in df_b.columns else 0
        rng=(df_b["High"]-df_b["Low"]).mean() if "High" in df_b.columns else 0
        for l,v,d,p in[
            ("Current Price",f"${last:,.0f}",f"{'▲'if pct>=0 else'▼'}{abs(pct):.1f}%",pct>=0),
            ("Avg Volatility",f"{vol:.1f}%","Annualised",vol<80),
            ("Avg Day Range",f"${rng:,.0f}","High−Low",True)]:
            kpi(l,v,d,pos=p)
            H("<div style='height:8px'></div>")
    ft()


# ══════════════════════════════════════════════════════════════════════════════
#  ANALYTICS  ★ UPGRADE: All charts + stable/volatile annotations
# ══════════════════════════════════════════════════════════════════════════════
def page_analytics():
    t=T()
    real_df, data_msg = load_real_data()
    using_real = real_df is not None

    badge = f'<span class="ds-badge-real">🟢 Real Data</span>' if using_real else f'<span class="ds-badge-sim">🔵 Simulated Data</span>'
    ph("📊 Analytics", "Volatility patterns, trend comparison, volume and KPIs", badge=badge)

    if using_real:
        df = real_df.copy()
        df["Close"] = df["Price"]
        df["High"]  = df.get("High",  df["Price"] * 1.02)
        df["Low"]   = df.get("Low",   df["Price"] * 0.98)
        df["Volume"]= df.get("Volume", pd.Series(np.random.randint(5000,80000,len(df))))
        df["Return"] = df["Price"].pct_change()
        df["RollingStd"] = df["Return"].rolling(14).std() * np.sqrt(252) * 100
    else:
        df=gen_btc(st.session_state.wave_type,st.session_state.amplitude*100,
                   st.session_state.frequency,st.session_state.drift*10)

    c1,c2=st.columns(2)
    with c1:
        H('<div class="cw-card">')
        H('<div class="sc-hdr">Volatility Distribution by Month</div>')
        df["Month"] = df["Date"].dt.month
        mv=df.groupby("Month")["RollingStd"].mean().reset_index()
        mv.columns=["m","vol"]; mv["mn"]=mv["m"].apply(lambda x:MONTHS[x-1])
        colors=[f"rgba(99,102,241,{0.5+i*0.04})" for i,_ in enumerate(mv["mn"])]
        fig=go.Figure(go.Bar(x=mv["mn"],y=mv["vol"].fillna(0),
            marker=dict(color=colors,line=dict(width=0)),
            hovertemplate="%{x}: <b>%{y:.1f}%</b><extra></extra>"))
        fig.update_layout(**CC(h=230))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        H('</div>')

    with c2:
        H('<div class="cw-card">')
        H('<div class="sc-hdr">Daily High vs Low (with Stable/Volatile Zones)</div>')
        s=df.iloc[::3]
        fig2=go.Figure()
        fig2.add_trace(go.Scatter(x=s["Date"],y=s["High"],mode="lines",name="High",
            line=dict(color=GR2,width=1.5),hovertemplate="High: $%{y:,.0f}<extra></extra>"))
        fig2.add_trace(go.Scatter(x=s["Date"],y=s["Low"],mode="lines",fill="tonexty",name="Low",
            fillcolor="rgba(16,185,129,0.08)",line=dict(color=RD,width=1.5),
            hovertemplate="Low: $%{y:,.0f}<extra></extra>"))
        # ★ Add stable/volatile annotations
        fig2 = add_stable_volatile_regions(fig2, df, date_col="Date", std_col="RollingStd")
        fig2.update_layout(**CC(leg=True,h=230))
        st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})
        H('</div>')

    st.markdown("<br>",unsafe_allow_html=True)
    c3,c4=st.columns(2)
    with c3:
        H('<div class="cw-card">')
        H('<div class="sc-hdr">Trading Volume (Green = Price Up, Red = Price Down)</div>')
        s2=df.iloc[::2]
        vc=[GR2 if (r or 0)>=0 else RD for r in s2["Return"].fillna(0)]
        fig3=go.Figure(go.Bar(x=s2["Date"],y=s2["Volume"],
            marker=dict(color=vc,line=dict(width=0)),
            hovertemplate="Vol: <b>%{y:,}</b><extra></extra>"))
        fig3.update_layout(**CC(h=220))
        st.plotly_chart(fig3,use_container_width=True,config={"displayModeBar":False})
        H('</div>')

    with c4:
        H('<div class="cw-card">')
        H('<div class="sc-hdr">Rolling Volatility Index (with Stable/Volatile Regions)</div>')
        dv=df.dropna(subset=["RollingStd"]); med=dv["RollingStd"].median()
        fig4=go.Figure(go.Scatter(x=dv["Date"],y=dv["RollingStd"],mode="lines",
            fill="tozeroy",fillcolor="rgba(245,158,11,0.1)",line=dict(color=AM2,width=2),
            hovertemplate="Vol: <b>%{y:.1f}%</b><extra></extra>"))
        fig4.add_hline(y=med,line_dash="dash",line_color=RD,
            annotation_text=f"Median {med:.1f}% (Stable/Volatile Threshold)",
            annotation_font=dict(color=RD,size=10))
        # ★ Add stable/volatile annotations on volatility chart too
        fig4 = add_stable_volatile_regions(fig4, df, date_col="Date", std_col="RollingStd")
        fig4.update_layout(**CC(h=220))
        st.plotly_chart(fig4,use_container_width=True,config={"displayModeBar":False})
        H('</div>')

    # ★ UPGRADE: Dedicated Stable vs Volatile Close Price Chart
    st.markdown("<br>",unsafe_allow_html=True)
    H('<div class="cw-card">')
    H(f'<div class="sc-hdr">📍 Close Price with Stable vs Volatile Period Annotations <span style="font-size:11px;font-weight:400;color:{t["sub"]};">— Red = Volatile, Green = Stable</span></div>')

    price_col = "Price" if "Price" in df.columns else "Close"
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=df["Date"], y=df[price_col], mode="lines",
        name="Close Price",
        line=dict(color=A2, width=2.5),
        fill="tozeroy", fillcolor="rgba(99,102,241,0.07)",
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Price: $%{y:,.0f}<extra></extra>"
    ))
    fig5 = add_stable_volatile_regions(fig5, df, date_col="Date", std_col="RollingStd")

    # Add median price reference line
    med_price = df[price_col].median()
    fig5.add_hline(y=med_price, line_dash="dot", line_color=AM2,
        annotation_text=f"Median: ${med_price:,.0f}",
        annotation_font=dict(color=AM2, size=10))

    layout5 = CC(leg=False, h=300)
    fig5.update_layout(**layout5)
    st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

    # Legend explanation
    H(f'<div style="display:flex;gap:20px;margin-top:12px;flex-wrap:wrap;">'
      f'<div style="display:flex;align-items:center;gap:8px;"><div style="width:16px;height:16px;border-radius:4px;background:rgba(244,63,94,0.2);border:1px solid rgba(244,63,94,0.4);"></div><span style="font-size:12px;color:{t["sub"]};">⚡ Volatile Period — Rolling Std Dev above median threshold</span></div>'
      f'<div style="display:flex;align-items:center;gap:8px;"><div style="width:16px;height:16px;border-radius:4px;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);"></div><span style="font-size:12px;color:{t["sub"]};">🟢 Stable Period — Rolling Std Dev below median threshold</span></div>'
      f'<div style="display:flex;align-items:center;gap:8px;"><div style="width:16px;height:3px;background:{AM2};border-radius:99px;margin:6px 0;"></div><span style="font-size:12px;color:{t["sub"]};">Median Price Reference Line</span></div>'
      f'</div>')
    H('</div>')

    st.markdown("<br>",unsafe_allow_html=True)
    H('<div class="cw-card">')
    H('<div class="sc-hdr">Key Performance Indicators</div>')
    price_col = "Price" if "Price" in df.columns else "Close"
    last=df[price_col].iloc[-1]; first=df[price_col].iloc[0]; pct=(last-first)/first*100
    kc=st.columns(4)
    kpi_colors=[A2,GR2,CY2,AM2]
    for col,(l,v,d,p),clr in zip(kc,[
        ("Avg Volatility",f"{df['RollingStd'].mean():.1f}%","+0.5%",True),
        ("Peak Price",    f"${df['High'].max():,.0f}","+12%",True),
        ("Day Range Avg", f"${(df['High']-df['Low']).mean():,.0f}","Hi−Lo",True),
        ("Period Return", f"{pct:+.1f}%","180d",pct>=0),
    ],kpi_colors):
        with col:
            H(f'<div style="text-align:center;padding:8px;">'
              f'<div style="font-size:10px;letter-spacing:.1em;font-weight:700;color:{t["sub"]};text-transform:uppercase;margin-bottom:8px;">{l}</div>'
              f'<div style="font-size:26px;font-weight:800;font-family:\'DM Mono\',monospace;color:{clr};margin-bottom:6px;">{v}</div>'
              f'<div style="font-size:12px;color:{GR2 if p else RD};font-weight:500;">{d}</div></div>')
    H('</div>')
    ft()


# ══════════════════════════════════════════════════════════════════════════════
#  REPORTS
# ══════════════════════════════════════════════════════════════════════════════
def page_reports():
    t=T()
    ph("📄 Reports","Download and manage simulation reports")

    hc1,hc2=st.columns([3,1])
    with hc2:
        if st.button("＋  Generate Report",use_container_width=True,key="gen_rpt"):
            st.session_state.reports.insert(0,{
                "name":f"{st.session_state.wave_type} — {datetime.now().strftime('%b %d %H:%M')}",
                "type":"CSV","date":datetime.now().strftime("%b %d, %Y"),"status":"COMPLETED"})
            st.success("✅ Report generated!"); st.rerun()

    st.markdown("<div style='height:16px'></div>",unsafe_allow_html=True)
    type_badge_colors={"PDF":("#c084fc","rgba(192,132,252,0.12)","rgba(192,132,252,0.3)"),
                       "CSV":("#22d3ee","rgba(34,211,238,0.12)","rgba(34,211,238,0.3)"),
                       "Excel":("#34d399","rgba(52,211,153,0.12)","rgba(52,211,153,0.3)")}
    rows_html=""
    for r in st.session_state.reports:
        tc,tbg,tbdr=type_badge_colors.get(r["type"],(A2,"rgba(99,102,241,0.12)","rgba(99,102,241,0.3)"))
        if r["status"]=="COMPLETED":
            badge=f'<span style="background:rgba(52,211,153,0.12);color:#34d399;font-size:10px;font-weight:700;padding:5px 14px;border-radius:99px;border:1px solid rgba(52,211,153,0.3);">✓ COMPLETED</span>'
        else:
            badge=f'<span style="background:rgba(251,191,36,0.12);color:#fbbf24;font-size:10px;font-weight:700;padding:5px 14px;border-radius:99px;border:1px solid rgba(251,191,36,0.3);">⏳ PROCESSING</span>'
        rows_html+=(f'<tr style="border-top:1px solid {t["border"]};">'
                    f'<td style="padding:15px 20px;"><div style="display:flex;align-items:center;gap:12px;">'
                    f'<div style="width:36px;height:36px;border-radius:10px;flex-shrink:0;background:linear-gradient(135deg,rgba(99,102,241,0.2),rgba(168,85,247,0.1));border:1px solid rgba(99,102,241,0.2);display:flex;align-items:center;justify-content:center;font-size:16px;">📄</div>'
                    f'<span style="font-size:13px;font-weight:600;color:{t["text"]};">{r["name"]}</span></div></td>'
                    f'<td style="padding:15px 20px;"><span style="color:{tc};font-weight:700;font-size:11px;background:{tbg};padding:4px 12px;border-radius:6px;border:1px solid {tbdr};">{r["type"]}</span></td>'
                    f'<td style="padding:15px 20px;font-size:13px;color:{t["sub"]};">{r["date"]}</td>'
                    f'<td style="padding:15px 20px;">{badge}</td>'
                    f'<td style="padding:15px 20px;text-align:center;"><span style="font-size:20px;color:{A2};">⬇</span></td></tr>')
    H(f'<div style="background:linear-gradient(145deg,{t["card"]},{t["card2"]});border:1px solid {t["border"]};border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.1);">'
      f'<table style="width:100%;border-collapse:collapse;font-family:Outfit,sans-serif;">'
      f'<thead><tr style="background:linear-gradient(135deg,{t["card2"]},{t["card"]});">'
      f'<th style="padding:13px 20px;font-size:10px;font-weight:700;color:{t["sub"]};text-align:left;letter-spacing:.12em;text-transform:uppercase;width:44%;">Report Name</th>'
      f'<th style="padding:13px 20px;font-size:10px;font-weight:700;color:{t["sub"]};text-align:left;letter-spacing:.12em;text-transform:uppercase;width:10%;">Type</th>'
      f'<th style="padding:13px 20px;font-size:10px;font-weight:700;color:{t["sub"]};text-align:left;letter-spacing:.12em;text-transform:uppercase;width:18%;">Date</th>'
      f'<th style="padding:13px 20px;font-size:10px;font-weight:700;color:{t["sub"]};text-align:left;letter-spacing:.12em;text-transform:uppercase;width:20%;">Status</th>'
      f'<th style="padding:13px 20px;font-size:10px;font-weight:700;color:{t["sub"]};text-align:center;letter-spacing:.12em;text-transform:uppercase;width:8%;">DL</th>'
      f'</tr></thead><tbody>{rows_html}</tbody></table></div>')

    st.markdown("<div style='height:16px'></div>",unsafe_allow_html=True)
    H('<div class="cw-card">')
    H('<div class="sc-hdr">📥 Download Simulation Data</div>')

    real_df, _ = load_real_data()
    if real_df is not None:
        df_dl = real_df.copy()
        df_dl["Close"] = df_dl["Price"]
    else:
        df_dl=gen_btc(st.session_state.wave_type,st.session_state.amplitude*100,
                      st.session_state.frequency,st.session_state.drift*10)

    csv_data  = df_dl.to_csv(index=False)
    json_data = df_dl.to_json(orient="records",date_format="iso")
    txt_data  = (f"CryptoWave Report\nGenerated: {datetime.now():%Y-%m-%d %H:%M}\n"
                 f"Wave: {st.session_state.wave_type}\nAmplitude: {st.session_state.amplitude}\n"
                 f"Frequency: {st.session_state.frequency}\nDrift: {st.session_state.drift}\n"
                 f"Data Source: {'Real CSV' if real_df is not None else 'Simulated'}\n"
                 f"Rows: {len(df_dl)}\n")
    d1,d2,d3=st.columns(3)
    with d1: st.download_button("⬇  Download CSV",csv_data,"cryptowave.csv","text/csv",use_container_width=True,key="dl_csv")
    with d2: st.download_button("⬇  Download JSON",json_data,"cryptowave.json","application/json",use_container_width=True,key="dl_json")
    with d3: st.download_button("⬇  Download TXT",txt_data,"summary.txt","text/plain",use_container_width=True,key="dl_txt")
    H('</div>')
    ft()


def page_messages():
    t=T()
    ph("📨 Messages","Team communication and simulation notifications")
    lc,cc=st.columns([1,2.8])
    with lc:
        H(f'<div style="background:linear-gradient(145deg,{t["card"]},{t["card2"]});border:1px solid {t["border"]};border-radius:16px;overflow:hidden;">')
        H(f'<div style="padding:14px 18px;border-bottom:1px solid {t["border"]};font-size:14px;font-weight:700;color:{t["text"]};font-family:\'Sora\',sans-serif;display:flex;align-items:center;gap:8px;"><span>Messages</span><span style="background:linear-gradient(135deg,{A},{PU});color:#fff;font-size:10px;padding:2px 8px;border-radius:99px;font-weight:700;">{len(st.session_state.messages)}</span></div>')
        for i,m in enumerate(st.session_state.messages):
            is_a=(i==st.session_state.active_thread)
            bg=f"linear-gradient(135deg,rgba(99,102,241,0.12),rgba(168,85,247,0.06))"if is_a else"transparent"
            bdr=f"3px solid {A}"if is_a else"3px solid transparent"
            H(f'<div style="padding:12px 16px;border-bottom:1px solid {t["border"]};background:{bg};border-left:{bdr};">'
              f'<div style="display:flex;justify-content:space-between;margin-bottom:3px;"><span style="font-size:12px;font-weight:600;color:{t["text"] if is_a else t["sub"]};">{m["from"]}</span><span style="font-size:10px;color:{t["sub"]};">{m["time"]}</span></div>'
              f'<div style="font-size:11px;color:{t["sub"]};overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{m["preview"]}</div></div>')
            if st.button(f"Open",key=f"thr_{i}",use_container_width=True):
                st.session_state.active_thread=i; st.rerun()
        H('</div>')
    with cc:
        a=st.session_state.messages[st.session_state.active_thread]
        H(f'<div style="background:linear-gradient(145deg,{t["card"]},{t["card2"]});border:1px solid {t["border"]};border-radius:16px;overflow:hidden;">'
          f'<div style="padding:15px 20px;border-bottom:1px solid {t["border"]};display:flex;align-items:center;gap:12px;background:linear-gradient(135deg,rgba(99,102,241,0.06),transparent);">'
          f'<div style="width:36px;height:36px;border-radius:50%;flex-shrink:0;background:linear-gradient(135deg,{A},{PU});display:flex;align-items:center;justify-content:center;color:#fff;font-size:13px;font-weight:700;">{a["from"][0]}</div>'
          f'<div><div style="font-size:13px;font-weight:600;color:{t["text"]};">{a["from"]}</div>'
          f'<div style="font-size:11px;color:{GR2};font-weight:500;"><span class="dlive"></span>ONLINE</div></div></div>')
        if not a["chat"]:
            H(f'<div style="padding:52px;text-align:center;color:{t["sub"]};font-size:13px;"><div style="font-size:32px;margin-bottom:10px;">💬</div>No messages yet.</div>')
        else:
            H('<div style="padding:20px;display:flex;flex-direction:column;gap:6px;min-height:180px;">')
            for m in a["chat"]:
                if m["from"]=="them": H(f'<div style="display:flex;justify-content:flex-start;margin-bottom:6px;"><div class="bthem">{m["text"]}</div></div>')
                else:                 H(f'<div style="display:flex;justify-content:flex-end;margin-bottom:6px;"><div class="bme">{m["text"]}</div></div>')
            H('</div>')
        ic,bc=st.columns([5,1])
        with ic: new_msg=st.text_input("",placeholder="Type a message…",label_visibility="collapsed",key="msg_box")
        with bc:
            if st.button("Send →",key="btn_send",use_container_width=True):
                if new_msg.strip():
                    idx=st.session_state.active_thread
                    st.session_state.messages[idx]["chat"].append({"from":"me","text":new_msg.strip()})
                    st.session_state.messages[idx]["chat"].append({"from":"them","text":"Got it! I'll get back to you shortly."})
                    st.rerun()
        H('</div>')
    ft()


def page_calendar():
    t=T()
    ph("📅 Calendar","Schedule and events — March 2026")
    EVENTS=[(4,"Volatility Sync",f"linear-gradient(135deg,{A},{PU})","SYNC"),
             (4,"Q1 Report",f"linear-gradient(135deg,{GR},{CY})","REPORT"),
             (13,"Maintenance",f"linear-gradient(135deg,{RD},{PK})","SYSTEM"),
             (20,"API Upgrade",f"linear-gradient(135deg,{AM},{OR})","DEV"),
             (25,"Review Call",f"linear-gradient(135deg,{PU},{PK})","MEETING")]
    ev_flat=[(d,l,g.split("(135deg,")[1].split(",")[0],g,e)for d,l,g,e in EVENTS]
    ev_map={}
    for d,l,c,g,e in ev_flat: ev_map.setdefault(d,[]).append((l,c,g,e))

    cal,sid=st.columns([2.8,1])
    with cal:
        H(f'<div style="background:linear-gradient(145deg,{t["card"]},{t["card2"]});border:1px solid {t["border"]};border-radius:16px;overflow:hidden;">')
        h1,h2,h3=st.columns([3,1,1])
        with h1: H(f'<div style="padding:16px 20px;font-size:18px;font-weight:800;color:{t["text"]};font-family:\'Sora\',sans-serif;">March 2026 <span style="font-size:10px;background:linear-gradient(135deg,{A},{PU});color:#fff;padding:3px 12px;border-radius:99px;font-weight:600;">CURRENT</span></div>')
        with h2:
            if st.button("← Prev",use_container_width=True,key="cal_p"): st.toast("📅 February 2026")
        with h3:
            if st.button("Next →",use_container_width=True,key="cal_n"): st.toast("📅 April 2026")
        dows=st.columns(7)
        for col,d in zip(dows,["SUN","MON","TUE","WED","THU","FRI","SAT"]):
            with col: H(f'<div style="text-align:center;font-size:10px;font-weight:700;color:{t["sub"]};padding:8px 2px;letter-spacing:.1em;">{d}</div>')
        cells=list(range(1,32)); today=4
        for row in range(5):
            rc=st.columns(7)
            for dow in range(7):
                idx=row*7+dow; day=cells[idx] if idx<len(cells) else None
                with rc[dow]:
                    html=f'<div style="min-height:78px;border-top:1px solid {t["border"]};padding:7px;">'
                    if day:
                        is_today=(day==today)
                        s=(f"color:#fff;font-weight:800;width:26px;height:26px;background:linear-gradient(135deg,{A},{PU});border-radius:8px;display:inline-flex;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(99,102,241,0.4);"
                           if is_today else f"color:{t['text']};font-size:12px;font-weight:500;")
                        html+=f'<div style="{s}font-size:12px;">{day}</div>'
                        for lbl,clr,grad,_ in ev_map.get(day,[]):
                            html+=f'<div style="margin-top:3px;background:{grad};color:#fff;font-size:9px;font-weight:600;padding:2px 6px;border-radius:5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{lbl}</div>'
                    html+='</div>'; H(html)
        H('</div>')
    with sid:
        H(f'<div style="background:linear-gradient(145deg,{t["card"]},{t["card2"]});border:1px solid {t["border"]};border-radius:16px;overflow:hidden;margin-bottom:12px;">')
        H(f'<div style="padding:14px 18px;border-bottom:1px solid {t["border"]};font-size:13px;font-weight:700;color:{t["text"]};font-family:\'Sora\',sans-serif;">Upcoming Events</div>')
        for day,lbl,clr,grad,etype in ev_flat:
            H(f'<div style="padding:10px 16px;border-bottom:1px solid {t["border"]};display:flex;align-items:center;gap:10px;">'
              f'<div style="text-align:center;min-width:34px;padding:4px 6px;background:{grad};border-radius:8px;">'
              f'<div style="font-size:14px;font-weight:800;color:#fff;line-height:1;">{day}</div>'
              f'<div style="font-size:8px;color:rgba(255,255,255,.75);letter-spacing:.1em;">MAR</div></div>'
              f'<div style="flex:1;"><div style="font-size:12px;font-weight:600;color:{t["text"]};">{lbl}</div>'
              f'<div style="font-size:9px;color:{t["sub"]};letter-spacing:.12em;font-family:\'DM Mono\',monospace;">{etype}</div></div>'
              f'<div style="width:8px;height:8px;border-radius:50%;background:{grad};"></div></div>')
        H('<div style="padding:10px 12px;">')
        if st.button("View All Schedule",use_container_width=True,key="view_sch"): st.toast("📅 Full schedule")
        H('</div></div>')
        with st.expander("➕ Add Event"):
            ev_d=st.number_input("Day (March)",1,31,10,key="ev_d")
            ev_n=st.text_input("Event Name",placeholder="Team meeting",key="ev_n")
            if st.button("Add to Calendar",use_container_width=True,key="add_ev"):
                st.success(f"✅ Added: {ev_n} on March {ev_d}") if ev_n else st.warning("Enter event name.")
    ft()


def page_users():
    t=T()
    ph("👥 Users","Real-time traffic and user analytics")
    np.random.seed(int(time.time())%100)
    u=1204+np.random.randint(-8,12); s=842+np.random.randint(-4,8); r=round(42.5+np.random.uniform(-0.3,0.5),1)
    tc=st.columns(3)
    grads=[f"linear-gradient(135deg,{CY},{A})",f"linear-gradient(135deg,{PU},{PK})",f"linear-gradient(135deg,{AM},{OR})"]
    for col,(l,v,c,ic,d),grad in zip(tc,[
        ("ACTIVE USERS",f"{u:,}",CY,"👤","+12% ↑"),
        ("LIVE SIMULATIONS",f"{s}",PU,"⚡","+5% ↑"),
        ("REVENUE TODAY",f"₹{r}k",AM,"💰","+8% ↑")],grads):
        with col:
            H(f'<div style="background:{grad};border-radius:16px;padding:20px 22px;color:#fff;box-shadow:0 8px 28px rgba(0,0,0,0.25);position:relative;overflow:hidden;">'
              f'<div style="position:absolute;top:-15px;right:-15px;width:70px;height:70px;border-radius:50%;background:rgba(255,255,255,0.1);"></div>'
              f'<div style="font-size:28px;margin-bottom:8px;position:relative;">{ic}</div>'
              f'<div style="font-size:26px;font-weight:800;font-family:\'DM Mono\',monospace;line-height:1.1;position:relative;">{v}</div>'
              f'<div style="font-size:10px;opacity:.8;letter-spacing:.1em;font-weight:700;text-transform:uppercase;margin:4px 0;position:relative;">{l}</div>'
              f'<div style="font-size:12px;font-weight:500;color:rgba(255,255,255,.8);position:relative;">{d}</div></div>')
    if st.button("🔄  Refresh",key="ref_u"): st.toast("✅ Refreshed!"); st.rerun()
    st.markdown("<br>",unsafe_allow_html=True)
    COUNTRIES=[("IN","India",450,100,"+12%",True),("US","United States",320,71,"+5%",True),
               ("GB","United Kingdom",180,40,"-2%",False),("DE","Germany",120,27,"+8%",True),("JP","Japan",90,20,"+15%",True)]
    bar_grads=[f"linear-gradient(90deg,{A},{PU})",f"linear-gradient(90deg,{CY},{A})",
               f"linear-gradient(90deg,{RD},{PK})",f"linear-gradient(90deg,{GR},{CY})",f"linear-gradient(90deg,{AM},{OR})"]
    H('<div class="cw-card">')
    H('<div class="sc-hdr">Real-time Traffic by Country</div>')
    for (code,name,users,pct,delta,pos),bg in zip(COUNTRIES,bar_grads):
        dc=GR2 if pos else RD
        H(f'<div style="margin-bottom:18px;">'
          f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:7px;">'
          f'<div style="display:flex;align-items:center;gap:10px;"><span style="font-size:10px;font-weight:700;color:#fff;background:{bg};padding:3px 9px;border-radius:6px;">{code}</span><span style="font-size:13px;font-weight:500;color:{t["text"]};">{name}</span></div>'
          f'<div style="display:flex;align-items:center;gap:14px;"><span style="font-size:12px;color:{t["sub"]};">{users} users</span><span style="font-size:12px;font-weight:700;color:{dc};">{delta}</span></div></div>'
          f'<div style="height:7px;background:{t["border"]};border-radius:99px;overflow:hidden;">'
          f'<div style="height:100%;width:{pct}%;background:{bg};border-radius:99px;box-shadow:0 2px 8px rgba(0,0,0,0.2);"></div></div></div>')
    H('</div>')
    st.markdown("<br>",unsafe_allow_html=True)
    H('<div class="cw-card">')
    H('<div class="sc-hdr">Traffic Chart</div>')
    fig=go.Figure(go.Bar(x=[c[1]for c in COUNTRIES],y=[c[2]for c in COUNTRIES],
        marker=dict(color=[A,CY,RD,GR,AM],line=dict(width=0)),
        hovertemplate="%{x}: <b>%{y} users</b><extra></extra>"))
    fig.update_layout(**CC(h=220)); st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    H('</div>')
    ft()


def page_settings():
    t=T()
    ph("⚙️ Settings","Manage your account preferences")
    tc,fc=st.columns([1,2.8])
    TABS=[("👤","Profile"),("🔔","Notifications"),("🛡️","Security"),("🎨","Appearance"),("💳","Billing"),("🌐","Language")]
    tab_grads={"Profile":f"linear-gradient(135deg,{A},{PU})","Notifications":f"linear-gradient(135deg,{AM},{OR})",
               "Security":f"linear-gradient(135deg,{RD},{PK})","Appearance":f"linear-gradient(135deg,{CY},{A})",
               "Billing":f"linear-gradient(135deg,{GR},{CY})","Language":f"linear-gradient(135deg,{PU},{PK})"}
    with tc:
        H(f'<div style="background:linear-gradient(145deg,{t["card"]},{t["card2"]});border:1px solid {t["border"]};border-radius:16px;overflow:hidden;">')
        for ico,lbl in TABS:
            is_a=(st.session_state.stab==lbl)
            grad=tab_grads.get(lbl,"")
            if is_a:
                H(f'<div style="padding:12px 16px;border-left:3px solid {A};background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(168,85,247,0.07));color:{t["text"]};font-size:13px;font-weight:700;display:flex;align-items:center;gap:10px;"><span style="width:28px;height:28px;border-radius:7px;background:{grad};display:flex;align-items:center;justify-content:center;font-size:14px;">{ico}</span>{lbl}</div>')
            else:
                H(f'<div style="padding:12px 16px;border-left:3px solid transparent;color:{t["sub"]};font-size:13px;font-weight:500;display:flex;align-items:center;gap:10px;"><span style="font-size:14px;">{ico}</span>{lbl}</div>')
            if st.button(f"Open",key=f"stb_{lbl}",use_container_width=True):
                st.session_state.stab=lbl; st.rerun()
        H('</div>')
    with fc:
        H('<div class="cw-card">')
        tab=st.session_state.stab
        if tab=="Profile":
            grad=tab_grads["Profile"]
            H(f'<div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">'
              f'<div style="width:70px;height:70px;border-radius:18px;background:{grad};display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:24px;box-shadow:0 8px 24px rgba(99,102,241,0.4);">AP</div>'
              f'<div><div style="font-size:17px;font-weight:800;color:{t["text"]};font-family:\'Sora\',sans-serif;">{st.session_state.profile_name}</div>'
              f'<div style="font-size:12px;color:{t["sub"]};margin-top:2px;">Product Manager</div>'
              f'<div style="margin-top:6px;"><span style="background:linear-gradient(135deg,rgba(16,185,129,0.2),rgba(52,211,153,0.1));color:{GR2};font-size:10px;font-weight:700;padding:3px 10px;border-radius:99px;border:1px solid rgba(52,211,153,0.25);">PRO PLAN</span></div></div></div>')
            f1,f2=st.columns(2)
            with f1: nn=st.text_input("Full Name",value=st.session_state.profile_name,key="pf_n")
            with f2: ne=st.text_input("Email Address",value=st.session_state.profile_email,key="pf_e")
            nb=st.text_area("Bio",value=st.session_state.profile_bio,height=90,key="pf_b")
            _,c2,c3=st.columns([2,1,1])
            with c2:
                if st.button("Cancel",key="pf_cancel"): st.toast("Discarded.")
            with c3:
                if st.button("Save Changes",key="pf_save"):
                    st.session_state.profile_name=nn; st.session_state.profile_email=ne
                    st.session_state.profile_bio=nb; st.success("✅ Saved!")
        elif tab=="Notifications":
            H(f'<div class="sc-hdr">Notification Preferences</div>')
            st.toggle("Email notifications",value=True,key="n_email")
            st.toggle("Push notifications",value=False,key="n_push")
            st.toggle("Simulation alerts",value=True,key="n_sim")
            st.toggle("Weekly digest",value=True,key="n_dig")
            n5=st.toggle("Volatility alerts",value=st.session_state.notifications,key="n_vol")
            if st.button("Save Preferences",key="save_notif"):
                st.session_state.notifications=n5; st.success("✅ Saved!")
        elif tab=="Security":
            H(f'<div class="sc-hdr">Change Password</div>')
            st.text_input("Current Password",type="password",key="s_old")
            st.text_input("New Password",type="password",key="s_new")
            st.text_input("Confirm Password",type="password",key="s_cnf")
            if st.button("Update Password",key="s_upd"): st.success("✅ Password updated!")
            st.markdown("---")
            H(f'<div class="sc-hdr">Two-Factor Authentication</div>')
            st.toggle("Enable 2FA",value=False,key="tfa")
            if st.button("Setup 2FA",key="s_2fa"): st.info("📱 Instructions sent to email.")
        elif tab=="Appearance":
            H(f'<div class="sc-hdr">Theme & Display</div>')
            dn=st.toggle("Dark Mode",value=st.session_state.dark,key="app_dark")
            if dn!=st.session_state.dark: st.session_state.dark=dn; st.rerun()
            tc_s=st.selectbox("Accent Color",["Indigo","Blue","Purple","Green","Red"],key="app_clr")
            st.select_slider("Font Size",["Small","Medium","Large"],value="Medium",key="app_font")
            if st.button("Apply",key="app_apply"): st.success(f"✅ Theme: {tc_s}!")
        elif tab=="Billing":
            H(f'<div style="background:linear-gradient(135deg,{A},{PU});border-radius:14px;padding:22px 24px;color:#fff;margin-bottom:20px;box-shadow:0 8px 28px rgba(99,102,241,0.35);">'
              f'<div style="font-size:10px;opacity:.8;letter-spacing:.12em;margin-bottom:6px;font-family:\'DM Mono\',monospace;">CURRENT PLAN</div>'
              f'<div style="font-size:24px;font-weight:800;font-family:\'Sora\',sans-serif;">Pro Plan ✦</div>'
              f'<div style="font-size:13px;opacity:.8;margin-top:4px;">₹2,499/mo · Renews Apr 1, 2026</div></div>')
            b1,b2=st.columns(2)
            with b1:
                if st.button("Upgrade to Enterprise",key="b_up"): st.success("🎉 Redirecting…")
            with b2:
                if st.button("Cancel Subscription",key="b_cancel"): st.warning("⚠️ Cancellation email sent.")
        elif tab=="Language":
            H(f'<div class="sc-hdr">Language & Region</div>')
            lang=st.selectbox("Display Language",["English","Hindi","Spanish","French","German","Japanese"],key="l_lang")
            tz=st.selectbox("Timezone",["Asia/Kolkata (IST)","America/New_York (EST)","Europe/London (GMT)","Asia/Tokyo (JST)"],key="l_tz")
            st.selectbox("Date Format",["DD/MM/YYYY","MM/DD/YYYY","YYYY-MM-DD"],key="l_fmt")
            if st.button("Save Language Settings",key="l_save"): st.success(f"✅ {lang} | {tz}")
        H('</div>')
    ft()


def page_trading():
    import streamlit.components.v1 as components
    t=T()
    ph("💹 Trading","CryptoWave Visualizer — Live Market Analytics Dashboard")

    coin_col,spacer=st.columns([1,4])
    with coin_col:
        coin=st.selectbox("Select Asset",["BTC / USDT","SOL / USDT"],key="trade_coin",label_visibility="collapsed")
    is_btc="BTC" in coin

    np.random.seed(42)
    days=90
    dates=pd.date_range(end=pd.Timestamp.today(),periods=days,freq="D")
    base=43000 if is_btc else 98
    vol_scale=1200 if is_btc else 4

    closes=[base]
    for _ in range(days-1): closes.append(closes[-1]*(1+np.random.normal(0.0008,0.022)))
    closes=np.array(closes)
    highs=closes*(1+np.abs(np.random.normal(0,0.012,days)))
    lows=closes*(1-np.abs(np.random.normal(0,0.012,days)))
    opens=np.roll(closes,1); opens[0]=closes[0]
    volumes=np.random.randint(8000,80000,days)*(vol_scale/10)

    price_now=closes[-1]; price_prev=closes[-2]
    price_chg=(price_now-price_prev)/price_prev*100
    high_24=highs[-1]; low_24=lows[-1]; high_mo=highs[-30:].max(); high_yr=highs.max()
    vol_24=volumes[-1]; mkt_cap=price_now*(19_700_000 if is_btc else 453_000_000)

    spread=price_now*0.0002; asks=[]; bids=[]
    ap=price_now+spread/2; bp=price_now-spread/2
    for i in range(12):
        aq=round(np.random.uniform(0.05,3.5),3); bq=round(np.random.uniform(0.05,3.5),3)
        asks.append({"price":round(ap+i*price_now*0.0003,2),"qty":aq,"total":round(ap*aq,2)})
        bids.append({"price":round(bp-i*price_now*0.0003,2),"qty":bq,"total":round(bp*bq,2)})

    hour_utc=datetime.utcnow().hour
    asian=0<=hour_utc<9; euro=7<=hour_utc<16; us_ses=13<=hour_utc<22
    coin_name="Bitcoin" if is_btc else "Solana"; symbol="BTC" if is_btc else "SOL"
    color_main="#f7931a" if is_btc else "#9945ff"; color_sec="#ffb347" if is_btc else "#14f195"

    def fmt_price(p): return f"${p:,.2f}" if is_btc else f"${p:,.3f}"
    def fmt_num(n):
        if n>=1e9: return f"${n/1e9:.2f}B"
        if n>=1e6: return f"${n/1e6:.2f}M"
        return f"${n:,.0f}"

    k1,k2,k3,k4,k5=st.columns(5)
    kpi_data=[(k1,f"{symbol} Price",fmt_price(price_now),f"{'▲'if price_chg>=0 else'▼'} {abs(price_chg):.2f}%",price_chg>=0,color_main),
              (k2,"Market Cap",fmt_num(mkt_cap),"Circulating supply",True,"#6366f1"),
              (k3,"24H Volume",fmt_num(vol_24),"Trading activity",True,"#06b6d4"),
              (k4,"24H High",fmt_price(high_24),f"Low: {fmt_price(low_24)}",True,"#10b981"),
              (k5,"Yearly High",fmt_price(high_yr),f"Mo. High: {fmt_price(high_mo)}",True,"#f59e0b")]
    for col,label,value,delta,pos,clr in kpi_data:
        with col:
            H(f'<div style="background:linear-gradient(145deg,{t["card"]},{t["card2"]});border:1px solid {t["border"]};border-radius:14px;padding:16px 18px;position:relative;overflow:hidden;">'
              f'<div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,{clr},{clr}88,transparent);"></div>'
              f'<div style="font-size:10px;font-weight:700;letter-spacing:.1em;color:{t["sub"]};text-transform:uppercase;margin-bottom:8px;">{label}</div>'
              f'<div style="font-size:20px;font-weight:800;color:{t["text"]};font-family:\'DM Mono\',monospace;line-height:1.1;margin-bottom:5px;">{value}</div>'
              f'<div style="font-size:11px;font-weight:600;color:{"#10b981"if pos else"#f43f5e"};">{delta}</div></div>')

    st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)
    chart_col,book_col,news_col=st.columns([2.6,1.1,1.1])

    with chart_col:
        H(f'<div style="background:linear-gradient(145deg,{t["card"]},{t["card2"]});border:1px solid {t["border"]};border-radius:16px;overflow:hidden;">')
        chg_color="#10b981"if price_chg>=0 else"#f43f5e"
        tf_buttons = "".join([
            f'<div style="padding:5px 12px;'
            f'background:{"rgba(99,102,241,0.2)" if tf=="1D" else t["card2"]};'
            f'border:1px solid {"#6366f1" if tf=="1D" else t["border"]};'
            f'border-radius:8px;font-size:11px;font-weight:600;'
            f'color:{"#818cf8" if tf=="1D" else t["sub"]}">{tf}</div>'
            for tf in ["1H","4H","1D","1W","1M"]
        ])
        H(f'<div style="padding:16px 20px;border-bottom:1px solid {t["border"]};display:flex;align-items:center;justify-content:space-between;">'
          f'<div style="display:flex;align-items:center;gap:12px;">'
          f'<div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,{color_main},{color_sec});display:flex;align-items:center;justify-content:center;font-size:16px;">{"₿"if is_btc else"◎"}</div>'
          f'<div><div style="font-size:15px;font-weight:800;color:{t["text"]};font-family:\'Sora\',sans-serif;">{symbol}/USDT</div>'
          f'<div style="font-size:12px;color:{chg_color};font-weight:600;">{fmt_price(price_now)} {("▲"if price_chg>=0 else"▼")} {abs(price_chg):.2f}%</div></div></div>'
          f'<div style="display:flex;gap:6px;">{tf_buttons}</div></div>')

        fig=go.Figure()
        fig.add_trace(go.Candlestick(x=dates,open=opens,high=highs,low=lows,close=closes,name=symbol,
            increasing=dict(line=dict(color=color_main,width=1.5),fillcolor=color_main),
            decreasing=dict(line=dict(color="#f43f5e",width=1.5),fillcolor="#f43f5e")))
        fig.add_trace(go.Bar(x=dates,y=volumes,name="Volume",
            marker=dict(color=["rgba(247,147,26,0.33)"if(color_main=="#f7931a"and c>=o)else"rgba(153,69,255,0.33)"if(color_main=="#9945ff"and c>=o)else"rgba(244,63,94,0.33)"for c,o in zip(closes,opens)],line=dict(width=0)),
            yaxis="y2",hovertemplate="Vol: <b>%{y:,.0f}</b><extra></extra>"))
        ma7=pd.Series(closes).rolling(7).mean(); ma25=pd.Series(closes).rolling(25).mean()
        fig.add_trace(go.Scatter(x=dates,y=ma7,mode="lines",name="MA7",line=dict(color="#f59e0b",width=1.2),hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=dates,y=ma25,mode="lines",name="MA25",line=dict(color="#06b6d4",width=1.2),hoverinfo="skip"))
        layout=CC(leg=True,h=360)
        layout.update(dict(yaxis=dict(**layout["yaxis"],title="",domain=[0.25,1]),
                           yaxis2=dict(domain=[0,0.2],gridcolor=t["grid"],zerolinecolor=t["grid"],tickfont=dict(size=9,color=t["sub"]),showgrid=False),
                           xaxis=dict(**layout["xaxis"],rangeslider=dict(visible=False)),
                           margin=dict(l=60,r=16,t=16,b=16)))
        fig.update_layout(**layout)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        H('</div>')

    with book_col:
        max_ask_qty=max(a["qty"]for a in asks); max_bid_qty=max(b["qty"]for b in bids)
        ask_rows="".join([
            f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;padding:5px 14px;position:relative;overflow:hidden;">'
            f'<div style="position:absolute;right:0;top:0;bottom:0;width:{int(a["qty"]/max_ask_qty*100)}%;background:rgba(244,63,94,0.08);"></div>'
            f'<div style="font-size:11px;font-weight:600;color:#f43f5e;font-family:DM Mono,monospace;position:relative;">{a["price"]:,.2f}</div>'
            f'<div style="font-size:11px;color:{t["sub"]};text-align:center;font-family:DM Mono,monospace;position:relative;">{a["qty"]:.3f}</div>'
            f'<div style="font-size:11px;color:{t["sub"]};text-align:right;font-family:DM Mono,monospace;position:relative;">{a["total"]:,.0f}</div></div>'
            for a in reversed(asks[:8])])
        bid_rows="".join([
            f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;padding:5px 14px;position:relative;overflow:hidden;">'
            f'<div style="position:absolute;right:0;top:0;bottom:0;width:{int(b["qty"]/max_bid_qty*100)}%;background:rgba(16,185,129,0.08);"></div>'
            f'<div style="font-size:11px;font-weight:600;color:#10b981;font-family:DM Mono,monospace;position:relative;">{b["price"]:,.2f}</div>'
            f'<div style="font-size:11px;color:{t["sub"]};text-align:center;font-family:DM Mono,monospace;position:relative;">{b["qty"]:.3f}</div>'
            f'<div style="font-size:11px;color:{t["sub"]};text-align:right;font-family:DM Mono,monospace;position:relative;">{b["total"]:,.0f}</div></div>'
            for b in bids[:8]])
        H(f'<div style="background:linear-gradient(145deg,{t["card"]},{t["card2"]});border:1px solid {t["border"]};border-radius:16px;overflow:hidden;height:100%;">'
          f'<div style="padding:14px 16px;border-bottom:1px solid {t["border"]};font-size:13px;font-weight:700;color:{t["text"]};display:flex;justify-content:space-between;align-items:center;"><span>Order Book</span><span style="font-size:10px;color:{t["sub"]};">LIVE</span></div>'
          f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;padding:8px 14px;border-bottom:1px solid {t["border"]};"><div style="font-size:10px;font-weight:700;color:{t["sub"]};">PRICE</div><div style="font-size:10px;font-weight:700;color:{t["sub"]};text-align:center;">QTY</div><div style="font-size:10px;font-weight:700;color:{t["sub"]};text-align:right;">TOTAL</div></div>'
          +ask_rows
          +f'<div style="padding:7px 14px;border-top:1px solid {t["border"]};border-bottom:1px solid {t["border"]};background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(168,85,247,0.05));"><span style="font-size:12px;font-weight:800;color:{t["text"]};">{fmt_price(price_now)}</span><span style="font-size:10px;color:{t["sub"]};margin-left:8px;">spread: {spread:.2f}</span></div>'
          +bid_rows+'</div>')

    with news_col:
        tag_colors={"ETF":"#6366f1","Macro":"#f59e0b","Network":"#06b6d4","Corporate":"#10b981",
                    "Market":"#a855f7","DeFi":"#14f195","Ecosystem":"#9945ff","Staking":"#f59e0b",
                    "Tech":"#06b6d4","NFT":"#ec4899"}
        btc_news=[{"title":"Bitcoin ETF inflows hit record $1.2B in single day","desc":"Spot Bitcoin ETFs saw massive institutional demand as price surged past $43K resistance.","time":"2h ago","tag":"ETF"},
                  {"title":"Fed signals potential rate cuts — BTC rallies 4.2%","desc":"Bitcoin responded strongly to dovish Fed commentary, breaking key technical levels.","time":"5h ago","tag":"Macro"},
                  {"title":"Bitcoin hash rate reaches all-time high of 620 EH/s","desc":"Network security has never been stronger as miners add capacity ahead of halving.","time":"8h ago","tag":"Network"},
                  {"title":"MicroStrategy adds 12,000 BTC to corporate treasury","desc":"Michael Saylor's firm now holds over 190,000 BTC worth approximately $8.2 billion.","time":"1d ago","tag":"Corporate"}]
        sol_news=[{"title":"Solana DEX volume surpasses Ethereum for third straight week","desc":"SOL-based protocols processed over $18B in weekly volume, led by Jupiter and Raydium.","time":"1h ago","tag":"DeFi"},
                  {"title":"Solana Mobile Chapter 2 pre-orders exceed 100,000 units","desc":"The crypto-native smartphone continues to see strong demand from Web3 users.","time":"4h ago","tag":"Ecosystem"},
                  {"title":"SOL staking yield rises to 7.2% APY amid network activity surge","desc":"Validator rewards increase as transaction volume hits new daily records on Solana.","time":"7h ago","tag":"Staking"},
                  {"title":"Firedancer validator client enters final testnet phase","desc":"Jump Crypto's high-performance client could push Solana to 1M+ TPS on mainnet.","time":"12h ago","tag":"Tech"}]
        news=btc_news if is_btc else sol_news
        H(f'<div style="background:linear-gradient(145deg,{t["card"]},{t["card2"]});border:1px solid {t["border"]};border-radius:16px;overflow:hidden;height:100%;">'
          f'<div style="padding:14px 16px;border-bottom:1px solid {t["border"]};font-size:13px;font-weight:700;color:{t["text"]};font-family:\'Sora\',sans-serif;display:flex;justify-content:space-between;align-items:center;"><span>📰 {coin_name} News</span><span style="font-size:10px;color:{t["sub"]};">Latest</span></div>')
        for item in news:
            tc2=tag_colors.get(item["tag"],"#6366f1")
            H(f'<div style="padding:13px 16px;border-bottom:1px solid {t["border"]};">'
              f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">'
              f'<span style="font-size:9px;font-weight:700;color:{tc2};background:rgba(99,102,241,0.12);padding:2px 8px;border-radius:99px;border:1px solid {tc2}44;letter-spacing:.06em;">{item["tag"]}</span>'
              f'<span style="font-size:10px;color:{t["sub"]};">{item["time"]}</span></div>'
              f'<div style="font-size:12px;font-weight:600;color:{t["text"]};line-height:1.45;margin-bottom:4px;">{item["title"]}</div>'
              f'<div style="font-size:11px;color:{t["sub"]};line-height:1.5;">{item["desc"][:70]}…</div></div>')
        H('</div>')

    st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)
    sess_col,stat_col,buysell_col=st.columns([1.4,1.4,1.2])

    with sess_col:
        H(f'<div style="background:linear-gradient(145deg,{t["card"]},{t["card2"]});border:1px solid {t["border"]};border-radius:16px;padding:18px 20px;">')
        H(f'<div style="font-size:13px;font-weight:700;color:{t["text"]};font-family:\'Sora\',sans-serif;margin-bottom:14px;">🌍 Global Trading Sessions</div>')
        sessions=[("🌏","Asian Market","Tokyo · Shanghai · Hong Kong","00:00 – 09:00 UTC",asian,"#f59e0b"),
                  ("🌍","European Market","London · Frankfurt · Paris","07:00 – 16:00 UTC",euro,"#6366f1"),
                  ("🌎","US Market","New York · Chicago","13:00 – 22:00 UTC",us_ses,"#10b981")]
        for icon,name,cities,hours,active,clr in sessions:
            bg=f"linear-gradient(135deg,{clr}22,{clr}0a)"if active else"rgba(255,255,255,0.02)"
            bdr=f"1px solid {clr}55"if active else f"1px solid {t['border']}"
            pulse=f'<span style="width:7px;height:7px;border-radius:50%;background:{clr};display:inline-block;margin-right:6px;box-shadow:0 0 8px {clr};animation:pulse 2s ease-in-out infinite;"></span>'if active else f'<span style="width:7px;height:7px;border-radius:50%;background:{t["border"]};display:inline-block;margin-right:6px;"></span>'
            H(f'<div style="background:{bg};border:{bdr};border-radius:12px;padding:12px 14px;margin-bottom:10px;">'
              f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">'
              f'<div style="display:flex;align-items:center;">{pulse}<span style="font-size:13px;font-weight:{"700"if active else"500"};color:{t["text"]if active else t["sub"]};">{icon} {name}</span></div>'
              f'<span style="font-size:10px;font-weight:700;color:{clr if active else t["sub"]};background:{clr+"22"if active else"transparent"};padding:2px 8px;border-radius:99px;">{"ACTIVE"if active else"CLOSED"}</span></div>'
              f'<div style="font-size:11px;color:{t["sub"]};margin-bottom:2px;">{cities}</div>'
              f'<div style="font-size:10px;color:{t["sub"]};font-family:\'DM Mono\',monospace;">{hours}</div></div>')
        H('</div>')

    with stat_col:
        H(f'<div style="background:linear-gradient(145deg,{t["card"]},{t["card2"]});border:1px solid {t["border"]};border-radius:16px;padding:18px 20px;">')
        H(f'<div style="font-size:13px;font-weight:700;color:{t["text"]};font-family:\'Sora\',sans-serif;margin-bottom:14px;">📊 Market Statistics</div>')
        stat_items=[("24H High",fmt_price(high_24),"#10b981","↑"),("24H Low",fmt_price(low_24),"#f43f5e","↓"),
                    ("Monthly High",fmt_price(high_mo),"#f59e0b","★"),("Yearly High",fmt_price(high_yr),"#6366f1","◆"),
                    ("Market Cap",fmt_num(mkt_cap),"#06b6d4","◉"),("24H Volume",fmt_num(vol_24),"#a855f7","≋")]
        sc1,sc2=st.columns(2)
        for i,(label,value,clr,icon) in enumerate(stat_items):
            col=sc1 if i%2==0 else sc2
            with col:
                H(f'<div style="background:linear-gradient(135deg,{clr}14,{clr}08);border:1px solid {clr}33;border-radius:12px;padding:13px 14px;margin-bottom:10px;">'
                  f'<div style="font-size:10px;font-weight:700;color:{t["sub"]};text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px;">{label}</div>'
                  f'<div style="font-size:16px;font-weight:800;color:{clr};font-family:\'DM Mono\',monospace;line-height:1.1;">{value}</div></div>')
        buy_pct=58 if is_btc else 63; sell_pct=100-buy_pct
        H(f'<div style="margin-top:4px;"><div style="display:flex;justify-content:space-between;margin-bottom:6px;">'
          f'<span style="font-size:11px;font-weight:700;color:#10b981;">Buy {buy_pct}%</span>'
          f'<span style="font-size:11px;font-weight:700;color:{t["sub"]};">Pressure</span>'
          f'<span style="font-size:11px;font-weight:700;color:#f43f5e;">Sell {sell_pct}%</span></div>'
          f'<div style="height:8px;background:{t["border"]};border-radius:99px;overflow:hidden;">'
          f'<div style="height:100%;width:{buy_pct}%;background:linear-gradient(90deg,#10b981,#34d399);border-radius:99px;"></div></div></div>')
        H('</div>')

    with buysell_col:
        H(f'<div style="background:linear-gradient(145deg,{t["card"]},{t["card2"]});border:1px solid {t["border"]};border-radius:16px;padding:18px 20px;">')
        H(f'<div style="font-size:13px;font-weight:700;color:{t["text"]};font-family:\'Sora\',sans-serif;margin-bottom:14px;">⚡ Quick Trade</div>')
        trade_tab=st.radio("",["Buy","Sell"],horizontal=True,key="trade_tab",label_visibility="collapsed")
        is_buy=trade_tab=="Buy"; tab_clr="#10b981"if is_buy else"#f43f5e"
        H(f'<div style="margin-top:8px;">')
        H(f'<div style="font-size:10px;font-weight:700;color:{t["sub"]};text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px;">Price (USDT)</div>')
        H(f'<div style="background:rgba(255,255,255,0.04);border:1.5px solid {tab_clr}44;border-radius:11px;padding:11px 14px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;">'
          f'<span style="font-size:14px;font-weight:700;color:{t["text"]};font-family:\'DM Mono\',monospace;">{fmt_price(price_now)}</span>'
          f'<span style="font-size:10px;color:{t["sub"]};">Market</span></div>')
        amount=st.number_input(f"Amount ({symbol})",min_value=0.0,value=0.1,step=0.01,format="%.4f",key="trade_amt")
        total_usdt=amount*price_now
        H(f'<div style="background:rgba(255,255,255,0.02);border:1px solid {t["border"]};border-radius:11px;padding:11px 14px;margin-bottom:14px;">'
          f'<div style="display:flex;justify-content:space-between;margin-bottom:5px;"><span style="font-size:11px;color:{t["sub"]};">Total</span><span style="font-size:13px;font-weight:700;color:{t["text"]};font-family:\'DM Mono\',monospace;">${total_usdt:,.2f}</span></div>'
          f'<div style="display:flex;justify-content:space-between;"><span style="font-size:11px;color:{t["sub"]};">Fee (0.1%)</span><span style="font-size:12px;color:{t["sub"]};font-family:\'DM Mono\',monospace;">${total_usdt*0.001:,.2f}</span></div></div>')
        H(f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:14px;">')
        for pct in ["25%","50%","75%","Max"]:
            H(f'<div style="text-align:center;padding:6px;background:{t["card2"]};border:1px solid {t["border"]};border-radius:8px;font-size:11px;font-weight:600;color:{t["sub"]};cursor:pointer;">{pct}</div>')
        H('</div>')
        if st.button(f"{'Buy'if is_buy else'Sell'} {symbol}",use_container_width=True,key="trade_btn"):
            st.success(f"✅ {'Buy'if is_buy else'Sell'} order placed: {amount:.4f} {symbol} @ {fmt_price(price_now)}")
        H('</div></div>')
    ft()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    inject_css()
    if not st.session_state.logged_in:
        login_page()
        return
    page=sidebar()
    dispatch={"Dashboard":page_dashboard,"Analytics":page_analytics,"Trading":page_trading,
               "Reports":page_reports,"Messages":page_messages,"Calendar":page_calendar,
               "Users":page_users,"Settings":page_settings}
    dispatch.get(page, page_dashboard)()

main()