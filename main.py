import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from dateutil.relativedelta import relativedelta
import requests
from io import StringIO
import calendar
import re

# Set page configuration
st.set_page_config(
    page_title="Joiners & Leavers Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to improve dashboard appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2563EB;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E40AF;
    }
    .metric-label {
        font-size: 1rem;
        color: #4B5563;
        margin-top: 0.25rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        background-color: #E5E7EB;
        border-radius: 4px 4px 0px 0px;
        gap: 1rem;
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #DBEAFE;
        color: #1E40AF;
    }
    div[data-testid="stSidebarNav"] {
        background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAABmJLR0QA/wD/AP+gvaeTAAADmUlEQVR4nO2ZT0gUURzHv29mZ2cVIwqEoEMWaGEY+A+i6GJFkZ06FGV0KOhQEFF0KugsRBR0CaJLkWDSoajwoGKQFUUUVKcIs0NbtLq77rzpMCvq7O782t1Z3Tecz+n3Zmbe5/t+v/eb3wOUSCQSiUQikUgkEolEIpFIsgM57o/v9sgnZxcrLYA7ABZQ0RYF/kCY0EG1Hqg7X/PZcU+uO58dH6D7bvoatIY7RDg+XVMCekGEuoHz1XesrGeJfG2w8NZGzg7MUA4AOFQIGhvoG75p1XOGM4AC1+GsEADbFWKHrHpmPgCxCEI+CxaA7RQTm616Zj4ABY4SXO7HqkPmA8BYFN3WLnK8QIgI+mCEP88CfQA5XiDshNGmBu9MkCxwCbLH8QKRDUgPUDrA6QE52oI52opOD1Bg8yWYrYegiL8FiQjlW5B4hAeAg6lQFlCZ+TkgiwgPAJGvBUJTcggSn/AAYOYLIFZzgOPTYjYRGwAFJH0AqJAeQEJzgHAPC4QGgH0t4LAjpIB9TZlcCAuAP7HI7xsMgNNjsYUCNwQFgA1j6psMgLLI8QKBAdApPcDkFihGDxAYAIMJ8j9FMAEWikE9ZkzJAkFYAFR6AKUHCA4ATXnxE+1rYeF5YCYA9HkONmSOF0gTeBRLpkmA6iluXyBtV+h+U3Sb2bQZJcjXFPP8ATTBivoVf5hcRIhpAtCUHyqAhWXHCPJbsCGWU7QeIDMNyQ2QWQ9QVwLGu4l5viD2lBRogsbzBnGNmA9ISzAzAeIewyI6w+Q6wt4CQnqAgAC4W4HS6wFiAkBTArD8YJQgvgJ+SQ8QGoCUHkCIZ4RiZhZQ0xAkeoCgAJDzHUFtJfgk9wOAa74FcQjWCAkNgIj9gJr7QvQ/zWAu8gfSA4QG4M8kON0DKOYzdJxFxAWAeITUFJg1BQaNWvD5PgClON0BZCZkPcDPfQwEBYDdHaBovQMKLKgzLCwA3BngXyCBPcCMh1gPcLwD1L06QGCB0CzgsgcoQFk4Gxsyfj+gGM8DwgLA1QOU1fuA+z2AWQVx3QGyswsxM1f6ZFhYAJTJDpDy4s/cDWIR4QFgGpPh4s0BYgLAU/6+1/tZ05RWgjFlOvVG6yt99c1WPWf0afCJZ4Ptl9RowhcCXXBZkwj61GhkdLi54b3dWvMCF99tm97rHqsmRvUEKifCemaumvh9fWTSC2KD5Pf4PaG5xvSP/HpkdHTks5WWEolEIpFIJBKJRCKRuJVfnNvzt/2UcCUAAAAASUVORK5CYII=');
        background-repeat: no-repeat;
        padding-top: 100px;
        background-position: 20px 20px;
    }
    .stDataFrame {
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        overflow: hidden;
    }
    .custom-filter-section {
        background-color: #F9FAFB;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .plotly-chart {
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        background-color: white;
        padding: 1rem;
    }
    div[data-testid="stSidebar"] > div:first-child {
        background-color: #F3F4F6;
    }
