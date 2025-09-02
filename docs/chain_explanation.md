
# Ngulik `chain.py` versi “lo-gue”: dari notebook jadi script, plus cara kerjanya di balik layar

## Gambaran besar: lo lagi bikin apa sih?

`chain.py` itu versi script dari notebook `chain.ipynb` (ala “lab eksperimen”) yang dijadikan file `.py` supaya gampang dijalankan di terminal. Isinya: contoh *paling minimal* bikin alur *tool-calling* pakai **LangGraph** + **LangChain**—LLM bisa ngobrol dan, kalau perlu, “manggil alat” (tool) kayak fungsi `multiply`. Inti arsitekturnya:

1. ada **state** buat nyimpen history pesan,
2. ada **reducer** biar pesan lama gak ketiban,
3. ada **graph** berisi satu **node** yang manggil model (yang sudah dibekali tools).
   Konsep-konsep ini memang standar di LangGraph. ([LangChain Docs][1], [LangChain AI][2])

---

## Step 0 — Instal & nyiapin kunci

Paket minimal: `langgraph`, `langchain_core`, `langchain_openai`. Terus `OPENAI_API_KEY` harus ada di environment; di script lo ada helper `_set_env()` yang minta input kalau belum diset. Di sisi LangChain/OpenAI, kelas **`ChatOpenAI`** memang butuh API key dan expose method `bind_tools(...)` buat ngenalin daftar tool ke model. ([LangChain][3])

**Kenapa ini penting?** Tanpa API key, obviously gak bisa akses model. Dan tanpa `bind_tools`, model cuma ngobrol teks; dia gak kenal fungsi `multiply`. Panduan resmi “tool calling” (cara ngebind & manggil tool) ada di docs LangChain. ([LangChain][4])

---

## Step 1 — Model + Tool: bikin “otak” dan “tangan”

Di file lo:

* **Model**: `llm = ChatOpenAI(model="gpt-4o")`
* **Tool**: fungsi Python polos

  ```py
  def multiply(a: int, b: int) -> int:
      return a * b
  ```
* **Binding**: `llm_with_tools = llm.bind_tools([multiply])`

Binding ini ngedaftarin *schema* tool ke model. Saat di-*invoke*, model bisa ngeluarin **AIMessage** yang mengandung **`tool_calls`** (niat/permintaan buat ngejalanin `multiply` dengan argumen tertentu). Mekanisme ini standar di LangChain; beberapa model OpenAI memang mendukung format *tool calling*. ([LangChain][4])

> Catatan penting: `bind_tools` **cuma** bikin model *mengusulkan* panggilan tool. Eksekusi fungsi sebenernya (jalanin Python-nya, terus balikin hasilnya ke percakapan) butuh langkah tambahan di sisi graph/agent. Kalau lo *hanya* memanggil `llm_with_tools.invoke(...)` lalu langsung nyambung ke END, yang keluar biasanya **rencana tool call** (metadata), bukan hasil perhitungannya—kecuali lo tambahin node eksekusi tool. Ini cara kerja resmi di LangGraph & di contoh “tool-calling agent”. ([LangChain AI][5])

---

## Step 2 — State & Reducer: biar chat gak “amnesia” (versi lebih rinci)

Inti: State di LangGraph berperan sebagai *external memory* percakapan. Reducer adalah cara terkontrol untuk menulis ke memory itu — bukan overwrite apa pun seenaknya, melainkan menerapkan kebijakan penggabungan/penulisan yang predictable (append, replace, compact, dsb.). Tanpa reducer yang sesuai, node yang return `{"messages": [...]}` bisa menggantikan seluruh history atau menyebabkan duplikasi.

Konsep teknis dan praktis:

1. Struktur state — canonical pattern
    - Pakai TypedDict + Annotated agar schema dan policy penulisan (reducer) eksplisit:
      ```py
      from typing_extensions import TypedDict
      from typing import Annotated, List
      from langgraph.graph.message import add_messages
      from langchain_core.messages import AnyMessage

      class State(TypedDict):
            messages: Annotated[List[AnyMessage], add_messages]
      ```
    - Penjelasan: Annotated/List + add_messages memberitahu LangGraph bahwa setiap node yang mereturn `{"messages": [...]}` harus digabungkan ke list `state["messages"]` dengan aturan `add_messages` (append/merge by id) — bukan mengganti field.

