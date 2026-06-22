from flask import Flask, url_for, session, redirect, render_template, request
from authlib.integrations.flask_client import OAuth
from flask_session import Session
import os
import logging
import sqlite3

# Load environment variables from .env file if it exists (for local development)
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()

# Configure logging to see OIDC errors
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key_change_in_production_1234567890')
DB_PATH = os.path.join(app.root_path, 'contacts.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT
            )
        ''')
        conn.commit()


init_db()

# SERVER-SIDE SESSION CONFIGURATION
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = './flask_session'
app.config['SESSION_COOKIE_SAMESITE'] = 'None' # Critical for OIDC redirects
app.config['SESSION_COOKIE_SECURE'] = True
Session(app)

# IdentityHub Credentials (loaded from environment variables in production)
IDENTITY_HUB_ISS_URL = os.getenv('IDENTITY_HUB_ISS_URL', 'https://ogsiamapp.azurewebsites.net')
CLIENT_ID = os.getenv('IDENTITY_HUB_CLIENT_ID', 'your-identity-hub-client-id')
CLIENT_SECRET = os.getenv('IDENTITY_HUB_CLIENT_SECRET', 'your-identity-hub-client-secret')

oauth = OAuth(app)
oauth.register(
    name='identityhub',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url=f'{IDENTITY_HUB_ISS_URL}/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid profile email',
        'code_challenge_method': 'S256'
    },
    token_endpoint_auth_method='client_secret_post'
)

@app.route('/')
def index():
    user = session.get('user')
    if user:
        return redirect(url_for('welcome'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    # Force use of 'localhost' instead of '127.0.0.1' for the redirect_uri
    redirect_uri = url_for('authorize', _external=True, _scheme='https').replace('127.0.0.1', 'localhost')
    return oauth.identityhub.authorize_redirect(redirect_uri, prompt='login')

@app.route('/signin-oidc')
def authorize():
    import traceback
    print("=== OIDC CALLBACK DIAGNOSTICS ===")
    print(f"Request URL: {request.url}")
    print(f"Request Args: {dict(request.args)}")
    print(f"Session Keys: {list(session.keys())}")
    print(f"Session Content: {dict(session)}")
    print(f"Request Cookies: {dict(request.cookies)}")
    try:
        token = oauth.identityhub.authorize_access_token()
        user = token.get('userinfo')
        if user:
            session['user'] = user
            session['token'] = token
            # Force session to be saved
            session.modified = True
            print(f"Successfully logged in as: {user.get('name')}")
        return redirect(url_for('welcome'))
    except Exception as e:
        print(f"!!! AUTH ERROR: {str(e)}")
        traceback.print_exc()
        # If it's a state mismatch, we should clear session and try again
        session.clear()
        return redirect(url_for('login'))

@app.route('/welcome')
def welcome():
    user = session.get('user')
    token = session.get('token')
    if not user:
        print("Access denied: No user in session. Redirecting to login.")
        return redirect(url_for('login'))
    with get_db_connection() as conn:
        contacts = conn.execute('SELECT id, name, email, phone FROM contacts ORDER BY id DESC').fetchall()
    return render_template('welcome.html', user=user, token=token, contacts=contacts)


@app.route('/contacts/add', methods=['POST'])
def add_contact():
    if not session.get('user'):
        return redirect(url_for('login'))

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()

    if name and email:
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO contacts (name, email, phone) VALUES (?, ?, ?)',
                (name, email, phone)
            )
            conn.commit()

    return redirect(url_for('welcome'))


@app.route('/contacts/edit/<int:contact_id>', methods=['POST'])
def edit_contact(contact_id):
    if not session.get('user'):
        return redirect(url_for('login'))

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()

    if name and email:
        with get_db_connection() as conn:
            conn.execute(
                'UPDATE contacts SET name = ?, email = ?, phone = ? WHERE id = ?',
                (name, email, phone, contact_id)
            )
            conn.commit()

    return redirect(url_for('welcome'))


@app.route('/contacts/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    if not session.get('user'):
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        conn.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
        conn.commit()

    return redirect(url_for('welcome'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists('./flask_session'):
        os.makedirs('./flask_session')
    
    # Run on localhost:7284 to match OIDC registration
    app.run(host='0.0.0.0', port=7284, ssl_context='adhoc', debug=True)
