# MySQL Setup for Kubernetes

This directory contains Kubernetes manifests to deploy a MySQL server for development.

## Files

- `mysql-secret.yaml` - Secret containing MySQL credentials
- `mysql-pvc.yaml` - PersistentVolumeClaim for MySQL data storage
- `mysql-configmap.yaml` - MySQL configuration
- `mysql-init-configmap.yaml` - Initialization SQL script to create database, tables, and TTL event
- `mysql-deployment.yaml` - MySQL deployment
- `mysql-service.yaml` - MySQL service for internal cluster access
- `mysql-ttl-setup-job.yaml` - Kubernetes Job to manually set up TTL event (optional)

## Default Credentials

- **Root Password**: `password`
- **Database User**: `metrics_user`
- **User Password**: `dev-metrics-password`
- **Database Name**: `nodes`

⚠️ **Warning**: These are development credentials. Change them for production use!

## Deployment

Deploy all resources:

```bash
kubectl apply -f mysql/
```

Or deploy individually:

```bash
kubectl apply -f mysql/mysql-secret.yaml
kubectl apply -f mysql/mysql-pvc.yaml
kubectl apply -f mysql/mysql-configmap.yaml
kubectl apply -f mysql/mysql-init-configmap.yaml
kubectl apply -f mysql/mysql-deployment.yaml
kubectl apply -f mysql/mysql-service.yaml
```

## Connection Details

The MySQL service is accessible within the cluster at:
- **Host**: `mysql.custom-metrics-collection.svc.cluster.local` or `mysql`
- **Port**: `3306`
- **Database**: `nodes`

## Environment Variables for Applications

Set these environment variables in your application deployments:

```yaml
env:
  - name: DB_HOST
    value: mysql
  - name: DB_PORT
    value: "3306"
  - name: DB_USER
    value: metrics_user
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: mysql-secret
        key: mysql-password
  - name: DB_NAME
    value: nodes
```

## Verify Deployment

Check if MySQL is running:

```bash
kubectl get pods -n custom-metrics-collection -l app=mysql
kubectl logs -n custom-metrics-collection -l app=mysql
```

## Connect to MySQL

Port-forward to access MySQL locally:

```bash
kubectl port-forward -n custom-metrics-collection svc/mysql 3306:3306
```

Then connect using:

```bash
mysql -h 127.0.0.1 -P 3306 -u metrics_user -p
# Password: dev-metrics-password
```

## TTL (Time To Live) Setup

The MySQL initialization script automatically sets up a TTL event that:
- Runs every 5 minutes
- Deletes metrics older than 30 minutes from the `node_metrics` table
- Event name: `cleanup_old_node_metrics`

The TTL event is automatically created when MySQL is first initialized. If you need to manually set it up or re-run it (e.g., if MySQL was already running), you can use the Job:

```bash
kubectl apply -f mysql/mysql-ttl-setup-job.yaml
```

To verify the TTL event is running:

```bash
kubectl port-forward -n custom-metrics-collection svc/mysql 3306:3306
mysql -h 127.0.0.1 -P 3306 -u root -p
# Enter password, then:
USE nodes;
SHOW EVENTS LIKE 'cleanup_old_node_metrics';
```

## Storage

The PVC uses 500Mi of storage. Adjust the `storageClassName` in `mysql-pvc.yaml` to match your cluster's storage class if needed.

## Cleanup

To remove the MySQL deployment:

```bash
kubectl delete -f mysql/
```

Note: This will delete the PVC and all data unless you delete the PVC separately.