2. Apa yang dilakukan add_messages (semantik umum)
    - Append: pesan baru ditambahkan ke akhir history.
    - Merge by id: jika pesan baru punya ID yang sama dengan pesan existing, reducer bisa update/replace entry tersebut alih-alih duplikat.
    - Deterministic ordering: reducer menjaga urutan waktu sehingga history tetap konsisten untuk step selanjutnya.
    - Keuntungan: memungkinkan multi-step flows (LLM → Tool → LLM) tanpa kehilangan konteks.

3. Antipattern & gotchas
    - Jangan shadow nama kelas state (contoh: `class MessagesState(MessagesState): pass`) — bikin ambigu dan susah dibaca.
    - Node yang mengembalikan list pesan besar tanpa reducer akan menimpa history (kalau reducer salah konfigurasi) atau menimbulkan duplikasi.
    - Perhatikan ukuran history: append tanpa batas → memory blow-up / cost bertambah ketika mengirim ke LLM.

4. Praktik umum untuk pengelolaan history (strategi reducer / post-processing)
    - Sliding window: hanya simpan N pesan terakhir. Cocok untuk prompt-length bound.
    - Summarization/compaction: periodik ringkas pesan lama menjadi satu ringkasan, lalu replace beberapa pesan lama dengan 1 summary message.
    - Event-based checkpointing: simpan snapshot conversation state penting (summary/slots) dan drop detail yang tidak perlu.
    - Dedup & replace by id: tool-call results sering punya message id; reducer dapat replace hasil sementara dengan hasil final.

5. Contoh custom reducer: batasi history ke N pesan
    ```py
    from typing import List
    from langchain_core.messages import AnyMessage
    from langgraph.graph.message import add_messages
    from langgraph.graph.reducer import Reducer  # ilustrasi API

    # contoh sederhana: pakai add_messages untuk append, lalu crop
    def cap_history_reducer(existing: List[AnyMessage], incoming: List[AnyMessage], cap: int = 50) -> List[AnyMessage]:
         merged = add_messages(existing, incoming)  # gunakan helper standar bila tersedia
         return merged[-cap:]

    # jika framework butuh wrapper atau Annotated, daftarkan reducer di schema atau saat compile graph
    ```
    Catatan: API implementasi reducer bisa berbeda tergantung versi LangGraph — ide utamanya: gunakan helper standar → lalu apply post-processing (cropping/summary).

6. Integrasi dengan tool-calling dan node flow
    - Saat node LLM mengembalikan AIMessage dengan `tool_calls`, reducer memastikan AIMessage itu masuk ke history. Node Tool (prebuilt atau custom) membaca `state["messages"][-1].tool_calls`, mengeksekusi tool, lalu return `{"messages": [ToolMessage(...)]}`. Reducer lalu append ToolMessage sehingga LLM (node berikutnya) punya konteks hasil eksekusi.
    - Pastikan reducer mempertahankan urutan: AIMessage (intent) → ToolMessage (result) → AIMessage (final answer).

7. Testing & determinisme
    - Unit test reducer: berikan `existing` + `incoming` deterministic input, assert output konsisten (order, dedup, size).
    - Simulasikan multi-node run untuk verifikasi bahwa reducer menjaga flow (LLM → Tool → LLM) tanpa kehilangan atau duplikasi pesan.
    - Logging/IDs: sertakan message IDs/timestamp agar mudah trace dan replay.

8. Relevansi ilmiah (latar belakang)
    - Ide state eksternal dan mekanisme baca/tulis punya akar di literature memory-augmented models dan architectures for long context:
      - Neural Turing Machines — Graves et al., 2014 (external read/write memory pattern)
         https://arxiv.org/abs/1410.5401
      - Memory Networks — Weston et al., 2014 (explicit memory for QA)
         https://arxiv.org/abs/1410.3916
      - Transformer-XL — Dai et al., 2019 (longer-context modeling via recurrence)
         https://arxiv.org/abs/1901.02860
      - Compressive Transformer — Rae et al., 2020 (memory compression for long contexts)
         https://arxiv.org/abs/1911.05507
      - Attention Is All You Need — Vaswani et al., 2017 (dasar transformer)
         https://arxiv.org/abs/1706.03762
    - Catatan: LangGraph reducer bukan neural memory, tapi desainnya berhubungan dengan kebutuhan menyimpan/merawat konteks yang sama: deterministic, bounded, dan efisien.

