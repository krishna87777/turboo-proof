# TurboProof 🚀

TurboProof is an advanced academic proof generator that uses artificial intelligence to create well-structured, technically sound proofs for academic and research topics.

## 📋 Overview

TurboProof leverages the power of AI to generate comprehensive academic proofs by analyzing relevant GitHub repositories and arXiv papers. The application provides users with detailed proofs along with clarity and depth scores, making it an invaluable tool for researchers, students, and professionals.

## ✨ Features

- **AI-Powered Proof Generation**: Generate academic-level proofs on any research topic
- **Source Integration**: Automatically fetches relevant information from GitHub repositories and arXiv papers
- **Quality Evaluation**: Each proof receives clarity and depth scores
- **User Management**: Secure login and signup functionality
- **Project History**: Save and manage all your generated proofs
- **Responsive UI**: Clean, intuitive interface for a seamless user experience

## 🏗️ Project Structure

```
turboproof/
├── .env                     # Environment variables (not tracked by git)
├── .streamlit/
│   └── secrets.toml         # Streamlit secrets (GitHub token, etc.)
├── app.py                   # Main application file
├── auth.py                  # Authentication functions
├── db.py                    # Database connection and operations
├── evaluation.py            # Proof evaluation functions
├── proof_generator.py       # Core proof generation functionality
├── requirements.txt         # Python dependencies
├── style.css                # Custom CSS styles
└── utils/
    ├── arxiv_scraper.py     # Functions to search arXiv papers
    ├── github_scraper.py    # Functions to search GitHub repositories
    └── vector_store.py      # Vector database utilities
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MongoDB (for user and project storage)
- GitHub token (optional, for higher rate limits)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/turboproof.git
   cd turboproof
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your secrets:
   
   Create a `.streamlit/secrets.toml` file with the following content:
   ```toml
   # MongoDB connection
   MONGODB_URI = "your_mongodb_connection_string"
   
   # GitHub token (optional)
   github_token = "your_github_token"
   ```

   Alternatively, you can set these as environment variables.

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## 🔧 Configuration

### GitHub API

The application can work with or without a GitHub token. However, using a token increases the rate limit for API calls.

To use GitHub without a token, the application will use the public API with lower rate limits.

### Database Setup

TurboProof uses MongoDB to store user accounts and generated proofs. Make sure to set up your MongoDB connection string in the secrets file or as an environment variable.

## 🧩 Core Components

### Proof Generation Process

1. **Research Collection**: Scans GitHub repositories and arXiv papers for relevant content
2. **Content Processing**: Filters and processes information using vector similarity
3. **AI Generation**: Uses AI to generate a comprehensive proof
4. **Quality Evaluation**: Scores each proof for clarity and depth

### User Authentication

The application provides secure user authentication with signup and login functionality. User credentials are stored securely in the MongoDB database.

## 🌐 Deployment

TurboProof can be deployed on Streamlit Cloud or any other platform that supports Streamlit applications.

For Streamlit Cloud deployment:
1. Push your code to a GitHub repository
2. Connect your repository to Streamlit Cloud
3. Configure your secrets in the Streamlit Cloud dashboard

## 📜 License

[MIT License](LICENSE)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📬 Contact

For questions or feedback, please contact support@turboproof.ai
