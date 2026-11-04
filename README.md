# PhishKit — Phishing Simulation Toolkit

Tool edukasi cybersecurity untuk demo phishing langsung di seminar.

## Persyaratan

- Python 3.8+
- Pip (Python package manager)

## Cara Install

1. Buka Command Prompt / PowerShell di folder `phishkit/`

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Jalankan server:
   ```
   python phishkit.py
   ```

4. Buka browser:
   - **Dashboard:** http://127.0.0.1:8080/dashboard
   - **Template selector:** http://127.0.0.1:8080

## Cara Pakai di Seminar

1. Pastikan laptop presenter dan audiens terhubung ke **WiFi/karingan yang sama**
2. Jalankan `python phishkit.py`
3. Buka Dashboard di browser laptop
4. Buka Template Selector, pilih template phishing yang diinginkan
5. Bagikan URL ke audiens: `http://<IP_LAPTOP>:8080/phish/<template>`
   - Cek IP laptop dengan `ipconfig` (cari IPv4 Address)
   - Contoh: `http://192.168.1.10:8080/phish/bpksdm`
6. Dashboard akan menampilkan data real-time
7. Akhiri demo dengan klik **Debrief Mode** untuk memperlihatkan data yang tertangkap
8. Klik **Edukasi** untuk materi anti-phishing
9. Klik **Export PDF** untuk laporan demo

## Template Tersedia

| Route | Template |
|-------|----------|
| `/phish/google` | Google Login |
| `/phish/linkedin` | LinkedIn Login |
| `/phish/instagram` | Instagram Login |
| `/phish/facebook` | Facebook Login |
| `/phish/bpksdm` | BPKSDM Kota Bekasi |

## ⚠️ Etika Penggunaan

- Alat ini **hanya untuk edukasi** dalam seminar/sosialisasi cybersecurity
- Tampilkan banner peringatan demo di setiap halaman
- Jangan gunakan untuk mencuri data sungguhan
- Hapus data setelah sesi selesai (tombol Reset di Dashboard)
- Semua data disimpan lokal, tidak dikirim ke mana pun

## Struktur File

```
phishkit/
├── phishkit.py                  # Main server
├── requirements.txt             # Python dependencies
├── README.md                    # Dokumentasi
├── templates/
│   ├── selector.html            # Template picker
│   ├── google.html              # Google phishing page
│   ├── linkedin.html            # LinkedIn phishing page
│   ├── instagram.html           # Instagram phishing page
│   ├── facebook.html            # Facebook phishing page
│   ├── bpksdm.html              # BPKSDM phishing page
│   └── dashboard/
│       ├── live.html            # Live monitoring dashboard
│       └── edukasi.html         # Edukasi anti-phishing
├── static/
│   ├── css/dashboard.css        # Dashboard styles
│   └── js/dashboard.js          # Dashboard logic
├── report/
│   ├── __init__.py
│   └── generator.py             # PDF report generator
└── data/
    └── phishkit.db              # SQLite database (auto-generated)
```