# 💳 Real-Time Fraud Detection Engine

A production-ready Machine Learning and Web Service application built with **FastAPI**, **Scikit-Learn**, **SQLite**, and **Streamlit**. It predicts whether a transaction is fraudulent based on historical behavior, distance parameters, and purchase metrics. Included in the project is an automated **GitHub Actions CI/CD pipeline** that trains, tests, and builds Docker container artifacts.

---

## 📸 Architecture & Workflow
┌─────────────────┐      HTTP POST      ┌─────────────────┐      Model Predict     ┌──────────────────────┐
│ Streamlit UI    │ ─────────────────>  │ FastAPI Service │ ────────────────────>  │ Trained Model        │
│ (Dashboard)     │ <─────────────────  │ (Backend API)   │ <────────────────────  │ (fraud_model.joblib) │
└─────────────────┘      JSON Response  └────────┬────────┘                        └──────────────────────┘
│
│ Logging
▼
┌─────────────────┐
│ SQLite DB       │
│(transactions.db)│
└─────────────────┘
---

## ✨ Features

- **Machine Learning Inference:** Fast classification model built with Scikit-Learn to evaluate fraud risk probabilities.
- **RESTful API Backend:** High-performance REST API served by **FastAPI** with built-in interactive Swagger UI docs.
- **Real-Time Interactive UI:** **Streamlit** dashboard to manually submit transactions and analyze historical transaction risks.
- **Database Logging:** Automatic logging of every evaluated transaction into an **SQLite** database (`transactions.db`).
- **CI/CD Pipeline:** Fully functional **GitHub Actions** workflow that handles automated dependency installation, unit testing with `pytest`, model training, and Docker image container builds.

---

## 🛠️ Tech Stack

- **Language:** Python 3.12
- **ML & Data:** Scikit-Learn, Joblib, Pandas, NumPy
- **Backend API:** FastAPI, Uvicorn, Pydantic
- **Database:** SQLite, `aiosqlite`
- **Frontend Dashboard:** Streamlit
- **Containerization & CI/CD:** Docker, GitHub Actions, Pytest

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Git

### 1. Clone the Repository

```bash
git clone [https://github.com/](https://github.com/)<Vala-Aditya-C>/fraud-detection-engine.git
cd fraud-detection-engine