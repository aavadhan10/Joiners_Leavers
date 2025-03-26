import streamlit as st
import pandas as pd
import hashlib
import os

# Attempt to import matplotlib and seaborn, handle potential ModuleNotFoundError
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_MATPLOTLIB = True
except ModuleNotFoundError as e:
    HAS_MATPLOTLIB = False
    st.warning(f"Matplotlib and/or Seaborn not found. Charts will not be displayed.  Error: {e}") # Include the specific error

# Attempt to import streamlit_option_menu, handle potential ModuleNotFoundError
try:
    from streamlit_option_menu import option_menu
    HAS_OPTION_MENU = True
except ModuleNotFoundError as e:
    HAS_OPTION_MENU = False
    st.warning(f"streamlit_option_menu not found. Tabbed navigation will not be displayed. Error: {e}")  # Include the specific error

# Password Protection
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# DB Management
hashed_psw = "b0efc7bd43f799c50dae1c9624717f18a54c10b835305c85f8185610b0b06e0d" # Hashed "joiners2025"

def login():
    username = st.sidebar.text_input("User Name")
    password = st.sidebar.text_input("Password", type='password')

    if st.sidebar.checkbox("Login"):
        if check_hashes(password, hashed_psw):
            st.success("Logged In as {}".format(username))
            st.session_state['logged_in'] = True
            return True
        else:
            st.warning("Incorrect Username/Password")
            return False
    else:
        return False


def load_data():
    try:
        df = pd.read_csv("2023_Joiners_Leavers.csv")
    except FileNotFoundError:
        st.error("Error: Could not find the file '2023_Joiners_Leavers.csv'.  Make sure the file is in the same directory as your script, or provide the correct path.")
        st.stop()

    df = df.fillna(0)

    date_columns = [col for col in df.columns if "Date" in col or "TTM" in col and df[col].dtype == 'object']
    for col in date_columns:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        except ValueError as e:
            st.warning(f"Warning: Could not convert column '{col}' to datetime.  Check the date format in your CSV file. Error: {e}")

    df.columns = [col.replace("Unnamed: ", "") for col in df.columns]
    header_row_index = df[df.iloc[:, 2].isin(['Billings', 'Collections'])].index.min()
    df.columns = df.iloc[header_row_index + 4]
    df = df.iloc[header_row_index + 5:]
    df = df[(df.T != 0).any()]

    numeric_cols = ['Start Year','Estimated Book', 'TTM', 'Annualized', 'Variance to Est'] + [col for col in df.columns if isinstance(col, float) or isinstance(col, int)]
    for col in numeric_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except ValueError as e:
                st.warning(f"Warning: Could not convert column '{col}' to numeric. Check the data in your CSV file. Error: {e}")
                df[col] = 0
    return df

# --- Data Analysis Functions ---
def calculate_quarterly_growth(df):
    df['Quarter'] = pd.to_datetime(df['Start Date'], errors='coerce').dt.to_period('Q')
    quarterly_growth = df.groupby('Quarter')['Estimated Book'].sum().reset_index()
    quarterly_growth.rename(columns={'Estimated Book': 'Net Growth'}, inplace=True)
    return quarterly_growth

def calculate_annualized_revenue_per_attorney(df):
    """Calculates the annualized revenue per attorney for the selected period."""
    total_annualized_revenue = df['Annualized'].sum()
    num_attorneys = len(df['J Paul Gignac'].unique()) #assuming "J Paul Gignac" is the unique attorney name
    if num_attorneys > 0:
        revenue_per_attorney = total_annualized_revenue / num_attorneys
        return revenue_per_attorney
    else:
        return 0

