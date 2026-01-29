# Data Visualization Agent

A premium, AI-powered Streamlit application that transforms raw datasets into professional, interactive dashboards in a matter of seconds.

## Features

- **Multi-Model Support**: Powered by Gemini 3 Flash for advanced design and code generation.
- **Dynamic Data Engine**: Generates self-contained HTML dashboards with built-in **PapaParse** and **SheetJS** support, allowing for real-time data updates in the browser.
- **Minimalist Aesthetic**: Features a clean, "Apple-style" UI with zero clutter and a focus on high-density information.
- **Interactive Previews**: Preview your dashboard directly in the app before downloading.
- **Custom Instructions**: Tailor the output with specific design or data requirements.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Set your OpenRouter or Gemini API key as an environment variable:
   ```bash
   export OPENROUTER_API_KEY="your-api-key-here"
   # OR
   export GRAPH_API_KEY="your-api-key-here"
   ```

3. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Upload Data**: Upload a CSV file to begin.
2. **Review Insights**: The AI will automatically analyze your data structure.
3. **Customize**: Add any specific instructions for the visual style or chart focus.
4. **Generate**: Click "Analyze & Generate Dashboard" to create your interactive visual.
5. **Download**: Use the download button to save your standalone dashboard for offline use or sharing.
