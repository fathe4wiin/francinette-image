#!/bin/bash
docker exec -it --workdir "$PWD" run-paco /francinette/venv/bin/python /francinette/main.py "$@"
