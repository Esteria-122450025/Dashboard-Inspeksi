import streamlit as st
import pandas as pd
import plotly.express as px

# Fungsi untuk membaca dan membersihkan data
def load_data(file_path):
    df = pd.read_excel(file_path)
    df['TANGGAL'] = pd.to_datetime(df['TANGGAL'], errors='coerce')
    df.dropna(subset=['TANGGAL'], inplace=True)
    return df

# Fungsi untuk visualisasi data
def visualize_data(df, period, selected_date=None):
    if period == "Daily":
        if selected_date:
            df = df[df['TANGGAL'].dt.date == selected_date]
        grouped = df.groupby(['TANGGAL', 'DEPT'], as_index=False).sum(numeric_only=True)
        x_axis = 'TANGGAL'
    elif period == "Weekly":
        df['Week'] = df['TANGGAL'].dt.isocalendar().week
        df['Year'] = df['TANGGAL'].dt.year
        df['Week'] = df.groupby(['Year', 'Week']).ngroup() + 1
        df['Week_Label'] = df['Week'].apply(lambda x: f"Week {x}")
        grouped = df.groupby(['Week_Label', 'DEPT'], as_index=False).sum(numeric_only=True)
        x_axis = 'Week_Label'
    else:  # Monthly
        df['Month'] = df['TANGGAL'].dt.strftime('%B')
        grouped = df.groupby(['Month', 'DEPT'], as_index=False).sum(numeric_only=True)
        x_axis = 'Month'

    st.subheader(f"{period} Report Visualization")

    # Menghitung persentase
    grouped['ODOI_Percent'] = grouped.groupby(x_axis)['ODOI'].transform(lambda x: (x / x.sum()) * 100)
    grouped['CHECK_IN_Percent'] = grouped.groupby(x_axis)['CHECK IN'].transform(lambda x: (x / x.sum()) * 100)

    # Visualisasi untuk ODOI
    bar_chart_odoi = px.bar(
        grouped,
        x=x_axis,
        y='ODOI_Percent',
        color='DEPT',
        text=grouped['ODOI_Percent'].apply(lambda x: f"{x:.2f}%"),
        title=f"ODOI Percentage by {period}",
        labels={x_axis: period, 'ODOI_Percent': 'ODOI (%)'}
    )
    bar_chart_odoi.update_traces(textposition='outside')
    bar_chart_odoi.update_layout(barmode='group', xaxis_tickangle=-45)
    st.plotly_chart(bar_chart_odoi, use_container_width=True)

    # Visualisasi untuk CHECK IN
    bar_chart_checkin = px.bar(
        grouped,
        x=x_axis,
        y='CHECK_IN_Percent',
        color='DEPT',
        text=grouped['CHECK_IN_Percent'].apply(lambda x: f"{x:.2f}%"),
        title=f"CHECK IN Percentage by {period}",
        labels={x_axis: period, 'CHECK_IN_Percent': 'CHECK IN (%)'}
    )
    bar_chart_checkin.update_traces(textposition='outside')
    bar_chart_checkin.update_layout(barmode='group', xaxis_tickangle=-45)
    st.plotly_chart(bar_chart_checkin, use_container_width=True)

    # Visualisasi perbandingan persentase antara CHECK IN dan ODOI
    comparison_data = grouped.melt(
        id_vars=[x_axis, 'DEPT'],
        value_vars=['ODOI_Percent', 'CHECK_IN_Percent'],
        var_name='Metric',
        value_name='Percentage'
    )
    comparison_chart = px.bar(
        comparison_data,
        x=x_axis,
        y='Percentage',
        color='Metric',
        barmode='group',
        text=comparison_data['Percentage'].apply(lambda x: f"{x:.2f}%"),
        title=f"Comparison of CHECK IN and ODOI Percentages by {period}",
        labels={x_axis: period, 'Percentage': 'Percentage (%)'}
    )
    comparison_chart.update_traces(textposition='outside')
    comparison_chart.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(comparison_chart, use_container_width=True)

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard Interaktif", page_icon="📊", layout="wide")

# Menampilkan logo organisasi
st.image("UPDATE LOGO PPA.jpg", width=500)  # Memperbesar ukuran logo
st.title("📊 One Day One Inspection Dashboard")
st.write("Unggah file Excel untuk menghasilkan visualisasi.")

# Unggah file
uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

if uploaded_file:
    try:
        data = load_data(uploaded_file)
        report_type = st.selectbox("Pilih jenis laporan", ["Daily", "Weekly", "Monthly"])
        
        selected_date = None
        if report_type == "Daily":
            unique_dates = data['TANGGAL'].dt.date.unique()
            selected_date = st.date_input("Pilih tanggal untuk visualisasi harian:", 
                                          min_value=min(unique_dates), 
                                          max_value=max(unique_dates))

        if st.button("Generate Report"):
            visualize_data(data, report_type, selected_date)
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca data: {e}")
else:
    st.info("Silakan unggah file Excel untuk melanjutkan.")
