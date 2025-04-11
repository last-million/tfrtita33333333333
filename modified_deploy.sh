#!/bin/bash
set -e

# -----------------------------------------------------------
# CONFIGURATION VARIABLES
# -----------------------------------------------------------
DOMAIN="ajingolik.fun"
EMAIL="hamzameliani1@gmail.com"
# --- IMPORTANT: SET MYSQL ROOT PASSWORD HERE ---
MYSQL_ROOT_PASSWORD="your_secure_mysql_root_password" # !!! CHANGE THIS !!!
# --- Application DB Credentials (MUST MATCH .env file) ---
APP_DB_NAME="tfrtita_db"
APP_DB_USER="tfrtita"
APP_DB_PASSWORD="AFINasahbi@11"

# --- Paths ---
# Assuming this script is run from the cloned repository root /root/tfrtita33333333333
APP_DIR="/root/tfrtita33333333333" # Use absolute path
BACKEND_DIR="${APP_DIR}/backend"
FRONTEND_DIR="${APP_DIR}/frontend"
WEB_ROOT="/var/www/${DOMAIN}/html"
SERVICE_FILE="/etc/systemd/system/tfrtita333.service"
VENV_DIR="${APP_DIR}/venv"

# -----------------------------------------------------------
# Logging helper
# -----------------------------------------------------------
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# -----------------------------------------------------------
# I. SYSTEM PREPARATION
# -----------------------------------------------------------
log "Updating system packages..."
sudo apt update && sudo apt upgrade -y

log "Installing required packages..."
# Added ffmpeg, mysql-server. Removed expect.
sudo apt install -y nginx certbot python3-certbot-nginx ufw git python3 python3-pip python3-venv libyaml-dev nodejs dos2unix ffmpeg mysql-server

# Convert this script to Unix line endings (if needed)
dos2unix "${APP_DIR}/modified_deploy.sh"

# --- MySQL Setup ---
log "Configuring MySQL Server..."
# Set root password non-interactively using debconf (Requires MYSQL_ROOT_PASSWORD to be set above)
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password password ${MYSQL_ROOT_PASSWORD}"
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password_again password ${MYSQL_ROOT_PASSWORD}"
# Re-install might be needed to apply debconf settings if MySQL was already partially installed
sudo apt install -y mysql-server

log "Creating MySQL database '${APP_DB_NAME}' and user '${APP_DB_USER}'..."
# Use non-interactive MySQL commands with the root password variable
sudo mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE DATABASE IF NOT EXISTS ${APP_DB_NAME};" || log "Failed to create database (maybe check root password?)"
sudo mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER IF NOT EXISTS '${APP_DB_USER}'@'localhost' IDENTIFIED BY '${APP_DB_PASSWORD}';" || log "Failed to create user (maybe check root password?)"
# If the user already exists, update the password instead
sudo mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -e "ALTER USER '${APP_DB_USER}'@'localhost' IDENTIFIED BY '${APP_DB_PASSWORD}';" || log "Failed to alter user (maybe check root password?)"
sudo mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON ${APP_DB_NAME}.* TO '${APP_DB_USER}'@'localhost';" || log "Failed to grant privileges (maybe check root password?)"
sudo mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -e "FLUSH PRIVILEGES;" || log "Failed to flush privileges (maybe check root password?)"
log "MySQL user and database setup attempted."
# --- End MySQL Setup ---

log "Configuring UFW firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full' # Use profile name
sudo ufw allow 8000/tcp # Allow backend port just in case
sudo ufw allow 3306/tcp # Allow MySQL port
sudo ufw --force enable
sudo ufw status verbose

# -----------------------------------------------------------
# II. APPLICATION SETUP
# -----------------------------------------------------------
log "Setting up the application environment in ${APP_DIR}..."

# Create and activate Python virtual environment
if [ ! -d "${VENV_DIR}" ]; then
  log "Creating Python virtual environment..."
  python3 -m venv "${VENV_DIR}"
fi
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip setuptools wheel cython

# -----------------------------------------------------------
# II.A. BACKEND SETUP
# -----------------------------------------------------------
log "Installing backend dependencies..."
cd "${BACKEND_DIR}"
# Ensure .env file exists before proceeding (should be transferred manually)
if [ ! -f "${BACKEND_DIR}/.env" ]; then
    log "ERROR: backend/.env file not found. Please create and transfer it with correct credentials."
    exit 1
fi
pip install -r requirements.txt # Use relative path now that we are in BACKEND_DIR

log "Initializing database (creating tables)..."
# Ensure MySQL service is running
sudo systemctl status mysql.service || log "Warning: MySQL service might not be running."
# Run the database script using the venv python
"${VENV_DIR}/bin/python3" -m app.database || log "Database initialization failed; please check MySQL logs and app logs."
# Deactivate venv after use in this section
deactivate

# -----------------------------------------------------------
# II.B. FRONTEND SETUP
# -----------------------------------------------------------
log "Building frontend..."
cd "${FRONTEND_DIR}"
npm install
npm run build

