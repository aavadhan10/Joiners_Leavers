import streamlit as st
import pandas as pd
import hashlib
import os
from datetime import datetime

# Attempt to import matplotlib and seaborn, handle potential ModuleNotFoundError
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_MATPLOTLIB = True
except ModuleNotFoundError as e:
    HAS_MATPLOTLIB = False
    st.warning(f"Matplotlib and/or Seaborn not found. Charts will not be displayed. Error: {e}")

# Attempt to import streamlit_option_menu, handle potential ModuleNotFoundError
try:
    from streamlit_option_menu import option_menu
    HAS_OPTION_MENU = True
except ModuleNotFoundError as e:
    HAS_OPTION_MENU = False
    st.warning(f"streamlit_option_menu not found. Tabbed navigation will not be displayed. Error: {e}")

# Password Protection
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# DB Management
hashed_psw = "b0efc7bd43f799c50dae1c9624717f18a54c10b835305c85f8185610b0b06e0d"  # Hashed "joiners2025"

def login():
    """Handle user login and return authentication status"""
    password = st.sidebar.text_input("Password", type='password', placeholder="Enter password: joiners2025")
    login_button = st.sidebar.checkbox("Login")

    if login_button:
        if check_hashes(password, hashed_psw):
            st.success("Successfully logged in")
            st.session_state['logged_in'] = True
            return True
        else:
            st.warning("Incorrect password")
            st.session_state['logged_in'] = False
            return False
    return st.session_state.get('logged_in', False)

