import streamlit as st
import pandas as pd
import plotly.express as px

# --- Simple Password Protection ---
PASSWORD = "joinersleavers2025"

st.set_page_config(layout="wide")

if "auth_passed" not in st.session_state:
    st.session_state.auth_passed = False

if not st.session_state.auth_passed:
    pw = st.text_input("Enter Password", type="password")
    if pw == PASSWORD:
        st.session_state.auth_passed = True
        st.experimental_rerun()
    else:
        st.stop()

st.title("Attorney Joiners, Leavers & Growth Dashboard")
file = st.file_uploader("Upload Excel File", type=[".xlsx"])

@st.cache_data

def load_clean_joiners(sheet_name, xls):
    raw = xls.parse(sheet_name, skiprows=5)
    df = raw.dropna(how='all').reset_index(drop=True)
    df.columns = [f'col_{i}' for i in range(len(df.columns))]
    df_people = df[["col_2", "col_3"] + [f"col_{i}" for i in range(65, 75)]].copy()
    df_people.columns = ["Name1", "Name2"] + [f"M{i}" for i in range(1, 11)]
    df_people["Book of Business"] = df["col_10"] if "col_10" in df.columns else None
    df_long = df_people.melt(id_vars=["Name1", "Name2", "Book of Business"], 
                              var_name="Month", value_name="Activity")
    df_long.dropna(subset=["Activity"], inplace=True)
    df_long["Name"] = df_long["Name1"].combine_first(df_long["Name2"])
    df_long["Type"] = "Joiner"
    df_long["Date"] = pd.date_range(start="2023-01-01" if "2023" in sheet_name else "2024-01-01", 
                                     periods=10, freq="MS").tolist() * (len(df_long) // 10 + 1)
    df_long["Date"] = df_long["Date"][:len(df_long)]
    return df_long[["Name", "Date", "Type", "Book of Business"]]

if file:
    xls = pd.ExcelFile(file)
    joiners_2023 = load_clean_joiners("2023 Joiners_Leavers", xls)
    joiners_2024 = load_clean_joiners("2024 New Joiners_Leavers", xls)

    # Load Quarterly Headcount
    try:
        df_quarterly = xls.parse("All Attorneys Quarterly", skiprows=2)
        df_quarterly = df_quarterly.dropna(how='all')
        df_quarterly.columns = df_quarterly.iloc[0]
        df_quarterly = df_quarterly[1:]
        df_quarterly = df_quarterly.rename(columns={df_quarterly.columns[0]: "Quarter"})
        df_quarterly = df_quarterly.melt(id_vars="Quarter", var_name="Office", value_name="Attorney Count")
    except Exception:
        df_quarterly = pd.DataFrame()

    all_data = pd.concat([joiners_2023, joiners_2024])

    with st.sidebar:
        st.header("Filters")
        name_filter = st.multiselect("Name", options=all_data["Name"].dropna().unique())
        type_filter = st.multiselect("Type", options=["Joiner"], default=["Joiner"])
        date_range = st.date_input("Date Range", [all_data["Date"].min(), all_data["Date"].max()])

    df_filtered = all_data.copy()
    if name_filter:
        df_filtered = df_filtered[df_filtered["Name"].isin(name_filter)]
    if type_filter:
        df_filtered = df_filtered[df_filtered["Type"].isin(type_filter)]
    df_filtered = df_filtered[(df_filtered["Date"] >= pd.to_datetime(date_range[0])) &
                              (df_filtered["Date"] <= pd.to_datetime(date_range[1]))]

    tab1, tab2, tab3 = st.tabs(["📈 Joiners", "📊 Net Growth", "🗂 Quarterly Headcount"])

    with tab1:
        st.subheader("Joiner Activity")
        st.metric("Total Joiners", df_filtered.shape[0])
        st.metric("Total Book of Business", f"${df_filtered['Book of Business'].dropna().astype(float).sum():,.0f}")

        chart_data = df_filtered.groupby(["Date", "Type"]).size().reset_index(name="Count")
        fig = px.bar(chart_data, x="Date", y="Count", color="Type", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_filtered.sort_values("Date"))

    with tab2:
        st.subheader("Net Growth Placeholder")
        st.info("Net growth logic can be implemented if we add 'leavers' structure")

    with tab3:
        st.subheader("Quarterly Headcount by Office")
        if not df_quarterly.empty:
            fig2 = px.line(df_quarterly, x="Quarter", y="Attorney Count", color="Office")
            st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(df_quarterly)
        else:
            st.warning("Quarterly data not available or misformatted.")
