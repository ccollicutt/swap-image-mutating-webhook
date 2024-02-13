#!/bin/bash

: ${PORT:=8443}
gunicorn --chdir /app \
    -w 1 \
    --threads 2 \
    -b 0.0.0.0:${PORT} \
    --certfile=/certs/tls.crt \
    --keyfile=/certs/tls.key \
    app:app