log "Deploying frontend files to ${WEB_ROOT}..."
sudo mkdir -p "${WEB_ROOT}"
sudo rm -rf "${WEB_ROOT:?}"/*
sudo cp -r dist/* "${WEB_ROOT}/"

# -----------------------------------------------------------
# III. CREATE SYSTEMD SERVICE FOR BACKEND
# -----------------------------------------------------------
log "Creating systemd service for backend..."
# Use explicit paths and EnvironmentFile
sudo tee ${SERVICE_FILE} > /dev/null <<EOF
[Unit]
Description=Tfrtita333 App Backend
After=network.target mysql.service # Ensure MySQL is started first

[Service]
User=root
WorkingDirectory=${BACKEND_DIR}
# Using Gunicorn command with absolute paths and 1 worker (adjust worker count for production)
ExecStart=${VENV_DIR}/bin/gunicorn -k uvicorn.workers.UvicornWorker -w 1 --bind 127.0.0.1:8080 app.main:app
Restart=always
# Redirect stdout and stderr to files for debugging
StandardOutput=file:/tmp/tfrtita333.stdout.log
StandardError=file:/tmp/tfrtita333.stderr.log
# Trying Environment variables directly AGAIN - ensure values are EXACTLY correct
# EnvironmentFile=${BACKEND_DIR}/.env # Commenting out EnvFile
Environment="PYTHONPATH=${BACKEND_DIR}"
Environment="DB_HOST=127.0.0.1"
Environment="DB_PORT=3306"
Environment="DB_USER=tfrtita"
Environment="DB_PASSWORD=AFINasahbi@11"
Environment="DB_NAME=tfrtita_db"
Environment="ULTRAVOX_API_KEY=vHUZrWdv.JAv2gzEM5Hf0LK56AajdAxjEYLMoIIOs"
Environment="TWILIO_ACCOUNT_SID=AC5a54e08142781af4e3762e1f12ecb24a"
Environment="TWILIO_AUTH_TOKEN=2c7995567077fedbc9701ff69afcc6ba"
Environment="TWILIO_FROM_NUMBER=+12762761877"
Environment="BASE_URL=https://ajingolik.fun"
# Add other required env vars from .env here if needed (e.g., Google, Supabase)
Environment="SUPABASE_URL=https://ahhsydchxwvassjbwvow.supabase.co"
Environment="SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFoaHN5ZGNoeHd2YXNzamJ3dm93Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzczMTA3ODMsImV4cCI6MjA1Mjg4Njc4M30.Zu7VADzlFTezQj2qydiAFvFcIUkLdPStfxzaXwRXxzw"
Environment="GOOGLE_CLIENT_ID=539634127336-nrin2lgnd455l4qgp4qcqfbsl7vm7vvv.apps.googleusercontent.com"
Environment="GOOGLE_CLIENT_SECRET=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"
# Add AIRTABLE_API_KEY if needed by config.py (even if empty)
Environment="AIRTABLE_API_KEY="

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable tfrtita333.service
# Restart is handled in the final step

# -----------------------------------------------------------
# IV. NGINX CONFIGURATION & SSL SETUP
# -----------------------------------------------------------
log "Configuring Nginx for ${DOMAIN}..."
NGINX_CONF="/etc/nginx/sites-available/${DOMAIN}"
sudo tee ${NGINX_CONF} > /dev/null <<EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    # ACME challenge & Static files
    location /.well-known/acme-challenge/ { allow all; root ${WEB_ROOT}; }
    location / { try_files \$uri \$uri/ /index.html; root ${WEB_ROOT}; }

    # Proxy API requests
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    # Add WebSocket proxying if needed for /media-stream (adjust path if necessary)
    location /media-stream {
        proxy_pass http://127.0.0.1:8080/media-stream; # Assuming backend handles WS on same port
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400; # Long timeout for persistent connection
    }
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN} www.${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security Headers (Optional but recommended)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    location /.well-known/acme-challenge/ { allow all; root ${WEB_ROOT}; }
    location / { try_files \$uri \$uri/ /index.html; root ${WEB_ROOT}; }

    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    # Add WebSocket proxying for SSL
    location /media-stream {
        proxy_pass http://127.0.0.1:8080/media-stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}
EOF

log "Enabling Nginx configuration..."
sudo ln -sf ${NGINX_CONF} /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# -----------------------------------------------------------
# V. OBTAIN SSL CERTIFICATE WITH CERTBOT
# -----------------------------------------------------------
log "Waiting for any running Certbot instance to finish..."
while pgrep -x certbot >/dev/null; do
    log "Certbot is already running. Waiting 10 seconds..."
    sleep 10
done

log "Obtaining/Renewing SSL certificate via Certbot..."
# Added --expand flag
sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos --email ${EMAIL} --expand --deploy-hook "systemctl reload nginx"

# -----------------------------------------------------------
# VI. FINAL RESTART OF SERVICES
# -----------------------------------------------------------
log "Restarting Nginx and backend service..."
# Nginx should have been reloaded by certbot hook, but restart just in case
sudo systemctl restart nginx
sudo systemctl restart tfrtita333.service

log "Deployment complete. Your site should be available at: https://${DOMAIN}"
log "Check backend service status with: systemctl status tfrtita333.service"
log "Check backend logs with: cat /tmp/tfrtita333.stderr.log"
