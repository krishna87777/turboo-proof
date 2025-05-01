import streamlit as st
import time
from auth import login, signup
from proof_generator import generate_proof
from evaluation import evaluate_proof
from db import projects_collection
from utils.github_scraper import search_github
from utils.arxiv_scraper import search_arxiv
import os

# Page configuration
st.set_page_config(
    page_title="TurboProof 🚀",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Configure your GitHub token
github_token = st.secrets.get("github_token", os.environ.get("GITHUB_TOKEN"))

# Session State initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'generated_proof' not in st.session_state:
    st.session_state.generated_proof = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'proof_history' not in st.session_state:
    st.session_state.proof_history = []


# Navigation functions
def set_page(page):
    st.session_state.current_page = page


def handle_login(username, password):
    if login(username, password):
        st.session_state.logged_in = True
        st.session_state.username = username
        set_page("dashboard")
        return True
    return False


def handle_signup(username, email, password):
    success, message = signup(username, email, password)
    return success, message


def handle_logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    set_page("home")


def generate_and_save_proof(topic):
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Step 1: Fetching sources
    status_text.text("Fetching relevant sources...")
    progress_bar.progress(20)
    time.sleep(0.5)  # Simulate processing time

    github_sources = search_github(topic, github_token=github_token)
    progress_bar.progress(40)

    arxiv_sources = search_arxiv(topic)
    progress_bar.progress(60)

    # Step 2: Generating proof
    status_text.text("Generating proof with AI...")
    progress_bar.progress(80)
    time.sleep(0.5)  # Simulate processing time

    proof = generate_proof(topic)

    # Step 3: Evaluating
    status_text.text("Evaluating proof quality...")
    clarity, depth = evaluate_proof(proof)
    progress_bar.progress(100)

    # Save to history in session state
    proof_data = {
        "topic": topic,
        "proof": proof,
        "clarity": clarity,
        "depth": depth,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "github_sources": github_sources,
        "arxiv_sources": arxiv_sources
    }

    # Save to DB
    if st.session_state.logged_in:
        projects_collection.insert_one({
            "username": st.session_state.username,
            "topic": topic,
            "generated_proof": proof,
            "clarity_score": clarity,
            "depth_score": depth,
            "sources": {
                "github": [{"title": src["title"], "url": src["url"], "readme": src["readme"]} for src in
                           github_sources],
                "arxiv": [{"title": src["title"], "url": src["url"]} for src in arxiv_sources]
            }
        })

    st.session_state.last_query = topic
    st.session_state.generated_proof = proof_data
    st.session_state.proof_history.insert(0, proof_data)  # Add to start of list

    # Clear progress indicators
    status_text.empty()
    progress_bar.empty()

    return proof_data


# Sidebar
def render_sidebar():
    with st.sidebar:

        if st.session_state.logged_in:
            st.markdown(f"### Welcome, {st.session_state.username} 👋")

            # Navigation menu
            st.subheader("Navigation")
            if st.button("🏠 Dashboard", use_container_width=True, key="nav_dashboard"):
                set_page("dashboard")
            if st.button("🧠 Generate Proof", use_container_width=True, key="nav_generate"):
                set_page("generate")
            if st.button("📚 My Proofs", use_container_width=True, key="nav_history"):
                set_page("history")
            if st.button("ℹ️ About", use_container_width=True, key="nav_about"):
                set_page("about")

            # Logout at bottom of sidebar
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True, key="btn_logout"):
                handle_logout()
        else:
            st.markdown("### TurboProof 🚀")
            st.markdown("Academic Proof Generator powered by AI")

            # Navigation for non-logged in users
            st.subheader("Navigation")
            if st.button("🏠 Home", use_container_width=True, key="nav_home"):
                set_page("home")
            if st.button("🔐 Login", use_container_width=True, key="nav_login"):
                set_page("login")
            if st.button("📝 Signup", use_container_width=True, key="nav_signup"):
                set_page("signup")
            if st.button("ℹ️ About", use_container_width=True, key="nav_about_no_login"):
                set_page("about")

        st.markdown("---")
        st.markdown("© 2025 TurboProof")


