if [ -z "${PYTHONEXE}" ]; then
    PYTHONEXE="python"
fi

"${PYTHONEXE}" -m pyshallow "${@}"

