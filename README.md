# Grace Allocator

## Intelligent Refugee-to-City Allocation Using Multi-Criteria Optimization

Grace Allocator is a full-stack decision-support system designed to optimize refugee-to-city allocation using advanced mathematical optimization techniques. The project combines clustering, compatibility scoring, and Mixed-Integer Linear Programming (MILP) to generate efficient and scalable allocation strategies while considering multiple socio-economic and policy-driven factors.

The system is designed to support policymakers, researchers, and humanitarian organizations by providing intelligent allocation recommendations through an interactive web-based platform.

---

# Table of Contents

1. Introduction
2. Features
3. System Architecture
4. Technologies Used
5. Project Workflow
6. Optimization Model
7. Installation Guide
8. Backend Setup
9. Frontend Setup
10. Running the Application
11. API Endpoints
12. Dataset Description
13. Policy Scenarios
14. Project Structure
15. Results
16. Future Improvements
17. Contributors
18. License

---

# 1. Introduction

Refugee resettlement is a complex humanitarian problem that involves assigning displaced populations to suitable destination cities while balancing multiple constraints such as:

* City capacity
* Employment opportunities
* Language compatibility
* Cost of living
* Education matching
* Integration support
* Skill demand
* Adaptability

Traditional allocation approaches are often manual or rule-based, which makes them inefficient and difficult to scale for large populations.

Grace Allocator addresses this challenge using:

* Multi-criteria compatibility scoring
* Refugee clustering
* Mixed-Integer Linear Programming (MILP)
* Scenario-based optimization
* Interactive dashboard visualization

The system aims to improve allocation quality, increase coverage, and provide transparent decision-making.

---

# 2. Features

## Core Features

* Intelligent refugee-to-city allocation
* Multi-criteria compatibility scoring
* Optimization using MILP
* Refugee clustering for scalability
* Scenario-based policy simulation
* Real-time allocation dashboard
* REST API-based backend
* Interactive frontend visualization

## Supported Policy Scenarios

* Balanced Allocation
* Jobs Priority
* Integration Priority
* Capacity Stress

## Performance Features

* High allocation coverage
* Reduced unallocated refugee groups
* Balanced city utilization
* Better compatibility compared to greedy methods

---

# 3. System Architecture

The system consists of the following major components:

1. Refugee Dataset Input
2. City Dataset Input
3. Preprocessing and Clustering Engine
4. Compatibility Scoring Engine
5. Policy Scenario Manager
6. MILP Optimization Engine
7. Flask Backend API
8. React Frontend Dashboard
9. Result Visualization Module

## Workflow Overview

```text
Refugee Dataset + City Dataset
            ↓
Preprocessing & Clustering
            ↓
Compatibility Scoring
            ↓
Policy Scenario Selection
            ↓
MILP Optimization Engine
            ↓
Allocation Results
            ↓
Dashboard Visualization
```

---

# 4. Technologies Used

| Technology      | Purpose                        |
| --------------- | ------------------------------ |
| Python          | Core programming language      |
| Flask           | Backend API development        |
| React           | Frontend user interface        |
| Google OR-Tools | Optimization solver            |
| Pandas          | Data preprocessing             |
| NumPy           | Numerical computation          |
| REST API        | Frontend-backend communication |
| JSON            | Data exchange format           |

---

# 5. Project Workflow

The complete workflow of the system includes:

## Step 1: Data Collection

The system collects:

### Refugee Data

* Language
* Skill type
* Education level
* Family size
* Adaptability
* Trauma level
* Cost preference

### City Data

* Capacity
* Employment demand
* Integration support
* Cost index
* Resource availability

## Step 2: Preprocessing

Data cleaning and normalization are performed to ensure consistency.

## Step 3: Clustering

Refugees are grouped into clusters based on:

* Language
* Skill type
* Education
* Cost preference

This reduces computational complexity.

## Step 4: Compatibility Scoring

A weighted score is computed between each refugee cluster and city.

