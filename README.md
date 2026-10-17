# Weather Viewer & Analyzer 📊🌤️

A lightweight, production-ready Python data pipeline that collects real-time meteorological data, stores it in a local relational database, and performs automated barometric trend analysis to predict upcoming weather changes.

Built with a clean, modular architecture, this project serves as a practical demonstration of data pipeline engineering, robust error handling, and local storage optimization.

P.S. Written by Google AI

---

## 🏗️ Architecture & Component Design

The application is strictly decoupled into independent layers, following software engineering best practices:

*   **`main.py` (Orchestrator):** The central dispatcher managing the execution flow of the pipeline.
*   **`src/collector.py` (Data Ingestion):** Interacts with the Open-Meteo REST API using `requests`. Features adaptive exception handling (network drops, JSON parsing errors) and safe dictionary navigation via `.get()`.
*   **`src/storage.py` (Persistence Layer):** Manages an embedded `SQLite` database. Implements parameterization against SQL injections, utilizes transactions (`commit`), and includes an **Automated Data Purge Block** to safely rotate logs and prevent disk bloating.
*   **`src/processor.py` (Analytics Engine):** Extracts historical intervals using `sqlite3.Row` formatting. Runs a statistical barometric algorithm calculating multi-hour pressure and humidity deltas to derive forecasts.
*   **`src/display.py` (UX/UI Layer):** A terminal dashboard featuring data-driven dynamic visual anchors (emojis) and clean data formatting.

---

## 🚀 Key Engineering Features

1.  **Zero-Downtime Design:** Network operations are protected by explicit HTTP `timeout` parameters to prevent forever-hanging background processes in Linux.
2.  **Idempotency & Deduplication:** The storage layer enforces a `UNIQUE` constraint on time stamps via `INSERT OR IGNORE`. Running the pipeline multiple times within the same hour will never corrupt or duplicate data.
3.  **Self-Cleaning Infrastructure:** Automatic data rotation purges data older than 30 days, keeping the SQLite database footprint incredibly lightweight (~100 bytes per record).

---

## 📦 Installation & Setup (Debian / Ubuntu Linux)

### 1. Clone the repository and navigate to the project directory:
```bash
git clone https://github.com
cd weather_viewer
```

### 2. Isolate the environment using Python Virtual Environment (`venv`):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install required dependencies:
```bash
pip install -r requirements.txt
```

### 4. Run the application:
```bash
python3 main.py
```

---

## 📊 Dashboard Preview

When executed, the system outputs a responsive, structured dashboard directly to your terminal:

```text
=== [MAIN] Запуск метеорологического конвейера...
[Коллектор] Данные успешно получены за 2026-10-16T23:30

==================================================
       📊 МЕТЕОРОЛОГИЧЕСКИЙ ДАШБОРД (АСТАНА)       
       (Записей в локальной базе данных: 3)
==================================================
🕒 Время замера:     2026-10-16 23:30
🌡️  Температура:     2.4 °C
💧 Влажность:       68%
🧭 Давление:        986.6 гПа
💨 Скорость ветра:   2.9 м/с
--------------------------------------------------
📈 Анализ тренда:
   Давление: -0.1 гПа, Влажность: 0%
--------------------------------------------------
🔮 НАШ ПРОГНОЗ:
   🌤️ Погода останется стабильной в ближайшие часы.
==================================================
```

---

## 🛠️ Tech Stack & Dependencies

*   **Core Language:** Python 3.11+
*   **Database:** SQLite3 (Embedded Relational Database)
*   **Networking:** HTTP `requests` library
*   **Environment Isolation:** Python Virtual Environments (`.venv`)
