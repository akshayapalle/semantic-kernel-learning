# Semantic Kernel Learning

Hands-on learning with **Microsoft Semantic Kernel**, Python, and Azure OpenAI. This repository explores plugins, AI function calling, workflows, process frameworks, and multi-agent orchestration through practical examples.

## Topics Covered

* Plugin basics and custom functions
* AI function calling
* Multiple functions and task automation
* Sequential workflows and Process Framework
* Asynchronous execution with `asyncio`
* Handoff, Group Chat, Sequential, Concurrent, and Magentic Orchestration

## Tech Stack

* Python 3.12
* Microsoft Semantic Kernel
* Azure OpenAI
* ChromaDB *(planned, if added later)*

## Project Structure

```text
semantic-kernel-learning/
├── .env.example
├── .gitignore
├── requirements.txt
├── main.py
├── 01_plugin_basics.py
├── 02_function_calling.py
├── 03_multiple_functions.py
├── 04_task_automation.py
├── 05_workflow_basics.py
├── 06_process_framework.py
├── 07_concurrent_workflow.py
├── 08_handoff_orchestration.py
├── 09_group_chat.py
├── 10_sequential_orchestration.py
├── 11_concurrent_orchestration.py
└── 12_magentic_orchestration.py
```

## Setup

1. Clone the repository:

   ```bash
   git clone <your-repository-url>
   cd semantic-kernel-learning
   ```

2. Create and activate a virtual environment:

   ```bash
   py -3.12 -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create your `.env` file by copying `.env.example`, then add your Azure OpenAI credentials and deployment settings.

5. Run an example:

   ```bash
   python 01_plugin_basics.py
   ```

## Environment Variables

Configure the following variables in `.env`:

* `AOAI_CHAT_ENDPOINT`
* `AOAI_CHAT_KEY`
* `AOAI_CHAT_DEPLOYMENT`
* `AOAI_API_VERSION_GPT`

**Security:** Never commit your actual `.env` file or expose your API key.

## Learning Goal

Understand how Semantic Kernel connects Python applications with AI models, plugins, workflows, and multi-agent orchestration through practical experimentation.

---

This repository is a learning project and will evolve as I explore more Semantic Kernel concepts.
