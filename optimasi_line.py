# ================================
# Distribusi Line (3 line) – balance by CT
# ================================
st.write("### Line (3 Line) – Balanced by CT")
line_groups = {1: [], 2: [], 3: []}
line_mp = {1: 0, 2: 0, 3: 0}

# Sort barang ascending CT supaya CT mirip bisa barengan
line_items_sorted = line_items.sort_values(by="CT").reset_index(drop=True)

for _, row in line_items_sorted.iterrows():
    # pilih line dengan MP terkecil
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

    st.write(f"**Line {ln}:**")
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
# Distribusi Stall (4 stall) – balance by CT
# ================================
st.write("### Stall (4 Stall) – Balanced by CT")
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

    st.write(f"**Stall {sn}:**")
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
