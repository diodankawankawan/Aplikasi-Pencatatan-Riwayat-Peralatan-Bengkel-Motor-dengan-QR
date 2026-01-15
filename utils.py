"""
Utils Module - Fungsi-fungsi untuk Aplikasi Pencatatan Riwayat Peralatan Bengkel Motor
Berisi: CRUD, QR Code, Statistik, Filter
"""

import pandas as pd
import os
import qrcode
from io import BytesIO
from PIL import Image
import zxingcpp

# ==================== KONFIGURASI ====================
DATA_DIR = "data"
QR_DIR = "qr"
EXCEL_FILE = os.path.join(DATA_DIR, "data_peralatan.xlsx")

# ==================== FUNGSI INISIALISASI ====================

def init_folders():
    """Inisialisasi folder data dan qr jika belum ada"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(QR_DIR):
        os.makedirs(QR_DIR)
    return True

def init_excel():
    """Inisialisasi file Excel jika belum ada"""
    init_folders()
    if not os.path.exists(EXCEL_FILE):
        df_alat = pd.DataFrame(columns=[
            "ID", "Nama", "Kondisi", "Tanggal_Beli", "Keterangan"
        ])
        df_servis = pd.DataFrame(columns=[
            "ID_Servis", "ID_Alat", "Tanggal", "Jenis_Servis", "Biaya", "Keterangan"
        ])
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            df_alat.to_excel(writer, sheet_name='Alat', index=False)
            df_servis.to_excel(writer, sheet_name='Servis', index=False)
    return True

# ==================== FUNGSI CRUD ALAT ====================

def get_all_alat():
    """Ambil semua data alat dari Excel"""
    init_excel()
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name='Alat')
        return df
    except Exception:
        return pd.DataFrame(columns=[
            "ID", "Nama", "Kondisi", "Tanggal_Beli", "Keterangan"
        ])

def get_alat_by_id(alat_id):
    """Ambil data alat berdasarkan ID"""
    df = get_all_alat()
    result = df[df['ID'] == alat_id]
    if len(result) > 0:
        return result.iloc[0].to_dict()
    return None

def generate_new_id():
    """Generate ID baru untuk alat"""
    df = get_all_alat()
    if len(df) == 0:
        return "ALT01"
    last_id = df['ID'].iloc[-1]
    try:
        num = int(last_id[3:]) + 1
        return f"ALT{num:02d}"
    except:
        return f"ALT{len(df)+1:02d}"

def add_alat(nama, kondisi, tanggal_beli, keterangan):
    """Tambah alat baru ke Excel"""
    init_excel()
    df_alat = get_all_alat()
    new_id = generate_new_id()
    new_row = pd.DataFrame([{
        "ID": new_id,
        "Nama": nama,
        "Kondisi": kondisi,
        "Tanggal_Beli": tanggal_beli,
        "Keterangan": keterangan
    }])
    df_alat = pd.concat([df_alat, new_row], ignore_index=True)
    df_servis = pd.read_excel(EXCEL_FILE, sheet_name='Servis')
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        df_alat.to_excel(writer, sheet_name='Alat', index=False)
        df_servis.to_excel(writer, sheet_name='Servis', index=False)
    return new_id

def update_alat(alat_id, nama, kondisi, tanggal_beli, keterangan):
    """Update data alat berdasarkan ID"""
    df_alat = get_all_alat()
    df_servis = pd.read_excel(EXCEL_FILE, sheet_name='Servis')
    mask = df_alat['ID'] == alat_id
    if mask.any():
        df_alat.loc[mask, 'Nama'] = nama
        df_alat.loc[mask, 'Kondisi'] = kondisi
        df_alat.loc[mask, 'Tanggal_Beli'] = tanggal_beli
        df_alat.loc[mask, 'Keterangan'] = keterangan
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            df_alat.to_excel(writer, sheet_name='Alat', index=False)
            df_servis.to_excel(writer, sheet_name='Servis', index=False)
        return True
    return False

def delete_alat(alat_id):
    """Hapus alat beserta riwayat servisnya"""
    df_alat = get_all_alat()
    df_servis = pd.read_excel(EXCEL_FILE, sheet_name='Servis')
    df_alat = df_alat[df_alat['ID'] != alat_id]
    df_servis = df_servis[df_servis['ID_Alat'] != alat_id]
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        df_alat.to_excel(writer, sheet_name='Alat', index=False)
        df_servis.to_excel(writer, sheet_name='Servis', index=False)
    return True

def filter_alat(keyword="", kondisi="Semua"):
    """Filter data alat berdasarkan keyword dan kondisi"""
    df = get_all_alat()
    if len(df) == 0:
        return df
    
    # Filter by keyword (nama atau ID)
    if keyword:
        keyword_lower = keyword.lower()
        mask = (df['Nama'].str.lower().str.contains(keyword_lower, na=False) | 
                df['ID'].str.lower().str.contains(keyword_lower, na=False))
        df = df[mask]
    
    # Filter by kondisi
    if kondisi != "Semua":
        df = df[df['Kondisi'] == kondisi]
    
    return df

# ==================== FUNGSI CRUD SERVIS ====================

def get_all_servis():
    """Ambil semua data servis dari Excel"""
    init_excel()
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name='Servis')
        return df
    except Exception:
        return pd.DataFrame(columns=[
            "ID_Servis", "ID_Alat", "Tanggal", "Jenis_Servis", "Biaya", "Keterangan"
        ])

def get_riwayat_servis(alat_id):
    """Ambil riwayat servis berdasarkan ID alat"""
    df = get_all_servis()
    return df[df['ID_Alat'] == alat_id]

def generate_servis_id():
    """Generate ID baru untuk servis"""
    df = get_all_servis()
    if len(df) == 0:
        return "SRV001"
    last_id = df['ID_Servis'].iloc[-1]
    try:
        num = int(last_id[3:]) + 1
        return f"SRV{num:03d}"
    except:
        return f"SRV{len(df)+1:03d}"

def add_servis(alat_id, tanggal, jenis_servis, biaya, keterangan):
    """Tambah catatan servis baru"""
    init_excel()
    df_alat = get_all_alat()
    df_servis = get_all_servis()
    new_id = generate_servis_id()
    new_row = pd.DataFrame([{
        "ID_Servis": new_id,
        "ID_Alat": alat_id,
        "Tanggal": tanggal,
        "Jenis_Servis": jenis_servis,
        "Biaya": biaya,
        "Keterangan": keterangan
    }])
    df_servis = pd.concat([df_servis, new_row], ignore_index=True)
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        df_alat.to_excel(writer, sheet_name='Alat', index=False)
        df_servis.to_excel(writer, sheet_name='Servis', index=False)
    return new_id

# ==================== FUNGSI STATISTIK & GRAFIK ====================

def get_statistik():
    """Ambil statistik peralatan untuk dashboard"""
    df = get_all_alat()
    df_servis = get_all_servis()
    total = len(df)
    kondisi_baik = len(df[df['Kondisi'] == 'Baik'])
    kondisi_rusak_ringan = len(df[df['Kondisi'] == 'Rusak Ringan'])
    kondisi_rusak_berat = len(df[df['Kondisi'] == 'Rusak Berat'])
    total_servis = len(df_servis)
    total_biaya = df_servis['Biaya'].sum() if len(df_servis) > 0 else 0
    
    return {
        "total": total,
        "baik": kondisi_baik,
        "rusak_ringan": kondisi_rusak_ringan,
        "rusak_berat": kondisi_rusak_berat,
        "total_servis": total_servis,
        "total_biaya": total_biaya
    }

def get_chart_kondisi():
    """Ambil data untuk grafik kondisi alat"""
    df = get_all_alat()
    if len(df) == 0:
        return None
    kondisi_count = df['Kondisi'].value_counts().to_dict()
    return kondisi_count



def get_servis_terbaru(limit=5):
    """Ambil catatan servis terbaru"""
    df = get_all_servis()
    if len(df) == 0:
        return df
    return df.tail(limit)

# ==================== FUNGSI QR CODE ====================

def generate_qr(alat_id):
    """Generate QR Code dari ID alat"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(alat_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def save_qr_to_file(alat_id):
    """Simpan QR Code ke folder /qr"""
    init_folders()
    qr_bytes = generate_qr(alat_id)
    file_path = os.path.join(QR_DIR, f"QR_{alat_id}.png")
    with open(file_path, 'wb') as f:
        f.write(qr_bytes.getvalue())
    return file_path

def get_qr_file_path(alat_id):
    """Ambil path file QR untuk alat tertentu"""
    file_path = os.path.join(QR_DIR, f"QR_{alat_id}.png")
    if os.path.exists(file_path):
        return file_path
    return None

def decode_qr(image_bytes):
    """Decode QR Code dari gambar menggunakan zxingcpp"""
    try:
        # Load image dengan PIL
        image = Image.open(BytesIO(image_bytes))
        
        # Decode dengan zxingcpp
        results = zxingcpp.read_barcodes(image)
        
        if results:
            # Ambil hasil pertama
            return results[0].text
        
        return None
    except Exception as e:
        print(f"Error decode: {e}")
        return None

# ==================== FUNGSI VALIDASI ====================

def validate_input(nama):
    """Validasi input form"""
    errors = []
    if not nama or nama.strip() == "":
        errors.append("Nama alat tidak boleh kosong")
    return errors
