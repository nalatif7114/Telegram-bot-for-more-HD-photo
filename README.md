# 🖼️ Telegram Image Upscaler Bot

Bot Telegram untuk meningkatkan resolusi gambar menggunakan algoritma **Lanczos** berkualitas tinggi.

## ✨ Fitur
- Upscale gambar 2x, 3x, atau 4x
- Mendukung pengiriman foto (compressed) maupun file dokumen (original)
- Algoritma Lanczos untuk hasil terbaik
- Antarmuka tombol interaktif

---

## 🚀 Deploy Gratis

### Opsi 1: Railway (Direkomendasikan)

1. **Buat bot Telegram:**
   - Buka [@BotFather](https://t.me/BotFather) di Telegram
   - Ketik `/newbot` dan ikuti instruksi
   - Salin **BOT_TOKEN** yang diberikan

2. **Deploy ke Railway:**
   - Daftar di [railway.app](https://railway.app) (gratis, cukup login dengan GitHub)
   - Klik **"New Project"** → **"Deploy from GitHub repo"**
   - Upload/push folder ini ke GitHub lalu hubungkan
   - Di Railway dashboard, buka tab **Variables**
   - Tambahkan variabel: `BOT_TOKEN` = token dari BotFather
   - Railway akan otomatis deploy!

3. **Cek bot berjalan:**
   - Buka tab **Logs** di Railway
   - Harusnya muncul: `🤖 Bot berjalan...`

---

### Opsi 2: Render

1. Daftar di [render.com](https://render.com)
2. Klik **"New"** → **"Background Worker"**
3. Hubungkan repo GitHub
4. Set **Start Command**: `python bot.py`
5. Tambahkan **Environment Variable**: `BOT_TOKEN` = token kamu
6. Klik Deploy

---

### Opsi 3: Lokal (Testing)

```bash
# Install dependencies
pip install -r requirements.txt

# Set token (Linux/Mac)
export BOT_TOKEN="token_kamu_di_sini"

# Set token (Windows)
set BOT_TOKEN=token_kamu_di_sini

# Jalankan bot
python bot.py
```

---

## 📂 Struktur File

```
telegram-upscale-bot/
├── bot.py           # Kode utama bot
├── requirements.txt # Dependencies Python
├── Procfile         # Untuk Railway/Heroku
├── railway.toml     # Konfigurasi Railway
└── README.md        # Panduan ini
```

---

## 🛠️ Cara Pakai Bot

1. Cari bot kamu di Telegram
2. Ketik `/start`
3. Kirim gambar (sebagai **foto** atau **file/dokumen**)
4. Pilih skala: **2x**, **3x**, atau **4x**
5. Tunggu beberapa detik → gambar HD siap diunduh! 🎉

> **Tips:** Kirim gambar sebagai *file/dokumen* agar kualitas asli terjaga sebelum diupscale.

---

## ⚠️ Batasan

- Telegram membatasi ukuran file output maksimal **20 MB**
- Gambar yang terlalu besar sebelum/sesudah upscale mungkin gagal
- Gunakan skala lebih kecil jika gambar awal sudah besar (> 2000px)

---

## 🧰 Teknologi

- [python-telegram-bot](https://python-telegram-bot.org/) v21
- [Pillow (PIL)](https://pillow.readthedocs.io/) — image processing dengan Lanczos resampling
