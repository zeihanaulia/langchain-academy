# Panduan: LangChain Academy — Introduction to LangGraph (Bahasa Indonesia)

## Pengantar
Selamat datang di kursus "Introduction to LangGraph" dari LangChain Academy. Kursus ini dibagi menjadi enam modul: dimulai dari dasar hingga topik lanjutan. Setiap modul berisi:

- Video pembelajaran yang menjelaskan konsep utama
- Notebook interaktif untuk praktik (Jupyter)
- Folder `module-x/studio/` yang berisi graph yang akan kita eksplor memakai LangGraph API dan LangGraph Studio

Dokumen ini menjelaskan langkah-langkah setup lokal agar Anda dapat menjalankan notebook dan LangGraph Studio di mesin Anda.

## Ringkasan checklist (apa yang akan kita lakukan)

- [ ] Pastikan Python 3.11 terpasang
- [ ] Clone repository
- [ ] Buat virtual environment dan install dependencies
- [ ] Siapkan API keys (LangSmith, OpenAI, Tavily bila diperlukan)
- [ ] Buat file `.env` untuk setiap module yang punya `studio`
- [ ] Jalankan `langgraph dev` di folder `module-x/studio` untuk membuka Studio

## 1. Persyaratan Python
Gunakan Python 3.11 untuk memastikan kompatibilitas terbaik dengan LangGraph.

Periksa versi Python:

```bash
python3 --version
```

Jika belum 3.11, upgrade atau instal versi yang sesuai.

## 2. Clone repository

```bash
git clone https://github.com/langchain-ai/langchain-academy.git
cd langchain-academy
```

## 3. Buat environment dan install dependensi

```bash
python3 -m venv lc-academy-env
source lc-academy-env/bin/activate
pip install -r requirements.txt
```

Catatan: di beberapa mesin, nama python/venv mungkin berbeda. Pastikan venv aktif (`which python` mengarah ke `lc-academy-env/bin/python`).

## 4. Menjalankan notebook
Jika belum memasang Jupyter, ikuti panduan instalasinya.

Jalankan:

```bash
jupyter notebook
```

Lalu buka notebook yang tersedia di folder `module-x`.

Jika ingin menjalankan di Google Colab, link notebook biasanya tersedia pada halaman masing-masing modul.

## 5. LangSmith (tracing & observability)
LangGraph Studio terintegrasi dengan LangSmith untuk tracing. Daftar dan dapatkan API key di LangSmith.

Tambahkan kunci dan pengaturan ke environment Anda (contoh di file `.env` atau environment shell):

```env
LANGSMITH_API_KEY="your-langsmith-api-key"
LANGSMITH_TRACING_V2=true
LANGSMITH_PROJECT="langchain-academy"
```

Anda bisa menambahkan variabel ini ke `~/.zshrc` atau `~/.bashrc` jika ingin tersedia global, atau menyimpan di file `.env` di setiap module studio.

## 6. OpenAI API Key
Jika menggunakan model OpenAI, daftarkan akun OpenAI dan dapatkan `OPENAI_API_KEY`. Simpan sebagai environment variable:

```bash
export OPENAI_API_KEY="sk-..."
```

Atau masukkan ke file `.env` yang akan dipakai oleh `langgraph dev`.

## 7. Tavily (opsional, digunakan di Module 4)
Tavily Search API digunakan oleh beberapa latihan pada Modul 4. Daftar untuk API key Tavily bila Anda ingin mengikuti bagian tersebut.

Simpan `TAVILY_API_KEY` di environment atau file `.env`:

```bash
export TAVILY_API_KEY="tavily-..."
```

## 8. Menyiapkan LangGraph Studio (lokal)
LangGraph Studio adalah UI untuk melihat, menjalankan, dan mendebug graph.

- Graph yang relevan berada di `module-x/studio/`.
- Untuk menjalankan Studio lokal, jalankan `langgraph dev` dari direktori `module-x/studio`.

