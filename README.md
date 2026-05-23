<h1>Marketplace</h1>

<h2>Project Overview</h2>

<p>
This is a backend-focused marketplace application built using FastAPI.
It provides user authentication, product listing management, and browsing functionality.
The system demonstrates clean backend architecture with database integration,
JWT-based authentication, and environment-based configuration.
</p>

<h2>Backend Technology</h2>

<ul>
  <li>FastAPI</li>
  <li>Python</li>
</ul>

<h2>Frontend Technology</h2>

<ul>
  <li>HTML</li>
  <li>CSS</li>
  <li>JavaScript</li>
</ul>

<h2>Features</h2>

<ul>
  <li>User registration and authentication (JWT-based)</li>
  <li>Create, update, and delete product listings</li>
  <li>Browse marketplace listings</li>
  <li>Secure password hashing</li>

</ul>

<h2>Instructions to Run (Tested on Ubuntu)</h2>

<h3>1. Clone the repository</h3>

<pre>
git clone repo_url
cd marketplace
</pre>

<h3>2. Create virtual environment and activate it</h3>

<pre>
python3 -m venv .venv
source .venv/bin/activate
</pre>

<h3>3. Install dependencies</h3>

<pre>
pip install -r requirements.txt
</pre>

<h3>4. Create environment variables</h3>

<pre>
Create a .env file in the root directory:

touch .env

Generate a secret key:

openssl rand -hex 32

Add it to .env:

SECRET_KEY=your_generated_secret_key
</pre>

<h3>5. Run the application</h3>

<pre>
./run.sh
</pre>

<h3>6. Access the application</h3>

<p>
Open in browser:
</p>

<pre>
http://127.0.0.1:8000/static/login.html
</pre>

<h2>Testing</h2>

<pre>
pytest
</pre>

<h2>Notes</h2>

<ul>
  <li>The database starts empty.</li>
  <li>You must create an account before adding listings.</li>
</ul>
