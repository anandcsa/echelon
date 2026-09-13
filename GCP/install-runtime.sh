#!/usr/bin/env bash
# Run on a fresh Ubuntu 22.04 GPU VM, after uploading game.tar.gz/player.tar.gz.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run as root on the dedicated VM.' >&2; exit 1; }
HOST=${1:?hostname required}
PUBLIC_IP=${2:?public IPv4 required}
[[ "$HOST" =~ ^[a-zA-Z0-9.-]+$ && "$PUBLIC_IP" =~ ^[0-9.]+$ ]] || exit 1
[[ -f game.tar.gz && -f player.tar.gz ]] || { echo 'Missing packaged game/player archives.' >&2; exit 1; }
[[ ! -d /opt/echelon ]] || { echo 'Runtime already exists; inspect before replacing it.' >&2; exit 1; }
export DEBIAN_FRONTEND=noninteractive
apt-get -o DPkg::Lock::Timeout=600 update
# Official signed Ubuntu repository: https://caddyserver.com/docs/install
apt-get -o DPkg::Lock::Timeout=600 install -y ca-certificates curl gnupg debian-keyring debian-archive-keyring apt-transport-https
if [[ ! -f /etc/apt/sources.list.d/caddy-stable.list ]]; then
 curl --fail --silent --show-error --location https://dl.cloudsmith.io/public/caddy/stable/gpg.key | gpg --batch --yes --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
 curl --fail --silent --show-error --location https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt -o /etc/apt/sources.list.d/caddy-stable.list
 chmod 644 /usr/share/keyrings/caddy-stable-archive-keyring.gpg /etc/apt/sources.list.d/caddy-stable.list
 apt-get -o DPkg::Lock::Timeout=600 update
fi
apt-get -o DPkg::Lock::Timeout=600 install -y ca-certificates curl git xz-utils python3 caddy coturn \
 nvidia-driver-570-server libnvidia-encode-570-server libvulkan1 vulkan-tools \
 libgbm1 libx11-6 libxcb1 libasound2 libxkbcommon0 libnss3 \
 libatk1.0-0 libatk-bridge2.0-0 libxcomposite1 libxdamage1 libxrandr2 \
 libdrm2 libcups2 libpango-1.0-0 libcairo2
# Node from the official distribution; verify its archive against official checksums.
NODE_VERSION=22.22.0
node_tmp=$(mktemp -d)
curl --fail --location "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" -o "$node_tmp/node-v${NODE_VERSION}-linux-x64.tar.xz"
curl --fail --location "https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt" -o "$node_tmp/SHASUMS256.txt"
# Match the exact archive (the upstream checksum list includes other platforms).
awk -v name="node-v${NODE_VERSION}-linux-x64.tar.xz" '$2 == name {print}' "$node_tmp/SHASUMS256.txt" > "$node_tmp/selected.sha256"
[[ -s "$node_tmp/selected.sha256" ]]
(cd "$node_tmp" && sha256sum -c selected.sha256)
tar -xJf "$node_tmp/node-v${NODE_VERSION}-linux-x64.tar.xz" -C /usr/local --strip-components=1
rm -rf "$node_tmp"
useradd --system --create-home --home-dir /opt/echelon --shell /usr/sbin/nologin echelon
install -d -o echelon -g echelon /opt/echelon/game /opt/echelon/player
# Archives are produced locally by provision.sh from trusted build output.
tar --no-same-owner -xzf game.tar.gz -C /opt/echelon/game
tar --no-same-owner -xzf player.tar.gz -C /opt/echelon/player
chmod +x /opt/echelon/game/Echelon.sh
find /opt/echelon/game/Echelon/Binaries/Linux -type f -name 'Echelon*' -exec chmod +x '{}' \;
git clone https://github.com/EpicGames/PixelStreamingInfrastructure.git /opt/echelon/infrastructure
git -C /opt/echelon/infrastructure checkout --detach 771b83692a0bd464a6c3b80a0b207aafd7825162
chown -R echelon:echelon /opt/echelon
cd /opt/echelon/infrastructure
runuser -u echelon -- npm ci --ignore-scripts --workspace Common --workspace Signalling --workspace SignallingWebServer --include-workspace-root
runuser -u echelon -- npm run build:cjs --workspace Common
runuser -u echelon -- npm run build:cjs --workspace Signalling
runuser -u echelon -- npm run build --workspace SignallingWebServer
# Generate per-install preview and TURN credentials on the host, never in source/metadata.
export HOST PUBLIC_IP
python3 - <<'PY'
import json, os, secrets, subprocess
from pathlib import Path
host, ip = os.environ['HOST'], os.environ['PUBLIC_IP']
password, turn_password = secrets.token_urlsafe(24), secrets.token_urlsafe(32)
hashed = subprocess.check_output(['caddy', 'hash-password'], input=(password+'\n').encode()).decode().strip()
Path('/root/echelon-preview-login').write_text('Username: echelon\nPassword: '+password+'\n')
Path('/root/echelon-preview-login').chmod(0o600)
Path('/etc/caddy/Caddyfile').write_text(f'''{host} {{
 basic_auth {{
  echelon {hashed}
 }}
 reverse_proxy 127.0.0.1:8080
}}
''')
Path('/etc/turnserver.conf').write_text(f'''listening-port=3478
external-ip={ip}
realm={host}
fingerprint
lt-cred-mech
user=echelon:{turn_password}
min-port=49252
max-port=49351
no-cli
no-multicast-peers
no-tls
no-dtls
user-quota=4
total-quota=8
deny-peer-ip=127.0.0.0-127.255.255.255
deny-peer-ip=10.0.0.0-10.255.255.255
deny-peer-ip=172.16.0.0-172.31.255.255
deny-peer-ip=192.168.0.0-192.168.255.255
deny-peer-ip=169.254.0.0-169.254.255.255
''')
peer = {'iceServers': [{'urls': ['stun:stun.l.google.com:19302']},
    {'urls': [f'turn:{host}:3478?transport=udp', f'turn:{host}:3478?transport=tcp'],
     'username': 'echelon', 'credential': turn_password}]}
