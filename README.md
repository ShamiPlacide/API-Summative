# Wrapify

Wrapify is a containerized **Flask web application** that visualizes your Spotify listening habits using the **Spotify Web API**.
It supports **multi-container deployment with Docker Compose** and includes **HAProxy load balancing** for scalability.

---

## Features
- View your Spotify listening statistics (tracks, artists, habits).
- Secure OAuth authentication with Spotify.
- Containerized for portability using Docker.
- Load-balanced with HAProxy for high availability.
- Easy deployment using Docker Compose.

---

## Architecture

```

\[Client] → \[HAProxy Load Balancer:8082] → \[web-01:80] or \[web-02:80]
(lb-01)                Flask App    Flask App
172.20.0.10            172.20.0.11   172.20.0.12

````

lb working.png

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)
- A [Spotify Developer account](https://developer.spotify.com/dashboard/) to get API credentials

---

## Environment Variables

| Variable                | Description                    | Example                          |
|-------------------------|--------------------------------|----------------------------------|
| `SPOTIFY_CLIENT_ID`     | Your Spotify app client ID     | `abc123def456`                   |
| `SPOTIFY_CLIENT_SECRET` | Your Spotify app client secret | `xyz789uvw000`                   |
| `SPOTIFY_REDIRECT_URI`  | OAuth redirect URI             | `http://localhost:8080/callback` |

---

## Installation & Setup

### Clone & Build Locally
```bash
# Clone or create project directory
mkdir spotify
cd spotify

# Create the required files (wrapify.py, requirements.txt, Dockerfile)

# Pull the Docker image
docker pull shamiplacide/wrapify:v3

---

### Using Docker Compose (Recommended)

```bash
# Set up directory structure
mkdir -p web lb
# Place application files in web/ directory
# Place HAProxy config in lb/ directory

# Build and start all containers
docker compose up -d --build

# Check running containers
docker compose ps

# View logs
docker compose logs
```

---

### Running Individual Containers

#### Web-01

```bash
docker run -d --name web-01 --hostname web-01 \
  --network lablan --ip 172.20.0.11 \
  -p 2211:22 -p 8080:80 \
  -e SPOTIFY_CLIENT_ID=your_client_id \
  -e SPOTIFY_CLIENT_SECRET=your_client_secret \
  -e SPOTIFY_REDIRECT_URI=http://localhost:8080/callback \
  shamiplacide/wrapify:v3
```

#### Web-02

```bash
docker run -d --name web-02 --hostname web-02 \
  --network lablan --ip 172.20.0.12 \
  -p 2212:22 -p 8081:80 \
  -e SPOTIFY_CLIENT_ID=your_client_id \
  -e SPOTIFY_CLIENT_SECRET=your_client_secret \
  -e SPOTIFY_REDIRECT_URI=http://localhost:8081/callback \
  shamiplacide/wrapify:v3
```

---

## Load Balancer (HAProxy)

### Configuration (`/etc/haproxy/haproxy.cfg`)

```haproxy
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
```

### Setup Commands

```bash
# Get into load balancer container
docker exec -it lb-01 /bin/bash

# Install HAProxy
apt update && apt install -y haproxy

# Edit HAProxy config
vim /etc/haproxy/haproxy.cfg

# Restart HAProxy
service haproxy restart
```

---

## Testing

1. **Test individual containers:**

   ```bash
   curl http://localhost:8080
   curl http://localhost:8081
   ```

2. **Test internal connectivity (from lb-01):**

   ```bash
   curl http://web-01:80
   curl http://web-02:80
   ```

3. **Test load balancing:**

   ```bash
   curl -I http://localhost:8082
   curl -I http://localhost:8082
   ```

**Expected Results:**

* Each request should return `HTTP 200`.
* The `X-Served-By` header alternates between `web01` and `web02`.

---

## Project Structure

```
spotify/
├── docker-compose.yml
├── web/
│   ├── Dockerfile
│   ├── wrapify.py
│   └── requirements.txt
└── lb/
    └── Dockerfile
```

---

## Resources

* [Spotify Web API](https://developer.spotify.com/documentation/web-api)

---