# --- Streamlit App ---
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login()
        if not st.session_state['logged_in']:
            return

    st.title("Joiners and Leavers Dashboard")

    df = load_data()

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")

    date_range = st.sidebar.date_input("Select Date Range",
                                       min_value=df['Start Date'].min().date(),
                                       max_value=df['Start Date'].max().date(),
                                       value=[df['Start Date'].min().date(), df['Start Date'].max().date()])
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

    years = df['Start Year'].dropna().unique().tolist()
    selected_years = st.sidebar.multiselect("Select Year(s)", options=years, default=years)

    person_column = "J Paul Gignac"
    if person_column in df.columns:
        people = df[person_column].dropna().unique().tolist()
        selected_people = st.sidebar.multiselect("Select Person(s)", options=people, default=people)
        filtered_df = df[df[person_column].isin(selected_people)]
    else:
        st.warning(f"Warning: Column '{person_column}' not found. Person filter disabled.")
        filtered_df = df.copy()

    filtered_df = filtered_df[(filtered_df['Start Date'] >= start_date) & (filtered_df['Start Date'] <= end_date)]
    filtered_df = filtered_df[filtered_df['Start Year'].isin(selected_years)]

    # --- Navigation Menu ---
    if HAS_OPTION_MENU: # Conditionally show the tab menu
        selected_tab = option_menu(
            menu_title=None,
            options=["Overview", "Joiners", "Leavers", "Growth", "Financials", "Monthly Trends"],
            icons=["house", "person-plus", "person-dash", "graph-up", "cash-coin", "calendar"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
        )
    else:
        st.write("Tabbed navigation is disabled because streamlit_option_menu is not installed.")
        selected_tab = "Overview" # Default to the overview if the menu is not available

    # --- Tab Contents ---

    if selected_tab == "Overview":
        st.header("Dashboard Overview")

        # Metric Row 1
        col1, col2, col3 = st.columns(3)
        with col1:
            total_estimated_book = filtered_df['Estimated Book'].sum()
            st.metric("Total Estimated Book Value", f"${total_estimated_book:,.2f}")
        with col2:
            total_annualized_billings = filtered_df['Annualized'].sum()
            st.metric("Total Annualized Billings", f"${total_annualized_billings:,.2f}")
        with col3:
            overall_variance = filtered_df['Variance to Est'].sum()
            st.metric("Overall Variance to Estimate", f"${overall_variance:,.2f}")

        # Metric Row 2
        col4, col5 = st.columns(2)
        with col4:
            revenue_per_attorney = calculate_annualized_revenue_per_attorney(filtered_df)
            st.metric("Annualized Revenue per Attorney", f"${revenue_per_attorney:,.2f}")

        # Quick view of Joiners/Leavers, Quarterly Growth
        st.subheader("Recent Activity")
        col6, col7 = st.columns(2)
        with col6:
            st.write("Recent Joiners")
            joiners_df = filtered_df[filtered_df['Leave Date'].isnull()].head(5)
            st.dataframe(joiners_df[['Start Date', 'J Paul Gignac', 'Estimated Book']])  # Show relevant columns
        with col7:
            st.write("Recent Leavers")
            leavers_df = filtered_df[filtered_df['Leave Date'].notnull()].head(5)
            st.dataframe(leavers_df[['Leave Date', 'J Paul Gignac', 'Estimated Book']])

    elif selected_tab == "Joiners":
        st.header("Joiners Data")
        joiners_df = filtered_df[filtered_df['Leave Date'].isnull()]
        st.dataframe(joiners_df)
        st.metric("Total Estimated Book Value (Joiners)", f"${joiners_df['Estimated Book'].sum():,.2f}")

    elif selected_tab == "Leavers":
        st.header("Leavers Data")
        leavers_df = filtered_df[filtered_df['Leave Date'].notnull()]
        st.dataframe(leavers_df)
        st.metric("Total Estimated Book Value (Leavers)", f"${leavers_df['Estimated Book'].sum():,.2f}")

    elif selected_tab == "Growth":
        st.header("Quarterly Net Growth (Estimated Book)")
        quarterly_growth = calculate_quarterly_growth(filtered_df.copy())

        if not quarterly_growth.empty:
            st.dataframe(quarterly_growth)

            if HAS_MATPLOTLIB: # Conditionally show the chart
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.lineplot(x='Quarter', y='Net Growth', data=quarterly_growth, ax=ax)
                ax.set_title('Quarterly Net Growth of Estimated Book')
                ax.tick_params(axis='x', rotation=45)
                st.pyplot(fig)
            else:
                st.write("Charts are disabled because Matplotlib is not installed.")

        else:
            st.write("No data available for the selected filters.")

    elif selected_tab == "Financials":
        st.header("Financial Metrics")
        revenue_per_attorney = calculate_annualized_revenue_per_attorney(filtered_df)
        st.metric("Annualized Revenue per Attorney", f"${revenue_per_attorney:,.2f}")

        #Additional metrics for finance professionals
        total_annualized_billings = filtered_df['Annualized'].sum()
        st.metric("Total Annualized Billings", f"${total_annualized_billings:,.2f}")

        overall_variance = filtered_df['Variance to Est'].sum()
        st.metric("Overall Variance to Estimate", f"${overall_variance:,.2f}")

        st.subheader("Detailed Financial Data")
        st.dataframe(filtered_df[['Start Date', 'J Paul Gignac', 'Estimated Book', 'Annualized', 'Variance to Est']]) # Show more financial-related data

    elif selected_tab == "Monthly Trends":
        st.header("Joiners and Leavers Over Time")
        df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
        df['Leave Date'] = pd.to_datetime(df['Leave Date'], errors='coerce')

        monthly_joiners = filtered_df.dropna(subset=['Start Date']).set_index('Start Date').resample('M').size()
        monthly_leavers = filtered_df[filtered_df['Leave Date'].notnull()].set_index('Leave Date').resample('M').size()

        time_series_data = pd.DataFrame({'Joiners': monthly_joiners, 'Leavers': monthly_leavers})
        time_series_data = time_series_data.fillna(0)

        if HAS_MATPLOTLIB: # Conditionally show the chart
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.lineplot(data=time_series_data, ax=ax)
            ax.set_title('Monthly Joiners and Leavers')
            ax.set_xlabel('Month')
            ax.set_ylabel('Count')
            st.pyplot(fig)
        else:
            st.write("Charts are disabled because Matplotlib is not installed.")

    # --- Download data ---
    st.download_button(
        label="Download Filtered Data as CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='filtered_data.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()
