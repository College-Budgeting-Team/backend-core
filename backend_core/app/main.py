from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Setup Path biar C++ kebaca
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import survival_lib
except ImportError:
    survival_lib = None 

app = FastAPI(title="College Budgeting API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Active", "engine": "C++ Ready" if survival_lib else "Missing"}

@app.get("/cek-survival")
def cek_survival(saldo: float, pengeluaran: float):
    if not survival_lib:
        return {"error": "Modul C++ belum di-compile!"}
    
    # 1. Panggil Otak C++
    sisa_hari = survival_lib.prediksi_bangkrut(saldo, pengeluaran)
    
    # 2. Logic "Black Zone"
    if sisa_hari <= 0:
        status_hari = "Tidak Ada Sisa "
        pesan = "💀 BLACK ZONE!!! HATI-HATI SEGERA KELUAR DARI ZONA INI!!"
        zona = "black"
    elif sisa_hari < 20:
        status_hari = sisa_hari
        pesan = "⚠️ RED ZONE!! Hemat lagi ya, jangan boros-boros!"
        zona = "red"
    else:
        status_hari = sisa_hari
        pesan = "✅ Green Zone. Aman."
        zona = "green"

    return {
        "saldo": saldo,
        "pengeluaran_harian": pengeluaran,
        "sisa_hari_bertahan": status_hari,
        "pesan": pesan,
        "zona": zona 
    }