# Home page
def home_page():
    st.markdown("""
    <div class="hero-container">
        <h1>Welcome to TurboProof</h1>
        <p class="hero-text">Generate academic-level proofs powered by AI</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="feature-section">
            <h2>How It Works</h2>
            <div class="feature-cards">
                <div class="feature-card">
                    <h3>1. Enter Topic</h3>
                    <p>Input any academic or research topic that needs proof</p>
                </div>
                <div class="feature-card">
                    <h3>2. Generate Proof</h3>
                    <p>Our AI analyzes GitHub and ArXiv sources</p>
                </div>
                <div class="feature-card">
                    <h3>3. Review Results</h3>
                    <p>Get detailed proofs with citations and clarity scores</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='cta-container'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔐 Login", use_container_width=True, key="home_login"):
                set_page("login")
        with col2:
            if st.button("📝 Signup", use_container_width=True, key="home_signup"):
                set_page("signup")
        st.markdown("</div>", unsafe_allow_html=True)

        # Testimonials
        st.markdown("""
        <div class="testimonials">
            <h2>What Users Say</h2>
            <div class="testimonial-cards">
                <div class="testimonial-card">
                    <p classname= "inside-para">"TurboProof helped me understand complex topics for my dissertation!"</p>
                    <p class="testimonial-author">- Computer Science Student</p>
                </div>
                <div class="testimonial-card">
                    <p  classname= "inside-para">"The AI-generated proofs saved me days of research work."</p>
                    <p class="testimonial-author">- Mathematics Professor</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# Login page
def login_page():
    st.markdown("<h1 class='page-title'>Login to TurboProof</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<div class='auth-form'>", unsafe_allow_html=True)
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True, key="btn_login_submit"):
                if handle_login(username, password):
                    st.success("Logged in successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
        with col2:
            if st.button("Back to Home", use_container_width=True, key="btn_login_back"):
                set_page("home")
                st.rerun()

        st.markdown("<div class='auth-links'>", unsafe_allow_html=True)
        if st.button("Don't have an account? Sign up here", key="to_signup"):
            set_page("signup")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# Signup page
def signup_page():
    st.markdown("<h1 class='page-title'>Create a TurboProof Account</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<div class='auth-form'>", unsafe_allow_html=True)
        new_username = st.text_input("Username", key="signup_user")
        email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_pass")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create Account", use_container_width=True, key="btn_signup_submit"):
                if new_password != confirm_password:
                    st.error("Passwords don't match.")
                elif not new_username or not email or not new_password:
                    st.error("All fields are required.")
                else:
                    success, message = handle_signup(new_username, email, new_password)
                    if success:
                        st.success(message)
                        time.sleep(1)
                        set_page("login")
                        st.rerun()
                    else:
                        st.error(message)
        with col2:
            if st.button("Back to Home", use_container_width=True, key="btn_signup_back"):
                set_page("home")
                st.rerun()

        st.markdown("<div class='auth-links'>", unsafe_allow_html=True)
        if st.button("Already have an account? Login here", key="to_login"):
            set_page("login")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# Dashboard (after login)
