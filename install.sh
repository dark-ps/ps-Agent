#!/bin/sh
# ══════════════════════════════════════════════════════════════════════
#   DarkPs installer — POSIX sh, pi-style
#
#       curl -fsSL <url>/install.sh | sh      ← installs right away
#       sh install.sh                          ← same, from a copy
#       install.sh --uninstall                 ← remove everything
#
#   Colored. Single-frame animated pixel logo (cursor-home redraw).
#   The archive digest is embedded below — no sidecar round-trip.
# ══════════════════════════════════════════════════════════════════════

DP_VER="4.0"
DP_URL_DEFAULT="__DARKPS_URL__"
DP_URL="${DARKPS_URL:-$DP_URL_DEFAULT}"
DP_SHA="__DARKPS_SHA__"
# agent must NOT live in ~/.darkps — main.py wipes that path on boot.
# XDG-style install root survives; ~/.darkps stays the agent's own data dir.
DP_BASE="$HOME/.local/share/darkps"
DP_AGENT="$DP_BASE/agent"
DP_ARCHIVE="$DP_BASE/agent.tar.gz"
DP_LOG="$DP_BASE/install.log"

# ── platform ──────────────────────────────────────────────────────────
DP_TERMUX=0
case "${TERMUX_VERSION:-}" in ?*) DP_TERMUX=1 ;; esac
if [ "$DP_TERMUX" = 1 ]; then
    DP_BIN_DIR="${TERMUX_PREFIX:-/data/data/com.termux/files/usr}/bin"
else
    DP_BIN_DIR="$HOME/.local/bin"
fi

# ── tty + palette ═════════════════════════════════════════════════════
dp_can_tty() { ( : < /dev/tty ) 2>/dev/null; }

DP_COLOR=0
if [ -t 1 ] || [ -t 2 ] || dp_can_tty; then
    case "${TERM:-}" in ""|dumb) : ;; *) [ -z "${NO_COLOR:-}" ] && DP_COLOR=1 ;; esac
fi
if [ "$DP_COLOR" = 1 ]; then
    DP_E=$(printf '\033')
    DP_R="$DP_E[0m";  DP_DIM="$DP_E[90m"; DP_BOLD="$DP_E[1m"
    DP_OK="$DP_E[32m"; DP_BAD="$DP_E[31m"; DP_ACC="$DP_E[96m"; DP_W="$DP_E[97m"
else
    DP_E=""; DP_R=""; DP_DIM=""; DP_BOLD=""; DP_OK=""; DP_BAD=""; DP_ACC=""; DP_W=""
fi
DP_TICK="$DP_OK$(printf '\342\234\223')$DP_R"          # ✓

fail(){ printf '\n  %serror:%s %s\n\n' "$DP_BAD" "$DP_R" "$1" >&2; exit 1; }

# ── task lines: colored in-place replace, plain ✓ lines otherwise ─────
dp_run(){ [ "$DP_COLOR" = 1 ] || return 0; printf '\033[2K\r  %s %s' "$DP_ACC>$DP_R" "$1"; }
ok()   { [ "$DP_COLOR" = 1 ] && printf '\033[2K\r'; printf '  %s %s\n' "$DP_TICK" "$1"; }

# ── logo: pixel PS, top-down reveal + blink, one screen region ────────
DP_GLYPH="###### .####.
##  ## ##....
###### ##....
##.... .####.
##.... ....##
##.... ##..##
##.... .####."
DP_WGlyph=13                                            # columns in the grid

dp_rows() {                                             # $1 lit rows, $2 accent
    printf '%s\n' "$DP_GLYPH" | {
        row=0
        while IFS= read -r dp_line; do
            row=$((row + 1))
            col=0
            out=""
            while [ $col -lt $DP_WGlyph ]; do
                col=$((col + 1))
                ch="$(printf '%s' "$dp_line" | cut -c "$col")"
                if [ "$ch" = "#" ]; then
                    if [ $col -ge 8 ]; then
                        out="$out$DP_ACC██$DP_R"
                    elif [ $row -le "$1" ]; then
                        out="$out$DP_W██$DP_R"
                    else
                        out="$out  "
                    fi
                else
                    out="$out  "
                fi
            done
            printf '  %s%s\n' "$out" "$DP_R"
        done
    }
}

