FROM dhi.io/python:3.10-alpine3.22-dev as build
WORKDIR /tmp/build
RUN python -m venv /tmp/build/venv
COPY requirements_collector.txt .
RUN venv/bin/pip install --no-cache-dir -r requirements_collector.txt

FROM dhi.io/python:3.10-alpine3.22 as runtime
WORKDIR /app
COPY --from=build /tmp/build/venv /app/venv
COPY . .
# Use the venv's Python interpreter
ENTRYPOINT ["/app/venv/bin/python", "collector.py"]