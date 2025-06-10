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
        grouped = df.groupby(['Week', 'DEPT'], as_index=False).sum(numeric_only=True)
        x_axis = 'Week'
    else:  # Monthly
        df['Month'] = df['TANGGAL'].dt.to_period('M').astype(str)
        grouped = df.groupby(['Month', 'DEPT'], as_index=False).sum(numeric_only=True)
        x_axis = 'Month'

    st.subheader(f"{period} Report Visualization")

    # Menambahkan kolom persentase ODOI per departemen
    grouped['ODOI_Percent'] = grouped.groupby(x_axis)['ODOI'].transform(lambda x: (x / x.sum()) * 100)

    # Bar chart untuk ODOI
    bar_chart_odoi = px.bar(
        grouped,
        x=x_axis,
        y='ODOI',
        color='DEPT',
        text='ODOI_Percent',
        title=f"ODOI by {period}",
        labels={x_axis: period, 'ODOI': 'Total ODOI'},
        text_auto='.2f'
    )
    bar_chart_odoi.update_layout(barmode='group', xaxis_tickangle=-45)
    st.plotly_chart(bar_chart_odoi, use_container_width=True)

    # Bar chart untuk CHECK IN
    bar_chart_checkin = px.bar(
        grouped,
        x=x_axis,
        y='CHECK IN',
        color='DEPT',
        title=f"CHECK IN by {period}",
        labels={x_axis: period, 'CHECK IN': 'Total CHECK IN'},
        text_auto='.2f'
    )
    bar_chart_checkin.update_layout(barmode='group', xaxis_tickangle=-45)
    st.plotly_chart(bar_chart_checkin, use_container_width=True)

    # Perbandingan ODOI dan CHECK IN
    comparison_chart = px.bar(
        grouped.melt(id_vars=[x_axis, 'DEPT'], value_vars=['ODOI', 'CHECK IN']),
        x=x_axis,
        y='value',
        color='variable',
        facet_col='DEPT',
        title=f"Comparison of ODOI and CHECK IN by {period}",
        labels={'value': 'Count', x_axis: period, 'variable': 'Metric'}
    )
    comparison_chart.update_layout(barmode='group', xaxis_tickangle=-45)
    st.plotly_chart(comparison_chart, use_container_width=True)

# Aplikasi utama
st.set_page_config(page_title="Dashboard Interaktif", page_icon="📊", layout="wide")

# Menampilkan logo organisasi
st.image("UPDATE LOGO PPA.jpg", width=150)  # Ganti path sesuai lokasi file logo
st.title("📊 One Day One Inspection Dashboard")
st.write("Unggah file Excel untuk menghasilkan visualisasi interaktif.")

uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

if uploaded_file:
    try:
        # Baca data dari file Excel
        data = load_data(uploaded_file)

        # Pilihan jenis laporan
        report_type = st.selectbox("Pilih jenis laporan", ["Daily", "Weekly", "Monthly"])
        
        # Tambahkan opsi pemilihan tanggal untuk Daily
        selected_date = None
        if report_type == "Daily":
            unique_dates = data['TANGGAL'].dt.date.unique()
            selected_date = st.date_input("Pilih tanggal untuk visualisasi harian:", min_value=min(unique_dates), max_value=max(unique_dates))

        # Tampilkan visualisasi
        if st.button("Generate Report"):
            visualize_data(data, report_type, selected_date)
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca data: {e}")
else:
    st.info("Silakan unggah file Excel untuk melanjutkan.")
