import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# --- Simple Password Protection ---
PASSWORD = "joinersleavers2025"

st.set_page_config(layout="wide")

if "auth_passed" not in st.session_state:
    st.session_state.auth_passed = False

if not st.session_state.auth_passed:
    pw = st.text_input("Enter Password", type="password")
    if pw == PASSWORD:
        st.session_state.auth_passed = True
    else:
        st.stop()

if st.session_state.auth_passed:
    st.title("Attorney Joiners, Leavers & Growth Dashboard")

    # Load CSV directly from GitHub
    csv_url = "https://raw.githubusercontent.com/aavadhan10/Joiners_Leavers/main/2023_Joiners_Leavers.csv"
    response = requests.get(csv_url)
    df = pd.read_csv(io.StringIO(response.text))

    st.write("### CSV Column Preview:")
    st.write(df.columns.tolist())

    df.rename(columns={"Join Date": "Date"}, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Type"] = df["Type"].fillna("Joiner")

    all_data = df.copy()

    with st.sidebar:
        st.header("Filters")
        name_filter = st.multiselect("Name", options=all_data["Name"].dropna().unique())
        office_filter = st.multiselect("Office", options=all_data["Office"].dropna().unique())
        title_filter = st.multiselect("Title", options=all_data["Title"].dropna().unique())
        group_filter = st.multiselect("Group", options=all_data["Group"].dropna().unique())
        type_filter = st.multiselect("Type", options=all_data["Type"].unique(), default=list(all_data["Type"].unique()))
        date_range = st.date_input("Date Range", [all_data["Date"].min(), all_data["Date"].max()])

    df_filtered = all_data.copy()
    if name_filter:
        df_filtered = df_filtered[df_filtered["Name"].isin(name_filter)]
    if office_filter:
        df_filtered = df_filtered[df_filtered["Office"].isin(office_filter)]
    if title_filter:
        df_filtered = df_filtered[df_filtered["Title"].isin(title_filter)]
    if group_filter:
        df_filtered = df_filtered[df_filtered["Group"].isin(group_filter)]
    if type_filter:
        df_filtered = df_filtered[df_filtered["Type"].isin(type_filter)]
    df_filtered = df_filtered[(df_filtered["Date"] >= pd.to_datetime(date_range[0])) &
                              (df_filtered["Date"] <= pd.to_datetime(date_range[1]))]

    tab1, tab2, tab3 = st.tabs([
        "📈 Joiners & Leavers", "📊 Net Growth & Attrition", "📤 Export Data"])

    with tab1:
        st.subheader("Activity Over Time")
        st.metric("Total Records", df_filtered.shape[0])
        st.metric("Total Book of Business", f"${df_filtered['Book of Business'].dropna().astype(float).sum():,.0f}")

        chart_data = df_filtered.groupby(["Date", "Type"]).size().reset_index(name="Count")
        fig = px.bar(chart_data, x="Date", y="Count", color="Type", barmode="group")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_filtered.sort_values("Date"))

    with tab2:
        st.subheader("Net Growth & Attrition")
        growth_df = df_filtered.groupby(["Date", "Type"]).size().unstack(fill_value=0)
        growth_df["Net Growth"] = growth_df.get("Joiner", 0) - growth_df.get("Leaver", 0)
        growth_df["Attrition Rate"] = (growth_df.get("Leaver", 0) / (growth_df.get("Joiner", 0) + growth_df.get("Leaver", 0))).fillna(0)
        growth_df = growth_df.reset_index()

        fig_growth = px.line(growth_df, x="Date", y="Net Growth", title="Net Growth Over Time")
        fig_attrition = px.line(growth_df, x="Date", y="Attrition Rate", title="Attrition Rate Over Time")
        st.plotly_chart(fig_growth, use_container_width=True)
        st.plotly_chart(fig_attrition, use_container_width=True)

    with tab3:
        st.subheader("Download Filtered Data")
        st.download_button("Download CSV", data=df_filtered.to_csv(index=False), file_name="filtered_attorneys.csv")

