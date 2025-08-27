# 📚 LLM Smart Librarian

Un proiect pentru gestionarea și interacțiunea cu documente folosind **Retrieval-Augmented Generation (RAG)** și interfețe de tip **chat** (CLI & UI).  
Scopul proiectului este să permită căutarea, rezumarea și monitorizarea răspunsurilor folosind modele LLM.

---

## 🚀 Funcționalități
- **Chat UI și CLI** pentru interacțiune naturală cu utilizatorul (`app/chat_ui.py`, `app/chat_cli.py`).
- **RAG Pipeline**:
  - *Ingestion* de documente (`rag/ingest.py`).
  - *Retriever* pentru căutare contextuală (`rag/retriever.py`).
- **Unelte de sumarizare** (`tools/summaries_tool.py`).
- **Monitorizare răspunsuri LLM** (`response_monitor.py`).
- **Extensibilitate**: suport pentru integrarea de noi unelte și surse de date.

---

## 📦 Instalare

### 1. Clonează repository-ul
```bash
git clone git@github.com:sfilipovici/LLM-Smart-Librarian.git
cd LLM-Smart-Librarian
```

### 2. Creează un mediu virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalează dependențele
```bash
pip install -r requirements.txt
```

## 🔑 Configurare

Creează un fișier .env pe baza template-ului:
```bash
cp .env.example .env
```

Completează valorile necesare (de ex. OPENAI_API_KEY).

⚠️ Notă: Nu include niciodată .env în repo! Este deja listat în .gitignore.

## ▶️ Utilizare
### 1. Ingestion documente
```bash
python rag/ingest.py
```

### Chat CLI
```bash
python app/chat_cli.py
```

### Chat Web UI
```bash
python app/chat_ui.py
```



## 📂 Structura proiectului

```bash
LLM-Smart-Librarian/
│── app/                 # Interfață utilizator (UI + CLI)
│── rag/                 # Ingestion și retrieval documente
│── tools/               # Unelte suplimentare (summaries, etc.)
│── response_monitor.py  # Monitorizare răspunsuri LLM
│── requirements.txt     # Dependențe Python
│── .env.example         # Template pentru variabile de mediu
│── .gitignore           # Ignoră fișiere sensibile / cache
```