## Step 5: Optimization

The MILP model determines the optimal allocation while satisfying:

* Capacity constraints
* Allocation constraints
* Demand balance

## Step 6: Visualization

Results are displayed through the dashboard.

---

# 6. Optimization Model

The allocation problem is formulated as a Mixed-Integer Linear Programming (MILP) model.

## Objective Function

The system maximizes the total compatibility score:

```math
Maximize Z = Σ Σ Scoreij * xij
```

Where:

* `Scoreij` = compatibility score between refugee group i and city j
* `xij` = allocation decision variable

## Constraints

### Assignment Constraint

Each refugee group must either:

* Be allocated to one city
* Or remain unallocated

### Capacity Constraint

Allocated refugees must not exceed city capacity.

### Binary Constraint

Decision variables are binary.

---

# 7. Installation Guide

## Prerequisites

Ensure the following are installed:

* Python 3.10+
* Node.js
* npm
* Git

---

# 8. Backend Setup

## Clone Repository

```bash
git clone https://github.com/your-username/grace-allocator.git
cd grace-allocator
```

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Flask Server

```bash
python app.py
```

Backend runs on:

```text
http://localhost:5000
```

---

# 9. Frontend Setup

Navigate to frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start React application:

```bash
npm start
```

Frontend runs on:

```text
http://localhost:3000
```

---

# 10. Running the Application

## Start Backend

```bash
python app.py
```

## Start Frontend

```bash
npm start
```

Open browser:

```text
http://localhost:3000
```

---

# 11. API Endpoints

| Method | Endpoint   | Description               |
| ------ | ---------- | ------------------------- |
| GET    | /          | Home route                |
| POST   | /optimize  | Run optimization          |
| GET    | /results   | Fetch allocation results  |
| GET    | /scenarios | Fetch available scenarios |

---

# 12. Dataset Description

## Refugee Dataset

The refugee dataset contains:

| Attribute    | Description                    |
| ------------ | ------------------------------ |
| Language     | Primary language               |
| Skill Type   | Professional skill category    |
| Education    | Education level                |
| Family Size  | Number of members              |
| Adaptability | Integration adaptability score |
| Trauma Level | Psychological condition score  |

## City Dataset

| Attribute           | Description                 |
| ------------------- | --------------------------- |
| Capacity            | Maximum supported refugees  |
| Job Demand          | Employment requirement      |
| Cost Index          | Cost of living              |
| Integration Support | Social support availability |
| Resources           | City resource availability  |

---

# 13. Policy Scenarios

## Balanced Scenario

Equal importance to all compatibility factors.

## Jobs Priority Scenario

Higher weight for employment matching.

## Integration Priority Scenario

Focuses on social integration and adaptability.

## Capacity Stress Scenario

Simulates resource-constrained environments.

---

# 14. Project Structure

```text
Grace-Allocator/
│
├── backend/
│   ├── app.py
│   ├── optimizer.py
│   ├── scoring.py
│   ├── clustering.py
│   └── datasets/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

# 15. Results

The proposed system demonstrates:

* Improved allocation quality
* Better compatibility scores
* Higher refugee coverage
* Balanced city utilization
* Reduced unallocated groups

Compared to greedy allocation methods, the optimization-based approach provides better global allocation outcomes.

---

# 16. Future Improvements

Potential future enhancements include:

* Integration with real-world datasets
* Real-time policy adaptation
* Machine learning-based compatibility prediction
* Advanced visualization dashboards
* Geographical and legal constraint modeling
* Cloud deployment support

---

# 17. Contributors

## Project Team

* Afeef Ahmed
* Project Contributors

---

# 18. License

This project is intended for academic and research purposes.

You may modify and extend the system for educational or non-commercial use.

---

# Acknowledgement

This project was developed as part of academic research in optimization and humanitarian decision-support systems. The project demonstrates the practical application of operations research, optimization algorithms, and full-stack development in solving real-world allocation challenges.