</style>
""", unsafe_allow_html=True)

# Login system
def check_password():
    """Returns `True` if the user enters the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        return True

    password = st.sidebar.text_input("Enter Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        if password == "joiners2025":
            st.session_state.authenticated = True
            st.sidebar.success("Login successful!")
            st.experimental_rerun()
            return True
        else:
            st.sidebar.error("Incorrect password")
            return False
    
    return False

# Data loading and processing
@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    try:
        # First try to load data from GitHub
        url = "https://raw.githubusercontent.com/username/repository/main/2023_Joiners_Leavers.csv"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            data = StringIO(response.text)
            df = pd.read_csv(data)
            st.toast("✅ Data successfully loaded from GitHub")
        except:
            # If GitHub fails, try to load from local file
            try:
                df = pd.read_csv("2023_Joiners_Leavers.csv")
                st.toast("✅ Data loaded from local file")
            except:
                # Create sample data for demo purposes
                st.warning("⚠️ Could not load data from GitHub or local file. Using sample data.")
                df = create_sample_data()
                
        # Clean and preprocess data
        df = clean_data(df)
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return create_sample_data()

def create_sample_data():
    """Create sample data for demonstration purposes"""
    # Create a date range for the past 2 years
    today = datetime.datetime.now()
    start_date = today - datetime.timedelta(days=730)
    date_range = pd.date_range(start=start_date, end=today, freq='10D')
    
    # Create sample names
    names = ['John Smith', 'Sarah Davis', 'Michael Johnson', 'Jessica Brown', 
             'David Miller', 'Lisa Wilson', 'Robert Taylor', 'Jennifer Garcia',
             'James Martinez', 'Mary Williams', 'Thomas Robinson', 'Patricia Clark',
             'Charles Rodriguez', 'Linda Lewis', 'Daniel Lee', 'Elizabeth Hall']
    
    # Create sample data
    data = []
    for i in range(100):
        start_date = date_range[np.random.randint(0, len(date_range)-20)]
        end_date = None
        
        # 40% chance of being a leaver
        if np.random.random() < 0.4:
            end_date = start_date + datetime.timedelta(days=np.random.randint(90, 550))
            if end_date > today:
                end_date = None
        
        name = np.random.choice(names)
        estimated_book = np.random.randint(100000, 2000000)
        ttm = estimated_book * (0.8 + np.random.random() * 0.4)  # 80-120% of estimated
        annualized = ttm * (0.9 + np.random.random() * 0.3)  # 90-120% of TTM
        variance = annualized - estimated_book
        
        data.append({
            'Start Date': start_date.strftime('%Y-%m-%d'),
            'Leave Date': end_date.strftime('%Y-%m-%d') if end_date else None,
            'Attorney Name': name,
            'Start Year': start_date.year,
            'Estimated Book': estimated_book,
            'TTM': ttm,
            'Annualized': annualized,
            'Variance to Est': variance,
            'Department': np.random.choice(['Litigation', 'Corporate', 'IP', 'Tax', 'Family Law']),
            'Office': np.random.choice(['New York', 'Chicago', 'Los Angeles', 'Miami', 'Austin'])
        })
    
    df = pd.DataFrame(data)
    return df

def clean_data(df):
    """Clean and preprocess the data"""
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # Check if we need to find header rows (real data might need this)
    if 'Unnamed' in str(df.columns[0]):
        # Find the header row based on column content
        potential_headers = df.iloc[:20].apply(lambda row: sum(['date' in str(val).lower() or 
                                                              'name' in str(val).lower() or
                                                              'book' in str(val).lower() 
                                                              for val in row]), axis=1)
        if potential_headers.max() >= 3:
            header_idx = potential_headers.idxmax()
            df.columns = df.iloc[header_idx]
            df = df.iloc[header_idx+1:].reset_index(drop=True)
    
    # Clean column names
    df.columns = [str(col).strip() for col in df.columns]
    
    # Rename columns if needed
    column_mapping = {}
    
    # Try to identify attorney name column if it doesn't exist
    if 'Attorney Name' not in df.columns:
        name_pattern = re.compile(r'(attorney|name|lawyer|person)', re.IGNORECASE)
        name_cols = [col for col in df.columns if name_pattern.search(str(col))]
        if name_cols:
            column_mapping[name_cols[0]] = 'Attorney Name'
    
    # Try to identify date columns
    date_pattern = re.compile(r'(start.*date|join.*date)', re.IGNORECASE)
    start_date_cols = [col for col in df.columns if date_pattern.search(str(col))]
    if start_date_cols and 'Start Date' not in df.columns:
        column_mapping[start_date_cols[0]] = 'Start Date'
    
    leave_pattern = re.compile(r'(leave.*date|end.*date|depart.*date)', re.IGNORECASE)
    leave_date_cols = [col for col in df.columns if leave_pattern.search(str(col))]
    if leave_date_cols and 'Leave Date' not in df.columns:
        column_mapping[leave_date_cols[0]] = 'Leave Date'
    
    # Apply column renaming
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    # Identify required columns, or try to find close matches
    required_cols = [
        'Start Date', 'Leave Date', 'Attorney Name', 'Estimated Book', 
        'TTM', 'Annualized', 'Variance to Est'
    ]
    
    # Find and convert date columns
    date_cols = [col for col in df.columns if 'date' in str(col).lower()]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Make sure Start Date is in datetime format
    if 'Start Date' in df.columns:
        df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
        # Add Start Year column if it doesn't exist
        if 'Start Year' not in df.columns:
            df['Start Year'] = df['Start Date'].dt.year
    
    # Make sure Leave Date is in datetime format
    if 'Leave Date' in df.columns:
        df['Leave Date'] = pd.to_datetime(df['Leave Date'], errors='coerce')
    
    # Convert numeric columns
    numeric_cols = ['Estimated Book', 'TTM', 'Annualized', 'Variance to Est', 'Start Year']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Fill NaN values for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # Replace any remaining NaN with appropriate values
    df.fillna({'Leave Date': pd.NaT}, inplace=True)
    
    # Add calculated fields
    if 'Start Date' in df.columns and 'Leave Date' in df.columns:
        # Calculate tenure (months employed)
        today = pd.Timestamp.today()
        df['End Date For Calc'] = df['Leave Date'].fillna(today)
        df['Tenure Months'] = ((df['End Date For Calc'] - df['Start Date']).dt.days / 30.44).round(1)
        df.drop('End Date For Calc', axis=1, inplace=True)
    
    return df

# KPI calculations
def calculate_kpis(df):
    """Calculate key performance indicators"""
    kpis = {}
    
    # Total estimated book value
    if 'Estimated Book' in df.columns:
        kpis['total_estimated_book'] = df['Estimated Book'].sum()
    else:
        kpis['total_estimated_book'] = 0
    
    # Total annualized billings/revenue
    if 'Annualized' in df.columns:
        kpis['total_annualized'] = df['Annualized'].sum()
    else:
        kpis['total_annualized'] = 0
    
    # Total variance to estimate
    if 'Variance to Est' in df.columns:
        kpis['total_variance'] = df['Variance to Est'].sum()
    else:
        kpis['total_variance'] = 0
    
    # Annualized revenue per attorney
    if 'Attorney Name' in df.columns and 'Annualized' in df.columns:
        num_attorneys = df['Attorney Name'].nunique()
        if num_attorneys > 0:
            kpis['revenue_per_attorney'] = kpis['total_annualized'] / num_attorneys
        else:
            kpis['revenue_per_attorney'] = 0
    else:
        kpis['revenue_per_attorney'] = 0
    
    # Joiners and leavers counts
    if 'Leave Date' in df.columns:
        kpis['joiners_count'] = len(df[df['Leave Date'].isna()])
        kpis['leavers_count'] = len(df[df['Leave Date'].notna()])
        
        # Calculate retention rate
        if len(df) > 0:
            kpis['retention_rate'] = (kpis['joiners_count'] / len(df)) * 100
        else:
            kpis['retention_rate'] = 0
    else:
        kpis['joiners_count'] = len(df)
        kpis['leavers_count'] = 0
        kpis['retention_rate'] = 100
    
    # Average tenure (for all attorneys and for leavers)
    if 'Tenure Months' in df.columns:
        kpis['avg_tenure_months'] = df['Tenure Months'].mean()
        leavers_df = df[df['Leave Date'].notna()]
        if not leavers_df.empty:
            kpis['avg_leaver_tenure_months'] = leavers_df['Tenure Months'].mean()
        else:
            kpis['avg_leaver_tenure_months'] = 0
    else:
        kpis['avg_tenure_months'] = 0
        kpis['avg_leaver_tenure_months'] = 0
    
    return kpis

# Time-based analysis functions
def monthly_joiners_leavers(df):
    """Calculate monthly joiners and leavers for trend analysis"""
    if 'Start Date' not in df.columns or df.empty:
        return pd.DataFrame()
    
    # Ensure dates are in datetime format
    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
    
    # Get valid dates only
    valid_start_dates_df = df.dropna(subset=['Start Date'])
    
    # Create monthly joiners counts
    if not valid_start_dates_df.empty:
        # Group by year and month
        valid_start_dates_df['Year-Month'] = valid_start_dates_df['Start Date'].dt.to_period('M')
        monthly_joiners = valid_start_dates_df.groupby('Year-Month').size().reset_index(name='Joiners')
        monthly_joiners['Date'] = monthly_joiners['Year-Month'].dt.to_timestamp()
    else:
        monthly_joiners = pd.DataFrame(columns=['Date', 'Joiners'])
    
    # Create monthly leavers counts (if Leave Date is available)
    if 'Leave Date' in df.columns:
        df['Leave Date'] = pd.to_datetime(df['Leave Date'], errors='coerce')
        valid_leave_dates_df = df.dropna(subset=['Leave Date'])
        
        if not valid_leave_dates_df.empty:
            valid_leave_dates_df['Year-Month'] = valid_leave_dates_df['Leave Date'].dt.to_period('M')
            monthly_leavers = valid_leave_dates_df.groupby('Year-Month').size().reset_index(name='Leavers')
            monthly_leavers['Date'] = monthly_leavers['Year-Month'].dt.to_timestamp()
        else:
            monthly_leavers = pd.DataFrame(columns=['Date', 'Leavers'])
    else:
        monthly_leavers = pd.DataFrame(columns=['Date', 'Leavers'])
    
    # Combine joiners and leavers
    if not monthly_joiners.empty and not monthly_leavers.empty:
        monthly_combined = pd.merge(monthly_joiners, monthly_leavers, on='Date', how='outer')
    elif not monthly_joiners.empty:
        monthly_combined = monthly_joiners
        monthly_combined['Leavers'] = 0
    elif not monthly_leavers.empty:
        monthly_combined = monthly_leavers
        monthly_combined['Joiners'] = 0
    else:
        return pd.DataFrame()
    
    # Fill NaN values with 0
    monthly_combined = monthly_combined.fillna(0)
    
    # Calculate net change
    monthly_combined['Net Change'] = monthly_combined['Joiners'] - monthly_combined['Leavers']
    
    # Sort by date
    monthly_combined = monthly_combined.sort_values('Date')
    
    # Calculate running total (cumulative sum of net change)
    monthly_combined['Cumulative Change'] = monthly_combined['Net Change'].cumsum()
    
    return monthly_combined

def quarterly_growth(df):
    """Calculate quarterly growth based on estimated book values"""
    if 'Start Date' not in df.columns or 'Estimated Book' not in df.columns or df.empty:
        return pd.DataFrame()
    
    # Ensure dates are in datetime format
    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
    
    # Get valid records only
    valid_df = df.dropna(subset=['Start Date'])
    
    if not valid_df.empty:
        # Create quarter column
        valid_df['Quarter'] = valid_df['Start Date'].dt.to_period('Q')
        
        # For joiners
        joiners_df = valid_df[valid_df['Leave Date'].isna()]
        joiners_by_quarter = joiners_df.groupby('Quarter')['Estimated Book'].sum().reset_index(name='Joiners Book')
        
        # For leavers
        if 'Leave Date' in valid_df.columns:
            leavers_df = valid_df[valid_df['Leave Date'].notna()]
            leavers_by_quarter = leavers_df.groupby('Quarter')['Estimated Book'].sum().reset_index(name='Leavers Book')
        else:
            leavers_by_quarter = pd.DataFrame(columns=['Quarter', 'Leavers Book'])
        
        # Combine data
        if not joiners_by_quarter.empty and not leavers_by_quarter.empty:
            quarterly_data = pd.merge(joiners_by_quarter, leavers_by_quarter, on='Quarter', how='outer')
        elif not joiners_by_quarter.empty:
            quarterly_data = joiners_by_quarter
            quarterly_data['Leavers Book'] = 0
        elif not leavers_by_quarter.empty:
            quarterly_data = leavers_by_quarter
            quarterly_data['Joiners Book'] = 0
        else:
            return pd.DataFrame()
            
        # Fill NaN values with 0
        quarterly_data = quarterly_data.fillna(0)
        
        # Calculate net growth
        quarterly_data['Net Growth'] = quarterly_data['Joiners Book'] - quarterly_data['Leavers Book']
        
        # Sort by quarter
        quarterly_data = quarterly_data.sort_values('Quarter')
        
        # Add human-readable quarter label
        quarterly_data['Quarter Label'] = quarterly_data['Quarter'].astype(str)
        
        return quarterly_data
    
    return pd.DataFrame()

def department_performance(df):
    """Analyze performance by department if department data exists"""
    if 'Department' not in df.columns:
        return None
    
    if not df.empty and 'Estimated Book' in df.columns:
        # Group by department
        dept_data = df.groupby('Department').agg({
            'Estimated Book': 'sum',
            'Annualized': 'sum',
            'Attorney Name': 'nunique',
            'Variance to Est': 'sum'
        }).reset_index()
        
        # Calculate revenue per attorney by department
        dept_data['Revenue per Attorney'] = dept_data['Annualized'] / dept_data['Attorney Name'].where(dept_data['Attorney Name'] > 0, 1)
        
        # Calculate performance ratio (Annualized / Estimated)
        dept_data['Performance Ratio'] = (dept_data['Annualized'] / dept_data['Estimated Book'].where(dept_data['Estimated Book'] > 0, 1)) * 100
        
        return dept_data
    
    return None

def create_attorney_heatmap_data(df):
    """Create data for attorney performance heatmap"""
    if 'Attorney Name' not in df.columns or 'Estimated Book' not in df.columns or 'Start Date' not in df.columns:
        return None
    
    # Ensure dates are in datetime format
    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
    
    # Add month and year columns
    df['Month'] = df['Start Date'].dt.month
    df['Month Name'] = df['Start Date'].dt.strftime('%b')
    
    # Create pivot table: attorneys vs months with estimated book values
    pivot_data = df.pivot_table(
        values='Estimated Book',
        index='Attorney Name',
        columns='Month Name',
        aggfunc='sum',
        fill_value=0
    )
    
    # Reorder columns by month
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ordered_cols = [col for col in month_order if col in pivot_data.columns]
    if ordered_cols:
        pivot_data = pivot_data[ordered_cols]
    
    return pivot_data

# Visualization functions
def create_kpi_cards(kpis):
    """Create visual KPI cards"""
    
    # Row 1: Financial KPIs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">${:,.0f}</div>
            <div class="metric-label">Total Estimated Book Value</div>
        </div>
        """.format(kpis['total_estimated_book']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">${:,.0f}</div>
            <div class="metric-label">Total Annualized Revenue</div>
        </div>
        """.format(kpis['total_annualized']), unsafe_allow_html=True)
    
    with col3:
        variance = kpis['total_variance']
        color = "#10B981" if variance >= 0 else "#EF4444"
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value" style="color: {};">${:,.0f}</div>
            <div class="metric-label">Overall Variance to Estimate</div>
        </div>
        """.format(color, variance), unsafe_allow_html=True)
    
    # Row 2: Operational KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">${:,.0f}</div>
            <div class="metric-label">Revenue per Attorney</div>
        </div>
        """.format(kpis['revenue_per_attorney']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{:,}</div>
            <div class="metric-label">Active Attorneys</div>
        </div>
        """.format(kpis['joiners_count']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{:,}</div>
            <div class="metric-label">Leavers</div>
        </div>
        """.format(kpis['leavers_count']), unsafe_allow_html=True)
    
    with col4:
        retention_color = "#10B981" if kpis['retention_rate'] >= 80 else (
            "#FBBF24" if kpis['retention_rate'] >= 70 else "#EF4444")
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value" style="color: {};">{:.1f}%</div>
            <div class="metric-label">Retention Rate</div>
        </div>
        """.format(retention_color, kpis['retention_rate']), unsafe_allow_html=True)

def plot_joiners_leavers_trend(monthly_data):
    """Create plot for joiners and leavers trend"""
    if monthly_data.empty:
        st.info("No valid time-series data available for trend visualization.")
        return
    
    # Create plotly figure with dual axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add joiners and leavers bars
    fig.add_trace(
        go.Bar(
            x=monthly_data['Date'],
            y=monthly_data['Joiners'],
            name="Joiners",
            marker_color='#3B82F6',
            hovertemplate='<b>%{x|%b %Y}</b><br>Joiners: %{y}<extra></extra>'
        ),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Bar(
            x=monthly_data['Date'],
            y=monthly_data['Leavers'],
            name="Leavers",
            marker_color='#EF4444',
            hovertemplate='<b>%{x|%b %Y}</b><br>Leavers: %{y}<extra></extra>'
        ),
        secondary_y=False,
    )
    
    # Add net change line
    fig.add_trace(
        go.Scatter(
            x=monthly_data['Date'],
            y=monthly_data['Net Change'],
            name="Net Change",
            line=dict(color='#10B981', width=3, dash='solid'),
            hovertemplate='<b>%{x|%b %Y}</b><br>Net Change: %{y}<extra></extra>'
        ),
        secondary_y=False,
    )
    
    # Add cumulative change line on secondary axis
    fig.add_trace(
        go.Scatter(
            x=monthly_data['Date'],
            y=monthly_data['Cumulative Change'],
            name="Cumulative Change",
            line=dict(color='#8B5CF6', width=3, dash='dot'),
            hovertemplate='<b>%{x|%b %Y}</b><br>Cumulative Change: %{y}<extra></extra>'
        ),
        secondary_y=True,
    )
    
    # Update layout
    fig.update_layout(
        title='Monthly Joiners and Leavers Trend',
        xaxis_title='',
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        hovermode='x unified',
        margin=dict(l=60, r=30, t=50, b=60),
        height=450
    )
    
    # Set y-axes titles
    fig.update_yaxes(title_text="Monthly Count", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative Change", secondary_y=True)
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def plot_quarterly_growth(quarterly_data):
    """Create plot for quarterly growth"""
    if quarterly_data.empty:
        st.info("No valid quarterly data available for growth visualization.")
        return
    
    # Create plotly figure
    fig = go.Figure()
    
    # Add bars for joiners and leavers book values
    fig.add_trace(
        go.Bar(
            x=quarterly_data['Quarter Label'],
            y=quarterly_data['Joiners Book'],
            name="Joiners Book Value",
            marker_color='#3B82F6',
            hovertemplate='<b>%{x}</b><br>Joiners Book Value: $%{y:,.0f}<extra></extra>'
        )
    )
    
    fig.add_trace(
        go.Bar(
            x=quarterly_data['Quarter Label'],
            y=-quarterly_data['Leavers Book'],  # Negative to show below x-axis
            name="Leavers Book Value",
            marker_color='#EF4444',
            hovertemplate='<b>%{x}</b><br>Leavers Book Value: $%{y:,.0f}<extra></extra>'
        )
    )
    
    # Add line for net growth
    fig.add_trace(
        go.Scatter(
            x=quarterly_data['Quarter Label'],
            y=quarterly_data['Net Growth'],
            name="Net Growth",
            line=dict(color='#10B981', width=4),
            mode='lines+markers',
            marker=dict(size=10),
            hovertemplate='<b>%{x}</b><br>Net Growth: $%{y:,.0f}<extra></extra>'
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Quarterly Book Value Growth',
        xaxis_title='Quarter',
        yaxis_title='Book Value ($)',
        barmode='relative',  # Use relative to show positive above and negative below x-axis
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        hovermode='x unified',
        margin=dict(l=60, r=30, t=50, b=60),
        height=450
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def plot_department_performance(dept_data):
    """Create plots for department performance"""
    if dept_data is None or dept_data.empty:
        st.info("No department data available for visualization.")
        return
    
    # Create two-column layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Department Book Value and Revenue
        fig1 = go.Figure()
        
        fig1.add_trace(
            go.Bar(
                x=dept_data['Department'],
                y=dept_data['Estimated Book'],
                name="Estimated Book",
                marker_color='#3B82F6',
                hovertemplate='<b>%{x}</b><br>Estimated Book: $%{y:,.0f}<extra></extra>'
            )
        )
        
        fig1.add_trace(
            go.Bar(
                x=dept_data['Department'],
                y=dept_data['Annualized'],
                name="Annualized Revenue",
                marker_color='#10B981',
                hovertemplate='<b>%{x}</b><br>Annualized Revenue: $%{y:,.0f}<extra></extra>'
            )
        )
        
        fig1.update_layout(
            title='Department Financial Performance',
            xaxis_title='',
            yaxis_title='Value ($)',
            barmode='group',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='white',
            height=350
        )
        
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        # Revenue per Attorney by Department
        fig2 = go.Figure()
        
        color_scale = px.colors.sequential.Blues[3:]  # Get a subset of the Blues color scale
        performance_colors = []
        
        for ratio in dept_data['Performance Ratio']:
            if ratio >= 100:
                performance_colors.append('#10B981')  # Green for good performance
            elif ratio >= 90:
                performance_colors.append('#FBBF24')  # Yellow for average performance
            else:
                performance_colors.append('#EF4444')  # Red for poor performance
        
        fig2.add_trace(
            go.Bar(
                x=dept_data['Department'],
                y=dept_data['Revenue per Attorney'],
                marker_color=color_scale,
                text=dept_data['Attorney Name'],
                textposition='auto',
                hovertemplate=(
                    '<b>%{x}</b><br>' +
                    'Revenue per Attorney: $%{y:,.0f}<br>' +
                    'Number of Attorneys: %{text}<extra></extra>'
                )
            )
        )
        
        fig2.update_layout(
            title='Revenue per Attorney by Department',
            xaxis_title='',
            yaxis_title='Revenue per Attorney ($)',
            plot_bgcolor='white',
            height=350
        )
        
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    
    # Performance Ratio Chart
    fig3 = go.Figure()
    
    fig3.add_trace(
        go.Bar(
            x=dept_data['Department'],
            y=dept_data['Performance Ratio'],
            marker=dict(
                color=performance_colors,
                line=dict(width=1, color='#000000')
            ),
            text=dept_data['Performance Ratio'].round(1),
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Performance Ratio: %{y:.1f}%<extra></extra>'
        )
    )
    
    # Add a line at 100%
    fig3.add_shape(
        type='line',
        x0=-0.5,
        y0=100,
        x1=len(dept_data['Department'])-0.5,
        y1=100,
        line=dict(
            color='rgba(0, 0, 0, 0.7)',
            width=2,
            dash='dash'
        )
    )
    
    fig3.update_layout(
        title='Department Performance Ratio (Annualized / Estimated Book)',
        xaxis_title='',
        yaxis_title='Performance Ratio (%)',
        plot_bgcolor='white',
        height=300,
        yaxis=dict(
            range=[min(60, min(dept_data['Performance Ratio'])*0.9), 
                   max(140, max(dept_data['Performance Ratio'])*1.1)]
        )
    )
    
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

def plot_heatmap(pivot_data):
    """Create a heatmap visualization for attorney performance"""
    if pivot_data is None or pivot_data.empty:
        st.info("No data available for heatmap visualization.")
        return
    
    # Create a custom colorscale from light to dark blue
    colorscale = [
        [0, '#EBF5FF'],  # Lightest blue
        [0.2, '#DBEAFE'],
        [0.4, '#93C5FD'],
        [0.6, '#60A5FA'],
        [0.8, '#3B82F6'],
        [1, '#1E40AF']   # Darkest blue
    ]
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale=colorscale,
        hovertemplate='<b>%{y}</b><br>%{x}: $%{z:,.0f}<extra></extra>',
        colorbar=dict(title='Book Value ($)')
    ))
    
    fig.update_layout(
        title='Attorney Performance Heatmap by Month',
        xaxis_title='Month',
        yaxis_title='Attorney',
        height=max(400, len(pivot_data) * 30),  # Dynamic height based on number of attorneys
        margin=dict(l=150, r=50, t=50, b=50),
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def display_recent_activity(df):
    """Display recent joiners and leavers"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recent Joiners")
        if 'Start Date' in df.columns and 'Attorney Name' in df.columns:
            recent_joiners = df.sort_values('Start Date', ascending=False).head(5)
            
            # Format data for display
            if 'Leave Date' in df.columns:
                joiners_df = recent_joiners[recent_joiners['Leave Date'].isna()]
            else:
                joiners_df = recent_joiners
            
            if not joiners_df.empty:
                display_cols = ['Start Date', 'Attorney Name']
                if 'Estimated Book' in df.columns:
                    display_cols.append('Estimated Book')
                if 'Department' in df.columns:
                    display_cols.append('Department')
                
                # Apply formatting
                formatted_joiners = joiners_df[display_cols].copy()
                if 'Estimated Book' in formatted_joiners.columns:
                    formatted_joiners['Estimated Book'] = formatted_joiners['Estimated Book'].apply(lambda x: f"${x:,.0f}")
                if 'Start Date' in formatted_joiners.columns:
                    formatted_joiners['Start Date'] = formatted_joiners['Start Date'].dt.strftime('%b %d, %Y')
                
                st.dataframe(formatted_joiners, hide_index=True, use_container_width=True)
            else:
                st.info("No recent joiners data available.")
        else:
            st.info("Joiners data not available.")
    
    with col2:
        st.subheader("Recent Leavers")
        if 'Leave Date' in df.columns and 'Attorney Name' in df.columns:
            leavers_df = df[df['Leave Date'].notna()].sort_values('Leave Date', ascending=False).head(5)
            
            if not leavers_df.empty:
                display_cols = ['Leave Date', 'Attorney Name']
                if 'Estimated Book' in df.columns:
                    display_cols.append('Estimated Book')
                if 'Department' in df.columns:
                    display_cols.append('Department')
                if 'Tenure Months' in df.columns:
                    display_cols.append('Tenure Months')
                
                # Apply formatting
                formatted_leavers = leavers_df[display_cols].copy()
                if 'Estimated Book' in formatted_leavers.columns:
                    formatted_leavers['Estimated Book'] = formatted_leavers['Estimated Book'].apply(lambda x: f"${x:,.0f}")
                if 'Leave Date' in formatted_leavers.columns:
                    formatted_leavers['Leave Date'] = formatted_leavers['Leave Date'].dt.strftime('%b %d, %Y')
                
                st.dataframe(formatted_leavers, hide_index=True, use_container_width=True)
            else:
                st.info("No recent leavers data available.")
        else:
            st.info("Leavers data not available.")