config = {'streamer_port': 8888, 'player_port': 8080, 'sfu_port': 8889,
    'max_players': 1, 'serve': True, 'http_root': '/opt/echelon/player', 'homepage': 'index.html',
    'https': False, 'https_redirect': False, 'rest_api': False, 'log_config': False,
    'peer_options_file': '/opt/echelon/infrastructure/SignallingWebServer/peer-options.json'}
p = Path('/opt/echelon/infrastructure/SignallingWebServer/config.json')
p.write_text(json.dumps(config, indent=2)); p.chmod(0o600)
peer_path = p.with_name('peer-options.json')
peer_path.write_text(json.dumps(peer, indent=2)); peer_path.chmod(0o600)
PY
chown echelon:echelon /opt/echelon/infrastructure/SignallingWebServer/config.json /opt/echelon/infrastructure/SignallingWebServer/peer-options.json
chown root:turnserver /etc/turnserver.conf
chmod 640 /etc/turnserver.conf
cat > /etc/systemd/system/echelon-signalling.service <<'UNIT'
[Unit]
Description=Echelon Epic signalling server
After=network-online.target
Wants=network-online.target
[Service]
User=echelon
WorkingDirectory=/opt/echelon/infrastructure/SignallingWebServer
ExecStart=/usr/local/bin/node dist/index.js
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
[Install]
WantedBy=multi-user.target
UNIT
cat > /etc/systemd/system/echelon-game.service <<'UNIT'
[Unit]
Description=Echelon Unreal GPU runtime
After=network-online.target echelon-signalling.service
Wants=echelon-signalling.service
StartLimitIntervalSec=300
StartLimitBurst=3
[Service]
User=echelon
WorkingDirectory=/opt/echelon/game
Environment=SDL_AUDIODRIVER=dummy
ExecStart=/opt/echelon/game/Echelon.sh -RenderOffscreen -AudioMixer -Unattended -PixelStreamingURL=ws://127.0.0.1:8888 -PixelStreamingID=Echelon -ResX=1920 -ResY=1080 -ForceRes -PixelStreamingWebRTCMinPort=49152 -PixelStreamingWebRTCMaxPort=49251 -PixelStreamingWebRTCMaxFps=60 -stdout -FullStdOutLogOutput
Restart=on-failure
RestartSec=15
LimitNOFILE=65536
NoNewPrivileges=true
[Install]
WantedBy=multi-user.target
UNIT
caddy validate --config /etc/caddy/Caddyfile
systemctl daemon-reload
systemctl enable coturn caddy echelon-signalling echelon-game
systemctl restart coturn caddy
systemctl start echelon-signalling
printf 'Runtime installed. Reboot to load NVIDIA driver, then verify GPU, game and browser connection.\n'
