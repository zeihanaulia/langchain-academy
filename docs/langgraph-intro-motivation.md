---
title: "LangGraph — Pengantar & Motivasi"
---

Sumber: docs/papers/LangChain_Academy_-_Introduction_to_LangGraph_-_Motivation.pdf
Dihasilkan: 2025-08-27

## Gambaran umum dan motivasi

Slide pembuka menekankan bahwa model bahasa yang berdiri sendiri memiliki keterbatasan. Tanpa akses ke alat eksternal atau konteks di luar prompt, LLM pada dasarnya hanya memberikan respons berdasarkan input saat itu. Untuk membuat aplikasi yang berguna, pengembang sering membangun lapisan di sekitar LLM: sebuah alur kontrol yang memecah tugas menjadi langkah-langkah, memanggil model pada titik tertentu, dan menjalankan pekerjaan pra/pasca panggilan model seperti pengambilan data, pemanggilan tool, atau transformasi hasil.

Lewat ilustrasi sederhana, slide menunjukkan alur mulai (start) → langkah 1 → panggilan LLM → ... → langkah N → akhir (end). Inti pesannya: pola pengembangan ini muncul berulang pada banyak aplikasi LLM karena kebutuhan akan orkestrasi kerja pra dan pasca model.

## Rantai kontrol (chain) dan reliabilitas

Alur berurutan ini sering disebut "chain". Chain memungkinkan perilaku yang dapat diprediksi: ketika alur dan input sama, hasilnya cenderung sama, sehingga mudah untuk debug dan direproduksi. Reliabilitas ini berguna ketika bagian besar sistem harus deterministik.

## Kebutuhan akan fleksibilitas — agen dan alur yang dinamis

Namun, chain yang terlalu kaku membatasi kemampuan adaptif sistem. Pada beberapa kasus kita menginginkan LLM untuk membuat keputusan tentang langkah berikutnya—misalnya memilih tool yang tepat, merencanakan beberapa langkah, atau mengarahkan alur berdasarkan konteks runtime. Konsep agen muncul dari kebutuhan ini: alih-alih mengikuti jalur tetap, alur dikendalikan (setidaknya sebagian) oleh keputusan LLM.

Agent di sini dipahami sebagai entitas yang menetapkan kontrol flow berdasarkan keluaran model. Pendekatan ini membuka berbagai varian agen: ada agen yang relatif sederhana (memilih beberapa opsi), dan ada agen yang kompleks (merencanakan, memanggil tool, dan berinteraksi dengan state yang dibagikan).

## Tantangan praktis

Transisi dari chain yang kaku ke agen yang dinamis membawa tantangan nyata: bagaimana menjaga reproducibility dan observability ketika alur dapat berubah, bagaimana mengelola state bersama di antara node, serta bagaimana menyusun ulang atau menguji perilaku agen yang tidak sepenuhnya deterministik. Pertanyaan-pertanyaan ini penting untuk adopsi di lingkungan produksi.

## Peran LangGraph

LangGraph diperkenalkan untuk menyeimbangkan kebutuhan reliabilitas dan fleksibilitas. Platform ini mendorong representasi alur kontrol sebagai graf komposisional di mana node merepresentasikan unit kerja (panggilan model, fungsi transformasi, panggilan tool) dan edge mengatur routing (termasuk routing yang bergantung pada keputusan LLM). Dengan memisahkan bagian yang harus deterministik dan bagian yang boleh adaptif, LangGraph memungkinkan pengembang mengatur batas-batas kontrol sambil tetap menyuntikkan inteligensi model di titik-titik yang diperlukan.

Fitur penting yang disorot meliputi memori (state yang dapat dibagikan sepanjang graf), integrasi tools (node dapat memanggil alat eksternal), dan mekanisme perencanaan/routing (edges yang dapat memilih rute berdasarkan keluaran LLM).

## Ringkasan modul kursus (dari slide terakhir)

Slide terakhir memetakan modul pembelajaran: fondasi LangGraph (chains, routers, agen otonom), memori (agen yang dapat mengingat), human-in-the-loop (pengawasan manusia), dan kustomisasi (membangun agen yang sesuai kebutuhan).

---

Catatan: teks di atas disusun menjadi narasi yang mengalir berdasarkan materi dan teks yang terdeteksi pada slide "Introduction to LangGraph — Motivation". Jika Anda mau saya lanjutkan dengan setiap slide berikutnya, beri tahu dan saya akan memproses seluruh PDF menjadi narasi lengkap per-slide.
