#!/bin/bash
set -e

# -----------------------------------------------------------
# CONFIGURATION VARIABLES
# -----------------------------------------------------------
DOMAIN="ajingolik.fun"
EMAIL="hamzameliani1@gmail.com"

# Absolute paths (assumes deploy.sh is in the repository root)
APP_DIR="$(pwd)"
BACKEND_DIR="${APP_DIR}/backend"
FRONTEND_DIR="${APP_DIR}/frontend"
WEB_ROOT="/var/www/${DOMAIN}/html"
SERVICE_FILE="/etc/systemd/system/tfrtita333.service"

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

log "Installing required packages (nginx, certbot, ufw, git, python3, nodejs, etc.)..."
# Also install dos2unix to fix any potential CRLF issues.
# Removed mysql-server and expect from this list, will be installed manually
sudo apt install -y nginx certbot python3-certbot-nginx ufw git python3 python3-pip python3-venv libyaml-dev nodejs dos2unix

# Convert deploy.sh to Unix line endings (if needed)
dos2unix deploy.sh

# --- MySQL Setup Removed ---
# MySQL installation and user/database creation should be done manually BEFORE running this script.
# --- End MySQL Setup Removed ---


log "Configuring UFW firewall..."
sudo ufw allow OpenSSH
sudo ufw allow "Nginx Full"
sudo ufw allow 8000
sudo ufw --force enable
sudo ufw status

# -----------------------------------------------------------
# (Optional) 4.3 IPtables RULES
# -----------------------------------------------------------
log "Configuring iptables rules (optional)..."
sudo tee /etc/iptables/rules.v4 > /dev/null <<'EOF'
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
# Allow established connections
-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
# Allow loopback interface
-A INPUT -i lo -j ACCEPT
# Allow SSH (port 22)
-A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
# Allow HTTP (port 80)
-A INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
# Allow HTTPS (port 443)
-A INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
# Allow additional port (e.g., 8000)
-A INPUT -p tcp -m state --state NEW -m tcp --dport 8000 -j ACCEPT
# Drop all other incoming traffic
-A INPUT -j DROP
COMMIT
EOF

sudo iptables-restore < /etc/iptables/rules.v4

# -----------------------------------------------------------
# II. APPLICATION SETUP
# -----------------------------------------------------------
log "Setting up the application environment in ${APP_DIR}..."

# (Optional) Clean previous deployment folders:
# rm -rf "${APP_DIR}/venv"
# sudo rm -rf "${WEB_ROOT}"

# Create and activate Python virtual environment for the backend
if [ ! -d "${APP_DIR}/venv" ]; then
  log "Creating Python virtual environment..."
  python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip setuptools wheel cython

# -----------------------------------------------------------
# II.A. BACKEND SETUP
# -----------------------------------------------------------
log "Installing backend dependencies..."
cd "${BACKEND_DIR}"
# Use an absolute path to the requirements file
pip install -r "${BACKEND_DIR}/requirements.txt"

log "Initializing database (creating tables)..."
# This now connects to MySQL and creates tables using the mysql.connector setup
# Ensure MySQL service is running before this step (systemd usually handles this)
sudo systemctl status mysql.service # Optional: check status
python3 -m app.database || log "Database initialization failed; please check MySQL logs (/var/log/mysql/error.log) and app logs."

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
sudo tee ${SERVICE_FILE} > /dev/null <<EOF
[Unit]
Description=Tfrtita333 App Backend
After=network.target

[Service]
User=root
WorkingDirectory=${BACKEND_DIR}
# Removed EnvironmentFile for debugging
# Restoring Gunicorn command with absolute paths and 1 worker
ExecStart=/root/tfrtita33333333333/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker -w 1 --bind 127.0.0.1:8080 app.main:app
Restart=always
# Redirect stdout and stderr to files for debugging
StandardOutput=file:/tmp/tfrtita333.stdout.log
StandardError=file:/tmp/tfrtita333.stderr.log
# Reverting to EnvironmentFile to load from .env
EnvironmentFile=${BACKEND_DIR}/.env
# Keep PYTHONPATH separate just in case
Environment="PYTHONPATH=${BACKEND_DIR}"

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable tfrtita333.service
sudo systemctl restart tfrtita333.service

# -----------------------------------------------------------
# IV. NGINX CONFIGURATION & SSL SETUP
# -----------------------------------------------------------
log "Configuring Nginx for ${DOMAIN}..."
NGINX_CONF="/etc/nginx/sites-available/${DOMAIN}"
sudo tee ${NGINX_CONF} > /dev/null <<EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    # ACME challenge for Certbot
    location /.well-known/acme-challenge/ {
        root ${WEB_ROOT};
    }

    # Proxy API requests to backend (adjust if your API routes differ)
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Serve static frontend files
    location / {
        root ${WEB_ROOT};
        try_files \$uri \$uri/ /index.html;
    }
}

server {
    listen 443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location /.well-known/acme-challenge/ {
        root ${WEB_ROOT};
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location / {
        root ${WEB_ROOT};
        try_files \$uri \$uri/ /index.html;
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

log "Obtaining SSL certificate via Certbot..."
# Added --expand flag to handle existing certificates
sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos --email ${EMAIL} --expand

# -----------------------------------------------------------
# VI. FINAL RESTART OF SERVICES
# -----------------------------------------------------------
log "Restarting Nginx and backend service..."
sudo systemctl restart nginx
sudo systemctl restart tfrtita333.service

log "Deployment complete. Your site is available at: https://${DOMAIN}"
