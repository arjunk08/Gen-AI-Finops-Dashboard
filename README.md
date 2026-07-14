# Gen AI FinOps Dashboard

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-Not%20specified-lightgrey)

An AI-powered FinOps dashboard for understanding, analyzing, and optimizing Generative AI cloud spend.
Enabled with a CI pipeline with tests before each new deployment on render.


**Live app:** https://gen-ai-finops-dashboard.streamlit.app

---

## Overview

**Gen AI FinOps Dashboard** helps organizations gain better visibility into AI-related cloud costs, review invoice-level spending, identify optimization opportunities, and receive AI-assisted FinOps guidance.

The platform is designed for teams that want to improve financial governance around Generative AI workloads by combining invoice analysis, cost insights, visual dashboards, and conversational recommendations in one Streamlit application.

---

## Key Capabilities

### AI Consultation

- Ask FinOps and AI cost-related questions through an interactive assistant.
- Get practical recommendations for reducing unnecessary AI spend.
- Understand cost patterns, anomalies, and optimization opportunities in plain language.
- Support business, finance, and engineering teams with AI-guided decision-making.

### Invoice Overview

- View consolidated invoice information in a simplified format.
- Understand total spend, service-level spend, and cost distribution.
- Review AI-related billing data in a dashboard-friendly layout.
- Make invoice analysis easier for finance and operations teams.

### Invoice Optimization

- Identify potential inefficiencies in AI/cloud usage.
- Generate AI-powered recommendations for cost reduction.
- Highlight opportunities to improve governance and accountability.
- Support better budget control and cloud financial management.

### Cost Insights & Analysis

- Visualize spending trends and major cost drivers.
- Analyze historical cost behavior across available categories.
- Detect high-impact areas for optimization.
- Translate cost data into actionable FinOps insights.

---

## Upcoming Features

### Forecasting Module

A future release will introduce forecasting capabilities to help teams:

- Predict upcoming AI spending trends.
- Improve budget planning and allocation.
- Identify potential cost risks earlier.
- Generate proactive FinOps recommendations.
- Support executive-level financial planning with projected spend insights.

---

## Use Cases

- Generative AI cost visibility
- AI/cloud invoice review
- Cost optimization and savings analysis
- FinOps governance and reporting
- Budget planning support
- Executive financial summaries
- AI-assisted cost management

---

## Technology Stack

- **Python** – Core application logic and data processing
- **Render PostgreSQL** - Database (switched from sqlite3)
- **FastAPI** - Main IPC connector between the streamlit frontend and the PostgreSQL backend
- **SQLAlchemy** - ORM
- **Streamlit** – Interactive dashboard interface
- **Generative AI / LLM Integration** – AI-powered consultation and recommendations

---

## Getting Started

### Option 1: Use the Live Application

Open the hosted Streamlit application:

https://gen-ai-finops-dashboard.streamlit.app

> **Note:** The app is hosted on a free Streamlit deployment. If it has been inactive for some time, the instance may go to sleep and require a short restart period.

If the app is sleeping:

1. Open the Streamlit URL.
2. Use the Streamlit prompt to wake or restart the application.
3. Wait for the instance to initialize.
4. Refresh the page if required.
5. The first login or user register request may take upto a minute to respond because the backend lives on a free render instance, which sleeps due to inactivity
6. Continue using the dashboard normally.
7. You can try uploading a small sample dataset, but if the data is too big it might crash due to being hosted on a free render instance
8. Use "testuser@email.com" as email and "test123" as password, for test user account wiith sample data uploaded
---

## Local Setup

Follow these steps if you want to run the project locally.

### 1. Clone the repository

```bash
git clone https://github.com/arjunk08/Gen-AI-Finops-Dashboard.git
cd Gen-AI-Finops-Dashboard
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the environment:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

If the application uses an LLM provider, API key, or other secrets, create a `.env` file in the project root.

Example:

```env
OPENAI_API_KEY=your_api_key_here
```

> Update the variable names based on the actual configuration used in the application.

### 5. Run the Streamlit app

```bash
streamlit run Dashboard.py
```


---

## Suggested Project Structure

```text
Gen-AI-Finops-Dashboard/
├── Dashboard.py                  # Streamlit application entry point  
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── Sample-data/            # Sample or uploaded invoice/cost data
├── pages/                  # Optional Streamlit multipage views
├── backend/                # Business logic, helpers, and AI modules
└── db_end/                 # PostgresSQL initialized database
```


---

## Dashboard Modules

| Module | Description |
|---|---|
| AI Consultation | Conversational assistant for FinOps questions and optimization guidance. |
| Invoice Overview | High-level invoice summaries and spend breakdowns. |
| Invoice Optimization | AI-generated cost-saving recommendations. |
| Cost Insights & Analysis | Visual analysis of trends, drivers, and spend patterns. |
| Forecasting | Planned module for future cost projections and proactive recommendations. |

---

## Roadmap

- [ ] Forecasting module
- [ ] Enhanced cost optimization recommendations
- [ ] Advanced FinOps analytics
- [ ] Expanded AI consultation capabilities
- [ ] Improved reporting and dashboards
- [ ] Exportable reports for leadership review
- [ ] Additional cloud/provider cost integrations

---

## Best Practices Supported

This dashboard supports practical FinOps workflows such as:

- Cost visibility and allocation
- Invoice analysis and review
- Usage and spend optimization
- Financial accountability
- Data-driven cost governance
- Continuous improvement of AI spend management

---

## Deployment Notes

The application is currently deployed on Streamlit Community Cloud.

Because free hosting environments may pause inactive applications, the first login request after inactivity may take longer than usual.after that the dashboard should continue working normally.

---

## Contributing

Contributions, improvements, and suggestions are welcome.

To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a pull request with a clear description of the update.

Example:

```bash
git checkout -b feature/your-feature-name
git commit -m "Add your feature description"
git push origin feature/your-feature-name
```

---

## License

---

## Author

Created and maintained by [arjunk08](https://github.com/arjunk08).

---

## Links

- **Live Streamlit App:** https://gen-ai-finops-dashboard.streamlit.app
- **GitHub Repository:** https://github.com/arjunk08/Gen-AI-Finops-Dashboard
