FROM dhi.io/python:3.10-alpine3.22-dev AS build
WORKDIR /app
RUN python -m venv /app/venv
COPY requirements_metrics_processor.txt .
RUN venv/bin/pip install --no-cache-dir -r requirements_metrics_processor.txt

FROM dhi.io/python:3.10-alpine3.22 AS runtime
WORKDIR /app
COPY --from=build /app/venv /app/venv
COPY . .
ENV PATH="/app/venv/bin:$PATH"
CMD ["uvicorn", "metrics_processor:app", "--host", "0.0.0.0", "--port", "9376"]