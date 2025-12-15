# CIF-AI (Customer-AI)

> **Automated Customer Support Agent with RAG & Intelligent Routing**

CIF-AI is a modular, AI-driven customer support pipeline designed to ingest emails, analyze intent, and autonomously resolve inquiries. It leverages **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware replies and features an intelligent routing system to escalate complex issues to human agents.

Currently in **Phase 1 (Prototype)**, this system runs locally with mocked integrations for rapid development and architectural validation.

---

## 🚀 Key Features

* **📧 Automated Ingestion**: Polls and parses incoming emails in real-time.
* **🧠 Intelligent Routing**: Uses LLM analysis to classify emails by intent (Billing, Technical, Logistics) (see `router/classifier.py`).
* **📚 RAG-Enhanced Replies**: Fetches relevant knowledge base articles (policies, shipping info) to ground AI responses in fact (see `rag/search.py`).
* **🛡️ Safety Escalation**: Automatically detects low-confidence scenarios or sensitive topics (e.g., refunds) and creates escalation tickets for human review (see `router/escalation.py`).
* **💾 Structured Storage**: Persists conversation history, message metadata, and analytics events using SQLite and SQLAlchemy (see `storage/models.py`).

---

## 🏗️ System Architecture

The project follows a modular "Pipeline" architecture, orchestrated by the central Router.

| Module | Role | Description |
| :--- | :--- | :--- |
| **Email Poller** | *The Listener* | Constantly watches for unread messages and parses raw email data into structured events. |
| **Router** | *The Controller* | The central brain. It coordinates the flow between the Database, RAG system, and AI Agent. |
| **RAG Engine** | *The Context* | Retrieves relevant documents (FAQs, Policies) based on the email content to prevent hallucinations. |
| **AI Agent** | *The Writer* | Generates summaries, analyzes sentiment, and drafts polite responses using LLM logic. |
| **Storage** | *The Memory* | A relational database tracking all conversations, messages, and escalation events. |

---

## 🛠️ Technology Stack

* **Language**: Python 3.11+
* **Core Logic**: Pydantic (Data Validation), SQLAlchemy (ORM)
* **API/Web**: FastAPI (Prepared for Phase 2 exposure)
* **Database**: SQLite (Local development default)
* **AI/LLM**: Modular design ready for Groq/OpenAI (Currently Mocked)

---

## ⚡ Getting Started

### Prerequisites
* Python 3.8 or higher
* `pip` (Python Package Manager)

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/aleng13/CIF-AI.git](https://github.com/aleng13/CIF-AI.git)
    cd CIF-AI
    ```

2.  **Create a Virtual Environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    Copy the example configuration file:
    ```bash
    cp .env.example .env
    ```
    *Note: The default settings work out-of-the-box for local testing.*

### Running the Application

Start the main application loop:
```bash
python main.py
You will see the logs indicating the system is polling for messages:

Plaintext

Starting mock email poller...
Found 1 unread message(s).
Processing message msg-1...
=== AI Reply ===
Hi — sorry to hear about this...
📂 Project Structure
Plaintext

CIF-AI/
├── agent/           # AI Logic (LLM Client & Prompting)
├── email/           # Email Ingestion (Poller, Parser, Mock Clients)
├── rag/             # Retrieval Augmented Generation (Search & Knowledge)
├── router/          # Core Business Logic (Decision making, Escalation)
├── storage/         # Database Models & CRUD Repositories
├── tests/           # Unit Tests
├── config.py        # Configuration Management
└── main.py          # Application Entry Point
🔮 Roadmap
Phase 1 (Current): Local prototype with mocked external services (Gmail/LLM).

Phase 2: Integration with real Gmail API and Groq/OpenAI APIs.

Phase 3: Vector Database integration (Pinecone/Chroma) for advanced RAG.

Phase 4: Dashboard frontend for human agents to view escalations.

🤝 Contributing
Contributions are welcome! Please follow these steps:

Fork the repository.

Create a feature branch (git checkout -b feature/AmazingFeature).

Commit your changes (git commit -m 'Add some AmazingFeature').

Push to the branch (git push origin feature/AmazingFeature).

Open a Pull Request.

📄 License
Distributed under the MIT License. See LICENSE for more information.
