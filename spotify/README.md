# Wrapify

A containerized Flask web application that displays users' Spotify listening habits using the Spotify Web API, deployed with Docker Compose and load balancing.
Image Details
* Docker Hub Repository: shamiplacide/wrapify
* Image Name: shamiplacide/wrapify
* Tags:
    * v1 - Initial release
    * v3 - Latest stable version
Build Instructions
Local Build
# Clone or create project directory
mkdir spotify
cd spotify

# Create the required files (wrapify.py, requirements.txt, Dockerfile)
# Build the Docker image
docker build -t shamiplacide/wrapify:v3 .

# Tag as latest
docker tag shamiplacide/wrapify:v3 shamiplacide/wrapify:v3

# Push to Docker Hub
docker login
docker push shamiplacide/wrapify:v3
docker push shamiplacide/wrapify:v3
Docker Compose Build
# Set up directory structure
mkdir -p web lb
# Place application files in web/ directory
# Place HAProxy config in lb/ directory

# Build and deploy entire infrastructure
docker compose up --build -d
Run Instructions
Docker Compose Method (Recommended)
The application uses Docker Compose to orchestrate multiple containers:
# Start all services
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs
Individual Container Method
For web-01 and web-02 containers:
# Web-01
docker run -d --name web-01 --hostname web-01 \
  --network lablan --ip 172.20.0.11 \
  -p 2211:22 -p 8080:80 \
  -e SPOTIFY_CLIENT_ID=your_client_id \
  -e SPOTIFY_CLIENT_SECRET=your_client_secret \
  -e SPOTIFY_REDIRECT_URI=http://localhost:8080/callback \
  shamiplacide/wrapify:v3

# Web-02
docker run -d --name web-02 --hostname web-02 \
  --network lablan --ip 172.20.0.12 \
  -p 2212:22 -p 8081:80 \
  -e SPOTIFY_CLIENT_ID=your_client_id \
  -e SPOTIFY_CLIENT_SECRET=your_client_secret \
  -e SPOTIFY_REDIRECT_URI=http://localhost:8081/callback \
  shamiplacide/wrapify:v3
Environment Variables
* SPOTIFY_CLIENT_ID: Your Spotify app client ID
* SPOTIFY_CLIENT_SECRET: Your Spotify app client secret
* SPOTIFY_REDIRECT_URI: OAuth callback URL
* PORT: Application port (default: 80)
Load Balancer Configuration
HAProxy Configuration
The load balancer (lb-01) uses HAProxy with the following configuration in /etc/haproxy/haproxy.cfg:
global
    daemon
    maxconn 256

defaults
    mode http
    timeout connect 5s
    timeout client  50s
    timeout server  50s

frontend http-in
    bind *:8082
    default_backend servers

backend servers
    balance roundrobin
    server web01 172.20.0.11:80 check
    server web02 172.20.0.12:80 check
    http-response set-header X-Served-By web01 if { srv_id 1 }
    http-response set-header X-Served-By web02 if { srv_id 2 }
HAProxy Setup Commands
# SSH into load balancer container
Docker exec -it lb-01 /bin/bash

# Install HAProxy
sudo apt update && sudo apt install -y haproxy

# Create configuration file (content above)
sudo vim /etc/haproxy/haproxy.cfg

# Reload HAProxy (if needed)
sudo service haproxy restart

Testing Steps & Evidence
1. Individual Container Testing
# Test web-01 directly
curl http://localhost:8080

# Test web-02 directly
curl http://localhost:8081
2. Internal Network Testing
# From inside lb-01 container
Docker exec -it lb-01 /bin/bash

# Test internal connectivity
curl http://web-01:80
curl http://web-02:80
3. Load Balancer Testing
# Test load balancing multiple times
curl -I http://localhost:8082
curl -I http://localhost:8082
curl -I http://localhost:8082
curl -I http://localhost:8082
Expected Results
* Each request should return HTTP 200
* The X-Served-By header should alternate between web01 and web02
* Both containers should receive requests in round-robin fashion
Evidence of Load Balancing
$ curl -I http://localhost:8082
HTTP/1.1 200 OK
X-Served-By: web01
Content-Type: text/html; charset=utf-8

$ curl -I http://localhost:8082
HTTP/1.1 200 OK
X-Served-By: web02
Content-Type: text/html; charset=utf-8
Architecture
[Client] → [HAProxy Load Balancer:8082] → [web-01:80] or [web-02:80]
                     (lb-01)                Flask App    Flask App
                  172.20.0.10            172.20.0.11   172.20.0.12

Project Structure
spotify/
├── docker-compose.yml
├── web/
│   ├── Dockerfile
│   ├── wrapify.py
│   └── requirements.txt
└── lb/
    └── Dockerfile


# Spotify web API link
https://developer.spotify.com/documentation/web-api
