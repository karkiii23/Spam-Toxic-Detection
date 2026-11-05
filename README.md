# Spam & Toxic Comment Detection System

A machine learning-based web application that detects spam messages, toxic comments, abusive language, and potentially harmful online communications using Natural Language Processing (NLP).

The system uses TF-IDF vectorization and Linear Support Vector Classification (LinearSVC) to classify messages into spam, normal, toxic, and safe categories.

## Project Overview

Online platforms receive large numbers of unwanted messages, promotional scams, phishing attempts, abusive comments, and harmful communications.

This project aims to provide a simple content analysis system that helps users identify suspicious and toxic messages.

Users can analyse individual messages or multiple messages, view prediction results, maintain analysis history, and generate PDF reports.

## Key Features

- **Spam Detection:** Identifies unwanted and suspicious messages.
- **Toxic Comment Detection:** Identifies potentially abusive and harmful language.
- **Single Message Analysis:** Analyse one message at a time.
- **Batch Message Analysis:** Analyse multiple messages together.
- **Machine Learning Predictions:** Uses trained TF-IDF and LinearSVC models.
- **User Authentication:** Registration, login, and logout.
- **User Dashboard:** Displays analysis statistics and recent predictions.
- **Analysis History:** Stores previous analysis results.
- **CSV Export:** Download batch analysis results.
- **PDF Reports:** Generate downloadable reports with analysis summaries and history.
- **Cybercrime Reporting Resources:** Provides links to official Indian cybercrime reporting channels in PDF reports.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend | Flask |
| Machine Learning | Scikit-learn |
| NLP | TF-IDF |
| Classification Algorithm | LinearSVC |
| Database | PostgreSQL |
| Database Library | Psycopg |
| Authentication | Werkzeug |
| PDF Generation | ReportLab |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Render |
| Version Control | Git and GitHub |

## Machine Learning Models

The application uses two independently trained classification models.

### 1. Spam Detection Model

- Algorithm: Linear Support Vector Classification (LinearSVC)
- Feature Extraction: TF-IDF Vectorizer
- Purpose: Classifies messages as SPAM or NORMAL.

Files:

- `spam_model.pkl`
- `tfidf_vectorizer.pkl`

### 2. Toxic Comment Detection Model

- Algorithm: Linear Support Vector Classification (LinearSVC)
- Feature Extraction: TF-IDF Vectorizer
- Purpose: Classifies messages as TOXIC or NORMAL.

Files:

- `toxic_model.pkl`
- `toxic_tfidf_vectorizer.pkl`

### Overall Classification

The application combines the predictions from both models.

| Spam Result | Toxic Result | Overall Result |
|---|---|---|
| NORMAL | NORMAL | SAFE |
| SPAM | NORMAL | SPAM DETECTED |
| NORMAL | TOXIC | TOXIC CONTENT |
| SPAM | TOXIC | SPAM + TOXIC |

*Predictions depend on the models and their training datasets.*

## Project Structure

```text
Spam-Toxic-Detection/
│
├── app.py
├── requirements.txt
├── Procfile
├── create_postgres_tables.py
├── README.md
│
├── models/
│   ├── spam_model.pkl
│   ├── tfidf_vectorizer.pkl
│   ├── toxic_model.pkl
│   └── toxic_tfidf_vectorizer.pkl
│
├── data/
│   ├── spam.csv
│   ├── spam_cleaned.csv
│   └── toxic_comments.csv
│
├── notebooks/
│   ├── 01_dataset_understanding.ipynb
│   └── 02_insult_detection.ipynb
│
├── database/
│   └── users.db
│
├── static/
│   └── css/
│       └── style.css
│
└── templates/
    ├── index.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── history.html
    └── account.html
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/karkiii23/Spam-Toxic-Detection.git
```

### 2. Open the Project Directory

