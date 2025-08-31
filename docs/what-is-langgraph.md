# Apa itu LangGraph?

Dokumen ini menjelaskan secara ringkas mengapa LangGraph dibuat, bagaimana keadaan sebelum ada LangGraph, apa yang berubah setelahnya, komponen utamanya, cara kerjanya, dan sebuah analogi sederhana untuk memahami perbedaan sebelum & sesudah.

---

## Problem statement — kenapa LangGraph dibuat

Seiring aplikasi berbasis LLM (Large Language Model) menjadi lebih kompleks, pengembang mulai membangun "agentic workflows": sejumlah komponen (agent) yang saling berinteraksi untuk menyelesaikan tugas kompleks — misalnya pipeline RAG, multi-step decision-making, atau sistem yang memerlukan interaksi manusia di tengah-tengah proses.

Masalah yang sering muncul sebelum LangGraph:

- Orkestrasi kompleks: menghubungkan banyak langkah/agent secara andal memerlukan banyak kode glue dan error-prone coordination.
- Manajemen state: menyimpan dan memulihkan state (konteks percakapan, intermediate results) di antara langkah-langkah sulit diimplementasikan secara konsisten.
- Long-running tasks: tugas yang berjalan lama (menit-jam) rentan terhadap timeouts, koneksi terputus, dan memerlukan mekanisme background/polling.
- Observability & debugging: sulit melihat apa yang terjadi di setiap langkah—menelusuri node, intermediate states, dan prompt/hasil membutuhkan tooling khusus.
- Skalabilitas & keandalan: menangani lonjakan trafik, antrean tugas, dan exactly-once processing memerlukan infra yang kompleks.

LangGraph dibuat untuk menyelesaikan masalah-masalah ini dengan menyediakan framework + platform yang berfokus pada orkestrasi agent, manajemen state, dan observability.

---

## Keadaan sebelum LangGraph

Sebelum LangGraph (atau tanpa framework semacam ini), pengembang biasanya:

- Menulis pipeline custom (scripts / serverless functions) yang memanggil LLM dan layanan lain secara berurutan.
- Mengandalkan HTTP / message queues dasar tanpa pola standar untuk checkpoints, replay, atau debugging langkah demi langkah.
- Mengelola persistence sendiri (databases, caches) untuk setiap kasus penggunaan.
- Menggunakan log, print, atau tracing minimal untuk debugging; tidak ada UI terpadu untuk memvisualisasikan alur agent.

Akibatnya sistem sering:
- Fragile pada perubahan kecil di flow
- Sulit dikembangkan oleh tim besar
- Sulit dioperasikan di produksi (masalah konsistensi state, retries, observability)

---

## Apa yang berubah dengan LangGraph

LangGraph memperkenalkan model berbasis graph untuk mendefinisikan agentic workflows. Perubahan utama:

- Deklaratif: flow dibangun sebagai graph (node + edges) sehingga struktur dan dependensi eksplisit.
- State-aware: state graph (messages, variables, checkpoints) dikelola secara native sehingga node dapat membaca/menulis state dengan aman.
- Runtime yang mendukung streaming & background runs: output incremental bisa disampaikan ke klien, dan job panjang dapat dijalankan di background dengan polling/webhook.
- Observability & tooling: LangGraph Studio (UI) + integrasi LangSmith untuk tracing, evaluasi, dan debugging interaktif.
- Deployment-ready: runtime yang dirancang untuk production (task queues, persistent storage, redis pub/sub, healthchecks, dan deployment options: cloud/helm/docker-compose).

Hasilnya: pengembang dapat membangun alur agent yang modular, mudah diuji, di-debug, dan dioperasikan.

---

## Komponen Utama LangGraph

1. LangGraph SDK / Graph Library
   - Library untuk mendefinisikan graph (nodes, edges, states) di level aplikasi (Python/JS).
   - Menyediakan tipe state umum (mis. MessagesState) dan helper untuk membuat node yang memanggil LLM, langkah logika, atau integrasi eksternal.

2. LangGraph Server (Runtime)
   - Menjalankan graph yang telah didefinisikan.
   - Mengelola eksekusi runs, state persistence, task queue, background jobs, dan streaming hasil.
   - Menyediakan REST/streaming API untuk menjalankan assistant, memantau runs, dan men-trigger actions.

3. LangGraph CLI
   - Tooling developer untuk: membuat project (`langgraph new`), menjalankan server lokal (`langgraph dev`), membangun image Docker (`langgraph build`), dan deployment.
   - Menggabungkan/packaging dependency, graphs, dan variabel environment melalui `langgraph.json`.

