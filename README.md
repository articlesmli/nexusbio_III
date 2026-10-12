# NexusBio_III: Fully Dynamic, Live-Running Multi-Agent Discovery Engine

NexusBio_III is a **fully dynamic, live-running multi-agent discovery engine** and automated cheminformatics sandbox environment designed for scalable containerised processing. This repository represents an advanced evolution of the original project, nexusbio, featuring a fully automated CI/CD pipeline using GitHub Actions deployed to **Microsoft Azure Container Apps and Azure Container Registry (ACR)**, powered by a local-first AI architecture, real RDKit mathematical chemistry, and structural biology modeling.

---

## What's New in `nexusbio_III`?

- **Fully Dynamic Multi-Agent Engine**: Replaced static placeholders with a live-running loop where agents compute real metrics on the fly and feed failure logs back into the system for closed-loop optimization.
- **Local-First BioGPT Integration**: Replaced external cloud dependencies (such as AWS Bedrock) with Microsoft's open-source `microsoft/biogpt` model for local, secure biomedical literature mining and text generation.
- **Boltz1 Structural Modeling**: Integrates dedicated structural protein prediction and target binding pocket validation capabilities via `boltz1_agent.py`.
- **Expanded Multi-Agent Intelligence**: Integrates specialised worker nodes for **ADMET toxicity prediction**, **patent/clinical intelligence**, **molecular design**, **pathway synthesis**, and **structural folding** under `lambda_orchestrator/agents/`.
- **Robust End-to-End Testing**: Includes comprehensive test suites covering molecular metrics (`test_descriptors.py`), BioGPT initialisation (`test_biogpt.py`), Boltz1 verification (`test_boltz1.py`), and multi-agent workflow orchestration (`test_orchestrator.py`).

---

## Recent Updates & Changelog

### Refactored Orchestrator & Closed-Loop Discovery
- **Dynamic Orchestrator Refactor (`handler.py`)**: Removed all static fallback dictionaries and hardcoded structural pools. The orchestrator now drives a fully dynamic, multi-agent iteration loop powered by live RDKit calculations and BioGPT generation prompts.
- **Beyond-Rule-of-Five (bRoF) Criteria**: Added advanced breakthrough criteria designed to correctly identify unconventional physical binding profiles and membrane-permeable macrocycles outside standard Lipinski boundaries.
- **Live API Tracing**: Validated end-to-end execution traces with live **Europe PMC** and **ChEMBL API** connections.

---

## Project Directory Structure

```text
nexusbio_III/
├── .github/
│   └── workflows/
│       └── ci-cd.yml                 # Automated GitHub Actions CI/CD pipeline
├── cheminformatics_sandbox/
│   ├── utils/                        # Utility scripts (e.g., RDKit descriptors)
│   ├── Dockerfile                    # Application container definition
│   ├── Dockerfile.base               # Base RDKit environment container definition
│   ├── main.py                       # Core sandbox entrypoint
│   └── requirements.txt              # Sandbox Python dependencies
├── frontend/
│   ├── app.py                        # Frontend web service application
│   ├── Dockerfile                    # Frontend container configuration
│   └── requirements.txt              # Frontend dependencies
├── lambda_orchestrator/              # Serverless orchestrator components & agents
│   ├── agents/                     
│   │   ├── admet_agent.py            # ADMET & toxicity prediction agent
│   │   ├── boltz1_agent.py           # Structural protein prediction & folding agent
│   │   ├── literature_miner.py       # Literature and research mining agent
│   │   ├── molecular_design.py       # Molecular generation and design agent
│   │   ├── patent_clinical_agent.py  # Patent & clinical trials intelligence agent
│   │   └── pathway_synthesizer.py    # Biological pathway synthesis agent
│   ├── handler.py                    # Orchestrator entrypoint & closed-loop discovery loop
│   └── requirements.txt              # Orchestrator Python dependencies
├── tests/                            # Root test suite
│   ├── test_bolz1.py                 # Boltz1 structural prediction tests
│   ├── test_biogpt.py                # Local BioGPT model & generation tests
│   ├── test_descriptors.py           # RDKit molecular metrics tests
│   └── test_orchestrator.py          # Multi-agent end-to-end pipeline tests
├── .gitignore
├── docker-compose.yaml               # Local multi-container orchestration
├── Dockerfile                        # Root container configuration
├── README.md
└── requirements.txt                  # Unified project dependencies

```

---

## Architecture & Tech Stack

* **Cloud Provider**: Microsoft Azure (`uksouth`)
* **Container Registry**: Azure Container Registry (`nexusbioacr.azurecr.io`)
* **Infrastructure**: Azure Resource Group (`nexusbio-rg`)
* **Core Frameworks**: Python 3.11, PyTorch, Hugging Face Transformers (`BioGPT`), Docker, RDKit, ChEMBL & Europe PMC Live APIs

---

## Multi-Agent Pipeline Components

The multi-agent framework features modular worker nodes designed to handle specific biochemical evaluation tasks dynamically:

