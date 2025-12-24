FROM dhi.io/python:3.10-alpine3.22-dev AS build
WORKDIR /app
RUN python -m venv /app/venv
COPY requirements_collector.txt .
RUN venv/bin/pip install --no-cache-dir -r requirements_collector.txt

FROM dhi.io/python:3.10-alpine3.22 AS runtime
WORKDIR /app
COPY --from=build /app/venv /app/venv
COPY . .
ENV PATH="/app/venv/bin:$PATH"
ENTRYPOINT ["python", "collector.py"]