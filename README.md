<div align="center">

<img src="https://img.shields.io/badge/₿-CryptoWave_Visualizer-6366f1?style=for-the-badge&logo=bitcoin&logoColor=white" alt="CryptoWave" height="50"/>

# 🌊 CryptoWave Visualizer

### *Decode Market Volatility with Mathematics & Python*

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-3F4F75?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?style=flat-square&logo=numpy&logoColor=white)](https://numpy.org)
[![License](https://img.shields.io/badge/License-MIT-10b981?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Live-34d399?style=flat-square&logo=checkmarx&logoColor=white)]()

[![GitHub](https://img.shields.io/badge/GitHub-View_Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Live_Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

<br/>

> **FA-2 Formative Assessment | Mathematics for AI-I | Year 1 | Artificial Intelligence**
>
> *A production-grade cryptocurrency volatility dashboard built with Python, Plotly & Streamlit — simulating market swings using sine waves, cosine waves, random noise, and real Bitcoin OHLCV data.*

<br/>

---

</div>

## 📋 Table of Contents

- [🎯 Project Overview](#-project-overview)
- [✨ Features](#-features)
- [🖥️ App Pages](#️-app-pages)
- [🧮 Mathematics Behind the App](#-mathematics-behind-the-app)
- [📂 Project Structure](#-project-structure)
- [⚙️ Installation & Setup](#️-installation--setup)
- [🚀 Deployment on Streamlit Cloud](#-deployment-on-streamlit-cloud)
- [🛠️ Tech Stack](#️-tech-stack)
- [📸 Screenshots](#-screenshots)
- [👤 Author](#-author)

---

## 🎯 Project Overview

**CryptoWave Visualizer** is a fully interactive web application built as part of the **FA-2 Formative Assessment** for the *Mathematics for AI-I* course. It bridges the gap between mathematical theory and real-world financial behaviour by:

- 📐 Using **sine, cosine, integrals, and random noise** functions to simulate cryptocurrency price patterns
- 📈 Visualising **real Bitcoin OHLCV data** (Open, High, Low, Close, Volume) with interactive Plotly charts
- 🎛️ Providing **slider controls** for amplitude, frequency, and drift to model market volatility
- 🟢🔴 Automatically **detecting and annotating stable vs volatile periods** using rolling standard deviation
- ☁️ Deployed live on **Streamlit Cloud** with a public URL

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **Login Page** | Secure sign-in with email/password or Google/GitHub OAuth |
| 🌗 **Dark / Light Mode** | Toggle between themes with full UI repainting |
| 📊 **8 Dashboard Pages** | Dashboard, Analytics, Trading, Reports, Messages, Calendar, Users, Settings |
| 🌊 **Wave Simulator** | Sine, Cosine, Random Noise, and Combined wave generators |
| 🎛️ **Interactive Sliders** | Amplitude (10–500), Frequency (0.5–5.0), Drift (-20 to +50) |
| 📂 **Real CSV Loader** | Loads actual Bitcoin price CSV with cleaning, timestamp conversion, and missing value handling |
| 🟢🔴 **Stable/Volatile Zones** | Automatic shaded region annotations on all charts |
| 💹 **Trading Page** | Candlestick chart with MA7/MA25, order book, news feed, buy/sell panel |
| 📄 **Reports** | Generate, view, and download reports as CSV, JSON, or TXT |
| 📅 **Calendar** | Event scheduler for March 2026 with upcoming events sidebar |
| 👥 **Users Analytics** | Real-time traffic stats by country with bar charts |
| ⚙️ **Settings** | Profile, notifications, security, appearance, billing, and language tabs |
| 📥 **Download Buttons** | Export simulation data in CSV, JSON, and TXT formats |

---

## 🖥️ App Pages
<img width="1907" height="972" alt="image" src="https://github.com/user-attachments/assets/db4cefe0-9b1b-4316-876b-b0b9234088bd" />

### 🏠 Dashboard
The main landing page after login. Shows:
<img width="1907" height="973" alt="image" src="https://github.com/user-attachments/assets/edbd1a3f-6acb-4dd0-9e87-7c5e63a67a56" />

- 4 KPI cards (Total Sales, Income, Sessions, Conversion Rate)
- Wave simulation engine with live chart updates on slider changes
- Bitcoin close price chart with **stable/volatile region annotations**
- Current Price, Avg Volatility, and Avg Day Range metrics

### 📊 Analytics
Deep-dive analysis page featuring:
<img width="1906" height="967" alt="image" src="https://github.com/user-attachments/assets/5c4b70e1-e443-4ad0-a334-2fce959c84e9" />

- **Monthly Volatility Distribution** bar chart
- **Daily High vs Low** comparison chart with shaded stable/volatile zones
- **Trading Volume** bar chart (green = price up, red = price down)
- **Rolling Volatility Index** with median threshold line
- **Dedicated Stable vs Volatile Price Chart** with annotated regions and legend
- 4 KPI tiles: Avg Volatility, Peak Price, Day Range Avg, Period Return

### 💹 Trading
Professional trading terminal with:
<img width="1906" height="971" alt="image" src="https://github.com/user-attachments/assets/e3e8596a-fa3e-4ee5-9cd5-da94a40ed9e7" />

- BTC/USDT and SOL/USDT asset selector
- 5 market KPI cards (Price, Market Cap, 24H Volume, High, Yearly High)
- **Candlestick chart** with volume subplot, MA7, MA25 overlays
- **Live Order Book** with bid/ask depth visualisation
- **News Feed** with tagged articles per asset
- Global Trading Sessions timeline (Asian, European, US)
- Market Statistics grid with Buy/Sell pressure bar
- Quick Trade panel with Buy/Sell toggle

### 📄 Reports
<img width="1903" height="972" alt="image" src="https://github.com/user-attachments/assets/a5569393-1639-4102-91fd-84962de2da63" />

- Report list table with type badges (PDF / CSV / Excel) and status badges
- One-click report generation
- Download buttons for CSV, JSON, TXT

### 📨 Messages
<img width="1907" height="975" alt="image" src="https://github.com/user-attachments/assets/1f869048-52b9-4b16-9307-1c7102cc69ea" />

- Threaded inbox with 4 pre-loaded conversations
- Chat bubble UI (sent/received)
- Send new messages with bot auto-reply

### 📅 Calendar
<img width="1907" height="970" alt="image" src="https://github.com/user-attachments/assets/bd7d53e4-3565-4f58-966f-0d52b30430c6" />

- Full March 2026 monthly calendar grid
- 5 pre-set events with colour-coded labels
- Add Event form via expander
- Upcoming events sidebar panel

### 👥 Users
<img width="1906" height="977" alt="image" src="https://github.com/user-attachments/assets/5d418376-1070-4b51-9596-e6653988fe66" />

- 3 live metric cards (Active Users, Live Simulations, Revenue)
- Country traffic breakdown with animated progress bars
- Bar chart of users by country

### ⚙️ Settings
<img width="1907" height="973" alt="image" src="https://github.com/user-attachments/assets/43643931-bae3-44b5-ba90-8bb42514062b" />

- **Profile** — Edit name, email, bio with save functionality
- **Notifications** — Toggle switches for email, push, alerts, digest
- **Security** — Password change form, 2FA toggle
- **Appearance** — Dark/light toggle, accent colour, font size
- **Billing** — Plan display, upgrade/cancel buttons
- **Language** — Language, timezone, date format selectors

---

## 🧮 Mathematics Behind the App

The simulation engine uses core mathematical functions from the course:

### 📐 Wave Functions

```python
# Sine Wave — smooth cyclical price oscillation
price = amplitude × sin(frequency × t)

# Cosine Wave — phase-shifted sine wave
price = amplitude × cos(frequency × t)

# Random Noise — models sudden unpredictable jumps
price = amplitude × cumsum(random.randn(n)) × 0.28

# Combined — realistic mix of wave + noise
price = (0.65 × amplitude × sin(freq × t)) + (0.35 × amplitude × cumsum(noise))
```

### 📈 Long-term Drift (Integral Approximation)

```python
# Linear drift simulates long-term upward or downward trend
drift_component = drift × cumsum(ones(n))  # ≈ ∫ drift dt
```

### 📉 Volatility Index (Rolling Standard Deviation)

```python
# Annualised rolling volatility — key risk metric
returns = Close.pct_change()
RollingStd = returns.rolling(14).std() × √252 × 100
```

### 🟢🔴 Stable vs Volatile Detection

```python
threshold = RollingStd.median()

# Volatile period: std > threshold  →  Red zone
# Stable period:   std ≤ threshold  →  Green zone
```

---

## 📂 Project Structure

```
CryptoWave-Visualizer/
│
├── app.py                  # Main Streamlit application (all pages + logic)
├── requirements.txt        # Python dependencies for deployment
└── README.md               # This file
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/cryptowave-visualizer.git
cd cryptowave-visualizer
```

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Run the App

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

### Login Credentials (Demo)
- Enter **any email and password** to sign in
- Or click **Google / GitHub** buttons for instant access

---

## 🚀 Deployment on Streamlit Cloud

### Step 1 — Create GitHub Repository

1. Go to [github.com](https://github.com) → **New Repository**
2. Name it `cryptowave-visualizer`
3. Upload these files:
   - `app.py`
   - `requirements.txt`

### Step 2 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your GitHub repository
4. Set **Main file path** → `app.py`
5. Click **Deploy**

Streamlit will build your app and give you a public URL like:
```
(https://cryptowavevisualizer.streamlit.app/)
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.8+** | Core programming language |
| **Streamlit** | Web app framework and deployment |
| **Plotly** | Interactive charts (line, bar, candlestick) |
| **Pandas** | Data loading, cleaning, manipulation |
| **NumPy** | Mathematical wave functions, random noise |
| **HTML/CSS** | Custom UI styling, gradients, animations |
| **GitHub** | Version control and hosting |
| **Streamlit Cloud** | Live deployment platform |

---

## 📸 Screenshots

| Page | Description |
|---|---|
| 🔐 Login | Split-panel login with animated particle background |
| 🏠 Dashboard | KPI cards + live wave simulation + BTC price chart |
| 📊 Analytics | 5 charts including stable/volatile annotated price chart |
| 💹 Trading | Candlestick + order book + news feed terminal |
| 📄 Reports | Downloadable reports table with status badges |
| 📅 Calendar | Full monthly calendar grid with event labels |

---

## 📐 Assessment Alignment

| Rubric Criteria | Implementation |
|---|---|
| ✅ **Data Preparation (5M)** | Real CSV loaded → timestamp converted → missing values handled → subset to 180 days → columns renamed |
| ✅ **Build Visualizations (10M)** | Line chart, High/Low comparison, Volume bar chart, Volatility index, Candlestick, Stable/Volatile annotations |
| ✅ **Streamlit Interface & Deployment (5M)** | 8-page app, sidebar sliders, live updates, key metrics, deployed on Streamlit Cloud with GitHub repo |

---

## 👤 Author

<div align="center">

| | |
|---|---|
| **Name** | Ankit Pradhan |
| **Roll Number** | 100390 |
| **School** | Viraj International School |
| **Programme** | Mathematics for AI-I |
| **Assessment** | FA-2 Formative Project |
| **Email** | ankitpradhana387@gmail.com |
| **GitHub** | [🔗(https://github.com/](https://github.com/Ankit4981/IDAI102-100390-CryptoWave-Visualizer/tree/main) |
| **Live App** | [🚀 (https://cryptowavevisualizer.streamlit.app/) |

</div>

---

<div align="center">

**Built with 💜 using Python · Streamlit · Plotly · Mathematics**

*CryptoWave Visualizer — Volatility Intelligence Engine*

`© 2026 CryptoWave Visualizer · Powered by Mathematics for AI`

</div>