4. LangGraph Studio
   - UI web untuk visualisasi graph, mengeksekusi runs interaktif, melihat node/transition/intermediate states, dan debugging (termasuk time-travel).
   - Terhubung ke runtime via baseUrl; mendukung dua mode: Graph Mode (detail penuh) dan Chat Mode (sederhana untuk chat agents).

5. LangSmith Integration
   - Sistem observability & tracing. Studio terintegrasi dengan LangSmith untuk menyimpan traces, menjalankan evaluasi, dan melakukan prompt engineering.

6. Infrastructure Primitives
   - Redis: pub/sub untuk streaming dan notifikasi real-time.
   - Postgres: persistence untuk assistants, threads, runs, dan state antrean tugas (exactly-once semantics).
   - Task queue & worker model: memastikan pekerjaan diproses andal, meng-handle retries dan long-running tasks.

7. Deployment options
   - Cloud, hybrid, atau self-hosted (Docker Compose / Kubernetes Helm).
   - Environment variables kritikal: REDIS_URI, DATABASE_URI, LANGSMITH_API_KEY, LANGGRAPH_CLOUD_LICENSE_KEY.

---

## Cara Kerja (overview teknis)

1. Definisi graph
   - Pengembang menulis graph sebagai kode (graph objects) yang terdiri dari nodes.
   - Setiap node merepresentasikan unit kerja: panggilan LLM, transformasi data, panggilan API eksternal, atau branching logic.

2. Start a run
   - Klien (SDK/REST) memulai sebuah run/assistant execution. Server membuat run record dan inisialisasi state.

3. Execution & state management
   - Runtime menjalankan node sesuai graf dan dependensi.
   - Node dapat membaca/menulis state bersama (mis. messages, metadata), dan server menyimpan checkpoint sesuai policy.

4. Streaming & client updates
   - Saat node menghasilkan output incremental (seperti token), server meng-publish event melalui Redis pub/sub dan/atau streaming endpoint.
   - Klien (atau Studio) menerima update real-time sehingga user mendapatkan feedback langsung.

5. Background runs & durable processing
   - Untuk tugas lama, server dapat men-schedule pekerjaan ke background worker.
   - Run state disimpan di Postgres; worker memproses pekerjaan sampai selesai, dan klien bisa polling atau menerima webhook saat selesai.

6. Observability & debugging
   - Semua runs dapat dilacak via LangSmith/Studio: Anda bisa melihat node mana yang dieksekusi, payload input/output, dan melakukan replay atau time-travel debugging.

7. Human-in-the-loop
   - Server menyediakan endpoint untuk menunda eksekusi sampai intervensi manusia, atau untuk memasukkan feedback selama run.

---

## Keunggulan Praktis

- Modular & reusable components: node/agent dapat dipakai ulang di graph berbeda.
- Lebih cepat untuk iterate: definisi graph + Studio membuat eksperimen lebih mudah.
- Produksi-friendly: task queue, persistence, and healthchecks mengurangi kejutan saat scale.
- Observability: tracing & Studio mempermudah debugging dan improvement.

---

## Analogi Sederhana: Sebelum vs Sesudah LangGraph

Bayangkan Anda mengelola restoran yang menerima pesanan kompleks (mis. multi-course, custom requests):

- Sebelum LangGraph: restoran ini seperti kumpulan koki yang bekerja tanpa tiket pesanan terpusat—pelayan lari sana-sini, tiap koki punya cara sendiri untuk mencatat, dan ketika pesanan rumit datang, semuanya jadi kacau. Kalau ada yang salah, susah melacak siapa yang membuat kesalahan.

- Dengan LangGraph: Anda punya sistem tiket terpusat (graph) dan kepala dapur (runtime) yang mengatur tugas ke masing-masing stasiun (nodes/agents). Ada papan yang menampilkan status setiap pesanan (Studio), notifikasi real-time saat makanan sudah siap (streaming), dan sistem arsip yang menyimpan catatan pesanan jika perlu diperiksa ulang (persistence). Anda juga bisa menangguhkan pesanan untuk pemeriksaan chef (human-in-the-loop) dan mengatasi lonjakan pesanan dengan menambah pekerja (task queue & scaling).

LangGraph mengubah "dapur yang kacau" menjadi "restoran yang terkoordinasi, dapat diobservasi, dan bisa diskalakan".

---

## Penutup dan referensi

Jika Anda ingin saya menyimpan ringkasan ini di file markdown di repo (sudah saya lakukan), atau menambahkan diagram sederhana/contoso example graph, beri tahu saya.

Referensi:
- LangGraph Platform docs: https://docs.langchain.com/langgraph-platform
- LangGraph local server tutorial: https://langchain-ai.github.io/langgraph/tutorials/langgraph-platform/local-server/
- Paper: "Agent AI with LangGraph" — arXiv:2412.03801
