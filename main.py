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
    else:
        st.stop()

if st.session_state.auth_passed:
    st.title("Attorney Joiners, Leavers & Growth Dashboard")
    file = st.file_uploader("Upload Excel File", type=[".xlsx"])

    @st.cache_data
    def load_clean_data(sheet_name, xls, type_label):
        raw = xls.parse(sheet_name, skiprows=5)
        df = raw.dropna(how='all').reset_index(drop=True)
        df.columns = [f'col_{i}' for i in range(len(df.columns))]
        df_people = df[["col_2", "col_3", "col_4", "col_5", "col_6"] + [f"col_{i}" for i in range(65, 75)]].copy()
        df_people.columns = ["Name1", "Name2", "Office", "Title", "Group"] + [f"M{i}" for i in range(1, 11)]
        df_people["Book of Business"] = df["col_10"] if "col_10" in df.columns else None
        df_long = df_people.melt(id_vars=["Name1", "Name2", "Office", "Title", "Group", "Book of Business"], 
                                  var_name="Month", value_name="Activity")
        df_long.dropna(subset=["Activity"], inplace=True)
        df_long["Name"] = df_long["Name1"].combine_first(df_long["Name2"])
        df_long["Type"] = type_label
        df_long["Date"] = pd.date_range(start="2023-01-01" if "2023" in sheet_name else "2024-01-01", 
                                         periods=10, freq="MS").tolist() * (len(df_long) // 10 + 1)
        df_long["Date"] = df_long["Date"][:len(df_long)]
        return df_long[["Name", "Date", "Type", "Book of Business", "Office", "Title", "Group"]]

    if file:
        xls = pd.ExcelFile(file)
        joiners_2023 = load_clean_data("2023 Joiners_Leavers", xls, "Joiner")
        joiners_2024 = load_clean_data("2024 New Joiners_Leavers", xls, "Joiner")
        leavers_sheet = [s for s in xls.sheet_names if "Leaver" in s and s != "2023 Joiners_Leavers" and s != "2024 New Joiners_Leavers"]
        leavers = pd.concat([load_clean_data(sheet, xls, "Leaver") for sheet in leavers_sheet]) if leavers_sheet else pd.DataFrame()

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

        # Load Monthly Headcount
        try:
            df_monthly = xls.parse("All Attnys Monthly", skiprows=2)
            df_monthly = df_monthly.dropna(how='all')
            df_monthly.columns = df_monthly.iloc[0]
            df_monthly = df_monthly[1:]
            df_monthly = df_monthly.rename(columns={df_monthly.columns[0]: "Month"})
            df_monthly = df_monthly.melt(id_vars="Month", var_name="Office", value_name="Attorney Count")
        except Exception:
            df_monthly = pd.DataFrame()

        all_data = pd.concat([joiners_2023, joiners_2024, leavers])

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

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Joiners & Leavers", "📊 Net Growth & Attrition", "📅 Quarterly Headcount",
            "📆 Monthly Headcount", "📤 Export Data"])

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
            st.subheader("Quarterly Headcount by Office")
            if not df_quarterly.empty:
                fig2 = px.line(df_quarterly, x="Quarter", y="Attorney Count", color="Office")
                st.plotly_chart(fig2, use_container_width=True)
                st.dataframe(df_quarterly)
            else:
                st.warning("Quarterly data not available or misformatted.")

        with tab4:
            st.subheader("Monthly Headcount by Office")
            if not df_monthly.empty:
                fig3 = px.line(df_monthly, x="Month", y="Attorney Count", color="Office")
                st.plotly_chart(fig3, use_container_width=True)
                st.dataframe(df_monthly)
            else:
                st.warning("Monthly data not available or misformatted.")

        with tab5:
            st.subheader("Download Filtered Data")
            st.download_button("Download CSV", data=df_filtered.to_csv(index=False), file_name="filtered_attorneys.csv")

