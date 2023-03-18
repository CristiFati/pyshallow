_SCRIPT="mue_idle.py"
_CWD="$(dirname "${0}")"
if [ ! "_CWD" = "" ]; then
    _SCRIPT="${_CWD}/${_SCRIPT}"
fi

if [ "${PYTHONEXE}" = "" ]; then
    PYTHONEXE="python3"
fi

"${PYTHONEXE}" "${_SCRIPT}" "${@}"

