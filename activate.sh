# Source this file in bash or zsh; it changes only this terminal session.
if [ -n "${ZSH_VERSION:-}" ]; then
    PTK_ACTIVATE_FILE=${(%):-%x}
else
    PTK_ACTIVATE_FILE=${BASH_SOURCE[0]}
fi
PTK_ACTIVE_ROOT=$(CDPATH= cd -- "$(dirname -- "$PTK_ACTIVATE_FILE")" && pwd)
export PATH="$PTK_ACTIVE_ROOT/bin:$PATH"
hash -r 2>/dev/null || true
printf 'PTK ready. Try: ptk doctor\n'
unset PTK_ACTIVATE_FILE PTK_ACTIVE_ROOT