# Main application
def main():
    # Check authentication
    if not check_password():
        st.markdown('<h1 class="main-header">Joiners & Leavers Dashboard</h1>', unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; padding: 2rem; background-color: #F3F4F6; border-radius: 0.5rem;">
                <h2 style="color: #1E40AF;">Please log in to access the dashboard</h2>
                <p>Enter your password in the sidebar to continue.</p>
            </div>
        """, unsafe_allow_html=True)
        return
    
    # Dashboard header
    st.markdown('<h1 class="main-header">Joiners & Leavers Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_data()
    
    # Sidebar filters
    st.sidebar.markdown("### Filters")
    
    # Date range filter
    if 'Start Date' in df.columns and not df['Start Date'].isna().all():
        min_date = df['Start Date'].min().date()
        max_date = df['Start Date'].max().date()
        
        date_range = st.sidebar.date_input(
            "Date Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            df = df[(df['Start Date'] >= start_date) & (df['Start Date'] <= end_date)]
    
    # Year filter
    if 'Start Year' in df.columns:
        years = sorted(df['Start Year'].dropna().unique().astype(int).tolist())
        if years:
            selected_years = st.sidebar.multiselect(
                "Year",
                options=years,
                default=years
            )
            if selected_years:
                df = df[df['Start Year'].isin(selected_years)]
    
    # Attorney filter
    if 'Attorney Name' in df.columns:
        attorneys = sorted(df['Attorney Name'].unique().tolist())
        selected_attorneys = st.sidebar.multiselect(
            "Attorney",
            options=attorneys,
            default=[]
        )
        if selected_attorneys:
            df = df[df['Attorney Name'].isin(selected_attorneys)]
    
    # Department filter
    if 'Department' in df.columns:
        departments = sorted(df['Department'].unique().tolist())
        selected_departments = st.sidebar.multiselect(
            "Department",
            options=departments,
            default=[]
        )
        if selected_departments:
            df = df[df['Department'].isin(selected_departments)]
    
    # Office filter
    if 'Office' in df.columns:
        offices = sorted(df['Office'].unique().tolist())
        selected_offices = st.sidebar.multiselect(
            "Office",
            options=offices,
            default=[]
        )
        if selected_offices:
            df = df[df['Office'].isin(selected_offices)]
    
    # Calculate KPIs from filtered data
    kpis = calculate_kpis(df)
    
    # Create tabs for different views
    tabs = st.tabs([
        "📊 Overview", 
        "📈 Trends", 
        "🔄 Joiners & Leavers", 
        "📊 Department Analysis",
        "🔥 Heatmap"
    ])
    
    # Tab 1: Overview
    with tabs[0]:
        # Display KPI cards
        create_kpi_cards(kpis)
        
        st.markdown('<h2 class="sub-header">Recent Activity</h2>', unsafe_allow_html=True)
        display_recent_activity(df)
        
        # Quarterly growth chart
        st.markdown('<h2 class="sub-header">Quarterly Book Value Growth</h2>', unsafe_allow_html=True)
        quarterly_data = quarterly_growth(df)
        plot_quarterly_growth(quarterly_data)
    
    # Tab 2: Trends
    with tabs[1]:
        st.markdown('<h2 class="sub-header">Joiners and Leavers Trends</h2>', unsafe_allow_html=True)
        monthly_data = monthly_joiners_leavers(df)
        plot_joiners_leavers_trend(monthly_data)
        
        # Display trend data table
        with st.expander("View Detailed Trend Data"):
            if not monthly_data.empty:
                # Format date for display
                formatted_monthly = monthly_data.copy()
                formatted_monthly['Date'] = formatted_monthly['Date'].dt.strftime('%b %Y')
                
                # Round numeric columns
                numeric_cols = ['Joiners', 'Leavers', 'Net Change', 'Cumulative Change']
                formatted_monthly[numeric_cols] = formatted_monthly[numeric_cols].round(0).astype(int)
                
                st.dataframe(formatted_monthly[['Date', 'Joiners', 'Leavers', 'Net Change', 'Cumulative Change']], 
                             use_container_width=True)
            else:
                st.info("No trend data available.")
    
    # Tab 3: Joiners & Leavers
    with tabs[2]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h2 class="sub-header">Joiners Data</h2>', unsafe_allow_html=True)
            if 'Leave Date' in df.columns:
                joiners_df = df[df['Leave Date'].isna()]
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(joiners_df)}</div>
                    <div class="metric-label">Total Joiners</div>
                </div>
                """, unsafe_allow_html=True)
                
                if not joiners_df.empty:
                    # Display additional joiners stats
                    if 'Estimated Book' in joiners_df.columns:
                        col1a, col1b = st.columns(2)
                        with col1a:
                            st.metric("Total Estimated Book", f"${joiners_df['Estimated Book'].sum():,.0f}")
                        with col1b:
                            if 'Annualized' in joiners_df.columns:
                                st.metric("Total Annualized Revenue", f"${joiners_df['Annualized'].sum():,.0f}")
                    
                    # Display joiners data table
                    display_cols = ['Start Date', 'Attorney Name']
                    if 'Estimated Book' in df.columns:
                        display_cols.append('Estimated Book')
                    if 'Annualized' in df.columns:
                        display_cols.append('Annualized')
                    if 'Department' in df.columns:
                        display_cols.append('Department')
                    
                    st.dataframe(joiners_df[display_cols].sort_values('Start Date', ascending=False), 
                                 use_container_width=True)
                else:
                    st.info("No joiners data available for the selected filters.")
            else:
                st.info("Leave Date column not found. Cannot identify joiners.")
        
        with col2:
            st.markdown('<h2 class="sub-header">Leavers Data</h2>', unsafe_allow_html=True)
            if 'Leave Date' in df.columns:
                leavers_df = df[df['Leave Date'].notna()]
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(leavers_df)}</div>
                    <div class="metric-label">Total Leavers</div>
                </div>
                """, unsafe_allow_html=True)
                
                if not leavers_df.empty:
                    # Display additional leavers stats
                    if 'Estimated Book' in leavers_df.columns:
                        col2a, col2b = st.columns(2)
                        with col2a:
                            st.metric("Total Estimated Book", f"${leavers_df['Estimated Book'].sum():,.0f}")
                        with col2b:
                            if 'Tenure Months' in leavers_df.columns:
                                st.metric("Avg. Tenure (Months)", f"{leavers_df['Tenure Months'].mean():.1f}")
                    
                    # Display leavers data table
                    display_cols = ['Leave Date', 'Attorney Name']
                    if 'Estimated Book' in df.columns:
                        display_cols.append('Estimated Book')
                    if 'Tenure Months' in df.columns:
                        display_cols.append('Tenure Months')
                    if 'Department' in df.columns:
                        display_cols.append('Department')
                    
                    st.dataframe(leavers_df[display_cols].sort_values('Leave Date', ascending=False), 
                                 use_container_width=True)
                else:
                    st.info("No leavers data available for the selected filters.")
            else:
                st.info("Leave Date column not found. Cannot identify leavers.")
    
    # Tab 4: Department Analysis
    with tabs[3]:
        st.markdown('<h2 class="sub-header">Department Performance Analysis</h2>', unsafe_allow_html=True)
        dept_data = department_performance(df)
        
        if dept_data is not None and not dept_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(
                    dept_data[['Department', 'Attorney Name', 'Estimated Book', 'Annualized']]
                    .sort_values('Annualized', ascending=False),
                    use_container_width=True,
                    column_config={
                        'Department': 'Department',
                        'Attorney Name': 'Number of Attorneys',
                        'Estimated Book': st.column_config.NumberColumn('Estimated Book', format="$%d"),
                        'Annualized': st.column_config.NumberColumn('Annualized Revenue', format="$%d")
                    }
                )
            
            with col2:
                st.dataframe(
                    dept_data[['Department', 'Revenue per Attorney', 'Performance Ratio', 'Variance to Est']]
                    .sort_values('Revenue per Attorney', ascending=False),
                    use_container_width=True,
                    column_config={
                        'Department': 'Department',
                        'Revenue per Attorney': st.column_config.NumberColumn('Revenue per Attorney', format="$%d"),
                        'Performance Ratio': st.column_config.NumberColumn('Performance Ratio', format="%0.1f%%"),
                        'Variance to Est': st.column_config.NumberColumn('Variance to Estimate', format="$%d")
                    }
                )
            
            # Department visualizations
            plot_department_performance(dept_data)
        else:
            st.info("Department data not available for analysis. Make sure the dataset includes a 'Department' column.")
    
    # Tab 5: Heatmap
    with tabs[4]:
        st.markdown('<h2 class="sub-header">Attorney Performance Heatmap</h2>', unsafe_allow_html=True)
        pivot_data = create_attorney_heatmap_data(df)
        plot_heatmap(pivot_data)
        
        with st.expander("View Heatmap Data"):
            if pivot_data is not None and not pivot_data.empty:
                # Format the data for better display
                formatted_pivot = pivot_data.copy()
                for col in formatted_pivot.columns:
                    formatted_pivot[col] = formatted_pivot[col].apply(lambda x: f"${x:,.0f}")
                
                # Add a total column
                formatted_pivot['Total'] = pivot_data.sum(axis=1).apply(lambda x: f"${x:,.0f}")
                
                st.dataframe(formatted_pivot, use_container_width=True)
            else:
                st.info("No data available for heatmap.")
    
    # Download filtered data button
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="Download Filtered Data",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='filtered_joiners_leavers_data.csv',
        mime='text/csv',
    )
    
    # Add timestamp and data info
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Data Updated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.sidebar.markdown(f"**Records:** {len(df)} shown of {len(load_data())} total")

if __name__ == "__main__":
    main()