9. Rekomendasi singkat
    - Gunakan TypedDict + Annotated[..., add_messages] supaya schema & policy eksplisit.
    - Implement/daftarkan reducer tambahan untuk bounding (sliding window) atau compaction (summarize).
    - Pastikan ToolNode/eksekutor terintegrasi sehingga tool results disimpan melalui reducer — ini mencegah “AIMessage dengan tool_calls” tetap jadi metadata tanpa hasil.
    - Tambahkan unit test untuk reducer behavior (append, replace-by-id, cropping).

Referensi langsung ke docs LangGraph untuk contoh implementasi reducer dan add_messages: lihat dokumentasi graph API & how-tos (link ada di bagian referensi utama dokumen).

Analogi singkat tentang state & reducer
- State itu seperti papan tulis bersama (whiteboard) di ruang kerja tim: setiap node adalah anggota tim yang bisa membaca catatan yang ada dan menulis catatan baru.
- Reducer adalah aturan tata tertib papan: menentukan apakah pesan baru di-"tempel" di akhir, mengganti pesan lama jika punya ID sama, atau merapikan dengan merangkum/menyimpan hanya N pesan terakhir.  
- Dalam flow tool-calling: LLM menulis niat memanggil tool sebagai catatan (tool_call) → reducer memastikan catatan itu tersimpan dengan cara yang terkontrol → node tool membaca catatan terakhir, menjalankan fungsi, lalu menambahkan hasilnya sebagai catatan baru sehingga LLM selanjutnya melihat konteks hasil eksekusi.

Ringkas: state = papan tulis bersama; reducer = aturan yang menjaga papan tetap terstruktur, tidak berantakan, dan dapat dipakai ulang untuk langkah-langkah berikutnya.

---

## Step 3 — Graph & Node: jalur eksekusi yang super sederhana

Strukturnya *straight line*:

* **START → tool\_calling\_llm → END**

Node `tool_calling_llm` isinya:

```py
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
```

Artinya: node ini cuma *invoke* model (yang sudah dibekali tools) berdasarkan seluruh history di `state["messages"]`, lalu nambahin output AI ke state (thanks to `add_messages`). Pola “START/END, StateGraph, .compile()” ini juga *by the book* di docs. ([LangChain AI][6])

> Tapi ingat catatan sebelumnya: **belum ada eksekusi tool**. Kalau model memutuskan “panggil `multiply`(2,3)”, hasil yang balik dari node ini masih berupa **AIMessage dengan `tool_calls`**, bukan angka 6. Supaya tool-nya beneran dieksekusi dan hasilnya ikut masuk ke chat, lo butuh **ToolNode** (atau node custom) yang:
> (1) baca `tool_calls`, (2) jalankan Python-nya, (3) masukkan hasilnya sebagai pesan tool-result, (4) *optional* loop balik ke LLM agar dia merangkum. Panduan langkah demi langkah ada di *how-to tool-calling agent* LangGraph. ([LangChain AI][5])

---

## Step 4 — `__main__`: yang bener-bener dieksekusi

Di bagian main lo coba dua input:

1. “Hello!” → LLM jawab biasa.
2. “Berapa 2 dikali 3?” → LLM kemungkinan *mengeluarkan* `tool_calls` ke `multiply`.

Kalau lo jalankan apa adanya, *printing* dengan `pretty_print()` akan kelihatan ada AIMessage (dan mungkin ada metadata `tool_calls`). **Kalau lo ingin jawaban final “6” nongol sebagai teks dari AI**, tambahkan node eksekusi tool seperti di bagian catatan di atas. Itu pattern standar agent/tool-calling. ([LangChain AI][5])

---

## (Opsional tapi direkomendasikan) Biar bener-bener “jalanin tool” end-to-end

Tiga cara paling gampang:

1. **Pakai `ToolNode` prebuilt**

   * Tambah node `tool_node = ToolNode([multiply])`
   * Alur: START → LLM → ToolNode → LLM (opsional) → END
     Ini nanganin parsing `tool_calls`, eksekusi fungsi, sampai naro hasil ke state. ([LangChain AI][5])

2. **Node custom eksekusi tool**

   * Bikin node yang baca `state["messages"][-1].tool_calls`, mapping ke fungsi Python, jalanin, terus append hasil sebagai `ToolMessage`. Pattern dasarnya identik dengan yang di docs “graph API + reducers”. ([LangChain Docs][1])

