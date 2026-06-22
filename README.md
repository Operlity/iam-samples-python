# Flask IdentityHub OIDC Sample

A sample Python Flask web application demonstrating secure authentication integration with **IdentityHub** using **OpenID Connect (OIDC)** and **Proof Key for Code Exchange (PKCE)**. The application features a glassmorphic dashboard with a contact manager utilizing a local SQLite database.

## Features
- **Secure OIDC Authentication**: Integrated with Authlib Flask Client.
- **PKCE Authorization Flow**: Secure authorization flow for public/web applications.
- **Session Management**: Server-side filesystem sessions managed by `flask-session`.
- **Contact Manager**: A SQLite-backed dashboard to add, edit, and delete contacts.
- **Premium Glassmorphic UI**: Styled with modern CSS styling, including visual cues and responsive layouts.

## Prerequisites
- Python 3.10 or higher
- An IdentityHub tenant (or another OIDC provider) with client registration.

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/iam-samples-python.git
   cd iam-samples-python
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows (Command Prompt):
   venv\Scripts\activate.bat
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**
   ```bash
   pip install Flask Authlib pyOpenSSL flask-session
   ```

4. **Configure Environment Variables**
   Copy the example environment file and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
   Open the newly created `.env` file and set the following values:
   - `FLASK_SECRET_KEY`: A unique random key for signing cookies.
   - `IDENTITY_HUB_ISS_URL`: The IdentityHub Issuer/Discovery URL.
   - `IDENTITY_HUB_CLIENT_ID`: Your registered IdentityHub Client ID.
   - `IDENTITY_HUB_CLIENT_SECRET`: Your registered IdentityHub Client Secret.

## Running the Application

Flask must be run with SSL support enabled because IdentityHub redirects require HTTPS callbacks. The application is configured to run locally on port `7284` with an adhoc SSL certificate.

Start the application:
```bash
python app.py
```

Visit the application at: **[https://localhost:7284](https://localhost:7284)**

> [!NOTE]
> Since an adhoc SSL certificate is generated at startup, your browser will display a warning page (e.g., "Your connection is not private"). It is safe to click **Advanced** -> **Proceed to localhost (unsafe)** in your local development environment.

## Database & Session Directory
- **Database**: SQLite database file (`contacts.db`) will be automatically created in the root directory on startup.
- **Session Cache**: Session data will be stored in a local `./flask_session` directory.
- Both of these components, along with IDE files, are ignored from version control via `.gitignore`.