#!/usr/bin/env python3
"""Patch Katenary-generated Helm charts to match production deployment manifests.

Aligns chart resources with kind-deployment-Local.yaml, kind-deployment-GitHub.yaml,
and GKE-deployment-GCP.yaml:
  - Backend Service: LoadBalancer default, port 80 (HTTP) -> 3000
  - Backend ConfigMap: POSTGRES_PORT ("5432"), PORT ("3000")
  - Backend Deployment: Readiness/Liveness probes on /api/items, optional OPENAI_API_KEY
  - Postgres Service: port 5432
  - Postgres ConfigMap / Deployment: PGDATA (/var/lib/postgresql/data/pgdata), pg_isready probes
  - Values: Environment-specific images, imagePullPolicy, StorageClass, and PVC sizes.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CHART = Path(sys.argv[1] if len(sys.argv) > 1 else
             "charts/getting-started-todo-app-openai-agent.local_kind")

SERVICE = CHART / "templates" / "backend" / "service.yaml"
BACKEND_CM = CHART / "templates" / "backend" / "configmap.yaml"
BACKEND_DEP = CHART / "templates" / "backend" / "deployment.yaml"
PG_SERVICE = CHART / "templates" / "postgres" / "service.yaml"
PG_CM = CHART / "templates" / "postgres" / "configmap.yaml"
PG_DEP = CHART / "templates" / "postgres" / "deployment.yaml"
PG_PVC = CHART / "templates" / "postgres" / "todo_postgres_data.volumeclaim.yaml"
VALUES = CHART / "values.yaml"


def patch_backend_service() -> None:
    if not SERVICE.is_file():
        return
    text = SERVICE.read_text(encoding="utf-8")
    
    # 1. Type
    if "backend.serviceType" not in text:
        type_line = '  type: {{ .Values.backend.serviceType | default "LoadBalancer" }}\n'
        for nl in ["\nspec:\n", "\r\nspec:\r\n"]:
            if nl in text:
                text = text.replace(nl, nl + type_line, 1)
                break
    elif 'default "ClusterIP"' in text:
        text = text.replace('default "ClusterIP"', 'default "LoadBalancer"')

    # 2. Port 80 -> 3000
    if "backend.servicePort" not in text:
        for nl in ["\n", "\r\n"]:
            old_port = f"    port: 3000{nl}    protocol: TCP{nl}    targetPort: 3000"
            new_port = f"    port: {{{{ .Values.backend.servicePort | default 80 }}}}{nl}    protocol: TCP{nl}    targetPort: 3000"
            if old_port in text:
                text = text.replace(old_port, new_port)

    # 3. Port name
    text = text.replace("name: port-3000", "name: http")
    SERVICE.write_text(text, encoding="utf-8")
    print(f"[ok]   patched backend service in {SERVICE}")


def patch_backend_configmap() -> None:
    if not BACKEND_CM.is_file():
        return
    text = BACKEND_CM.read_text(encoding="utf-8")
    if 'POSTGRES_PORT:' not in text:
        if 'data:\n' in text:
            text = text.replace('data:\n', 'data:\n  POSTGRES_PORT: "5432"\n  PORT: "3000"\n')
        elif 'data:\r\n' in text:
            text = text.replace('data:\r\n', 'data:\r\n  POSTGRES_PORT: "5432"\r\n  PORT: "3000"\r\n')
        BACKEND_CM.write_text(text, encoding="utf-8")
        print(f"[ok]   patched backend configmap in {BACKEND_CM}")


def patch_backend_deployment() -> None:
    if not BACKEND_DEP.is_file():
        return
    text = BACKEND_DEP.read_text(encoding="utf-8")

    # Add probes if missing
    if "readinessProbe:" not in text:
        probes = """        readinessProbe:
          httpGet:
            path: /api/items
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /api/items
            port: 3000
          initialDelaySeconds: 15
          periodSeconds: 10
"""
        # Insert after name: port-3000 or name: http
        for port_target in ["name: port-3000\n", "name: http\n", "name: port-3000\r\n", "name: http\r\n"]:
            if port_target in text:
                text = text.replace(port_target, port_target + probes, 1)
                break

    # Add optional OPENAI_API_KEY if missing
    if "OPENAI_API_KEY" not in text:
        ai_env = """        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: todo-ai-secret
              key: OPENAI_API_KEY
              optional: true
"""
        if "envFrom:\n" in text:
            text = text.replace("envFrom:\n", ai_env + "        envFrom:\n", 1)
        elif "envFrom:\r\n" in text:
            text = text.replace("envFrom:\r\n", ai_env + "        envFrom:\r\n", 1)

    text = text.replace("name: port-3000", "name: http")
    BACKEND_DEP.write_text(text, encoding="utf-8")
    print(f"[ok]   patched backend deployment in {BACKEND_DEP}")


def patch_postgres() -> None:
    if PG_DEP.is_file():
        text = PG_DEP.read_text(encoding="utf-8")
        # Ensure PGDATA is set
        if "PGDATA" not in text:
            pgdata = """        env:
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
"""
            if "envFrom:\n" in text:
                text = text.replace("envFrom:\n", pgdata + "        envFrom:\n", 1)
            elif "envFrom:\r\n" in text:
                text = text.replace("envFrom:\r\n", pgdata + "        envFrom:\r\n", 1)

        # Fix pg_isready probe command
        if "pg_isready -U postgres -d todos" in text:
            probe_fixed = """            command:
            - pg_isready
            - -U
            - postgres
            - -d
            - todos"""
            text = text.replace("            command:\n            - pg_isready -U postgres -d todos", probe_fixed)
            text = text.replace("            command:\r\n            - pg_isready -U postgres -d todos", probe_fixed)

        # Fix potential Katenary line break in claimName
        for bad_pvc in [
            '{{- end }}\n            . }}-postgres-todo-postgres-data',
            '{{- end }}\r\n            . }}-postgres-todo-postgres-data'
        ]:
            if bad_pvc in text:
                text = text.replace(bad_pvc, '. }}-postgres-todo-postgres-data')

        PG_DEP.write_text(text, encoding="utf-8")
        print(f"[ok]   patched postgres deployment in {PG_DEP}")

    if PG_SERVICE.is_file():
        text = PG_SERVICE.read_text(encoding="utf-8")
        text = text.replace("targetPort: postgresql", "targetPort: 5432")
        PG_SERVICE.write_text(text, encoding="utf-8")
        print(f"[ok]   patched postgres service in {PG_SERVICE}")


def patch_values() -> None:
    if not VALUES.is_file():
        return
    chart_name = CHART.name.lower()
    text = VALUES.read_text(encoding="utf-8")

    # 1. serviceType
    if "\n  serviceType:" not in text and "\r\n  serviceType:" not in text:
        text = text.replace("backend:\n", "backend:\n  serviceType: LoadBalancer\n  servicePort: 80\n")
        text = text.replace("backend:\r\n", "backend:\r\n  serviceType: LoadBalancer\r\n  servicePort: 80\r\n")

    # 2. Adjust for specific environment
    if "gcp_gke" in chart_name:
        text = text.replace("storageClass: '-'", "storageClass: standard-rwo")
        text = text.replace("size: 1Gi", "size: 10Gi")
    elif "kind" in chart_name:
        text = text.replace("storageClass: '-'", "storageClass: standard")

    VALUES.write_text(text, encoding="utf-8")
    print(f"[ok]   patched values in {VALUES}")


if __name__ == "__main__":
    patch_backend_service()
    patch_backend_configmap()
    patch_backend_deployment()
    patch_postgres()
    patch_values()