3. **Pakai prebuilt agent LangGraph**

   * Ada varian yang udah “jadi”, cocok buat *quickstart*, tinggal daftarin tools & model. ([LangChain Docs][7])

---

## Kenapa reducer itu krusial (sekali lagi)?

Tanpa `add_messages`, *return* node yang berisi list pesan **nimpuk** state lama (history hilang). Dengan `add_messages`, list pesan **di-append** (atau di-update kalau ada ID cocok). Ini bikin percakapan multi-step (LLM → Tool → LLM) tetap punya konteks. Ini persis problem yang dibahas di bagian “reducers” pada dokumen *graph API*. ([LangChain AI][2])

---

## Good practices & tips kecil

* **Jangan shadow nama kelas**: ganti `class MessagesState(MessagesState): pass` dengan schema `TypedDict` + `Annotated[... , add_messages]` biar lebih eksplisit & gampang dirawat. ([LangChain Docs][1])
* **Tahu batas `bind_tools`**: itu *pemberi niat*, bukan *eksekutor*. Pastikan ada node eksekusi tool. ([LangChain AI][5], [LangChain][4])
* **Model params**: beberapa opsi kayak `parallel_tool_calls` bisa di-bind juga kalau lo perlu kontrol perilaku panggilan tool paralel. ([LangChain][8])
* **Streaming & retry**: `ChatOpenAI` ikut *Runnable interface*, jadi lo bisa pasang `.with_retry()`, dsb., kalau nanti graph lo tambah kompleks. ([LangChain Python API][9])

---

## Ringkasan alur eksekusi (versi singkat tapi padat)

1. User ngetik → jadi `HumanMessage` → masuk `state.messages`.
2. Node `tool_calling_llm` manggil `llm_with_tools.invoke(state.messages)` → hasilnya `AIMessage` (bisa berisi `tool_calls`).
3. **Kalau ada ToolNode**: dia eksekusi `tool_calls` → hasil tool dibungkus sebagai pesan → optional balik ke LLM buat merangkum → END.
   Semua update ke `messages` **di-append** karena pakai `add_messages`. ([LangChain AI][2])

---

## Referensi (buat lo ngulik lebih dalem)

* **State, reducer, `add_messages`, dan graph API (START/END, node, compile)** — dokumentasi LangGraph: *low-level concepts* dan *how-tos graph API/tool-calling*. ([LangChain AI][6], [LangChain Docs][1])
* **Tool calling di LangChain (cara `bind_tools`, skema tool, dsb.)** — panduan resmi. ([LangChain][4])
* **`ChatOpenAI` (parameter, binding, runnable interface)** — API reference LangChain OpenAI. ([LangChain][8], [LangChain Python API][9])
* **Quickstart LangGraph (varian agent & tools)** — buat liat pola lengkap end-to-end. ([LangChain Docs][7])

---

kalau lo mau, gue bisa langsung **tambahin ToolNode** ke script lo dan kasih versi `chain.py` yang bener-bener ngejalanin `multiply` sampe keluar “6” sebagai jawaban final — tinggal bilang “gasin versi ToolNode”, gue drop kodenya.

[1]: https://docs.langchain.com/oss/python/langgraph/use-graph-api?utm_source=chatgpt.com "Use the graph API - Docs by LangChain"
[2]: https://langchain-ai.github.io/langgraph/how-tos/graph-api/?utm_source=chatgpt.com "Use the Graph API - GitHub Pages"
[3]: https://python.langchain.com/docs/integrations/chat/openai/?utm_source=chatgpt.com "ChatOpenAI | 🦜️🔗 LangChain"
[4]: https://python.langchain.com/docs/how_to/tool_calling/?utm_source=chatgpt.com "How to use chat models to call tools"
[5]: https://langchain-ai.github.io/langgraph/how-tos/tool-calling/?utm_source=chatgpt.com "Call tools - GitHub Pages"
[6]: https://langchain-ai.github.io/langgraph/concepts/low_level/?utm_source=chatgpt.com "state graph node - GitHub Pages"
[7]: https://docs.langchain.com/oss/python/langgraph/quickstart?utm_source=chatgpt.com "Quickstart - Docs by LangChain"
[8]: https://python.langchain.com/api_reference/openai/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html?utm_source=chatgpt.com "ChatOpenAI — 🦜🔗 LangChain documentation"
[9]: https://api.python.langchain.com/en/latest/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html?utm_source=chatgpt.com "langchain_openai.chat_models.base.ChatOpenAI"
