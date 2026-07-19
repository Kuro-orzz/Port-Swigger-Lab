#!/usr/bin/env bash
# scan.sh — map IP Cloudflare → colo cho MỘT domain mục tiêu
set -euo pipefail

D=${1:?Example: bash scan.sh viblo.asia}
SAMPLE_PER_CIDR=${2:-100}
SENDERS=${3:-100}
RATELIMIT=${4:-200}
OUT=out-$D.json

command -v prips >/dev/null || { echo "sudo apt install -y prips"; exit 1; }

curl -s https://www.cloudflare.com/ips-v4 -o cf.txt; echo >> cf.txt

: > "$OUT"
while read -r cidr; do
  [ -z "$cidr" ] && continue
  prips "$cidr" | shuf -n "$SAMPLE_PER_CIDR" | sed "s/\$/,$D/" > targets.csv
  echo "== $cidr → $(wc -l < targets.csv) IP =="
  ~/zgrab2/zgrab2 http --port 80 --endpoint /cdn-cgi/trace \
    --connect-timeout 5s -t 15s \
    --senders "$SENDERS" --server-rate-limit "$RATELIMIT" \
    -f targets.csv >> "$OUT" 2>/dev/null
done < cf.txt

# Extract IP + colo from /cdn-cgi/trace response
jq -r '
  select(.data.http.status=="success")
  | .ip as $ip
  | (.data.http.result.response.body // "" | capture("colo=(?<c>[A-Z]+)").c) as $colo
  | select($colo != null) | [$ip, $colo] | @tsv
' "$OUT" > map-$D.tsv

echo
echo "== Phân bố colo cho $D =="
awk '{print $2}' map-$D.tsv | sort | uniq -c | sort -rn
echo
echo "== Mỗi colo 1 IP (định dạng như bài research) =="
awk '!x[$2]++ {printf "%-18s %s\n", $1, $2}' map-$D.tsv | tee reps-$D.tsv