```bash
cd Spam-Toxic-Detection
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

The application requires two environment variables:

- `DATABASE_URL`: PostgreSQL connection URL.
- `SECRET_KEY`: Secure Flask session key.

For Windows PowerShell:

```powershell
$env:DATABASE_URL = "YOUR_POSTGRESQL_DATABASE_URL"
$env:SECRET_KEY = "YOUR_SECRET_KEY"
```

Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Do not upload your actual database URL or secret key to GitHub.

### 6. Run the Application

```bash
python app.py
```

Open your browser:

```text
http://127.0.0.1:5000/
```

## Database Configuration

The application uses PostgreSQL to store user information and analysis history.

### Database Tables

**Users**

Stores registered user information.

| Column | Description |
|---|---|
| id | Unique user ID |
| username | Username |
| email | Email address |
| password | Hashed password |

**Analysis History**

Stores the results of message analysis.

| Column | Description |
|---|---|
| id | Unique analysis ID |
| user_id | Associated user ID |
| message | Analysed message |
| spam_result | Spam classification |
| toxic_result | Toxicity classification |
| overall_result | Combined result |
| analysis_type | Single or Batch |
| created_at | Analysis timestamp |

Database tables are initialized by the Flask application when it connects to PostgreSQL.

## Deployment on Render

The project can be deployed using Render and GitHub.

### Deployment Steps

1. Upload the project to GitHub.
2. Create a PostgreSQL database on Render.
3. Create a new Render Web Service.
4. Connect the GitHub repository.
5. Configure the build and start commands.

**Build Command**

```bash
pip install -r requirements.txt
```

**Start Command**

```bash
gunicorn app:app
```

### Environment Variables on Render

Configure the following variables in the Web Service Environment settings:

| Key | Value |
|---|---|
| DATABASE_URL | PostgreSQL Internal Database URL |
| SECRET_KEY | Newly generated secure secret key |

Use the same Render region for your PostgreSQL database and Web Service.

## Cybercrime Reporting Resources (India)

The project provides information about official reporting channels for users who encounter online fraud, harassment, impersonation, or suspicious communications.

| Resource | Purpose | Official Website |
|---|---|---|
| National Cyber Crime Reporting Portal | Report cybercrime, online harassment, phishing, and impersonation | https://cybercrime.gov.in/ |
| Cybercrime Helpline 1930 | Report financial cyber fraud | 1930 |
| Sanchar Saathi – Chakshu | Report suspected fraudulent communications | https://sancharsaathi.gov.in/ |

These resources are provided for guidance. The application does not automatically submit complaints to government authorities.

## Testing Examples

Try these sample messages:

**Normal Message**

```text
Hello! How are you doing today?
```

**Spam Message**

```text
Congratulations! You have won 10 lakh rupees.
Click this link immediately to claim your prize!
```

**Phishing Message**

```text
Your bank account will be blocked.
Verify your details immediately.
```

**Toxic Message**

```text
You are stupid and completely useless.
```

**Hinglish Message**

```text
Aapne 10 lakh rupaye jeete hain.
Prize claim karne ke liye link click karein.
```

Note: Prediction accuracy depends on the training data. English-trained models may not reliably classify Hindi and Hinglish messages without suitable multilingual training data.

## Security Considerations

- Passwords are stored using password hashing.
- Database credentials are configured through environment variables.
- Flask sessions use a secret key.
- User analysis history is associated with individual accounts.
- Never commit `.env` files, database passwords, or secret keys to GitHub.

## Future Enhancements

- Improved Hindi and Hinglish spam detection.
- Multilingual NLP model support.
- Advanced phishing and malicious URL detection.
- Model performance evaluation and confidence reporting.
- Admin dashboard and user management.
- REST API for third-party integration.
- Improved real-time content moderation.

## Project Purpose

This project demonstrates the application of Machine Learning, Natural Language Processing, web development, and database management to an online security problem.

It aims to help users recognise spam and toxic communications and become more aware of online safety.

## Author

**Shubham Karki**

BCA Student

GitHub: https://github.com/karkiii23

---

*Spam & Toxic Comment Detection – NLP + Security Project*
