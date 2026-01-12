# Data Visualization Agent (Standalone)

This is a standalone Streamlit application for AI-driven Data Visualization.

## Features
- **Upload CSV**: Load your dataset.
- **AI Design**: The agent analyzes your data and proposes a dashboard design based on business domain and style (Power BI, Tableau, etc.).
- **Code Generation**: The agent writes a complete, self-contained HTML/JS dashboard using Chart.js and TailwindCSS.
- **Live Preview**: See the dashboard instantly.
- **Download**: Export the dashboard as an HTML file.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```
3. **API Key**: Ensure you have `OPENROUTER_API_KEY` set in your environment, or configure it in `app.py`.
