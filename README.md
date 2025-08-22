# *PyShallow*

*PyShallow* - **prevents** (when possible):
- Screen saver
- Screen lock
- Turn off

from kicking in


## Install

Use *PIP* (**starting with *v2025.08.23***):

```commandline
python -m pip install pyshallow
```


## Run

1. Invoke entry-point:
    ```commandline
    pyshallow
    ```
    entry-point path must be present in *PATH* environment variable (otherwise its fullpath must be specified)
2. Manually:
    ```commandline
    python -m pyshallow
    ```


## Notes

- Depends on [\[PyPI\]: pycfutils](https://pypi.org/project/pycfutils).
- *Linux* (this is the fallback):
    - Relies on *X11* server running
- **Use it responsibly** (be aware of all implications)!
