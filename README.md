# Custom Kubernetes Metrics Collector

A mini-project for collecting, processing, storing, and visualizing Kubernetes node metrics. This system scrapes node metrics from Kubernetes clusters, processes them, stores them in MySQL, and provides visualization through Grafana dashboards.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Configuration](#configuration)
- [Development Mode](#development-mode)
- [Monitoring and Visualization](#monitoring-and-visualization)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

## 🎯 Overview

This project provides a custom Kubernetes metrics collection system that:

- **Collects** node metrics (CPU and memory) from Kubernetes clusters using the metrics.k8s.io API
- **Processes** metrics by converting units (nanocores → millicores, KiB → MiB)
- **Stores** metrics in MySQL with automatic TTL-based cleanup
- **Visualizes** metrics through Grafana dashboards

## 🏗️ Architecture

```
┌─────────────────┐
│  Kubernetes     │
│  Metrics API    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      HTTP POST      ┌──────────────────┐
│   Collector     │ ──────────────────► │ Metrics Processor│
│   (Python)      │                      │   (FastAPI)      │
└─────────────────┘                      └────────┬─────────┘
                                                  │
                                                  ▼
                                         ┌──────────────────┐
                                         │   MySQL Database │
                                         └────────┬─────────┘
                                                  │
                                                  ▼
                                         ┌──────────────────┐
                                         │     Grafana      │
                                         │   (Dashboards)   │
                                         └──────────────────┘
```

### Data Flow

1. **Collector** scrapes node metrics from the Kubernetes metrics API at configurable intervals
2. **Metrics Processor** receives metrics via HTTP POST, converts units, and stores them in MySQL
3. **MySQL** stores metrics with automatic cleanup of data older than 30 minutes
4. **Grafana** queries MySQL to visualize metrics in real-time dashboards

## 🧩 Components

### 1. Metrics Collector (`collector/`)
- Python service that queries the Kubernetes metrics.k8s.io API
- Configurable collection interval (minimum 15 seconds)
- Supports both in-cluster and local development modes
- Requires RBAC permissions to access metrics API

### 2. Metrics Processor (`metrics_processor/`)
- FastAPI microservice that receives and processes metrics
- Converts resource units:
  - CPU: nanocores → millicores
  - Memory: KiB → MiB
- Handles database transactions with proper error handling

### 3. MySQL Database (`mysql/`)
- Containerized MySQL deployment
- Automatic TTL event scheduler (deletes metrics older than 30 minutes)
- Persistent storage with PVC
- Pre-configured database schema

### 4. Grafana (`graphana/`)
- Pre-configured dashboards for metrics visualization
- Auto-provisioned MySQL datasource
- Persistent storage for dashboards and settings

## 📦 Prerequisites

Before deploying this system, ensure you have:

1. **Kubernetes Cluster** (v1.20+)
   - Access to a running Kubernetes cluster
   - `kubectl` configured to access your cluster
   - Metrics Server installed and running (required for metrics.k8s.io API)

2. **Storage Class**
   - A default storage class or specify one in PVC manifests
   - Required for MySQL and Grafana persistent volumes

3. **RBAC Permissions**
   - Cluster admin access to create ClusterRole and ClusterRoleBinding
   - Or permissions to create resources in the target namespace

4. **Docker Images**
   - Pre-built images or build them yourself:
     - `kartikvr20/custom-metrics-collector:v0.1.1`
     - `kartikvr20/custom-metrics-processor:v0.1.0`

## 🚀 Quick Start

### 1. Create Namespace

```bash
kubectl apply -f collector_ns.yaml
```

### 2. Deploy MySQL

```bash
kubectl apply -f mysql/
```

Wait for MySQL to be ready:
```bash
kubectl wait --for=condition=ready pod -l app=mysql -n custom-metrics-collection --timeout=300s
```

### 3. Deploy Metrics Processor

```bash
kubectl apply -f metrics_processor/
```

### 4. Deploy Collector

```bash
kubectl apply -f collector/
```

### 5. Deploy Grafana

```bash
kubectl apply -f graphana/
```

### 6. Access Grafana

```bash
kubectl port-forward -n custom-metrics-collection svc/grafana 3000:3000
```

Open http://localhost:3000 in your browser
- Username: `admin`
- Password: `admin`

## 📝 Detailed Setup

### Step 1: Create Namespace

```bash
kubectl apply -f collector_ns.yaml
```

This creates the `custom-metrics-collection` namespace where all components will be deployed.

### Step 2: Deploy MySQL Database

MySQL is the data store for all collected metrics.

```bash
# Deploy all MySQL resources
kubectl apply -f mysql/
```

This includes:
- Secret with database credentials
- PersistentVolumeClaim for data storage
- ConfigMap with MySQL configuration
- Init ConfigMap with database schema and TTL setup
- Deployment and Service

**Default Credentials:**
- Root Password: `password`
- Database User: `metrics_user`
- User Password: `dev-metrics-password`
- Database Name: `nodes`

⚠️ **Warning**: Change these credentials for production use!

**Verify MySQL is running:**
```bash
kubectl get pods -n custom-metrics-collection -l app=mysql
kubectl logs -n custom-metrics-collection -l app=mysql
```

**Connect to MySQL (for debugging):**
```bash
kubectl port-forward -n custom-metrics-collection svc/mysql 3306:3306
mysql -h 127.0.0.1 -P 3306 -u metrics_user -p
# Password: dev-metrics-password
```

### Step 3: Deploy Metrics Processor

The metrics processor receives metrics from the collector and stores them in MySQL.

```bash
kubectl apply -f metrics_processor/metrics_processor_deployment.yaml
kubectl apply -f metrics_processor/metrics_processor_svc.yaml
```

**Verify deployment:**
```bash
kubectl get pods -n custom-metrics-collection -l app=metrics-processor
kubectl logs -n custom-metrics-collection -l app=metrics-processor
```

### Step 4: Deploy Metrics Collector

The collector scrapes metrics from the Kubernetes API.

```bash
# Deploy RBAC resources first
kubectl apply -f collector/collector_sa.yaml
kubectl apply -f collector/collector_clusterrole.yaml
kubectl apply -f collector/collector_crb.yaml

# Deploy the collector
kubectl apply -f collector/collector_deployment.yaml
```

**Verify deployment:**
```bash
kubectl get pods -n custom-metrics-collection -l app=custom-metrics-collector
kubectl logs -n custom-metrics-collection -l app=custom-metrics-collector
```

### Step 5: Deploy Grafana

Grafana provides visualization dashboards for the collected metrics.

```bash
kubectl apply -f graphana/
```

**Access Grafana:**
```bash
kubectl port-forward -n custom-metrics-collection svc/grafana 3000:3000
```

Then open http://localhost:3000
- Username: `admin`
- Password: `admin`

**Change the default password** after first login!

## ⚙️ Configuration

### Collector Configuration

The collector can be configured via environment variables in `collector_deployment.yaml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `METRICS_RESOLUTION_TIME` | Collection interval in seconds (minimum 15) | `15` |
| `METRICS_PROCESSOR_SERVICE` | Metrics processor service name | `metrics-processor` |
| `METRICS_PROCESSOR_SERVICE_NAMESPACE` | Metrics processor namespace | `custom-metrics-collection` |
| `METRICS_PROCESSOR_SERVICE_PORT` | Metrics processor service port | `9376` |

### Metrics Processor Configuration

The metrics processor connects to MySQL using environment variables:

| Variable | Description | Source |
|----------|-------------|--------|
| `DB_HOST` | MySQL hostname | `mysql` (service name) |
| `DB_PORT` | MySQL port | `3306` |
| `DB_USER` | MySQL username | From `mysql-secret` |
| `DB_PASSWORD` | MySQL password | From `mysql-secret` |

### MySQL TTL Configuration

Metrics are automatically deleted after 30 minutes. This is configured in `mysql/mysql-init-script.sql`:

- **TTL Duration**: 30 minutes
- **Cleanup Interval**: Every 5 minutes
- **Event Name**: `cleanup_old_node_metrics`

To modify, edit the SQL script and recreate the init ConfigMap.

### Storage Configuration

Both MySQL and Grafana use PersistentVolumeClaims:

- **MySQL PVC**: 500Mi (configurable in `mysql/mysql-pvc.yaml`)
- **Grafana PVC**: 1Gi (configurable in `graphana/grafana-pvc.yaml`)

Update the `storageClassName` if your cluster uses a different storage class.

## 💻 Development Mode

### Running Collector Locally

1. **Install dependencies:**
   ```bash
   pip install -r collector/requirements_collector_dev.txt
   ```

2. **Create `.env` file:**
   ```env
   METRICS_RESOLUTION_TIME=15
   METRICS_PROCESSOR_URL=http://localhost:9376
   ```

3. **Ensure kubectl is configured:**
   ```bash
   kubectl config current-context
   ```

4. **Run collector:**
   ```bash
   python collector/collector.py --dev
   ```

### Running Metrics Processor Locally

1. **Install dependencies:**
   ```bash
   pip install -r metrics_processor/requirements_metrics_processor.txt
   ```

2. **Create `.env` file:**
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=metrics_user
   DB_PASSWORD=dev-metrics-password
   ```

3. **Ensure MySQL is accessible** (port-forward if needed):
   ```bash
   kubectl port-forward -n custom-metrics-collection svc/mysql 3306:3306
   ```

4. **Run metrics processor:**
   ```bash
   uvicorn metrics_processor.metrics_processor:app --host 0.0.0.0 --port 9376 --reload
   ```

## 📊 Monitoring and Visualization

### Grafana Dashboards

Grafana is pre-configured with a MySQL datasource. Create dashboards using SQL queries:

**CPU Usage Query:**
```sql
SELECT
  collected_at AS time,
  cpu_millicores
FROM node_metrics
WHERE node_name = 'minikube'
ORDER BY collected_at;
```

**Memory Usage Query:**
```sql
SELECT
  collected_at AS time,
  memory_mb
FROM node_metrics
WHERE node_name = 'minikube'
ORDER BY collected_at;
```

**Multiple Nodes:**
```sql
SELECT
  collected_at AS time,
  node_name,
  cpu_millicores,
  memory_mb
FROM node_metrics
WHERE collected_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
ORDER BY collected_at, node_name;
```

### Verifying Data Collection

**Check if metrics are being collected:**
```bash
# Check collector logs
kubectl logs -n custom-metrics-collection -l app=custom-metrics-collector

# Check metrics processor logs
kubectl logs -n custom-metrics-collection -l app=metrics-processor

# Query MySQL directly
kubectl port-forward -n custom-metrics-collection svc/mysql 3306:3306
mysql -h 127.0.0.1 -P 3306 -u metrics_user -p nodes
```

```sql
SELECT COUNT(*) FROM node_metrics;
SELECT * FROM node_metrics ORDER BY collected_at DESC LIMIT 10;
```

## 🔧 Troubleshooting

### Collector Issues

**Problem**: Collector can't access metrics API
```bash
# Check RBAC permissions
kubectl get clusterrole custom-metrics-collector-cr
kubectl get clusterrolebinding custom-metrics-collector-crb

# Check service account
kubectl get sa -n custom-metrics-collection custom-metrics-collector

# Check collector logs
kubectl logs -n custom-metrics-collection -l app=custom-metrics-collector
```

**Problem**: Metrics Server not available
```bash
# Check if metrics server is running
kubectl get deployment metrics-server -n kube-system

# Test metrics API
kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes
```

### Metrics Processor Issues

**Problem**: Can't connect to MySQL
```bash
# Check MySQL service
kubectl get svc -n custom-metrics-collection mysql

# Check MySQL pod
kubectl get pods -n custom-metrics-collection -l app=mysql

# Check metrics processor logs
kubectl logs -n custom-metrics-collection -l app=metrics-processor

# Verify database credentials in secret
kubectl get secret mysql-secret -n custom-metrics-collection -o yaml
```

**Problem**: Database connection errors
- Verify MySQL is ready: `kubectl get pods -n custom-metrics-collection -l app=mysql`
- Check MySQL logs: `kubectl logs -n custom-metrics-collection -l app=mysql`
- Verify environment variables in metrics processor deployment

### MySQL Issues

**Problem**: TTL event not running
```bash
# Connect to MySQL
kubectl port-forward -n custom-metrics-collection svc/mysql 3306:3306
mysql -h 127.0.0.1 -P 3306 -u root -p

# Check event scheduler
SHOW VARIABLES LIKE 'event_scheduler';

# Check events
USE nodes;
SHOW EVENTS LIKE 'cleanup_old_node_metrics';

# Manually run TTL setup job
kubectl apply -f mysql/mysql-ttl-setup-job.yaml
```

**Problem**: PVC not binding
```bash
# Check PVC status
kubectl get pvc -n custom-metrics-collection

# Check storage class
kubectl get storageclass

# Update storageClassName in mysql-pvc.yaml if needed
```

### Grafana Issues

**Problem**: Can't access Grafana
```bash
# Check Grafana pod
kubectl get pods -n custom-metrics-collection -l app=grafana

# Check Grafana logs
kubectl logs -n custom-metrics-collection -l app=grafana

# Check service
kubectl get svc -n custom-metrics-collection grafana
```

**Problem**: Datasource connection failed
- Verify MySQL service is accessible from Grafana pod
- Check datasource configuration in `graphana/grafana-datasources-configmap.yaml`
- Verify MySQL credentials match the secret

## 📁 Project Structure

```
custom-k8s-metrics-collector/
├── collector/                          # Metrics collector service
│   ├── collector.py                    # Main collector script
│   ├── Dockerfile                      # Container image definition
│   ├── requirements_collector.txt      # Production dependencies
│   ├── requirements_collector_dev.txt  # Development dependencies
│   ├── collector_deployment.yaml       # Kubernetes deployment
│   ├── collector_sa.yaml               # Service account
│   ├── collector_clusterrole.yaml      # RBAC cluster role
│   └── collector_crb.yaml              # Cluster role binding
│
├── metrics_processor/                  # Metrics processing service
│   ├── metrics_processor.py            # FastAPI application
│   ├── Dockerfile                      # Container image definition
│   ├── requirements_metrics_processor.txt
│   ├── metrics_processor_deployment.yaml
│   ├── metrics_processor_svc.yaml
│   ├── models/
│   │   └── node_metrics_model.py       # Pydantic models
│   └── utils/
│       ├── convert_nano_to_milli_cores.py
│       ├── convert_ki_to_mi.py
│       ├── convert_time_to_mysql_format.py
│       └── get_db_connection.py
│
├── mysql/                              # MySQL database setup
│   ├── mysql-deployment.yaml
│   ├── mysql-service.yaml
│   ├── mysql-secret.yaml
│   ├── mysql-pvc.yaml
│   ├── mysql-configmap.yaml
│   ├── mysql-init-configmap.yaml
│   ├── mysql-init-script.sql
│   ├── mysql-ttl-setup-job.yaml
│   └── README.md
│
├── graphana/                           # Grafana setup
│   ├── grafana-deployment.yaml
│   ├── grafana-service.yaml
│   ├── grafana-pvc.yaml
│   ├── grafana-secret.yaml
│   ├── grafana-datasources-configmap.yaml
│   ├── grafana-dashboards-configmap.yaml
│   └── README.md
│
├── collector_ns.yaml                  # Namespace definition
└── README.md                           # This file
```

## 🔐 Security Considerations

1. **Change Default Passwords**: Update MySQL and Grafana default credentials for production
2. **Use Secrets**: All sensitive data should be stored in Kubernetes Secrets
3. **RBAC**: The collector uses minimal RBAC permissions (only metrics API access)
4. **Network Policies**: Consider implementing network policies to restrict pod-to-pod communication
5. **Image Security**: Use trusted base images and scan for vulnerabilities

## 📄 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📞 Support

For issues or questions, please open an issue in the repository.

---

**Built with ❤️ for Kubernetes monitoring**

