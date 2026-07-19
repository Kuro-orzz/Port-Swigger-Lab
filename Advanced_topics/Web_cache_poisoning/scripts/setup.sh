#!/usr/bin/env bash
# setup.sh — cài môi trường cho scan.sh trên Ubuntu mới
set -euo pipefail

sudo apt-get update
sudo apt-get install -y git curl jq prips dnsutils build-essential golang-go

cd ~
if [ ! -d zgrab2 ]; then
  git clone https://github.com/zmap/zgrab2.git
fi
cd zgrab2
make

echo '104.21.6.150,viblo.asia' | ~/zgrab2/zgrab2 http --port 80 --endpoint /cdn-cgi/trace | jq -r .data.http.status