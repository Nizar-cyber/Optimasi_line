import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Konstanta waktu kerja
WORKING_TIME_PER_DAY = 430  # menit

# Fungsi untuk membuat template Excel
def create_template_excel():
    template_data = {
        "Nama Barang": ["Barang A", "Barang B", "Barang C"],
        "Cycle Time": [10, 8, 12],
        "Demand/day": [100, 80, 120],
        "Working Day": [20, 22, 18]
    }
    df_template = pd.DataFrame(template_data)
    df_template.to_excel("template_perhitungan_barang.xlsx", index=False)

# Buat file template
create_template_excel()

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Distribusi Produksi", layout="wide")
st.title("📊 Perhitungan MP, Kapasitas dan Distribusi Line & Stall")

# Tombol unduh template
with open("template_perhitungan_barang.xlsx", "rb") as f:
    st.download_button("📥 Unduh Template Excel", f, file_name="template_perhitungan_barang.xlsx")

# Upload file Excel
uploaded_file = st.file_uploader("📤 Unggah file data barang (Excel)", type=["xlsx"])
if uploaded_file:
    df_input = pd.read_excel(uploaded_file, engine="openpyxl")
    st.subheader("📋 Data Barang (Input)")
    st.dataframe(df_input)

    # Perhitungan hasil
    df_result = df_input.copy()
    df_result["Taktime"] = WORKING_TIME_PER_DAY / df_result["Demand/day"]
    df_result["Jumlah MP"] = df_result["Cycle Time"] / df_result["Taktime"]
    df_result["Kapasitas/day"] = df_result["Demand/day"]
    df_result["Kapasitas/month"] = df_result["Demand/day"] * df_result["Working Day"]

    total_cap_month = df_result["Kapasitas/month"].sum()

    st.subheader("✅ Hasil Perhitungan")
    st.dataframe(df_result)
    st.markdown(f"**Total Kapasitas Bulanan: {total_cap_month:.0f} unit**")

    # Distribusi Line
    st.subheader("🏭 Distribusi Line (max 10 MP)")
    line_groups = {1: [], 2: [], 3: []}
    line_mp = {1: 0, 2: 0, 3: 0}
    line_cap_month = {1: 0, 2: 0, 3: 0}

    sorted_items = df_result.sort_values(by="Jumlah MP").reset_index(drop=True)

    for _, row in sorted_items.iterrows():
        for ln in line_groups:
            if line_mp[ln] + row["Jumlah MP"] <= 10:
                line_groups[ln].append(row)
                line_mp[ln] += row["Jumlah MP"]
                line_cap_month[ln] += row["Kapasitas/month"]
                break

    for ln in line_groups:
        items = line_groups[ln]
        if not items:
            st.write(f"Line {ln} : kosong")
            continue
        df_line = pd.DataFrame(items)
        st.markdown(f"**Line {ln}:**")
        st.write(f"- Barang: {', '.join(df_line['Nama Barang'])}")
        st.write(f"- Total MP: {line_mp[ln]:.2f} orang")
        st.write(f"- Total Kapasitas Bulanan: {line_cap_month[ln]:.0f} unit")

    # Distribusi Stall
    st.subheader("🔧 Distribusi Stall (max 4 MP)")
    stall_groups = {1: [], 2: [], 3: [], 4: []}
    stall_mp = {1: 0, 2: 0, 3: 0, 4: 0}
    stall_cap_month = {1: 0, 2: 0, 3: 0, 4: 0}

    for _, row in sorted_items.iterrows():
        for sn in stall_groups:
            if stall_mp[sn] + row["Jumlah MP"] <= 4:
                stall_groups[sn].append(row)
                stall_mp[sn] += row["Jumlah MP"]
                stall_cap_month[sn] += row["Kapasitas/month"]
                break

    for sn in stall_groups:
        items = stall_groups[sn]
        if not items:
            st.write(f"Stall {sn} : kosong")
            continue
        df_stall = pd.DataFrame(items)
        st.markdown(f"**Stall {sn}:**")
        st.write(f"- Barang: {', '.join(df_stall['Nama Barang'])}")
        st.write(f"- Total MP: {stall_mp[sn]:.2f} orang")
        st.write(f"- Total Kapasitas Bulanan: {stall_cap_month[sn]:.0f} unit")

    # Visualisasi Grafik
    st.subheader("📊 Grafik Distribusi")

    def plot_bar(data, title, xlabel, ylabel):
        fig, ax = plt.subplots()
        ax.bar(data.keys(), data.values(), color='skyblue')
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        st.pyplot(fig)

    plot_bar(line_mp, "Jumlah MP per Line", "Line", "Jumlah MP")
    plot_bar(line_cap_month, "Kapasitas Bulanan per Line", "Line", "Kapasitas Bulanan")
    plot_bar(stall_mp, "Jumlah MP per Stall", "Stall", "Jumlah MP")
    plot_bar(stall_cap_month, "Kapasitas Bulanan per Stall", "Stall", "Kapasitas Bulanan")

    # Ekspor hasil ke Excel
    st.subheader("📤 Ekspor Hasil ke Excel")

    with pd.ExcelWriter("hasil_perhitungan.xlsx", engine="openpyxl") as writer:
        df_result.to_excel(writer, sheet_name="Perhitungan", index=False)
        pd.DataFrame([{"Line": k, "Total MP": line_mp[k], "Total Kapasitas Bulanan": line_cap_month[k]} for k in line_mp]).to_excel(writer, sheet_name="Distribusi Line", index=False)
        pd.DataFrame([{"Stall": k, "Total MP": stall_mp[k], "Total Kapasitas Bulanan": stall_cap_month[k]} for k in stall_mp]).to_excel(writer, sheet_name="Distribusi Stall", index=False)

    with open("hasil_perhitungan.xlsx", "rb") as f:
        st.download_button("📥 Unduh Hasil Perhitungan", f, file_name="hasil_perhitungan.xlsx")