def load_data():
    """Load and preprocess data from CSV file"""
    try:
        df = pd.read_csv("2023_Joiners_Leavers.csv")
    except FileNotFoundError:
        st.error("Error: Could not find the file '2023_Joiners_Leavers.csv'. Make sure the file is in the same directory as your script, or provide the correct path.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()
    
    # Fill NaN values with 0 for numeric columns only
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # Process date columns
    date_columns = [col for col in df.columns if "Date" in col]
    for col in date_columns:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        except Exception as e:
            st.warning(f"Warning: Could not convert column '{col}' to datetime. Error: {e}")
    
    # Clean column names
    df.columns = [str(col).replace("Unnamed: ", "") for col in df.columns]
    
    # Attempt to find the header row based on billings/collections keywords
    try:
        potential_header_rows = df[df.apply(lambda row: row.astype(str).str.contains('Billings|Collections').any(), axis=1)].index
        if len(potential_header_rows) > 0:
            header_row_index = potential_header_rows.min() + 4  # Add offset to get to actual header
            if header_row_index < len(df):
                df.columns = df.iloc[header_row_index]
                df = df.iloc[header_row_index + 1:]
                # Drop rows with all zeros or NaN
                df = df.dropna(how='all')
                df = df[(df.select_dtypes(include=['number']) != 0).any(axis=1)]
    except Exception as e:
        st.warning(f"Warning: Could not process header rows properly. Using original columns. Error: {e}")
    
    # Convert numeric columns
    for col in df.columns:
        if col in ['Start Year', 'Estimated Book', 'TTM', 'Annualized', 'Variance to Est'] or isinstance(col, (int, float)):
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except Exception:
                # If conversion fails, leave as is
                pass
    
    return df

# --- Data Analysis Functions ---
def calculate_quarterly_growth(df):
    """Calculate quarterly growth based on estimated book values"""
    try:
        # Make sure Start Date is datetime
        df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
        # Only use rows with valid dates
        df = df.dropna(subset=['Start Date'])
        # Create quarter periods
        df['Quarter'] = df['Start Date'].dt.to_period('Q')
        # Group by quarter and sum estimated book
        quarterly_growth = df.groupby('Quarter')['Estimated Book'].sum().reset_index()
        quarterly_growth.rename(columns={'Estimated Book': 'Net Growth'}, inplace=True)
        return quarterly_growth
    except Exception as e:
        st.warning(f"Could not calculate quarterly growth: {e}")
        return pd.DataFrame(columns=['Quarter', 'Net Growth'])

def calculate_annualized_revenue_per_attorney(df, attorney_column):
    """Calculates the annualized revenue per attorney for the selected period."""
    try:
        # Check if the attorney column exists
        if attorney_column not in df.columns:
            st.warning(f"Column '{attorney_column}' not found. Cannot calculate revenue per attorney.")
            return 0
            
        total_annualized_revenue = df['Annualized'].sum()
        # Count unique attorneys
        num_attorneys = df[attorney_column].nunique()
        
        if num_attorneys > 0:
            revenue_per_attorney = total_annualized_revenue / num_attorneys
            return revenue_per_attorney
        else:
            return 0
    except Exception as e:
        st.warning(f"Could not calculate revenue per attorney: {e}")
        return 0

# --- Streamlit App ---
def main():
    # Initialize session state for login
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Check login status
    if not login():
        return

    st.title("Joiners and Leavers Dashboard")

    # Load data
    df = load_data()
    
    # Determine the attorney column - look for common names in columns
    attorney_column = None
    potential_attorney_cols = [col for col in df.columns if any(name in str(col).lower() for name in 
                                                               ['attorney', 'lawyer', 'name', 'person'])]
    
    if len(potential_attorney_cols) > 0:
        attorney_column = potential_attorney_cols[0]
    elif 'J Paul Gignac' in df.columns:
        attorney_column = 'J Paul Gignac'
    else:
        # Find columns with string values that might contain names
        string_cols = df.select_dtypes(include=['object']).columns
        if len(string_cols) > 0:
            attorney_column = string_cols[0]  # Use the first string column as fallback
    
    # --- Sidebar Filters ---
    st.sidebar.header("Filters")

    # Date range filter - handle potential missing or invalid dates
    start_date_min = datetime.now().date()
    start_date_max = datetime.now().date()
    
    if 'Start Date' in df.columns and not df['Start Date'].isna().all():
        valid_dates = df['Start Date'].dropna()
        if not valid_dates.empty:
            start_date_min = valid_dates.min().date()
            start_date_max = valid_dates.max().date()

    try:
        date_range = st.sidebar.date_input("Select Date Range",
                                        value=[start_date_min, start_date_max],
                                        min_value=start_date_min,
                                        max_value=start_date_max)
        if len(date_range) == 2:
            start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        else:
            start_date, end_date = pd.to_datetime(start_date_min), pd.to_datetime(start_date_max)
    except Exception as e:
        st.warning(f"Error with date range selection: {e}")
        start_date, end_date = pd.to_datetime(start_date_min), pd.to_datetime(start_date_max)

    # Year filter
    if 'Start Year' in df.columns:
        years = sorted(df['Start Year'].dropna().unique().tolist())
        if years:
            selected_years = st.sidebar.multiselect("Select Year(s)", options=years, default=years)
        else:
            selected_years = []
            st.sidebar.text("No years available to filter")
    else:
        selected_years = []
        st.sidebar.text("Start Year column not found")

    # Person/attorney filter
    filtered_df = df.copy()
    
    if attorney_column:
        people = sorted(df[attorney_column].dropna().unique().tolist())
        if people:
            selected_people = st.sidebar.multiselect("Select Person(s)", options=people, default=people)
            if selected_people:
                filtered_df = filtered_df[filtered_df[attorney_column].isin(selected_people)]
        else:
            st.sidebar.text("No people available to filter")
    else:
        st.warning("No suitable column found for person filtering")

    # Apply date and year filters
    if 'Start Date' in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df['Start Date'] >= start_date) & 
                                 (filtered_df['Start Date'] <= end_date)]
    
    if 'Start Year' in filtered_df.columns and selected_years:
        filtered_df = filtered_df[filtered_df['Start Year'].isin(selected_years)]

    # --- Navigation Menu ---
    if HAS_OPTION_MENU:
        selected_tab = option_menu(
            menu_title=None,
            options=["Overview", "Joiners", "Leavers", "Growth", "Financials", "Monthly Trends", "Heatmap"],
            icons=["house", "person-plus", "person-dash", "graph-up", "cash-coin", "calendar", "grid-3x3"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
        )
    else:
        selected_tab = st.selectbox("Select Tab", 
                                  ["Overview", "Joiners", "Leavers", "Growth", "Financials", "Monthly Trends", "Heatmap"])

    # --- Tab Contents ---
    if selected_tab == "Overview":
        st.header("Dashboard Overview")

        # Metric Row 1
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'Estimated Book' in filtered_df.columns:
                total_estimated_book = filtered_df['Estimated Book'].sum()
                st.metric("Total Estimated Book Value", f"${total_estimated_book:,.2f}")
            else:
                st.metric("Total Estimated Book Value", "N/A")
        
        with col2:
            if 'Annualized' in filtered_df.columns:
                total_annualized_billings = filtered_df['Annualized'].sum()
                st.metric("Total Annualized Billings", f"${total_annualized_billings:,.2f}")
            else:
                st.metric("Total Annualized Billings", "N/A")
        
        with col3:
            if 'Variance to Est' in filtered_df.columns:
                overall_variance = filtered_df['Variance to Est'].sum()
                st.metric("Overall Variance to Estimate", f"${overall_variance:,.2f}")
            else:
                st.metric("Overall Variance to Estimate", "N/A")

        # Metric Row 2
        col4, col5 = st.columns(2)
        with col4:
            if attorney_column and 'Annualized' in filtered_df.columns:
                revenue_per_attorney = calculate_annualized_revenue_per_attorney(filtered_df, attorney_column)
                st.metric("Annualized Revenue per Attorney", f"${revenue_per_attorney:,.2f}")
            else:
                st.metric("Annualized Revenue per Attorney", "N/A")

        # Quick view of Joiners/Leavers
        st.subheader("Recent Activity")
        col6, col7 = st.columns(2)
        
        with col6:
            st.write("Recent Joiners")
            if 'Leave Date' in filtered_df.columns and 'Start Date' in filtered_df.columns:
                joiners_df = filtered_df[filtered_df['Leave Date'].isna()].sort_values('Start Date', ascending=False).head(5)
                display_columns = ['Start Date'] + ([attorney_column] if attorney_column else []) + (['Estimated Book'] if 'Estimated Book' in filtered_df.columns else [])
                if not joiners_df.empty and display_columns:
                    st.dataframe(joiners_df[display_columns])
                else:
                    st.write("No recent joiners data available")
            else:
                st.write("Required columns not found")
        
        with col7:
            st.write("Recent Leavers")
            if 'Leave Date' in filtered_df.columns:
                leavers_df = filtered_df[filtered_df['Leave Date'].notna()].sort_values('Leave Date', ascending=False).head(5)
                display_columns = ['Leave Date'] + ([attorney_column] if attorney_column else []) + (['Estimated Book'] if 'Estimated Book' in filtered_df.columns else [])
                if not leavers_df.empty and display_columns:
                    st.dataframe(leavers_df[display_columns])
                else:
                    st.write("No recent leavers data available")
            else:
                st.write("Leave Date column not found")

    elif selected_tab == "Joiners":
        st.header("Joiners Data")
        if 'Leave Date' in filtered_df.columns:
            joiners_df = filtered_df[filtered_df['Leave Date'].isna()]
            if not joiners_df.empty:
                st.dataframe(joiners_df)
                if 'Estimated Book' in joiners_df.columns:
                    st.metric("Total Estimated Book Value (Joiners)", f"${joiners_df['Estimated Book'].sum():,.2f}")
            else:
                st.write("No joiners data available for the selected filters")
        else:
            st.write("Leave Date column not found")

    elif selected_tab == "Leavers":
        st.header("Leavers Data")
        if 'Leave Date' in filtered_df.columns:
            leavers_df = filtered_df[filtered_df['Leave Date'].notna()]
            if not leavers_df.empty:
                st.dataframe(leavers_df)
                if 'Estimated Book' in leavers_df.columns:
                    st.metric("Total Estimated Book Value (Leavers)", f"${leavers_df['Estimated Book'].sum():,.2f}")
            else:
                st.write("No leavers data available for the selected filters")
        else:
            st.write("Leave Date column not found")

    elif selected_tab == "Growth":
        st.header("Quarterly Net Growth (Estimated Book)")
        if 'Start Date' in filtered_df.columns and 'Estimated Book' in filtered_df.columns:
            quarterly_growth = calculate_quarterly_growth(filtered_df.copy())
            
            if not quarterly_growth.empty and 'Net Growth' in quarterly_growth.columns:
                st.dataframe(quarterly_growth)
                
                if HAS_MATPLOTLIB:
                    try:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        sns.lineplot(data=quarterly_growth, x='Quarter', y='Net Growth', ax=ax)
                        ax.set_title('Quarterly Net Growth of Estimated Book')
                        ax.tick_params(axis='x', rotation=45)
                        st.pyplot(fig)
                    except Exception as e:
                        st.warning(f"Could not generate chart: {e}")
                else:
                    st.write("Charts are disabled because Matplotlib is not installed.")
            else:
                st.write("No quarterly growth data available for the selected filters")
        else:
            st.write("Required columns for growth calculation not found")

    elif selected_tab == "Financials":
        st.header("Financial Metrics")
        
        if attorney_column and 'Annualized' in filtered_df.columns:
            revenue_per_attorney = calculate_annualized_revenue_per_attorney(filtered_df, attorney_column)
            st.metric("Annualized Revenue per Attorney", f"${revenue_per_attorney:,.2f}")
        else:
            st.metric("Annualized Revenue per Attorney", "N/A")
        
        if 'Annualized' in filtered_df.columns:
            total_annualized_billings = filtered_df['Annualized'].sum()
            st.metric("Total Annualized Billings", f"${total_annualized_billings:,.2f}")
        else:
            st.metric("Total Annualized Billings", "N/A")
        
        if 'Variance to Est' in filtered_df.columns:
            overall_variance = filtered_df['Variance to Est'].sum()
            st.metric("Overall Variance to Estimate", f"${overall_variance:,.2f}")
        else:
            st.metric("Overall Variance to Estimate", "N/A")
        
        st.subheader("Detailed Financial Data")
        financial_cols = ['Start Date'] + ([attorney_column] if attorney_column else []) + \
                         [col for col in ['Estimated Book', 'Annualized', 'Variance to Est'] if col in filtered_df.columns]
        
        if financial_cols:
            st.dataframe(filtered_df[financial_cols])
        else:
            st.write("No financial data columns available")

    elif selected_tab == "Monthly Trends":
        st.header("Joiners and Leavers Over Time")
        
        if 'Start Date' in filtered_df.columns and 'Leave Date' in filtered_df.columns:
            try:
                # Convert to datetime if not already
                filtered_df['Start Date'] = pd.to_datetime(filtered_df['Start Date'], errors='coerce')
                filtered_df['Leave Date'] = pd.to_datetime(filtered_df['Leave Date'], errors='coerce')
                
                # Filter out rows with invalid dates
                valid_start_dates = filtered_df.dropna(subset=['Start Date'])
                valid_leave_dates = filtered_df[filtered_df['Leave Date'].notna()]
                
                # Create monthly time series
                if not valid_start_dates.empty:
                    monthly_joiners = valid_start_dates.set_index('Start Date').resample('M').size()
                else:
                    monthly_joiners = pd.Series()
                
                if not valid_leave_dates.empty:
                    monthly_leavers = valid_leave_dates.set_index('Leave Date').resample('M').size()
                else:
                    monthly_leavers = pd.Series()
                
                # Combine the series
                if not monthly_joiners.empty or not monthly_leavers.empty:
                    time_series_data = pd.DataFrame({'Joiners': monthly_joiners, 'Leavers': monthly_leavers})
                    time_series_data = time_series_data.fillna(0)
                    
                    # Display the dataframe
                    st.dataframe(time_series_data)
                    
                    if HAS_MATPLOTLIB and not time_series_data.empty:
                        try:
                            fig, ax = plt.subplots(figsize=(12, 6))
                            time_series_data.plot(ax=ax)
                            ax.set_title('Monthly Joiners and Leavers')
                            ax.set_xlabel('Month')
                            ax.set_ylabel('Count')
                            st.pyplot(fig)
                        except Exception as e:
                            st.warning(f"Could not generate chart: {e}")
                    else:
                        if not HAS_MATPLOTLIB:
                            st.write("Charts are disabled because Matplotlib is not installed.")
                        else:
                            st.write("No data available for charting")
                else:
                    st.write("No time series data available for the selected filters")
            except Exception as e:
                st.warning(f"Error calculating monthly trends: {e}")
        else:
            st.write("Required date columns not found")
            
    elif selected_tab == "Heatmap":
        st.header("Attorney Performance Heatmap")
        
        if attorney_column and 'Estimated Book' in filtered_df.columns and 'Start Year' in filtered_df.columns:
            try:
                # Create a pivot table for the heatmap
                if 'Start Date' in filtered_df.columns:
                    # Add month column if we have dates
                    filtered_df['Month'] = filtered_df['Start Date'].dt.month_name()
                    
                    # Create pivot table: attorneys vs months with estimated book values
                    pivot_data = filtered_df.pivot_table(
                        values='Estimated Book', 
                        index=attorney_column, 
                        columns='Month', 
                        aggfunc='sum',
                        fill_value=0
                    )
                    
                    # Sort pivot table by month order
                    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                                'July', 'August', 'September', 'October', 'November', 'December']
                    pivot_columns = [col for col in month_order if col in pivot_data.columns]
                    pivot_data = pivot_data[pivot_columns]
                else:
                    # Alternative: create year-based pivot if no detailed dates
                    pivot_data = filtered_df.pivot_table(
                        values='Estimated Book', 
                        index=attorney_column, 
                        columns='Start Year', 
                        aggfunc='sum',
                        fill_value=0
                    )
                
                # Display the pivot table
                st.subheader("Estimated Book Values")
                st.dataframe(pivot_data)
                
                # Create heatmap
                if HAS_MATPLOTLIB and not pivot_data.empty:
                    try:
                        fig, ax = plt.subplots(figsize=(12, max(8, len(pivot_data) * 0.4)))
                        
                        # Create the heatmap with a blue color map
                        heatmap = sns.heatmap(
                            pivot_data, 
                            annot=True, 
                            fmt=".1f", 
                            cmap="Blues", 
                            linewidths=0.5,
                            ax=ax,
                            cbar_kws={'label': 'Estimated Book Value'}
                        )
                        
                        ax.set_title('Attorney Performance by Period')
                        plt.tight_layout()
                        st.pyplot(fig)
                        
                        # Additional heatmap for normalized data (percentage of total)
                        st.subheader("Normalized Performance (% of Total)")
                        fig2, ax2 = plt.subplots(figsize=(12, max(8, len(pivot_data) * 0.4)))
                        
                        # Normalize data by row (attorney)
                        normalized_data = pivot_data.div(pivot_data.sum(axis=1), axis=0) * 100
                        
                        heatmap2 = sns.heatmap(
                            normalized_data, 
                            annot=True, 
                            fmt=".1f", 
                            cmap="YlGnBu", 
                            linewidths=0.5,
                            ax=ax2,
                            cbar_kws={'label': '% of Attorney\'s Total'}
                        )
                        
                        ax2.set_title('Normalized Attorney Performance by Period (%)')
                        plt.tight_layout()
                        st.pyplot(fig2)
                        
                    except Exception as e:
                        st.warning(f"Could not generate heatmap: {e}")
                else:
                    if not HAS_MATPLOTLIB:
                        st.write("Heatmap visualization requires Matplotlib and Seaborn")
                    else:
                        st.write("No data available for heatmap")
            except Exception as e:
                st.warning(f"Error creating performance heatmap: {e}")
        else:
            missing = []
            if not attorney_column:
                missing.append("attorney column")
            if 'Estimated Book' not in filtered_df.columns:
                missing.append("Estimated Book column")
            if 'Start Year' not in filtered_df.columns:
                missing.append("Start Year column")
                
            st.write(f"Cannot create heatmap: Missing {', '.join(missing)}")

    # --- Download data ---
    if not filtered_df.empty:
        st.download_button(
            label="Download Filtered Data as CSV",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name='filtered_data.csv',
            mime='text/csv',
        )
    else:
        st.write("No data available to download")

if __name__ == "__main__":
    main()