* **Molecular Design Agent** (`molecular_design.py`): Computes real physical properties (Exact Molecular Weight, LogP, and QED scores) dynamically using **RDKit**.
* **ADMET & Toxicity Agent** (`admet_agent.py`): Screens candidate structures against physiological rules to flag toxicity risks and Lipinski violations (including bRoF exceptions).
* **Boltz1 Structural Agent** (`boltz1_agent.py`): Evaluates protein target sequences, computes estimated structural metrics, and identifies binding pockets.
* **Patent & Clinical Trials Agent** (`patent_clinical_agent.py`): Queries live public databases (such as the ChEMBL API) to cross-reference compounds with existing trial data.
* **Literature Miner Agent** (`literature_miner.py`): Fetches real-time biomedical literature and abstracts via live APIs (Europe PMC) alongside local **BioGPT** (`microsoft/biogpt`) context parsing.
* **Pathway Synthesiser Agent** (`pathway_synthesizer.py`): Analyses downstream pathway impacts and biological target responses.
* **Orchestration Test Suite** (`test_orchestrator.py`): Validates multi-agent interoperability and end-to-end task chains.

---

## CI/CD Pipeline (`ci-cd.yml`)

The automated pipeline handles two core stages on every push to `main`:

1. **Python Testing (`test-python`)**:
* Sets up Python 3.11 with pip caching.
* Installs standardised dependencies (`torch`, `transformers`, `pytest`, `rdkit`).
* Runs linting and executes the full root-level test suite (`pytest tests/`).


2. **Azure Deployment (`deploy-azure`)**:
* Authenticates securely with Azure Container Registry using admin credentials.
* Builds and pushes the RDKit base image and FastAPI application container images directly to ACR.



---

## Getting Started Locally

### Prerequisites

* Python 3.11+
* Docker & WSL (Ubuntu)
* Azure CLI (`az`)

### Local Setup & Testing

1. **Clone the repository:**
```bash
git clone [https://github.com/articlesmli/nexusbio_III.git](https://github.com/articlesmli/nexusbio_III.git)
cd nexusbio_III

```


2. **Set up a Python virtual environment:**
```bash

python3.10 -m venv nexusbio
source nexusbio/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

```


3. **Run the test suite (including BioGPT & Boltz1 verification):**
```bash
PYTHONPATH=. pytest tests/

```


4. **Run the multi-agent orchestrator test:**
```bash
python3 tests/test_orchestrator.py

```



---

## Building and Pushing Docker Images Locally

To manually build and push the two-tier container architecture to Azure Container Registry (`nexusbioacr.azurecr.io`), execute the following steps:

### 1. Authenticate with Azure Container Registry

Enable admin access via Azure CLI (or Cloud Shell) and log in locally:

```bash
az acr update --name nexusbioacr --admin-enabled true
docker login nexusbioacr.azurecr.io -u nexusbioacr -p <the_acr_password>

```

### 2. Build and Push the Scientific Base Image (`Dockerfile.base`)

```bash
cd cheminformatics_sandbox
docker build -t nexusbioacr.azurecr.io/nexusbio-sandbox-base:latest -f Dockerfile.base .
docker push nexusbioacr.azurecr.io/nexusbio-sandbox-base:latest

```

### 3. Build and Push the Main FastAPI Application Image (`Dockerfile`)

```bash
cd ~/nexusbio_III
docker build -t nexusbioacr.azurecr.io/nexusbio-app:latest -f Dockerfile .
docker push nexusbioacr.azurecr.io/nexusbio-app:latest

```

---

## Azure Secrets Configuration

To enable GitHub Actions automated deployments, configure the following repository secrets under **Settings > Secrets and variables > Actions**:

* `REGISTRY_USERNAME`: Set to `nexusbioacr`.
* `REGISTRY_PASSWORD`: The Azure Container Registry admin password.

---

## Important Runtime Considerations

Keep the following runtime details in mind when executing the autonomous discovery loop:

1. **RDKit Data Dependencies**
   The PAINS filter relies on RDKit's internal catalog files. Depending on how RDKit was installed in the Python environment (e.g., via `conda` vs `pip`), ensure the PAINS catalog files are present on your system path, or the filter initialisation may throw a missing-file lookup error.

2. **Model Output Variability**
   BioGPT is a small-to-medium language model. Even with temperature tuning and prompt shaping, it can occasionally output text that matches the regex pattern for a SMILES string but contains rare valences that RDKit parses with warnings or rejects outright (which is why the orchestration script relies heavily on robust `try...except` and validation gates).

3. **Mock vs. Live Agent Modules**
   Ensure that your companion agent files (`agents/admet_agent.py`, `agents/boltz1_agent.py`, etc.) return dictionaries containing the exact keys expected by the orchestrator—specifically `toxicity_risk`, `binding_pocket_predicted`, and associated metric keys.


---

## Contributing

Contributions, bug reports, and feature pull requests are welcome! Feel free to open an issue or submit a PR to help improve the orchestrator, safety filters, or agent capabilities.

---

## License

This project is open-source and released under the [MIT License](LICENSE). 

Feel free to use, modify, and distribute this software for academic, research, or commercial purposes.
---
