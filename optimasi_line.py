import streamlit as st
import pandas as pd
import math

st.title("🔧 Optimasi MP Line & Stall")

# Data barang
if "barang" not in st.session_state:
    st.session_state.barang = []

st.subheader("Input Barang")
nama = st.text_input("Nama Barang")
ct = st.number_input("Cycle Time (menit/unit)", min_value=0.1, step=0.1)
qty = st.number_input("Planning Bulanan (unit)", min_value=0, step=1)

if st.button("➕ Tambah Barang"):
    if nama:  # jangan kosong
        st.session_state.barang.append({"Nama": nama, "CT": ct, "Qty": qty})
        st.success(f"Barang '{nama}' berhasil ditambahkan!")
    else:
        st.warning("Nama barang tidak boleh kosong!")

# ============================
# Tampilkan Data, Edit & Hapus
# ============================
if st.session_state.barang:
    df = pd.DataFrame(st.session_state.barang)
    st.table(df)

    st.subheader("✏️ Edit / Hapus Barang")
    idx = st.selectbox("Pilih barang", range(len(df)), 
                       format_func=lambda x: df.iloc[x]["Nama"])

    edit_nama = st.text_input("Edit Nama Barang", value=df.iloc[idx]["Nama"], key="edit_nama")
    edit_ct = st.number_input("Edit CT", min_value=0.1, step=0.1, value=float(df.iloc[idx]["CT"]), key="edit_ct")
    edit_qty = st.number_input("Edit Qty", min_value=0, step=1, value=int(df.iloc[idx]["Qty"]), key="edit_qty")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Simpan Perubahan"):
            st.session_state.barang[idx] = {"Nama": edit_nama, "CT": edit_ct, "Qty": edit_qty}
            st.success(f"Barang '{edit_nama}' berhasil diupdate!")
    with col2:
        if st.button("🗑 Hapus Barang"):
            removed = st.session_state.barang.pop(idx)
            st.success(f"Barang '{removed['Nama']}' berhasil dihapus!")

st.subheader("Parameter Produksi")
jam_kerja = st.number_input("Jam Kerja (menit per hari)", value=430, step=10)
hari_kerja = st.number_input("Hari Kerja (per bulan)", value=20, step=1)
max_mp_line = st.number_input("Max MP per Line", value=11, step=1)
max_mp_stall = st.number_input("Max MP per Stall", value=4, step=1)

# ======================
# Kalkulasi Distribusi
# ======================
if st.button("🚀 Kalkulasi"):
    df = pd.DataFrame(st.session_state.barang)
    if df.empty:
        st.warning("Masukkan barang terlebih dahulu!")
    else:
        waktu_per_orang = jam_kerja * hari_kerja
        df["Total Waktu"] = df["CT"] * df["Qty"]

        # Tentukan median CT sebagai batas Line/Stall
        median_ct = df["CT"].median()
        line_items = df[df["CT"] <= median_ct].sort_values("CT").reset_index(drop=True)
        stall_items = df[df["CT"] > median_ct].sort_values("CT").reset_index(drop=True)

        st.subheader("📌 Hasil Kalkulasi")

        # ================================
        # Distribusi Line (3 line)
        # ================================
        st.write("### Line (3 Line)")
        line_groups = {1: [], 2: [], 3: []}
        for i, row in line_items.iterrows():
            line_num = (i % 3) + 1  # round robin
            line_groups[line_num].append(row)

        for ln in line_groups:
            items = line_groups[ln]
            if not items:
                st.write(f"Line {ln} : kosong")
                continue
            df_line = pd.DataFrame(items)
            total_waktu = df_line["Total Waktu"].sum()
            total_qty = df_line["Qty"].sum()
            mp = math.ceil(total_waktu / waktu_per_orang)
            mp = min(mp, max_mp_line)
            takt = jam_kerja / (total_qty / hari_kerja) if total_qty else 0
            cap = jam_kerja / df_line["CT"].mean() if not df_line.empty else 0

            st.write(f"**Line {ln}:**")
            st.write(f"- Barang: {', '.join(df_line['Nama'])}")
            st.write(f"- Takt Time: {takt:.2f} menit")
            st.write(f"- MP Dibutuhkan: {mp} orang (max {max_mp_line})")
            st.write(f"- Kapasitas max/hari: {cap:.0f} unit")

        # ================================
        # Distribusi Stall (4 stall)
        # ================================
        st.write("### Stall (4 Stall)")
        stall_groups = {1: [], 2: [], 3: [], 4: []}
        for i, row in stall_items.iterrows():
            stall_num = (i % 4) + 1  # round robin
            stall_groups[stall_num].append(row)

        for sn in stall_groups:
            items = stall_groups[sn]
            if not items:
                st.write(f"Stall {sn} : kosong")
                continue
            df_stall = pd.DataFrame(items)
            total_waktu = df_stall["Total Waktu"].sum()
            total_qty = df_stall["Qty"].sum()
            mp = math.ceil(total_waktu / waktu_per_orang)
            mp = min(mp, max_mp_stall)
            takt = jam_kerja / (total_qty / hari_kerja) if total_qty else 0
            cap = jam_kerja / df_stall["CT"].mean() if not df_stall.empty else 0

            st.write(f"**Stall {sn}:**")
            st.write(f"- Barang: {', '.join(df_stall['Nama'])}")
            st.write(f"- Takt Time: {takt:.2f} menit")
            st.write(f"- MP Dibutuhkan: {mp} orang (max {max_mp_stall})")
            st.write(f"- Kapasitas max/hari: {cap:.0f} unit")

        # ================================
        # Rangkuman per Barang
        # ================================
        st.write("### 📊 Rangkuman Total per Barang")
        df_summary = df.copy()
        df_summary["Unit/Day"] = (jam_kerja / df_summary["CT"]).astype(int)
        df_summary["Unit/Month"] = df_summary["Unit/Day"] * hari_kerja

        st.table(df_summary[["Nama", "CT", "Qty", "Unit/Day", "Unit/Month"]])