dp_logo() {
    if [ "$DP_COLOR" = 0 ] || [ "${TERM:-}" = "dumb" ] || [ "${DARKPS_NO_ANIM:-}" = "1" ]; then
        dp_rows 99 acc
        printf '\n\n'
        return 0
    fi
    printf '%s%s' "$DP_E[?25l" "$DP_E[2J$DP_E[H"      # one clear; frames overwrite
    trap 'printf "%s%s\n" "$DP_R" "$DP_E[?25h"; trap - INT TERM; exit 130' INT TERM
    n=0
    while [ $n -le 7 ]; do
        printf '%s' "$DP_E[H"
        dp_rows "$n" no
        n=$((n + 1))
        sleep 0.05 2>/dev/null
    done
    printf '%s' "$DP_E[H"; dp_rows 99 acc
    sleep 0.35
    printf '%s' "$DP_E[H"; dp_rows -1 no              # blink
    sleep 0.07
    printf '%s' "$DP_E[H"; dp_rows 99 acc
    printf '\n\n'
    printf '%s%s' "$DP_R" "$DP_E[?25h"
    trap - INT TERM
}

# ── discovery ─────────────────────────────────────────────────────────
dp_has()    { command -v "$1" >/dev/null 2>&1; }
dp_python() {
    if dp_has python3; then echo python3; return 0; fi
    if dp_has python;  then echo python;  return 0; fi
    return 1
}
dp_fetch() {                                            # url dest
    if dp_has curl; then curl -fsSL "$1" -o "$2"; return $?; fi
    if dp_has wget; then wget -q  "$1" -O "$2";   return $?; fi
    return 127
}
dp_sha() {                                              # file → hex hash
    if dp_has sha256sum; then sha256sum "$1" | cut -d' ' -f1 | tr -d '\r'
    elif dp_has shasum;   then shasum -a 256 "$1" | cut -d' ' -f1 | tr -d '\r'
    else echo ""; fi
}

dp_checks() {
    if _p="$(dp_python 2>/dev/null)"; then
        v="$("$_p" -c 'import sys;print("%d.%d.%d"%sys.version_info[:3])' 2>/dev/null)"
        ok "python $v"
    else
        printf '  %sx python not found%s\n' "$DP_BAD" "$DP_R"
        say="    "
        printf '%s\n' "    ${DP_DIM}fix:${DP_R}   ${DP_ACC}pkg install python${DP_R}   ${DP_DIM}(Termux)${DP_R}"
        printf '%s\n' "    ${DP_DIM}or:${DP_R}    ${DP_ACC}apt install python3${DP_R} ${DP_DIM}(Debian/Ubuntu)${DP_R}"
        fail "python is required"
    fi
    dp_has tar          && ok "tar"      || fail "tar not found — pkg install tar"
    { dp_has curl || dp_has wget; } && ok "https fetch" || fail "curl/wget missing — pkg install curl"
}

# ── payload ───────────────────────────────────────────────────────────
dp_have_local() { [ -f "$PWD/main.py" ] && [ -d "$PWD/ps" ]; }

dp_get_archive() {
    mkdir -p "$DP_BASE"
    if dp_have_local; then
        dp_run "packing local agent files"
        tar -czf "$DP_ARCHIVE.tmp" \
            --exclude=.git --exclude=.venv --exclude=__pycache__ \
            --exclude='*.pyc' --exclude='*.log' \
            --exclude=Logos --exclude=Projects \
            -C "$PWD" . 2>/dev/null || fail "packaging failed"
        mv "$DP_ARCHIVE.tmp" "$DP_ARCHIVE"
        ok "agent files (local copy)"
        return 0
    fi
    [ -n "$DP_URL" ] || fail "no local agent files here and DARKPS_URL is not set"
    dp_run "downloading agent"
    dp_fetch "$DP_URL/agent.tar.gz" "$DP_ARCHIVE.tmp" \
        || fail "download failed — check the url / connection"
    mv "$DP_ARCHIVE.tmp" "$DP_ARCHIVE"
    kb=$(( $(wc -c < "$DP_ARCHIVE") / 1024 ))
    if [ -n "$DP_SHA" ]; then
        got="$(dp_sha "$DP_ARCHIVE")"
        if [ -n "$got" ]; then
            want="$(printf '%s' "$DP_SHA" | tr -cd '0-9a-f')"
            if [ "$got" != "$want" ]; then
                ok "agent ($kb KB)"
                printf '  %schecksum retry%s\n' "$DP_BAD" "$DP_R" >&2
                dp_fetch "$DP_URL/agent.tar.gz" "$DP_ARCHIVE.tmp" \
                    || fail "download failed on retry"
                mv "$DP_ARCHIVE.tmp" "$DP_ARCHIVE"
                got="$(dp_sha "$DP_ARCHIVE")"
                [ "$got" = "$want" ] || fail "checksum mismatch — download corrupted, run the command again"
            fi
            ok "agent ($kb KB, checksum verified)"
            return 0
        fi
    fi
    ok "agent ($kb KB)"
}

