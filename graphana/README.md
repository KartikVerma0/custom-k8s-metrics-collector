# Grafana Setup for Kubernetes

This directory contains Kubernetes manifests to deploy Grafana for visualizing metrics from the custom Kubernetes metrics collector.

## Files

- `grafana-deployment.yaml` - Grafana deployment configuration
- `grafana-service.yaml` - Service to expose Grafana (ClusterIP)
- `grafana-pvc.yaml` - Persistent volume claim for Grafana data
- `grafana-secret.yaml` - Secret containing Grafana admin credentials
- `grafana-datasources-configmap.yaml` - Pre-configured MySQL datasource
- `grafana-dashboards-configmap.yaml` - Dashboard provisioning configuration

## Prerequisites

- Kubernetes cluster with storage class `standard` (or update `grafana-pvc.yaml` with your storage class)
- MySQL service running in the `custom-metrics-collection` namespace
- The `mysql-secret` must exist with database credentials

## Installation

1. **Apply all Grafana manifests:**
   ```bash
   kubectl apply -f grafana-secret.yaml
   kubectl apply -f grafana-pvc.yaml
   kubectl apply -f grafana-datasources-configmap.yaml
   kubectl apply -f grafana-dashboards-configmap.yaml
   kubectl apply -f grafana-deployment.yaml
   kubectl apply -f grafana-service.yaml
   ```

   Or apply all at once:
   ```bash
   kubectl apply -f .
   ```

2. **Check deployment status:**
   ```bash
   kubectl get pods -n custom-metrics-collection -l app=grafana
   kubectl get svc -n custom-metrics-collection grafana
   ```

3. **Access Grafana:**

   **Option 1: Port Forward (Recommended for local access)**
   ```bash
   kubectl port-forward -n custom-metrics-collection svc/grafana 3000:3000
   ```
   Then open http://localhost:3000 in your browser

   **Option 2: Change Service Type to NodePort**
   Edit `grafana-service.yaml` and change `type: ClusterIP` to `type: NodePort`, then apply:
   ```bash
   kubectl apply -f grafana-service.yaml
   kubectl get svc -n custom-metrics-collection grafana
   ```
   Access via `<node-ip>:<nodeport>`

   **Option 3: Ingress (if you have an ingress controller)**
   Create an Ingress resource to expose Grafana

## Default Credentials

- **Username:** admin
- **Password:** admin

**⚠️ IMPORTANT:** Change the default password after first login! Update `grafana-secret.yaml` and restart the deployment.

## Pre-configured Datasource

Grafana is pre-configured with a MySQL datasource pointing to:
- **Host:** mysql:3306 (MySQL service in the same namespace)
- **Database:** nodes
- **User:** metrics_user
- **Password:** (from mysql-secret)

The datasource is automatically provisioned and will appear in Grafana's datasources list.

## Customization

### Change Storage Size
Edit `grafana-pvc.yaml` and modify the `storage` value under `resources.requests`.

### Change Admin Credentials
1. Update `grafana-secret.yaml` with new credentials
2. Apply the secret: `kubectl apply -f grafana-secret.yaml`
3. Restart the deployment: `kubectl rollout restart deployment/grafana -n custom-metrics-collection`

### Add Custom Dashboards
1. Create dashboard JSON files
2. Mount them as a ConfigMap or PersistentVolume
3. Update `grafana-dashboards-configmap.yaml` or the deployment volume mounts

## Troubleshooting

**Check Grafana logs:**
```bash
kubectl logs -n custom-metrics-collection -l app=grafana
```

**Check if PVC is bound:**
```bash
kubectl get pvc -n custom-metrics-collection grafana-pvc
```

**Verify datasource connection:**
- Log into Grafana
- Go to Configuration > Data Sources
- Test the MySQL datasource connection