Contoh output yang diharapkan saat server siap:

- 🚀 API: http://127.0.0.1:2024
- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- 📚 API Docs: http://127.0.0.1:2024/docs

Lalu buka browser ke:

```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

### 8.1 Membuat `.env` untuk setiap module yang punya `studio`
Berikut contoh command yang aman dijalankan — skrip ini hanya membuat `.env` jika `module-x/studio/.env.example` ada, lalu menambahkan `OPENAI_API_KEY`. Untuk Modul 4 juga akan menambahkan `TAVILY_API_KEY`.

```bash
# Jalankan dari root repo (langchain-academy)
for i in 1 2 3 4 5 6; do
  ex="module-$i/studio/.env.example"
  dst="module-$i/studio/.env"
  if [ -f "$ex" ]; then
    cp "$ex" "$dst"
    # tambahkan OPENAI key (gunakan env var bila tersedia, jika tidak sisipkan placeholder)
    if [ -n "${OPENAI_API_KEY+x}" ] && [ -n "$OPENAI_API_KEY" ]; then
      printf 'OPENAI_API_KEY="%s"\n' "$OPENAI_API_KEY" >> "$dst"
    else
      printf 'OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"\n' >> "$dst"
    fi
    # tambahkan TAVILY hanya untuk module-4
    if [ "$i" -eq 4 ]; then
      if [ -n "${TAVILY_API_KEY+x}" ] && [ -n "$TAVILY_API_KEY" ]; then
        printf 'TAVILY_API_KEY="%s"\n' "$TAVILY_API_KEY" >> "$dst"
      else
        printf 'TAVILY_API_KEY="YOUR_TAVILY_API_KEY_HERE"\n' >> "$dst"
      fi
    fi
    echo "Created $dst"
  else
    echo "Skipping module-$i: .env.example not found"
  fi
done
```

> Catatan: Pada workspace Anda beberapa modul tidak memiliki `studio/.env.example` (mis. module-6), jadi skrip akan meng-skip modul tersebut.

### 8.2 Menjalankan LangGraph Server untuk sebuah module

Contoh menjalankan untuk module-1 (pastikan venv aktif atau panggil bin/langgraph secara eksplisit):

```bash
cd module-1/studio
# jika venv lc-academy-env aktif dan langgraph terinstal di sana
../../lc-academy-env/bin/langgraph dev
# atau jika langgraph di PATH
langgraph dev
```

Jika server berjalan, periksa URL Studio yang dicetak di output dan buka di browser.

## 9. Troubleshooting cepat
- Jika `langgraph` tidak ditemukan, jalankan dari virtualenv yang berisi `langgraph-cli` (`lc-academy-env`) atau install `langgraph-cli` di environment aktif.
- Jika port 2024 sudah terpakai, server akan mencoba port lain — periksa output.
- Jika Studio tidak memuat, gunakan `127.0.0.1` pada `baseUrl` (Safari membutuhkan `127.0.0.1` kadang-kadang).

## 10. Contoh alur kerja singkat

1. Aktifkan venv

```bash
source lc-academy-env/bin/activate
```

2. Siapkan `.env` (jalankan skrip di atas)
3. Jalankan server untuk modul yang ingin Anda eksplor

```bash
cd module-4/studio
../../lc-academy-env/bin/langgraph dev
```

4. Buka Studio UI di browser

## Referensi
- Local Studio dev server docs: https://docs.langchain.com/langgraph-platform/langgraph-studio#local-development-server
- Local server tutorial: https://langchain-ai.github.io/langgraph/tutorials/langgraph-platform/local-server/

---

Jika Anda mau, saya bisa:

- Menjalankan `langgraph dev` untuk modul tertentu sekarang (sebutkan nomor modul), atau
- Membuat scaffold `module-0/studio` jika Anda ingin menjalankan Studio dari module-0.

Pilih satu opsi untuk saya jalankan berikutnya.
