import streamlit as st
import pandas as pd
import requests
import io
import json
from langchain_openai import ChatOpenAI
import streamlit.components.v1 as components
import os
from style_utils import apply_apple_style

def generate_design_prompt(df_head, df_info, business_domain, report_type, api_key):
    """
    Analyzes data and generates a specific PROMPT for the coding agent.
    """
    try:
        llm = ChatOpenAI(
            model="google/gemini-3-flash-preview",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.3
        )
        
        system_prompt = f"You are a Senior Design Architect specializing in {report_type} dashboards."
        user_prompt = f"""
Goal: Write a strict, detailed INSTRUCTION PROMPT for a Frontend Developer to build a {report_type}-style dashboard.

Context:
- Domain: {business_domain}
- Style: {report_type} (Strictly mimic the layout, color palette, and component style of {report_type})
- Data Sample: {df_head}
- Data Info: {df_info}

Your Prompts MUST include:
1. Specific layout instructions typical of {report_type} (e.g., Tiled layout for Tableau, Canvas for Power BI).
2. Which specific columns to use for X and Y axes.
3. Which chart types (Bar, Line, etc.) are best for this data.
4. Color palette instructions matching {report_type}'s default themes.

Output only the PROMPT text that I will feed into the coding agent.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"Prompt generation failed: {e}"

def generate_dashboard_html(df_head, df_info, business_domain, report_type, design_safe_prompt, api_key):
    """
    Generates HTML dashboard using the generated prompt.
    """
    try:
        llm = ChatOpenAI(
            model="google/gemini-3-flash-preview",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.2
        )
        
        # specific layout rules
        layout_rules = ""
        if report_type == "Power BI":
            layout_rules = """
            - LAYOUT: Use a 'Canvas' style approach. Main container background #f3f2f1.
            - CARDS: White background (#ffffff) with subtle shadow (box-shadow: 0 4px 8px rgba(0,0,0,0.1)) and rounded corners (5px).
            - HEADER: Top navigation bar, left aligned title.
            - KPIs: Top row, distinct 'Card' visual.
            """
        elif report_type == "Tableau":
            layout_rules = """
            - LAYOUT: Tiled, dashboard grid layout. Minimal whitespace between containers.
            - FONT: Use a font similar to 'Tableau Book' or system sans-serif.
            - CONTAINERS: Distinct borders, white background.
            - LEGENDS: Floating or right-sidebar attached.
            """
        elif report_type == "Looker":
            layout_rules = """
            - LAYOUT: Top-heavy filter bar (gray/purple accent).
            - STYLE: Very flat design, no shadows.
            - FONTS: 'Open Sans' or 'Roboto'.
            - COLORS: Use Looker's default purple/gray palette for accents.
            """
        else: # Generic/Google Data Studio
             layout_rules = "- LAYOUT: Clean 2-column or 3-column grid. Standard Material Design vibes."

        system_prompt = f"""You are a Frontend Data Visualization Expert. 
Your goal is to write a SINGLE, self-contained HTML file that visualizes the provided data.

Style Preference: **{report_type}** 
STRICT LAYOUT RULES:
{layout_rules}

Requirements:
1. Use **TailwindCSS** for styling (via CDN).
2. Use **Chart.js**, **PapaParse**, and **SheetJS** (via CDN) for visualizations and client-side data swap.
3. The design must be modern, clean, and business-professional.
4. HYBRID LOADING: Pre-aggregate the data into `const initialData` JSON.
5. **CRITICAL**: The dashboard theme MUST be DARK. Use a deep navy or black background (#0f172a, #0b0f19). Use light-colored text (#f8fafc) and high-contrast vibrant chart colors that stand out.
6. **CLIENT-SIDE ENGINE**: Include a sleek button/uploader in the HTML that allows users to upload NEW CSV/XLSX files. When a new file is uploaded, the charts must update INSTANTLY using PapaParse/SheetJS without refreshing.
7. Return ONLY the raw HTML. No explanations.
"""

        user_prompt = f"""
Domain: {business_domain}
Data Sample:
{df_head}

Data Info:
{df_info}

DESIGN INSTRUCTIONS (Follow Strictly):
{design_safe_prompt}

Generate the full premium dashboard HTML now.
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = llm.invoke(messages)
        html_code = response.content.strip()
        
        # Cleanup
        import re
        html_match = re.search(r'```html\n(.*?)```', html_code, re.DOTALL) or re.search(r'```(.*?)```', html_code, re.DOTALL)
        if html_match:
            html_code = html_match.group(1).strip()
            
        return html_code

    except Exception as e:
        return f"Error generating dashboard: {e}"

def main():
    st.set_page_config(page_title="Data Viz Generator", page_icon=None, layout="wide")
    apply_apple_style()
    st.title("Data Visualization Agent")
    st.markdown("Upload data -> AI Analyzes -> AI Codes -> Live Dashboard.")

    # Sidebar Configuration
    st.sidebar.header("Configuration")
    
    # Secure API Key Loading
    api_key = os.getenv("GRAPH_API_KEY") or os.getenv("OPENROUTER_API_KEY", "your-api-key-here")
    
    business_domain = st.sidebar.selectbox(
        "Select Business Domain",
        ["Banking", "Utility", "Retail", "Healthcare", "Manufacturing", "Marketing", "Sales", "HR"]
    )
    
    report_type = st.sidebar.selectbox(
        "Dashboard Style",
        ["Power BI", "Tableau", "Looker", "QlikSense", "Google Data Studio"]
    )

    uploaded_file = st.file_uploader("Upload Data File (CSV or XLSX)", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Data Analysis
            st.write("### Data Snapshot")
            st.dataframe(df.head())
            
            df_head = df.head(100).to_csv(index=False)
            
            buffer = io.StringIO()
            df.info(buf=buffer)
            df_info = buffer.getvalue()
            
            st.info(f"Loaded {len(df)} rows. Agent is ready.")

            # Custom Instruction Box
            custom_instructions = st.text_area("Custom Instructions (Optional)", placeholder="e.g., Focus on regional sales trends, use deep blue accents...", help="Add specific details you want the AI to include in the dashboard design.")

            if st.button("Analyze & Generate Dashboard", type="primary"):
                if not api_key or api_key == "your-graph-api-key-here":
                    st.error("Please provide a valid API Key in the environment.")
                    return

                # Progress Bar UX
                progress_bar = st.progress(0, text="Analyzing dataset...")
                import time
                
                # 1. Prompt Generation Step
                for percent_complete in range(40):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete + 1, text="Engineering Design specifications...")
                
                generated_prompt = generate_design_prompt(df_head, df_info, business_domain, report_type, api_key)
                
                # 2. Code Generation Step
                for percent_complete in range(40, 90):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete + 1, text="Crafting HTML/JS Dashboard...")
                
                html_code = generate_dashboard_html(df_head, df_info, business_domain, report_type, generated_prompt + f"\n\nAdditional User Request: {custom_instructions}", api_key)
                
                for percent_complete in range(90, 100):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete + 1, text="Finalizing components...")
                
                progress_bar.empty()
                
                # 3. Output Handling
                if "Error" in html_code:
                    st.error(html_code)
                else:
                    # Red Glass/Alert Notes
                    st.markdown('<div style="color: #ff4b4b; background-color: #ffeaea; padding: 12px; border-radius: 8px; margin-bottom: 15px; font-weight: 500; border: 1px solid #ffcaca; text-align: center;">Please upload the data set below to the generated dashboard to get the accurate results</div>', unsafe_allow_html=True)
                    
                    st.markdown("""
                        <div style="
                            background: rgba(255, 75, 75, 0.1); 
                            backdrop-filter: blur(10px); 
                            -webkit-backdrop-filter: blur(10px);
                            border: 1px solid rgba(255, 75, 75, 0.2);
                            padding: 15px; 
                            border-radius: 12px; 
                            color: #ff4b4b; 
                            font-weight: 500; 
                            margin-bottom: 25px;
                            text-align: center;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                        ">
                            Please download the dashboard and open it using any browser. 
                            You can then upload data in the same format directly within the dashboard to dynamically change the visuals.
                        </div>
                    """, unsafe_allow_html=True)

                    # SECTION 1: PREVIEW
                    st.divider()
                    col_header, col_btn = st.columns([3, 1])
                    with col_header:
                        st.subheader(f"Live Data Preview ({report_type} Style)")
                    with col_btn:
                        st.download_button(
                            label="Download Dashboard",
                            data=html_code,
                            file_name="dashboard.html",
                            mime="text/html",
                            type="primary",
                            use_container_width=True
                        )
                    
                    components.html(html_code, height=800, scrolling=True)

                    # SECTION 2: PROMPT
                    st.divider()
                    with st.expander("View AI Design Prompt Used", expanded=False):
                        st.markdown(generated_prompt)

        except Exception as e:
            st.error(f"Error reading file: {e}")

if __name__ == "__main__":
    main()
