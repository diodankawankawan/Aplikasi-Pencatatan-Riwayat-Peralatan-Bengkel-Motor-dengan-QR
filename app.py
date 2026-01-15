"""
Aplikasi Pencatatan Riwayat Peralatan Bengkel Motor dengan QR
Main Application - Streamlit UI
"""

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt

# Import fungsi dari utils.py
from utils import (
    init_excel, init_folders,
    get_all_alat, get_alat_by_id, add_alat, update_alat, delete_alat, filter_alat,
    get_all_servis, get_riwayat_servis, add_servis,
    get_statistik, get_chart_kondisi, get_servis_terbaru,
    generate_qr, save_qr_to_file, get_qr_file_path, decode_qr,
    validate_input
)

# ==================== KONFIGURASI STREAMLIT ====================
st.set_page_config(
    page_title="Pencatatan Peralatan Bengkel Motor",
    page_icon=None,
    layout="wide"
)

# Inisialisasi
init_excel()
init_folders()

# ==================== SIDEBAR MENU ====================
with st.sidebar:
    st.title("Bengkel Motor")
    st.divider()
    selected = option_menu(
        menu_title="Menu Utama",
        options=["Dashboard", "Data Alat", "Scan QR", "Riwayat Servis"],
        icons=None,
        menu_icon=None,
        default_index=0,
    )

