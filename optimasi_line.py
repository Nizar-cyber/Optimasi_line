import streamlit as st
import pandas as pd

# Fungsi untuk membuat template Excel
def create_template_excel():
    template_data = {
        "Nama": ["Barang A", "Barang B", "Barang C"],
        "CT": [10, 8, 12],
        "MP": [2, 1, 3],
        "Demand/day": [100, 80, 120],
        "Qty": [3000, 2400, 3600]
    }
    df_template = pd.DataFrame(template_data)
    df_template.to_excel("template_barang.xlsx", index=False)

# Buat file template saat aplikasi dijalankan
create_template_excel()

# UI Streamlit
st.set_page_config(page_title="Distribusi Line & Stall", layout="wide")
st.title("📊 Distribusi Line dan Stall Berdasarkan CT")

# Tombol unduh template
with open("template_barang.xlsx", "rb") as f:
    st.download_button("📥 Unduh Template Excel", f, file_name="template_barang.xlsx")

# Upload file input
uploaded_file = st.file_uploader("📤 Unggah file data barang (Excel)", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    st.subheader("📋 Data Barang")
    st.dataframe(df)

    # Inisialisasi variabel
    line_items = df.copy()
    stall_items = df.copy()
    max_mp_line = 5
    max_mp_stall = 4
    total_mp_all = 0
    result_data = []
    takt = 12.5

    # ================================
    # Distribusi Line (3 line)
    # ================================
    st.subheader("🏭 Distribusi Line (3 Line) - Balanced by CT")
    line_groups = {1: [], 2: [], 3: []}
    line_mp = {1: 0, 2: 0, 3: 0}

    line_items_sorted = line_items.sort_values(by="CT").reset_index(drop=True)

    for _, row in line_items_sorted.iterrows():
        min_line = min(line_mp, key=line_mp.get)
        line_groups[min_line].append(row)
        line_mp[min_line] += row["MP"]

    for ln in line_groups:
        items = line_groups[ln]
        if not items:
            st.write(f"Line {ln} : kosong")
            continue
        df_line = pd.DataFrame(items)

        mp = df_line["MP"].sum()
        mp = min(mp, max_mp_line)
        cap_day = df_line["Demand/day"].sum()
        cap_month = df_line["Qty"].sum()

        total_mp_all += mp

        st.markdown(f"**Line {ln}:**")
        st.write(f"- Barang: {', '.join(df_line['Nama'])}")
        st.write(f"- MP Dibutuhkan: {mp} orang (max {max_mp_line})")
        st.write(f"- Kapasitas: {cap_day:.0f} unit/hari ({cap_month:.0f} unit/bulan)")

        result_data.append({
            "Grup": f"Line {ln}",
            "Barang": ", ".join(df_line["Nama"]),
            "Takt": f"{takt:.2f}",
            "MP": mp,
            "Cap/Hari": cap_day,
            "Cap/Bulan": cap_month
        })

    # ================================
    # Distribusi Stall (4 stall)
    # ================================
    st.subheader("🔧 Distribusi Stall (4 Stall) - Balanced by CT")
    stall_groups = {1: [], 2: [], 3: [], 4: []}
    stall_mp = {1: 0, 2: 0, 3: 0, 4: 0}

    stall_items_sorted = stall_items.sort_values(by="CT").reset_index(drop=True)

    for _, row in stall_items_sorted.iterrows():
        min_stall = min(stall_mp, key=stall_mp.get)
        stall_groups[min_stall].append(row)
        stall_mp[min_stall] += row["MP"]

    for sn in stall_groups:
        items = stall_groups[sn]
        if not items:
            st.write(f"Stall {sn} : kosong")
            continue
        df_stall = pd.DataFrame(items)

        mp = df_stall["MP"].sum()
        mp = min(mp, max_mp_stall)
        cap_day = df_stall["Demand/day"].sum()
        cap_month = df_stall["Qty"].sum()

        total_mp_all += mp

        st.markdown(f"**Stall {sn}:**")
        st.write(f"- Barang: {', '.join(df_stall['Nama'])}")
        st.write(f"- MP Dibutuhkan: {mp} orang (max {max_mp_stall})")
        st.write(f"- Kapasitas: {cap_day:.0f} unit/hari ({cap_month:.0f} unit/bulan)")

        result_data.append({
            "Grup": f"Stall {sn}",
            "Barang": ", ".join(df_stall["Nama"]),
            "Takt": f"{takt:.2f}",
            "MP": mp,
            "Cap/Hari": cap_day,
            "Cap/Bulan": cap_month
        })

    # Tampilkan hasil akhir
    st.subheader("📊 Rekap Distribusi")
    st.dataframe(pd.DataFrame(result_data))
