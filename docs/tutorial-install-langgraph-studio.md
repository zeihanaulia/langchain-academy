# Tutorial Instalasi LangGraph Studio di Local

## Pendahuluan

LangGraph Studio adalah IDE khusus untuk sistem agent yang memungkinkan visualisasi, interaksi, dan debugging aplikasi LangGraph. Studio ini dapat digunakan untuk development lokal dengan server LangGraph yang berjalan di mesin Anda.

## Prasyarat

Sebelum memulai, pastikan Anda memiliki:

- **Python >= 3.11**
- **API key LangSmith** (gratis, daftar di [LangSmith](https://smith.langchain.com/settings))

## Langkah 1: Install LangGraph CLI

LangGraph CLI adalah alat command-line untuk mengelola aplikasi LangGraph. Install dengan perintah berikut:

```bash
pip install --upgrade "langgraph-cli[inmem]"
```

Opsi `[inmem]` menginstall mode in-memory untuk development dan testing.

## Langkah 2: Buat Aplikasi LangGraph Baru

Buat aplikasi baru dari template yang tersedia:

```bash
langgraph new path/to/your/app --template new-langgraph-project-python
```

Template ini mendemonstrasikan aplikasi single-node yang dapat Anda kembangkan dengan logika Anda sendiri.

**Catatan**: Jika Anda menjalankan `langgraph new` tanpa template, Anda akan mendapat menu interaktif untuk memilih template yang tersedia.

## Langkah 3: Install Dependencies

Masuk ke direktori aplikasi yang baru dibuat dan install dependencies dalam mode edit:

```bash
cd path/to/your/app
pip install -e .
```

Mode edit memungkinkan perubahan lokal Anda langsung digunakan oleh server.

## Langkah 4: Buat File .env

Di root direktori aplikasi, Anda akan menemukan file `.env.example`. Buat file `.env` baru dan salin isinya, kemudian isi API key yang diperlukan:

```bash
cp .env.example .env
```

Edit file `.env` dan isi:

```env
LANGSMITH_API_KEY=lsv2_your_api_key_here
```

## Langkah 5: Jalankan LangGraph Server

Start server LangGraph secara lokal:

```bash
langgraph dev
```

Output yang berhasil akan terlihat seperti ini:

```
>    Ready!
>
>    - API: http://localhost:2024
>
>    - Docs: http://localhost:2024/docs
>
>    - LangGraph Studio Web UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

**Catatan**: Perintah `langgraph dev` menjalankan server dalam mode in-memory yang cocok untuk development dan testing. Untuk production, gunakan deployment dengan persistent storage.

## Langkah 6: Test di LangGraph Studio

LangGraph Studio adalah UI khusus untuk visualisasi, interaksi, dan debugging aplikasi LangGraph. Akses melalui URL yang diberikan di output perintah sebelumnya:

```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

### Fitur Utama LangGraph Studio:

- **Visualisasi arsitektur graph**
- **Interaksi dan testing agent**
- **Manajemen assistants**
- **Manajemen threads**
- **Iterasi prompts**
- **Running experiments dengan dataset**
- **Manajemen long-term memory**
- **Debug state via time travel**

### Mode Studio:

- **Graph Mode**: Menampilkan detail lengkap eksekusi agent termasuk nodes yang dilalui, intermediate states, dan integrasi LangSmith
- **Chat Mode**: UI sederhana untuk testing agent chat-specific (hanya untuk graph dengan MessagesState)

## Langkah 7: Test API (Opsional)

Install LangGraph Python SDK untuk testing API:

```bash
pip install langgraph-sdk
```

Contoh kode untuk testing:

```python
from langgraph_sdk import get_client
import asyncio

client = get_client(url="http://localhost:2024")

async def main():
    async for chunk in client.runs.stream(
        None,  # Threadless run
        "agent", # Name of assistant. Defined in langgraph.json.
        input={
            "messages": [{
                "role": "human",
                "content": "What is LangGraph?",
            }],
        },
    ):
        print(f"Receiving new event of type: {chunk.event}...")
        print(chunk.data)
        print("\n\n")

asyncio.run(main())
```

## Troubleshooting

### Port Sudah Digunakan
Jika port 2024 sudah digunakan, server akan otomatis menggunakan port yang tersedia berikutnya.

### Safari Compatibility
Untuk browser Safari, pastikan untuk menggunakan `127.0.0.1` bukan `localhost` di URL.

### Custom Host/Port
Jika server berjalan di host/port custom, update parameter `baseUrl` di URL Studio:
```
https://smith.langchain.com/studio/?baseUrl=http://your-custom-host:your-port
```

## Next Steps

Setelah berhasil menjalankan LangGraph Studio secara lokal:

- **Deployment**: Pelajari cara deploy aplikasi ke LangGraph Platform
- **API Reference**: Eksplorasi dokumentasi LangGraph Server API
- **Python SDK**: Pelajari referensi Python SDK
- **Advanced Features**: Eksplorasi fitur lanjutan seperti workflows dan agent architectures

## Referensi

- [LangGraph Platform Overview](https://langchain-ai.github.io/langgraph/concepts/langgraph_platform/)
- [Deployment Quickstart](https://langchain-ai.github.io/langgraph/cloud/quick_start/)
- [LangGraph Server API Reference](https://langchain-ai.github.io/langgraph/cloud/reference/api/api_ref.html)
- [Python SDK Reference](https://langchain-ai.github.io/langgraph/cloud/reference/sdk/python_sdk_ref/)</content>
<parameter name="filePath">/Users/zeihanaulia/Programming/learn-llm/langchain-academy/docs/tutorial-install-langgraph-studio.md