# ==================== HALAMAN DASHBOARD ====================
if selected == "Dashboard":
    st.title("Dashboard Peralatan Bengkel")
    
    stats = get_statistik()
    
    # Statistik Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Alat", value=stats['total'])
    with col2:
        st.metric(label="Kondisi Baik", value=stats['baik'])
    with col3:
        st.metric(label="Rusak Ringan", value=stats['rusak_ringan'])
    with col4:
        st.metric(label="Rusak Berat", value=stats['rusak_berat'])
    
    st.divider()
    
    # Grafik
    col_chart, col_empty = st.columns([1, 2])
    with col_chart:
        st.subheader("Grafik Kondisi Alat")
        chart_kondisi = get_chart_kondisi()
        if chart_kondisi:
            fig1, ax1 = plt.subplots(figsize=(3, 3))
            fig1.patch.set_alpha(0)
            ax1.set_facecolor('none')
            colors = ['#28a745', '#ffc107', '#dc3545']
            ax1.pie(
                chart_kondisi.values(), 
                labels=chart_kondisi.keys(), 
                autopct='%1.0f%%',
                colors=colors[:len(chart_kondisi)],
                startangle=90,
                textprops={'color': 'white'}
            )
            ax1.axis('equal')
            st.pyplot(fig1, transparent=True)
        else:
            st.info("Belum ada data.")
    
    st.divider()
    
    # Ringkasan
    col_stat1, col_stat2 = st.columns(2)
    
    with col_stat1:
        st.subheader("Total Servis")
        st.metric(label="Jumlah Servis", value=stats['total_servis'])
        st.metric(label="Total Biaya Servis", value=f"Rp {stats['total_biaya']:,.0f}")
    
    with col_stat2:
        st.subheader("Catatan Servis Terbaru")
        df_terbaru = get_servis_terbaru(5)
        if len(df_terbaru) > 0:
            st.dataframe(df_terbaru, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada catatan servis.")
    
    st.divider()
    
    # Daftar Semua Alat
    st.subheader("Daftar Semua Alat")
    df_alat = get_all_alat()
    if len(df_alat) > 0:
        st.dataframe(df_alat, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data alat. Silakan tambah alat baru di menu Data Alat.")

# ==================== HALAMAN DATA ALAT ====================
elif selected == "Data Alat":
    st.title("Manajemen Data Alat")
    
    tab1, tab2 = st.tabs(["Tambah Alat Baru", "Daftar Alat"])
    
    with tab1:
        st.subheader("Form Tambah Alat Baru")
        
        with st.form("form_tambah_alat", clear_on_submit=True):
            nama = st.text_input("Nama Alat *", placeholder="Contoh: Kunci Pas 10mm")
            kondisi = st.selectbox(
                "Kondisi *",
                options=["Baik", "Rusak Ringan", "Rusak Berat"]
            )
            tanggal_beli = st.date_input("Tanggal Beli", value=date.today())
            keterangan = st.text_area("Keterangan", placeholder="Keterangan tambahan...")
            
            submitted = st.form_submit_button("Simpan", use_container_width=True)
            
            if submitted:
                if not nama or nama.strip() == "":
                    st.error("Nama alat tidak boleh kosong")
                else:
                    new_id = add_alat(nama, kondisi, str(tanggal_beli), keterangan)
                    st.success(f"Alat berhasil ditambahkan dengan ID: {new_id}")
                    st.rerun()
    
    with tab2:
        st.subheader("Daftar Alat")
        
        # Filter Section
        st.write("**Filter Data:**")
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            keyword = st.text_input("Cari Nama/ID", placeholder="Ketik untuk mencari...")
        with col_filter2:
            filter_kondisi = st.selectbox(
                "Kondisi",
                options=["Semua", "Baik", "Rusak Ringan", "Rusak Berat"],
                key="filter_kond"
            )
        
        # Tampilkan data dengan filter
        df_alat = filter_alat(keyword, filter_kondisi)
        
        if len(df_alat) > 0:
            st.dataframe(df_alat, use_container_width=True, hide_index=True)
            st.write(f"Menampilkan {len(df_alat)} data")
            
            st.divider()
            
            # Edit Section
            st.subheader("Edit / Hapus Alat")
            
            # Dropdown dengan format "ID - Nama"
            alat_options = [f"{row['ID']} - {row['Nama']}" for _, row in df_alat.iterrows()]
            selected_option = st.selectbox("Pilih Alat", options=alat_options, key="edit_select")
            
            if selected_option:
                selected_id = selected_option.split(" - ")[0]
                alat_data = get_alat_by_id(selected_id)
                
                if alat_data:
                    col_edit, col_qr = st.columns([2, 1])
                    
                    with col_edit:
                        with st.form("form_edit_alat"):
                            nama_edit = st.text_input("Nama Alat", value=alat_data['Nama'])
                            kondisi_options = ["Baik", "Rusak Ringan", "Rusak Berat"]
                            kondisi_index = kondisi_options.index(alat_data['Kondisi']) if alat_data['Kondisi'] in kondisi_options else 0
                            kondisi_edit = st.selectbox("Kondisi", options=kondisi_options, index=kondisi_index)
                            
                            try:
                                tgl_beli_value = pd.to_datetime(alat_data['Tanggal_Beli']).date()
                            except:
                                tgl_beli_value = date.today()
                            tanggal_beli_edit = st.date_input("Tanggal Beli", value=tgl_beli_value)
                            keterangan_edit = st.text_area("Keterangan", value=str(alat_data['Keterangan']) if pd.notna(alat_data['Keterangan']) else "")
                            
                            col_btn1, col_btn2 = st.columns(2)
                            
                            with col_btn1:
                                btn_update = st.form_submit_button("Update", use_container_width=True)
                            with col_btn2:
                                btn_delete = st.form_submit_button("Hapus", use_container_width=True, type="secondary")
                            
                            if btn_update:
                                update_alat(selected_id, nama_edit, kondisi_edit, str(tanggal_beli_edit), keterangan_edit)
                                st.success("Data alat berhasil diupdate!")
                                st.rerun()
                            
                            if btn_delete:
                                delete_alat(selected_id)
                                st.success("Alat berhasil dihapus!")
                                st.rerun()
                    
                    with col_qr:
                        st.subheader("QR Code")
                        qr_bytes = generate_qr(selected_id)
                        st.image(qr_bytes, caption=f"QR: {selected_id}", width=150)
                        st.download_button(
                            label="Download QR",
                            data=qr_bytes.getvalue(),
                            file_name=f"QR_{selected_id}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                        if st.button("Simpan ke /qr", use_container_width=True):
                            file_path = save_qr_to_file(selected_id)
                            st.success(f"Disimpan: {file_path}")
        else:
            st.info("Tidak ada data yang sesuai filter.")

# ==================== HALAMAN SCAN QR ====================
elif selected == "Scan QR":
    st.title("Scan QR Code")
    
    tab_scan1, tab_scan2 = st.tabs(["Scan dengan Kamera", "Upload Gambar"])
    
    with tab_scan1:
        st.subheader("Scan dengan Kamera")
        camera_image = st.camera_input("Arahkan kamera ke QR Code")
        
        if camera_image is not None:
            image_bytes = camera_image.getvalue()
            alat_id = decode_qr(image_bytes)
            
            if alat_id:
                st.success(f"QR Code terdeteksi: {alat_id}")
                alat_data = get_alat_by_id(alat_id)
                
                if alat_data:
                    st.subheader("Detail Alat")
                    st.write(f"**ID:** {alat_data['ID']}")
                    st.write(f"**Nama:** {alat_data['Nama']}")
                    st.write(f"**Kondisi:** {alat_data['Kondisi']}")
                else:
                    st.warning(f"Alat dengan ID {alat_id} tidak ditemukan.")
            else:
                st.info("Arahkan kamera ke QR Code dan ambil foto.")
    
    with tab_scan2:
        st.subheader("Upload Gambar QR Code")
        uploaded_file = st.file_uploader("Pilih file gambar QR", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, caption="Gambar QR yang diupload", width=300)
        
        image_bytes = uploaded_file.getvalue()
        alat_id = decode_qr(image_bytes)
        
        with col2:
            if alat_id:
                st.success(f"QR Code terdeteksi: {alat_id}")
                alat_data = get_alat_by_id(alat_id)
                
                if alat_data:
                    st.subheader("Detail Alat")
                    st.write(f"**ID:** {alat_data['ID']}")
                    st.write(f"**Nama:** {alat_data['Nama']}")
                    st.write(f"**Kondisi:** {alat_data['Kondisi']}")
                    st.write(f"**Tanggal Beli:** {alat_data['Tanggal_Beli']}")
                    st.write(f"**Keterangan:** {alat_data['Keterangan'] if pd.notna(alat_data['Keterangan']) else '-'}")
                else:
                    st.warning(f"Alat dengan ID {alat_id} tidak ditemukan dalam database.")
            else:
                st.error("Tidak dapat membaca QR Code. Pastikan gambar jelas dan berisi QR Code yang valid.")
        
        # Jika QR terdeteksi dan alat ditemukan, tampilkan fitur tambahan
        if alat_id:
            alat_data = get_alat_by_id(alat_id)
            
            if alat_data:
                st.divider()
                
                # Riwayat Servis
                st.subheader("Riwayat Servis")
                df_servis = get_riwayat_servis(alat_id)
                
                if len(df_servis) > 0:
                    st.dataframe(df_servis, use_container_width=True, hide_index=True)
                else:
                    st.info("Belum ada riwayat servis untuk alat ini.")
                
                st.divider()
                
                # Form Tambah Servis
                col_form1, col_form2 = st.columns(2)
                
                with col_form1:
                    st.subheader("Tambah Catatan Servis")
                    
                    with st.form("form_tambah_servis"):
                        tanggal_servis = st.date_input("Tanggal Servis", value=date.today())
                        jenis_servis = st.selectbox(
                            "Jenis Servis",
                            options=["Perbaikan", "Perawatan Rutin", "Penggantian Komponen", "Kalibrasi", "Lainnya"]
                        )
                        biaya = st.number_input("Biaya (Rp)", min_value=0, step=1000)
                        keterangan_servis = st.text_area("Keterangan", placeholder="Detail servis yang dilakukan...")
                        
                        submitted = st.form_submit_button("Simpan Servis", use_container_width=True)
                        
                        if submitted:
                            servis_id = add_servis(alat_id, str(tanggal_servis), jenis_servis, biaya, keterangan_servis)
                            st.success(f"Catatan servis berhasil ditambahkan dengan ID: {servis_id}")
                            st.rerun()
                
                with col_form2:
                    st.subheader("Update Kondisi Alat")
                    
                    with st.form("form_update_kondisi"):
                        kondisi_options = ["Baik", "Rusak Ringan", "Rusak Berat"]
                        kondisi_index = kondisi_options.index(alat_data['Kondisi']) if alat_data['Kondisi'] in kondisi_options else 0
                        new_kondisi = st.selectbox("Kondisi Baru", options=kondisi_options, index=kondisi_index)
                        
                        submitted_kondisi = st.form_submit_button("Update Kondisi", use_container_width=True)
                        
                        if submitted_kondisi:
                            update_alat(
                                alat_id, 
                                alat_data['Nama'], 
                                new_kondisi, 
                                str(alat_data['Tanggal_Beli']), 
                                alat_data['Keterangan'] if pd.notna(alat_data['Keterangan']) else ""
                            )
                            st.success("Kondisi alat berhasil diupdate!")
                            st.rerun()

# ==================== HALAMAN RIWAYAT SERVIS ====================
elif selected == "Riwayat Servis":
    st.title("Riwayat Servis")
    
    df_alat = get_all_alat()
    df_servis = get_all_servis()
    
    # Filter
    st.subheader("Filter")
    filter_options = ["Semua Alat"] + [f"{row['ID']} - {row['Nama']}" for _, row in df_alat.iterrows()]
    selected_filter = st.selectbox("Pilih Alat", options=filter_options)
    
    st.divider()
    
    st.subheader("Data Riwayat Servis")
    
    if selected_filter == "Semua Alat":
        if len(df_servis) > 0:
            df_display = df_servis.copy()
            
            def get_nama_alat(alat_id):
                alat = get_alat_by_id(alat_id)
                return alat['Nama'] if alat else "-"
            
            df_display['Nama_Alat'] = df_display['ID_Alat'].apply(get_nama_alat)
            cols = ['ID_Servis', 'ID_Alat', 'Nama_Alat', 'Tanggal', 'Jenis_Servis', 'Biaya', 'Keterangan']
            df_display = df_display[cols]
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Statistik
            total_biaya = df_servis['Biaya'].sum()
            st.write(f"**Total Biaya Servis:** Rp {total_biaya:,.0f}")
        else:
            st.info("Belum ada data riwayat servis.")
    else:
        alat_id = selected_filter.split(" - ")[0]
        df_filtered = get_riwayat_servis(alat_id)
        
        if len(df_filtered) > 0:
            st.dataframe(df_filtered, use_container_width=True, hide_index=True)
            
            total_biaya = df_filtered['Biaya'].sum()
            st.write(f"**Total Biaya Servis untuk {selected_filter}:** Rp {total_biaya:,.0f}")
        else:
            st.info(f"Belum ada riwayat servis untuk {selected_filter}.")


