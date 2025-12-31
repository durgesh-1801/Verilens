# VeriLens  
### Explainable AI for Public Fraud & Anomaly Detection

---

## 📌 Problem Statement

Government audit systems process large volumes of transaction data, but audits are often manual, delayed, and sample-based. As a result, suspicious spending patterns are frequently detected after funds have already been disbursed.

The core challenge is not data availability, but the absence of tools that can proactively highlight which transactions deserve attention first—without overwhelming auditors or making opaque decisions.

---

## 🎯 Solution Overview

**VeriLens** is a software-based, AI-assisted decision-support system designed to help government auditors prioritize transactions for review.

Instead of automatically declaring fraud, the system:
- Learns normal spending behavior from historical data
- Flags statistically unusual transactions
- Presents them for human review, ensuring final decisions remain with auditors

This approach emphasizes practicality, explainability, and responsible use of AI in public-sector environments.

---

## 🧠 Design Principles (USP)

- **Explainability-first:** Every flagged transaction includes a clear, human-readable reason  
- **Human-in-the-loop:** Assists auditors rather than replacing them  
- **Low false-positive focus:** Flags only the most significant anomalies  
- **Software-only & integration-ready:** No hardware dependency; compatible with existing systems  

---

## ⚙️ How It Works (High Level)

1. Structured transaction data is ingested (CSV / database extracts)  
2. Key behavioral features such as transaction amount and frequency are processed  
3. An unsupervised ML model identifies anomalous patterns  
4. Flagged transactions are displayed with risk indicators and explanations  

---

## 🛠️ Technology Stack

- **Python** – Core development language  
- **Scikit-learn (Isolation Forest)** – Unsupervised anomaly detection  
- **FastAPI** – Backend API architecture (API-ready)  
- **Streamlit** – Interactive dashboard and visualization  
- **CSV / SQLite** – Lightweight data storage  

The stack is intentionally minimal to ensure clarity, transparency, and ease of deployment.

---

## 🧪 Prototype Scope

This repository contains a **Minimum Viable Prototype (MVP)** that demonstrates:
- End-to-end anomaly detection on transaction data  
- Explainable risk flagging  
- A working interactive dashboard  

**Note:** This prototype is a proof of concept and not a production deployment.

---

## ⚠️ Data & Ethics Disclaimer

- The dataset used is synthetic and created for demonstration purposes  
- VeriLens does not label transactions as fraudulent; it flags anomalies for review only  
- All outputs are intended to support, not replace, human auditors  

---

## 📎 Repository Structure

- `app.py` – Streamlit-based prototype  
- `data.csv` – Sample transaction dataset  
- `requirements.txt` – Project dependencies  
- `README.md` – Project documentation  

---

## 👥 Team

Developed as part of **Hack4Delhi**  
Focused on realistic, explainable, and deployable public-sector AI solutions.

---

### ⭐ Final Note

VeriLens prioritizes trust, explainability, and feasibility over complexity—key requirements for responsible AI adoption in government systems.
