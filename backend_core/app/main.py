from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .db import models, database
import sys
import os

models.Base.metadata.create_all(bind=database.engine)

# Setup Path biar C++ kebaca
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    return {"status": "Active", "engine": " Ready" if survival_lib else "Missing"}

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
    
@app.post("/simpan-hasil")
def save_result(saldo: float, pengeluaran: float, sisa: str, zona: str, db: Session = Depends(get_db)):
    new_record = models.SurvivalRecord(
        saldo=saldo,
        pengeluaran_harian=pengeluaran,
        sisa_hari=sisa,
        zona=zona
    )
    db.add(new_record)
    db.commit()
    return {"status": "success", "message": "Data tersimpan!"}

@app.get("/riwayat")
def ambil_riwayat(db: Session = Depends(get_db)):
    records = db.query(models.SurvivalRecord).order_by(models.SurvivalRecord.id.desc()).all()
    return records

@app.delete("/hapus-riwayat/{id}")
def hapus_riwayat(id: int, db: Session = Depends(get_db)):
    record = db.query(models.SurvivalRecord).filter(models.SurvivalRecord.id == id).first()
    
    if not record:
        return {"error": "Data tidak ditemukan!"}
    
    db.delete(record)
    db.commit()
    return {"status": "success", "message": f"{id} berhasil dihapus"}