dp_extract() {
    dp_run "extracting"
    rm -rf "${DP_AGENT:?}"                                    # clean old version
    mkdir -p "$DP_AGENT"
    if ! tar -xzf "$DP_ARCHIVE" -C "$DP_AGENT" 2>>"$DP_LOG"; then
        dp_run "tar failed — trying python extractor"
        "$(dp_python)" -c \
            "import tarfile; tarfile.open(r'$DP_ARCHIVE', 'r:gz').extractall(r'$DP_AGENT')" \
            >>"$DP_LOG" 2>&1 || true
    fi
    if [ ! -f "$DP_AGENT/main.py" ] || [ ! -d "$DP_AGENT/ps" ] \
        || [ ! -f "$DP_AGENT/bin/darkps" ]; then
        # tar dropped members — python's own extractor is the reliable path
        dp_run "incomplete — retrying with python extractor"
        rm -rf "${DP_AGENT:?}"; mkdir -p "$DP_AGENT"
        "$(dp_python)" -c \
            "import tarfile; tarfile.open(r'$DP_ARCHIVE', 'r:gz').extractall(r'$DP_AGENT')" \
            >>"$DP_LOG" 2>&1 || true
    fi
    if [ ! -f "$DP_AGENT/main.py" ] || [ ! -d "$DP_AGENT/ps" ] \
        || [ ! -f "$DP_AGENT/bin/darkps" ]; then
        fail "extraction incomplete — see $DP_LOG"
    fi
    ok "agent files (fresh install, old removed)"
}

# ── native deps: Termux ships them via pkg (pip builds fail there) ────
DP_NATIVES="pillow psutil cryptography"

dp_termux_pkg_missing() {                               # → space list
    _miss=""
    for p in $1; do
        dpkg -s "python-$p" >/dev/null 2>&1 || _miss="$_miss $p"
    done
    echo "${_miss# }"
}

dp_native_deps() {
    if [ "$DP_TERMUX" = 1 ]; then
        _miss="$(dp_termux_pkg_missing "$DP_NATIVES")"
        [ -n "$_miss" ] || return 0
        dp_run "pkg install (native deps)"
        pkg install -y unzip python-pillow python-cryptography python-psutil \
            >>"$DP_LOG" 2>&1 \
            || fail "pkg install failed — run: pkg install -y python unzip python-cryptography python-psutil python-pillow"
        ok "native deps"
    else
        :
    fi
}

dp_venv() {
    _py="$(dp_python)"
    dp_run "virtual environment"
    : > "$DP_LOG"
    _venvflags=""
    [ "$DP_TERMUX" = 1 ] && _venvflags="--system-site-packages"
    if ! "$_py" -m venv $_venvflags "$DP_AGENT/.venv" >>"$DP_LOG" 2>&1; then
        fail "venv creation failed — see $DP_LOG"
    fi
    if   [ -x "$DP_AGENT/.venv/bin/python" ];         then VP="$DP_AGENT/.venv/bin/python"
    elif [ -x "$DP_AGENT/.venv/Scripts/python" ];    then VP="$DP_AGENT/.venv/Scripts/python"
    elif [ -x "$DP_AGENT/.venv/Scripts/python.exe" ]; then VP="$DP_AGENT/.venv/Scripts/python.exe"
    else fail "venv python missing — see $DP_LOG"; fi
    "$VP" -m pip --version >/dev/null 2>&1 || "$VP" -m ensurepip >>"$DP_LOG" 2>&1
    ok "virtual environment"

    dp_run "dependencies (requests)"
    if "$VP" -m pip install --quiet --no-input --disable-pip-version-check \
            requests >>"$DP_LOG" 2>&1; then
        ok "dependencies"
    else
        "$VP" -m pip install --no-input --disable-pip-version-check \
            requests >>"$DP_LOG" 2>&1 || fail "pip failed — see $DP_LOG"
        ok "dependencies"
    fi

    if [ "$DP_TERMUX" != 1 ]; then
        for _x in $DP_NATIVES; do                       # wheels everywhere else
            "$VP" -m pip install --quiet --no-input \
                --disable-pip-version-check "$_x" >>"$DP_LOG" 2>&1 \
                || printf '  %s %s skipped (%s)\n' "$DP_DIM" "$_x" "see log"
        done
        ok "native deps"
    fi
}

