# 🌍 AI Trip Planner — Agentic Multi-Agent Travel Planning System

<div align="center">

![AI Trip Planner Banner](https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=200&section=header&text=AI%20Trip%20Planner&fontSize=50&fontColor=fff&animation=twinkling&fontAlignY=35&desc=Agentic%20Multi-Agent%20Travel%20Planning%20with%20LangGraph%20%2B%20Groq&descAlignY=55&descSize=18)

**Built with ❤️ by [Kaustav Roy Chowdhury](https://github.com/kaustavroy11)**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-FF6B6B?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-llama3--8b--instant-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev)
[![Tavily](https://img.shields.io/badge/Tavily-Search_API-00B4D8?style=for-the-badge&logo=searchengin&logoColor=white)](https://tavily.com)
[![OpenWeatherMap](https://img.shields.io/badge/OpenWeatherMap-Live_Weather-EB6E4B?style=for-the-badge&logo=openweathermap&logoColor=white)](https://openweathermap.org)
[![UV](https://img.shields.io/badge/uv-Package_Manager-DE5FE9?style=for-the-badge&logo=astral&logoColor=white)](https://docs.astral.sh/uv/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge)](https://github.com/kaustavroy11)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Live Demo Features](#-live-demo-features)
- [Architecture](#-architecture)
- [Agent Nodes](#-agent-nodes)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation with uv](#-installation-with-uv)
- [Environment Variables](#-environment-variables)
- [Running the App](#-running-the-app)
- [Currency Logic](#-currency-logic)
- [Output Format](#-output-format)
- [Troubleshooting](#-troubleshooting)
- [Author](#-author)

---

## 🎯 Overview

**AI Trip Planner** is a production-ready, **agentic multi-agent AI system** that generates complete,
structured travel plans for any destination in the world. Built for Indian travelers, it intelligently
handles **INR-based budgeting**, **live currency conversion**, **real-time weather**, and **hotel discovery**
— all powered by a collaborative network of specialized AI agents orchestrated through **LangGraph**.

> Think of it as your personal MakeMyTrip AI — but powered by LLMs, real-time search, and structured outputs.

### ✨ What Makes It Special

- 🤖 **8 Specialized AI Agents** collaborating via LangGraph state graph
- 💱 **Live Currency Conversion** — INR → Local Currency → USD automatically
- 🌤️ **Real-Time Weather** — Current conditions + 5-day forecast via OpenWeatherMap
- 🏨 **Hotel Discovery** — Real hotels with booking links (Booking.com / MakeMyTrip)
- 📅 **Day-wise Itinerary** — Clickable Google Maps links for every activity
- 📦 **Strict Pydantic Output** — Every response is validated structured JSON
- 🎨 **Elite Glassmorphism UI** — Dark gradient design with smooth interactions

---

## 🚀 Live Demo Features

| Feature | Description |
|---------|-------------|
| 🏙️ Destination Research | AI researches your destination using Tavily Search |
| 💰 Smart Budget Planning | Auto-splits budget into flights, hotels, food, activities, transport |
| 🏨 Hotel Recommendations | 3 real hotel options with ratings and booking links |
| 📅 Day-wise Itinerary | Full day plan with time slots and Google Maps links |
| ✈️ Transport Options | Flight/train/local transport with cost estimates |
| 🌤️ Live Weather | Real-time weather + 5-day forecast + travel tips |
| 💱 Currency Conversion | Auto-detects destination currency and converts all prices |
| 📊 Budget Charts | Interactive Plotly donut chart with breakdown table |
| ⬇️ JSON Export | Download complete trip plan as structured JSON |

---


## 🧠 Architecture

```text
User Input (Streamlit Sidebar)
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ LangGraph StateGraph │
│ │
│ START │
│ │ │
│ ▼ │
│ [1] Destination Research ──► Tavily Search + LLM Analysis │
│ │ City DB Fallback (25+ cities) │
│ ▼ │
│ [2] Currency Conversion ──► ExchangeRate API + Auto-detect │
│ │ INR → Local → USD │
│ ▼ │
│ [3] Weather Node ──► OpenWeatherMap API │
│ │ Current + 5-day Forecast │
│ ▼ │
│ [4] Budget Planner ──► Rule-based split (primary) │
│ │ LLM refinement (secondary) │
│ ▼ │
│ [5] Hotel Finder ──► Tavily Search + LLM │
│ │ Hardcoded fallback (always 3) │
│ ▼ │
│ [6] Itinerary Planner ──► Tavily + LLM + City Activity DB │
│ │ Generic templates fallback │
│ ▼ │
│ [7] Transport Node ──► Tavily Search + LLM │
│ │ Hardcoded domestic/intl fallback │
│ ▼ │
│ [8] Aggregator ──► Combines all into TripPlan │
│ │ Pydantic validation │
│ ▼ │
│ END │
└─────────────────────────────────────────────────────────────────┘

│
▼
Streamlit UI Display
├── 📍 Destination Card
├── 💱 Currency Info
├── 🌤️ Weather Widget (current + 5-day)
├── 💰 Budget Overview + Donut Chart
├── 🏨 Hotel Cards (clickable → booking)
├── 📅 Itinerary (expandable + Google Maps)
├── ✈️ Transport Options
├── 💡 AI Travel Tips
└── ⬇️ JSON Download

```

## 🤖 Agent Nodes

### Node 1 — Destination Research
- Uses **Tavily Search API** for real-time destination data
- Falls back to a **hardcoded city database** of 25+ cities (Kolkata, Paris, Tokyo, Bali, etc.)
- Extracts: country, currency code, weather, best time to visit, top highlights
- Detects: **domestic vs international** trip automatically

### Node 2 — Currency Conversion
- Calls **ExchangeRate API** for live rates
- Auto-detects destination currency from country name
- Sets up INR → Local → USD conversion rates for all downstream nodes

### Node 3 — Weather Node *(New)*
- Calls **OpenWeatherMap API** (geocoding + current + 5-day forecast)
- Falls back to **Tavily weather search** if no API key
- Generates **weather-based travel tips** (heat, rain, wind advice)

### Node 4 — Budget Planner
- **Rule-based split runs first** (guaranteed non-zero output)
- LLM refines if all values are valid and sum is correct
- Domestic vs international ratio logic
- Converts all amounts to multi-currency

### Node 5 — Hotel Finder
- Searches via **Tavily** for real hotels with booking URLs
- LLM extracts structured hotel data
- **Always returns 3 hotels** using hardcoded templates as fallback
- Booking links: Booking.com / MakeMyTrip / Goibibo

### Node 6 — Itinerary Planner
- Fetches real attractions via **Tavily**
- LLM creates time-slotted day plan
- Falls back to **city-specific activity templates** (pre-built for 13 cities)
- Every activity has a **Google Maps clickable link**

### Node 7 — Transport Node
- Researches flights, trains, local transport
- Domestic: Flight + IRCTC Train + Ola/Uber
- International: International Flight + Airport Transfer + Local Transport
- All booking links included

### Node 8 — Aggregator
- Combines all node outputs into one **validated `TripPlan`** Pydantic model
- Generates AI travel tips
- Emergency fallbacks for every missing field
- Returns clean structured JSON

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology |
|-------|-----------|
| 🧠 **LLM** | ![Groq](https://img.shields.io/badge/Groq-llama3--8b--instant-F55036?style=flat-square&logo=groq) |
| 🔗 **Agent Orchestration** | ![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-FF6B6B?style=flat-square&logo=langchain) |
| 🔍 **Web Search** | ![Tavily](https://img.shields.io/badge/Tavily-Search_API-00B4D8?style=flat-square) |
| 🌤️ **Weather** | ![OpenWeatherMap](https://img.shields.io/badge/OpenWeatherMap-API-EB6E4B?style=flat-square&logo=openweathermap) |
| 💱 **Currency** | ![ExchangeRate](https://img.shields.io/badge/ExchangeRate-API-4CAF50?style=flat-square&logo=currency) |
| 📦 **Validation** | ![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic) |
| 🎨 **UI** | ![Streamlit](https://img.shields.io/badge/Streamlit-1.39+-FF4B4B?style=flat-square&logo=streamlit) |
| 📊 **Charts** | ![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=flat-square&logo=plotly) |
| 📦 **Package Manager** | ![UV](https://img.shields.io/badge/uv-Fast_Package_Manager-DE5FE9?style=flat-square) |
| 🐍 **Language** | ![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python) |
| 💾 **Caching** | ![DiskCache](https://img.shields.io/badge/DiskCache-Persistent-FF9800?style=flat-square) |
| 🔁 **Retry Logic** | ![Tenacity](https://img.shields.io/badge/Tenacity-Exponential_Backoff-607D8B?style=flat-square) |

</div>

---

## 📁 Project Structure

```text

trip_planner/
│
├── 📄 main.py # CLI entry point for testing
├── 📄 streamlit_app.py # Main Streamlit UI application
├── 📄 requirements.txt # Python dependencies
├── 📄 pyproject.toml # uv project configuration
├── 📄 .env.example # Environment variable template
├── 📄 .env # Your actual API keys (git-ignored)
├── 📄 README.md # This file
│
├── 🤖 agents/
│ └── init.py
│
├── 🔗 nodes/ # LangGraph agent nodes
│ ├── init.py
│ ├── destination_research.py # Node 1: Destination + City DB
│ ├── currency_conversion.py # Node 2: Live currency rates
│ ├── weather_node.py # Node 3: OpenWeatherMap
│ ├── budget_planner.py # Node 4: Budget allocation
│ ├── hotel_finder.py # Node 5: Hotel discovery
│ ├── itinerary_planner.py # Node 6: Day-wise planning
│ ├── transport_node.py # Node 7: Transport options
│ └── aggregator.py # Node 8: Final aggregation
│
├── 🔀 graph/
│ ├── init.py
│ └── trip_graph.py # LangGraph StateGraph definition
│
├── 🧠 llm/
│ ├── init.py
│ └── groq_client.py # Groq API client with retry
│
├── 🛠️ tools/
│ ├── init.py
│ ├── tavily_search.py # Tavily search wrapper
│ ├── currency_converter.py # ExchangeRate API + fallbacks
│ └── weather_tool.py # OpenWeatherMap wrapper
│
├── 📦 models/
│ ├── init.py
│ └── trip_models.py # Pydantic models (TripPlan, etc.)
│
├── 🔧 utils/
│ ├── init.py
│ ├── logger.py # Centralized logging
│ ├── cache.py # DiskCache wrapper
│ └── retry.py # Tenacity retry decorators
│
└── 🎨 ui/
├── init.py
└── components.py # Streamlit UI components
```

---

## 📋 Prerequisites

Before you begin, make sure you have:

- **Python 3.11+** installed
- **uv** package manager installed
- API keys for the services below

### 🔑 Required API Keys

| Service | Purpose | Free Tier | Get Key |
|---------|---------|-----------|---------|
| **Groq** | LLM inference (llama3-8b-instant) | ✅ Free | [console.groq.com](https://console.groq.com) |
| **Tavily** | Web search for hotels & places | ✅ Free | [tavily.com](https://tavily.com) |
| **ExchangeRate API** | Live currency conversion | ✅ Free | [exchangerate-api.com](https://exchangerate-api.com) |
| **OpenWeatherMap** | Real-time weather data | ✅ Free | [openweathermap.org/api](https://openweathermap.org/api) |

---

## ⚡ Installation with uv

### Step 1 — Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version

```
### Step 2 — Clone the Repository

```bash
git clone https://github.com/kaustavroy11/ai-trip-planner.git
cd ai-trip-planner

```

### Step 3 — Create Project with uv 

```bash 
# Initialize uv project (if pyproject.toml doesn't exist)
uv init

# Create virtual environment
uv venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

```

### Step 4 — Install Dependencies 
```
# Install all dependencies using uv (much faster than pip)
uv add langgraph langchain langchain-groq langchain-community
uv add tavily-python pydantic streamlit plotly
uv add requests python-dotenv tenacity diskcache
uv add streamlit-extras altair

# Or install from requirements.txt
uv pip install -r requirements.txt
```

### Step 5 — Verify Installation 

```bash 
uv run python -c "import langgraph, streamlit, pydantic; print('✅ All packages installed!')"

``` 

# 🔐 Environment Variables 

### Create your .env file

```bash 
cp .env.example .env

```

### Edit .env with your API keys

```env
# ── Required ──────────────────────────────────────────────────
# Groq API Key (LLM - llama3-8b-instant)
# Get free key at: https://console.groq.com
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Tavily Search API Key (Web search for hotels, places, weather)
# Get free key at: https://tavily.com
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ── Optional but Recommended ──────────────────────────────────
# ExchangeRate API Key (Live currency conversion)
# Get free key at: https://www.exchangerate-api.com
# Falls back to hardcoded rates if not set
EXCHANGE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenWeatherMap API Key (Real-time weather + 5-day forecast)
# Get free key at: https://openweathermap.org/api
# Falls back to Tavily weather search if not set
OPENWEATHER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx

```
# 🚀 Running the App

## Option 1 — Streamlit UI (Recommended)

```bash
# Using uv
uv run streamlit run streamlit_app.py

# Or with activated venv
streamlit run streamlit_app.py 

```

### Option 2 — CLI Test

```bash
# Test the graph directly without UI
uv run python main.py

```

### Option 3 — Run with Custom Port
```bash

streamlit run streamlit_app.py --server.port 8080

```

# 💱 Currency Logic

```text
The system automatically handles currency based on destination:

text

User always inputs budget in INR (Indian Rupees ₹)
                    │
                    ▼
         Detect destination country
                    │
          ┌─────────┴──────────┐
          │                    │
    India (Domestic)    International
          │                    │
    Show INR only       Show all three:
                        ├── ₹ INR (base)
                        ├── Local Currency
                        │   (THB, EUR, USD, etc.)
                        └── $ USD (reference)

```

### Supported Currencies (50+)

Region	Currencies
🌏 Asia	THB, JPY, SGD, MYR, IDR, PHP, VND, KRW, CNY, HKD
🌍 Europe	EUR, GBP, CHF, SEK, NOK, DKK
🌎 Americas	USD, CAD, BRL, MXN
🌏 South Asia	INR, NPR, LKR, BDT, MVR, BTN, PKR
🌍 Middle East	AED, QAR, SAR, KWD, BHD, OMR
🌍 Africa	ZAR, KES, NGN, GHS, EGP, MAD

# 📦 Output Format
Every trip plan is returned as strict validated JSON via Pydantic:

```JSON

{
  "destination": "Paris",
  "country": "France",
  "is_domestic": false,
  "currency": {
    "base": "INR",
    "local": "EUR",
    "usd": "USD",
    "exchange_rate_inr_to_local": 0.011,
    "exchange_rate_inr_to_usd": 0.012
  },
  "duration_days": 7,
  "budget": {
    "inr": 200000,
    "local": 2200.0,
    "usd": 2400.0
  },
  "budget_breakdown": {
    "flights":    { "inr": 76000, "local": 836.0, "usd": 912.0 },
    "hotels":     { "inr": 56000, "local": 616.0, "usd": 672.0 },
    "food":       { "inr": 28000, "local": 308.0, "usd": 336.0 },
    "activities": { "inr": 24000, "local": 264.0, "usd": 288.0 },
    "transport":  { "inr": 16000, "local": 176.0, "usd": 192.0 }
  },
  "weather": {
    "current": {
      "temperature_c": 18.5,
      "condition": "Partly Cloudy",
      "emoji": "⛅",
      "humidity_pct": 72
    },
    "forecast": [ "... 5 days ..." ]
  },
  "hotels": [
    {
      "name": "Hotel Le Marais Paris",
      "price_per_night": { "inr": 8000, "local": 88.0, "usd": 96.0 },
      "rating": 4.2,
      "location": "Le Marais, Paris",
      "booking_link": "https://www.booking.com/..."
    }
  ],
  "itinerary": [
    {
      "day": 1,
      "date_note": "Day 1 — Arrival & Eiffel Tower",
      "plan": [
        {
          "time": "10:00 AM",
          "activity": "Visit Eiffel Tower",
          "place": "Eiffel Tower, Paris",
          "place_link": "https://www.google.com/maps/search/Eiffel+Tower+Paris"
        }
      ]
    }
  ],
  "transport": [
    {
      "mode": "International Flight",
      "provider": "Air India / IndiGo",
      "estimated_cost": { "inr": 76000, "local": 836.0, "usd": 912.0 },
      "booking_link": "https://www.makemytrip.com/flights/international/"
    }
  ],
  "tips": [
    "Book Eiffel Tower tickets online to skip long queues",
    "Get a Paris Museum Pass for unlimited entry to 50+ museums"
  ]
}
```

# 🐛 Troubleshooting
### Common Issues & Fixes
### ❌ Raw HTML showing on screen
``` bash

# This was a known bug - fixed in current version
# Make sure you have the latest ui/components.py
# All HTML is now single-line with _e() escaping

```

### ❌ Hotels / Itinerary showing empty
```bash

# Check your GROQ_API_KEY and TAVILY_API_KEY
# The system now has hardcoded fallbacks - should always show data
# Check logs for errors:
streamlit run streamlit_app.py --logger.level=debug
```
### ❌ Budget showing ₹0
```bash

# Fixed: rule-based split now runs first
# LLM only overrides if all values are valid (>0)
# Clear cache if issue persists:
python -c "from utils.cache import clear_cache; clear_cache()"
```
### ❌ Weather not showing
```bash

# Add OPENWEATHER_API_KEY to .env
# Get free key at: https://openweathermap.org/api
# System falls back to Tavily if key missing
```
### ❌ Currency not converting
```bash

# Add EXCHANGE_API_KEY to .env
# Get free key at: https://exchangerate-api.com
# System uses hardcoded fallback rates if key missing
```
### ❌ Groq rate limit errors
```bash

# The system has built-in retry with exponential backoff
# Wait 30 seconds and try again
# Consider using a paid Groq plan for production
```
### Clear Cache
```bash

python -c "from utils.cache import clear_cache; clear_cache(); print('Cache cleared!')"
```
# Check Logs
```bash

# Logs are saved to logs/ directory
tail -f logs/trip_planner_$(date +%Y%m%d).log
```
# 🗺️ Supported Cities (Built-in Database)
The system has a hardcoded database for instant fallback when APIs fail:

- 🇮🇳 Indian Cities:
Kolkata · Mumbai · Delhi · Goa · Jaipur · Kerala · Agra · Bangalore · Hyderabad · Varanasi · Chennai · Shimla · Manali

- 🌍 International:
Bangkok · Paris · Dubai · Singapore · Tokyo · Bali · London · New York · Maldives · Sri Lanka · Nepal

# 📈 Performance & Production Notes
Feature	Detail
Caching	DiskCache — 500MB limit, 1-2hr TTL for API responses
Retry Logic	Tenacity — 3 attempts, exponential backoff (1s → 10s)
Rate Limiting	500ms minimum between Groq API calls
Fallback Chain	Every node: LLM → City DB → Generic Template
Response Time	30-90 seconds for full plan generation
JSON Validation	Pydantic v2 validates every field with type safety
# 🤝 Contributing
Contributions are welcome! Here's how:

```bsh

# Fork the repo, then:
git clone https://github.com/YOUR_USERNAME/ai-trip-planner.git
cd ai-trip-planner

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, then
git commit -m "✨ Add: your feature description"
git push origin feature/your-feature-name

# Open a Pull Request
```
# 📄 License
```text

MIT License

Copyright (c) 2025 Kaustav Roy Chowdhury

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```
- See LICENSE for full text.

# 👨‍💻 Author

<div align="center">

**Kaustav Roy Chowdhury**

[GitHub](https://github.com/KaustavWayne) • [LinkedIn](https://linkedin.com/in/kaustavroychowdhury) • [Email](mailto:krc.app7@gmail.com)

*Built with passion for AI, travel, and clean code 🌍✈️*

</div>

---

<div align="center">

### ⭐ Star this repo if it helped you! ⭐

© 2026 Kaustav Roy Chowdhury — AI Trip Planner

</div>