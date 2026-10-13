# ⚽ Football Player Performance Analytics Dashboard

An interactive, portfolio-quality football analytics dashboard built with **Python**, **Streamlit**, and **Plotly**.

> ⚠️ **Data Disclaimer:** All player and team data in this project is **entirely synthetic** and was generated programmatically for demonstration purposes. It does **not** represent real-world football statistics, players, or clubs.

---

## 📸 Features

| Page | What you get |
|---|---|
| **Overview** | KPI cards (players, goals, assists, minutes, rating) · Top 10 scorers · Goals by position donut · Rating histogram |
| **Player Analysis** | Goals vs Assists scatter · Shots vs Goals scatter · Radar comparison (2–5 players) · Searchable stats table |
| **Team Analysis** | Goals & Assists grouped bar · Avg rating · Squad depth · Team summary table |
| **Position Analysis** | Goals box plot · Pass accuracy violin · Squad composition · GK clean sheets · Position KPI table |

**Sidebar filters** — Season · Team · Position · Player · Min Rating · CSV download

---

## 🗂 Project Structure

```
football analytics dashboard/
├── app.py                  ← Main Streamlit application (single file)
├── football_players.csv    ← Synthetic dataset (240 rows · 21 columns)
├── requirements.txt        ← Python dependencies
└── README.md               ← This file
```

---

## 🚀 Local Setup

### Prerequisites
- Python **3.9** or higher
- `pip` package manager

### Steps

```bash
# 1. Clone or download the project
cd "football analytics dashboard"

# 2. (Recommended) Create a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**.

---

## 🌐 Deploy to Streamlit Community Cloud (Free)

1. Push this project to a **public GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"** → select your repository and branch.
4. Set **Main file path** to `app.py`.
5. Click **Deploy** — your app will be live within ~2 minutes.

No secrets or environment variables are required.

---

## 📊 Dataset Schema

The synthetic dataset (`football_players.csv`) has **240 rows** and **21 columns** (120 players × 2 seasons).

| Column | Type | Description |
|---|---|---|
| `player_id` | int | Unique player identifier (1–120) |
| `player_name` | str | Synthetic full name |
| `team` | str | One of 10 fictional Premier League-style clubs |
| `position` | str | GK / DEF / MID / FWD |
| `season` | str | 2022-23 or 2023-24 |
| `age` | int | Player age (18–36) |
| `nationality` | str | One of 10 nationalities |
| `matches_played` | int | Appearances (5–38) |
| `minutes_played` | int | Total minutes on pitch |
| `goals` | int | Goals scored (position-scaled) |
| `assists` | int | Assists (position-scaled) |
| `shots` | int | Total shots attempted |
| `shots_on_target` | int | Shots on target (30–70 % of shots) |
| `passes` | int | Passes completed |
| `pass_accuracy` | float | Pass accuracy percentage |
| `tackles` | int | Tackles made |
| `interceptions` | int | Interceptions |
| `yellow_cards` | int | Yellow card bookings |
| `red_cards` | int | Red cards |
| `clean_sheets` | int | Clean sheets (relevant for GK/DEF) |
| `rating` | float | Average match rating (1–10 scale) |

Two derived columns are computed at runtime and never stored in the CSV:

| Derived Column | Formula |
|---|---|
| `shot_conversion` | `goals / shots × 100` (0 if shots = 0) |
| `goals_per_90` | `goals / minutes_played × 90` |
| `assists_per_90` | `assists / minutes_played × 90` |

---

## 🛠 Technology Stack

| Library | Version | Purpose |
|---|---|---|
| Streamlit | ≥ 1.32 | Web app framework & UI |
| Pandas | ≥ 2.0 | Data loading, filtering, aggregation |
| NumPy | ≥ 1.26 | Vectorised calculations |
| Plotly | ≥ 5.20 | Interactive charts & radar graphs |

---

## 🎨 Design

- **Theme:** Dark, football-inspired UI with a professional pitch-green accent (`#00c853`)
- **Layout:** Wide Streamlit layout with responsive two-column sections
- **Charts:** Plotly dark template with custom colour palette
- **CSS:** Injected via `st.markdown` — no external CSS files required

---

## 📝 License

This project is released under the **MIT License**. Feel free to use, modify, and distribute it.

---

*Built with ❤️ using Python · Streamlit · Plotly · Pandas*
