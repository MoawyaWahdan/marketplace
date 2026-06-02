<h1>Marketplace</h1>

<h2>Live Demo</h2>

<p>
https://marketplace-1lnf.onrender.com/
</p>

<h2>Project Overview</h2>

<p>
Backend-focused marketplace application built using FastAPI.
The project demonstrates backend API development, authentication,
database design, CRUD operations, and cloud-based image storage.

Users can register, authenticate using JWT tokens,
create marketplace listings, upload listing images,
and browse available products through a lightweight frontend interface.
</p>

<h2>Backend Technology</h2>

<ul>
  <li>FastAPI</li>
  <li>Python</li>
  <li>PostgreSQL (migrated from SQLite)</li>
  <li>SQLAlchemy ORM</li>
  <li>JWT Authentication</li>
</ul>

<h2>Cloud & Storage</h2>

<ul>
  <li>Amazon S3 (image upload, retrieval, deletion)</li>
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
  <li>Create, update, and delete marketplace listings</li>
  <li>Upload and manage listing images</li>
  <li>Browse marketplace listings</li>
  <li>Secure password hashing</li>
  <li>RESTful API endpoints</li>
  <li>Cloud-based image storage with S3</li>
</ul>

<h2>API Documentation</h2>

<p>Swagger UI:</p>

<pre>
Local:
http://127.0.0.1:8000/docs

Deployed:
https://marketplace-1lnf.onrender.com/docs
</pre>

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
touch .env

SECRET_KEY=your_generated_secret_key
DATABASE_URL=your_postgres_url
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-2
S3_BUCKET_NAME=your_bucket_name
</pre>

<h3>5. Run the application</h3>

<pre>
./run.sh
</pre>

<h3>6. Access the application</h3>

<pre>
http://127.0.0.1:8000/
</pre>

<h2>Run Tests</h2>

<pre>
pytest
</pre>

<h2>Notes</h2>

<ul>
  <li>You must create an account before adding listings.</li>
</ul>