from fastapi import FastAPI
import sys
import os

# Trik biar Python bisa nemu file .so hasil compile C++ di folder root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Modul C++ (Nama harus sama kayak di PYBIND11_MODULE)
try:
    import survival_lib
except ImportError:
    survival_lib = None # Fallback kalau belum dicompile

app = FastAPI(title="College Budgeting API")

@app.get("/")
def read_root():
    return {"message": "Server Backend Aktif!", "cpp_status": "Ready" if survival_lib else "Not Compiled"}

@app.get("/cek-survival")
def cek_survival(saldo: float, pengeluaran: float):
    if not survival_lib:
        return {"error": "Modul C++ belum di-compile!"}
    
    # PANGGIL FUNGSI C++ DISINI
    sisa_hari = survival_lib.prediksi_bangkrut(saldo, pengeluaran)
    
    return {
        "saldo": saldo,
        "pengeluaran_harian": pengeluaran,
        "sisa_hari_bertahan": sisa_hari,
        "pesan": "Hemat bang!" if sisa_hari < 30 else "Aman sentosa."
    }