def dashboard_page():
    st.markdown("<h1 class='page-title'>Your Dashboard</h1>", unsafe_allow_html=True)

    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <h3 classname = "inside-para">Total Proofs</h3>
            <p class="stat-number">{}</p>
        </div>
        """.format(len(st.session_state.proof_history)), unsafe_allow_html=True)

    with col2:
        avg_clarity = 0
        if len(st.session_state.proof_history) > 0:
            avg_clarity = sum([p.get("clarity", 0) for p in st.session_state.proof_history]) / len(
                st.session_state.proof_history)

        st.markdown("""
        <div class="stat-card">
            <h3>Avg. Clarity</h3>
            <p class="stat-number">{:.1f}/10</p>
        </div>
        """.format(avg_clarity), unsafe_allow_html=True)

    with col3:
        avg_depth = 0
        if len(st.session_state.proof_history) > 0:
            avg_depth = sum([p.get("depth", 0) for p in st.session_state.proof_history]) / len(
                st.session_state.proof_history)

        st.markdown("""
        <div class="stat-card">
            <h3>Avg. Depth</h3>
            <p class="stat-number">{:.1f}/10</p>
        </div>
        """.format(avg_depth), unsafe_allow_html=True)

    # Recent proofs
    st.markdown("<h2>Recent Proofs</h2>", unsafe_allow_html=True)

    if st.session_state.proof_history:
        for i, proof in enumerate(st.session_state.proof_history[:3]):  # Show only 3 recent proofs
            with st.expander(f"**{proof['topic']}** - {proof['timestamp']}"):
                st.markdown(f"**Clarity Score:** {proof['clarity']}/10 | **Depth Score:** {proof['depth']}/10")
                st.markdown(proof['proof'])
    else:
        st.info("You haven't generated any proofs yet. Go to 'Generate Proof' to create your first one!")

    # Quick access
    st.markdown("<h2>Quick Actions</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧠 Generate New Proof", use_container_width=True):
            set_page("generate")
            st.rerun()

    with col2:
        if st.button("📚 View All My Proofs", use_container_width=True):
            set_page("history")
            st.rerun()


# Generate proof page
def generate_proof_page():
    st.markdown("<h1 class='page-title'>Generate New Proof</h1>", unsafe_allow_html=True)

    topic = st.text_input("Enter your project topic or research title:",
                          placeholder="e.g., Quantum Computing Applications in Cryptography")

    generate_button = st.button("Generate TurboProof 🚀", use_container_width=True)

    if generate_button and topic:
        proof_data = generate_and_save_proof(topic)

        # Display proof results
        st.markdown("<h2>📄 TurboProof Output</h2>", unsafe_allow_html=True)

        # Scores in columns
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Clarity Score", value=f"{proof_data['clarity']}/10")
        with col2:
            st.metric(label="Depth Score", value=f"{proof_data['depth']}/10")

        # Main content
        st.markdown("### Proof Content")
        st.markdown(proof_data['proof'])

        # Sources
        st.markdown("<h3>🔍 Sources Used</h3>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["GitHub Repositories", "arXiv Papers"])

        with tab1:
            if proof_data['github_sources']:
                for i, repo in enumerate(proof_data['github_sources']):
                    st.markdown(f"**[{repo['full_name']}]({repo['url']})**")
                    st.write(f"*Stars:* {repo['stars']}")
                    st.write(f"*Description:* {repo['description']}")

                    # Create expandable section for README
                    with st.expander(f"View README for {repo['title']}"):
                        st.markdown(repo['readme'])

                    st.markdown("---")
            else:
                st.info("No GitHub repositories found for this topic.")

        with tab2:
            if proof_data['arxiv_sources']:
                for src in proof_data['arxiv_sources']:
                    st.markdown(f"**[{src['title']}]({src['url']})**")
                    st.write(f"*Authors:* {src['authors']}")
                    st.write(f"*Published:* {src['published']}")
                    st.write(f"*Summary:* {src['summary']}")
                    st.markdown("---")
            else:
                st.info("No arXiv papers found for this topic.")

    elif generate_button and not topic:
        st.error("Please enter a topic to generate a proof.")


# History page
def history_page():
    st.markdown("<h1 class='page-title'>My Proofs</h1>", unsafe_allow_html=True)

    if not st.session_state.proof_history:
        st.info("You haven't generated any proofs yet.")
        if st.button("Generate your first proof", use_container_width=True):
            set_page("generate")
            st.rerun()
    else:
        # Search and filter
        search_term = st.text_input("Search your proofs:", placeholder="Enter keywords...")

        filtered_proofs = st.session_state.proof_history
        if search_term:
            filtered_proofs = [p for p in st.session_state.proof_history
                               if search_term.lower() in p['topic'].lower() or
                               search_term.lower() in p['proof'].lower()]

        st.markdown(f"### Showing {len(filtered_proofs)} proofs")

        # Display proofs
        for i, proof in enumerate(filtered_proofs):
            with st.expander(f"**{proof['topic']}** - {proof['timestamp']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Clarity Score", f"{proof['clarity']}/10")
                with col2:
                    st.metric("Depth Score", f"{proof['depth']}/10")

                st.markdown("### Proof Content")
                st.markdown(proof['proof'])

                # Sources
                st.markdown("<h4>🔍 Sources Used</h4>", unsafe_allow_html=True)

                tab1, tab2 = st.tabs(["GitHub", "arXiv"])

                with tab1:
                    if proof['github_sources']:
                        for repo in proof['github_sources']:
                            st.markdown(f"**[{repo['title']}]({repo['url']})**")
                            st.write(f"*Stars:* {repo['stars']}")
                    else:
                        st.info("No GitHub sources.")

                with tab2:
                    if proof['arxiv_sources']:
                        for src in proof['arxiv_sources']:
                            st.markdown(f"**[{src['title']}]({src['url']})**")
                            st.write(f"*Authors:* {src['authors']}")
                    else:
                        st.info("No arXiv sources.")


# About page
def about_page():
    st.markdown("<h1 class='page-title'>About TurboProof</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div class="about-content">
        <h2>What is TurboProof?</h2>
        <p>TurboProof is an advanced academic proof generator that uses artificial intelligence to create well-structured, 
        technically sound proofs for academic and research topics.</p>

        <h2>How It Works</h2>
        <p>Our system searches through relevant GitHub repositories and arXiv papers to gather information about your topic.
        Then, using advanced AI models, it synthesizes this information into a coherent, academic-level proof.</p>

        <h3>The Process:</h3>
        <ol>
            <li><strong>Research Collection:</strong> We scan GitHub and arXiv for the most relevant content.</li>
            <li><strong>Content Processing:</strong> Our vector database ensures only the most relevant information is used.</li>
            <li><strong>AI Generation:</strong> Using Gemini 1.5 Pro, we generate a comprehensive proof.</li>
            <li><strong>Quality Evaluation:</strong> Each proof is automatically scored for clarity and depth.</li>
        </ol>

        <h2>Use Cases</h2>
        <p>TurboProof is ideal for:</p>
        <ul>
            <li>Academic researchers seeking to understand complex topics</li>
            <li>Students working on dissertations and theses</li>
            <li>Professionals exploring technical concepts</li>
            <li>Anyone looking to deepen their understanding of specialized subjects</li>
        </ul>

        <h2>Contact Us</h2>
        <p>Have questions or feedback? Contact us at support@turboproof.ai</p>
    </div>
    """, unsafe_allow_html=True)


# Main app routing
def main():
    render_sidebar()

    if st.session_state.current_page == "home":
        home_page()
    elif st.session_state.current_page == "login":
        login_page()
    elif st.session_state.current_page == "signup":
        signup_page()
    elif st.session_state.current_page == "dashboard":
        if st.session_state.logged_in:
            dashboard_page()
        else:
            set_page("login")
            st.rerun()
    elif st.session_state.current_page == "generate":
        if st.session_state.logged_in:
            generate_proof_page()
        else:
            set_page("login")
            st.rerun()
    elif st.session_state.current_page == "history":
        if st.session_state.logged_in:
            history_page()
        else:
            set_page("login")
            st.rerun()
    elif st.session_state.current_page == "about":
        about_page()


if __name__ == "__main__":
    main()