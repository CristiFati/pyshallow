_SCRIPT="mue_idle.py"
_CWD="$(dirname "${0}")"
if [ -n "${_CWD}" ]; then
    _SCRIPT="${_CWD}/${_SCRIPT}"
fi

if [ -z "${PYTHONEXE}" ]; then
    PYTHONEXE="python"
fi

"${PYTHONEXE}" "${_SCRIPT}" "${@}"