# ── launcher + PATH ───────────────────────────────────────────────────
dp_launcher() {
    mkdir -p "$DP_BIN_DIR"
    cp "$DP_AGENT/bin/darkps" "$DP_BIN_DIR/darkps" || fail "launcher copy failed"
    chmod +x "$DP_BIN_DIR/darkps" 2>/dev/null
    ok "launcher"

    case ":$PATH:" in
        *":$DP_BIN_DIR:"*) return 0 ;;
    esac
    if [ "$DP_TERMUX" = 1 ]; then
        printf '  %s PATH %s\n' "$DP_TICK" "$DP_DIM\$PREFIX/bin (built-in)${DP_R}"
        return 0
    fi
    if [ -t 0 ] || dp_can_tty; then
        printf '  %s add %s to PATH? %s ' "$DP_ACC>$DP_R" "$DP_BIN_DIR" "$DP_DIM[Y/n]$DP_R"
        if [ -t 0 ]; then
            IFS= read -r DP_ANS
        else
            IFS= read -r DP_ANS < /dev/tty
        fi
        case "$DP_ANS" in
            n*|N*)
                printf '\n  %s\n' "${DP_DIM}then run:  export PATH=\"$DP_BIN_DIR:\$PATH\"${DP_R}"
                return 0 ;;
        esac
        rc="$HOME/.bashrc"
        [ -n "${ZSH_VERSION:-}" ] && rc="$HOME/.zshrc"
        printf '\n# DarkPs\nexport PATH="%s:$PATH"\n' "$DP_BIN_DIR" >> "$rc"
        printf '\n'
        ok "PATH updated ($rc) — restart the shell"
    else
        printf '  %s\n' "${DP_DIM}add to your profile:  export PATH=\"$DP_BIN_DIR:\$PATH\"${DP_R}"
    fi
}

# ── flows ─────────────────────────────────────────────────────────────
flow_install() {
    dp_get_archive
    dp_extract
    dp_native_deps
    dp_venv
    dp_launcher
    printf '\n'
    printf '%s\n' "  ${DP_BOLD}DarkPs $DP_VER installed${DP_R}"
    printf '%s\n' "  ${DP_DIM}agent     $DP_AGENT${DP_R}"
    printf '%s\n' "  ${DP_BOLD}darkps${DP_R}                ${DP_DIM}terminal agent${DP_R}"
    printf '%s\n' "  ${DP_BOLD}darkps --ui${DP_R}          ${DP_DIM}Web UI — http://127.0.0.1:7861${DP_R}"
    printf '%s\n' "  ${DP_BOLD}darkps --web-port N${DP_R}   ${DP_DIM}Web UI on any port${DP_R}"
    if [ "${DARKPS_NO_OPEN:-}" = "1" ]; then printf '\n'; return 0; fi
    if [ -t 0 ] || dp_can_tty; then
        printf '\n  %sstart darkps now? %s' "$DP_BOLD" "$DP_DIM[Y/n]$DP_R"
        if [ -t 0 ]; then
            IFS= read -r DP_ANS
        else
            IFS= read -r DP_ANS < /dev/tty
        fi
        case "$DP_ANS" in
            n*|N*) printf '\n\n'; return 0 ;;
        esac
        printf '\n'
        DARKPS_ROOT="$DP_AGENT" exec "$DP_BIN_DIR/darkps"
    fi
    printf '\n'
    return 0
}

flow_uninstall() {
    dp_run "removing"
    rm -rf "$DP_BASE" "$DP_ARCHIVE"
    ok "agent files"
    if [ -e "$DP_BIN_DIR/darkps" ]; then
        rm -f "$DP_BIN_DIR/darkps"
        ok "launcher"
    fi
    rm -rf "$HOME/.darkps"                                 # agent's own data dir
    printf '\n%s\n' "  ${DP_BOLD}DarkPs uninstalled${DP_R}${DP_DIM} · ~/.local/share/darkps + ~/.darkps removed${DP_R}"
}

dp_usage() {
    printf 'usage: install.sh [flag]\n\n'
    printf '  (none)       install\n'
    printf '  --uninstall  remove everything\n'
}

# ── main ──────────────────────────────────────────────────────────────
dp_main() {
    DP_UNINSTALL=""
    for a in "$@"; do
        case "$a" in
            --uninstall) DP_UNINSTALL=1 ;;
            -h|--help)   dp_logo; printf '\n'; dp_usage; printf '\n'; exit 0 ;;
        esac
    done

    dp_logo
    printf '  %sDarkPs Installer%s  %sv%s%s\n' "$DP_BOLD" "$DP_R" "$DP_DIM" "$DP_VER" "$DP_R"
    printf '  %sthe dark terminal agent + WebUI%s\n\n' "$DP_DIM" "$DP_R"

    if [ "$DP_UNINSTALL" = "1" ]; then
        flow_uninstall
        return 0
    fi
    dp_checks
    flow_install
}

dp_main "$@"
exit 0
