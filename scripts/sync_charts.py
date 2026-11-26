"""Synchronize all 3 Helm charts with kind-deployment-Local.yaml, kind-deployment-GitHub.yaml, and GKE-deployment-GCP.yaml."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARTS_DIR = ROOT / "charts"

BACKEND_DEPLOYMENT = """apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    {{- include "getting-started-todo-app-openai-agent.labels" . | nindent 4 }}
    app.kubernetes.io/name: getting-started-todo-app-openai-agent
    app.kubernetes.io/component: backend
    katenary.v3/component: backend
  name: '{{ include "getting-started-todo-app-openai-agent.fullname" . }}-backend'
spec:
  replicas: {{ .Values.backend.replicas | default 2 }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      {{- include "getting-started-todo-app-openai-agent.selectorLabels" . | nindent 6 }}
      katenary.v3/component: backend
  template:
    metadata:
      labels:
        {{- include "getting-started-todo-app-openai-agent.selectorLabels" . | nindent 8 }}
        app: todo-backend
        app.kubernetes.io/name: getting-started-todo-app-openai-agent
        app.kubernetes.io/component: backend
        katenary.v3/component: backend
    spec:
      initContainers:
      - name: wait-for-postgres
        image: busybox:1.36
        imagePullPolicy: IfNotPresent
        command:
        - sh
        - -c
        - |-
          echo "Waiting for PostgreSQL service at {{ include "getting-started-todo-app-openai-agent.fullname" . }}-postgres:5432..."
          until nc -z -v -w3 {{ include "getting-started-todo-app-openai-agent.fullname" . }}-postgres 5432; do
            echo "PostgreSQL is not ready yet, sleeping 2s..."
            sleep 2
          done
          echo "PostgreSQL is available!"
      containers:
      - name: backend
        image: '{{ tpl .Values.backend.repository.image $ }}:{{ tpl .Values.backend.repository.tag $ | default "latest" }}'
        imagePullPolicy: {{ .Values.backend.imagePullPolicy }}
        ports:
        - containerPort: 3000
          name: http
        envFrom:
        - configMapRef:
            name: '{{ include "getting-started-todo-app-openai-agent.fullname" . }}-backend'
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: todo-ai-secret
              key: OPENAI_API_KEY
              optional: true
        resources:
          {{- if .Values.backend.resources }}
          {{- .Values.backend.resources | toYaml | nindent 10 }}
          {{- else }}
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "300m"
            memory: "512Mi"
          {{- end }}
        readinessProbe:
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
      {{- if .Values.pullSecrets }}
      imagePullSecrets:
      {{- .Values.pullSecrets | toYaml | nindent 6 }}
      {{- end }}
      {{- if .Values.backend.nodeSelector }}
      nodeSelector:
        {{- .Values.backend.nodeSelector | toYaml | nindent 8 }}
      {{- end }}
      {{- if ne (default "" .Values.backend.serviceAccount) "" }}
      serviceAccountName: {{ .Values.backend.serviceAccount | quote }}
      {{- end }}
"""

BACKEND_CONFIGMAP = """apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    {{- include "getting-started-todo-app-openai-agent.labels" . | nindent 4 }}
    app.kubernetes.io/name: getting-started-todo-app-openai-agent
    app.kubernetes.io/component: backend
    katenary.v3/component: backend
  name: '{{ include "getting-started-todo-app-openai-agent.fullname" . }}-backend'
data:
  POSTGRES_HOST: '{{ include "getting-started-todo-app-openai-agent.fullname" . }}-postgres'
  POSTGRES_USER: "postgres"
  POSTGRES_DB: "todos"
  POSTGRES_PASSWORD: "secret"
  POSTGRES_PORT: "5432"
  PORT: "3000"
"""

BACKEND_SERVICE = """apiVersion: v1
kind: Service
metadata:
  labels:
    {{- include "getting-started-todo-app-openai-agent.labels" . | nindent 4 }}
    app.kubernetes.io/name: getting-started-todo-app-openai-agent
    app.kubernetes.io/component: backend
    katenary.v3/component: backend
  name: '{{ include "getting-started-todo-app-openai-agent.fullname" . }}-backend'
spec:
  type: {{ .Values.backend.serviceType | default "LoadBalancer" }}
  ports:
  - name: http
    port: {{ .Values.backend.servicePort | default 80 }}
    protocol: TCP
    targetPort: 3000
  selector:
    {{- include "getting-started-todo-app-openai-agent.selectorLabels" . | nindent 4 }}
    katenary.v3/component: backend
"""

POSTGRES_DEPLOYMENT = """apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    {{- include "getting-started-todo-app-openai-agent.labels" . | nindent 4 }}
    app.kubernetes.io/name: getting-started-todo-app-openai-agent
    app.kubernetes.io/component: database
    katenary.v3/component: postgres
  name: '{{ include "getting-started-todo-app-openai-agent.fullname" . }}-postgres'
spec:
  replicas: {{ .Values.postgres.replicas | default 1 }}
  strategy:
    type: Recreate
  selector:
    matchLabels:
      {{- include "getting-started-todo-app-openai-agent.selectorLabels" . | nindent 6 }}
      katenary.v3/component: postgres
  template:
    metadata:
      labels:
        {{- include "getting-started-todo-app-openai-agent.selectorLabels" . | nindent 8 }}
        app: postgres
        app.kubernetes.io/name: getting-started-todo-app-openai-agent
        app.kubernetes.io/component: database
        katenary.v3/component: postgres
    spec:
      containers:
      - name: postgres
        image: '{{ tpl .Values.postgres.repository.image $ }}:{{ tpl .Values.postgres.repository.tag $ | default "latest" }}'
        imagePullPolicy: {{ .Values.postgres.imagePullPolicy }}
        ports:
        - containerPort: 5432
          name: postgres
        envFrom:
        - configMapRef:
            name: '{{ include "getting-started-todo-app-openai-agent.fullname" . }}-postgres'
        env:
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        resources:
          {{- if .Values.postgres.resources }}
          {{- .Values.postgres.resources | toYaml | nindent 10 }}
          {{- else }}
          requests:
            cpu: "100m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "1Gi"
          {{- end }}
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
            - -d
            - todos
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
            - -d
            - todos
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 3
        volumeMounts:
        {{- if .Values.postgres.persistence.todo_postgres_data.enabled }}
        - mountPath: /var/lib/postgresql/data
          name: todo-postgres-data
        {{- end }}
      {{- if .Values.pullSecrets }}
      imagePullSecrets:
      {{- .Values.pullSecrets | toYaml | nindent 6 }}
      {{- end }}
      {{- if .Values.postgres.nodeSelector }}
      nodeSelector:
        {{- .Values.postgres.nodeSelector | toYaml | nindent 8 }}
      {{- end }}
      {{- if ne (default "" .Values.postgres.serviceAccount) "" }}
      serviceAccountName: {{ .Values.postgres.serviceAccount | quote }}
      {{- end }}
      volumes:
      {{- if .Values.postgres.persistence.todo_postgres_data.enabled }}
      - name: todo-postgres-data
        persistentVolumeClaim:
          claimName: '{{ include "getting-started-todo-app-openai-agent.fullname" . }}-postgres-todo-postgres-data'
      {{- end }}
"""

POSTGRES_CONFIGMAP = """apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    {{- include "getting-started-todo-app-openai-agent.labels" . | nindent 4 }}
    app.kubernetes.io/name: getting-started-todo-app-openai-agent
    app.kubernetes.io/component: database
    katenary.v3/component: postgres
  name: '{{ include "getting-started-todo-app-openai-agent.fullname" . }}-postgres'
data:
  POSTGRES_DB: todos
  POSTGRES_PASSWORD: "secret"
  POSTGRES_USER: "postgres"
"""

POSTGRES_SERVICE = """apiVersion: v1
kind: Service
metadata:
  labels:
    {{- include "getting-started-todo-app-openai-agent.labels" . | nindent 4 }}
    app.kubernetes.io/name: getting-started-todo-app-openai-agent
    app.kubernetes.io/component: database
    katenary.v3/component: postgres
  name: '{{ include "getting-started-todo-app-openai-agent.fullname" . }}-postgres'
spec:
  type: ClusterIP
  ports:
  - name: postgres
    port: 5432
    protocol: TCP
    targetPort: 5432
  selector:
    {{- include "getting-started-todo-app-openai-agent.selectorLabels" . | nindent 4 }}
    katenary.v3/component: postgres
"""

POSTGRES_PVC = """{{- if .Values.postgres.persistence.todo_postgres_data.enabled }}
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  labels:
    {{- include "getting-started-todo-app-openai-agent.labels" . | nindent 4 }}
    app.kubernetes.io/name: getting-started-todo-app-openai-agent
    app.kubernetes.io/component: database
    katenary.v3/component: postgres
  name: '{{ include "getting-started-todo-app-openai-agent.fullname" . }}-postgres-todo-postgres-data'
spec:
  accessModes:
  {{- .Values.postgres.persistence.todo_postgres_data.accessMode | toYaml | nindent 2 }}
  resources:
    requests:
      storage: {{ tpl .Values.postgres.persistence.todo_postgres_data.size $ }}
  {{- if and (ne .Values.postgres.persistence.todo_postgres_data.storageClass "-") (ne .Values.postgres.persistence.todo_postgres_data.storageClass "") }}
  storageClassName: '{{ .Values.postgres.persistence.todo_postgres_data.storageClass }}'
  {{- end }}
{{- end }}
"""

CONFIGS = {
    "getting-started-todo-app-openai-agent.local_kind": {
        "backend_image": "getting-started-todo-app-openai-agent",
        "backend_tag": "prod",
        "backend_pull_policy": "IfNotPresent",
        "storage_class": "standard",
        "storage_size": "1Gi",
    },
    "getting-started-todo-app-openai-agent.github_kind": {
        "backend_image": "ghcr.io/cstpeace0191/getting-started-todo-app-openai-agent",
        "backend_tag": "prod",
        "backend_pull_policy": "Always",
        "storage_class": "standard",
        "storage_size": "1Gi",
    },
    "getting-started-todo-app-openai-agent.gcp_gke": {
        "backend_image": "asia-northeast3-docker.pkg.dev/ssu-agent-vertex-509708/suntaechung-repo/getting-started-todo-app-openai-agent",
        "backend_tag": "prod",
        "backend_pull_policy": "Always",
        "storage_class": "standard-rwo",
        "storage_size": "10Gi",
    },
}

def make_values_yaml(cfg):
    return f"""# Values for {cfg['backend_image']}
backend:
  serviceType: LoadBalancer
  servicePort: 80
  repository:
    image: {cfg['backend_image']}
    tag: {cfg['backend_tag']}
  replicas: 2
  nodeSelector: {{}}
  resources:
    requests:
      cpu: "100m"
      memory: "128Mi"
    limits:
      cpu: "300m"
      memory: "512Mi"
  imagePullPolicy: {cfg['backend_pull_policy']}
  serviceAccount: ""

postgres:
  repository:
    image: postgres
    tag: "17"
  persistence:
    todo_postgres_data:
      storageClass: {cfg['storage_class']}
      size: {cfg['storage_size']}
      accessMode:
        - ReadWriteOnce
      enabled: true
  replicas: 1
  nodeSelector: {{}}
  resources:
    requests:
      cpu: "100m"
      memory: "256Mi"
    limits:
      cpu: "500m"
      memory: "1Gi"
  imagePullPolicy: IfNotPresent
  serviceAccount: ""

pullSecrets: []
"""

def sync():
    for chart_name, cfg in CONFIGS.items():
        chart_dir = CHARTS_DIR / chart_name
        templates_dir = chart_dir / "templates"
        backend_dir = templates_dir / "backend"
        postgres_dir = templates_dir / "postgres"
        
        backend_dir.mkdir(parents=True, exist_ok=True)
        postgres_dir.mkdir(parents=True, exist_ok=True)
        
        # Remove old mysql directory if it exists
        old_mysql = templates_dir / "mysql"
        if old_mysql.exists():
            import shutil
            shutil.rmtree(old_mysql)
            print(f"Removed deprecated {old_mysql}")
            
        (backend_dir / "deployment.yaml").write_text(BACKEND_DEPLOYMENT, encoding="utf-8")
        (backend_dir / "configmap.yaml").write_text(BACKEND_CONFIGMAP, encoding="utf-8")
        (backend_dir / "service.yaml").write_text(BACKEND_SERVICE, encoding="utf-8")
        
        (postgres_dir / "deployment.yaml").write_text(POSTGRES_DEPLOYMENT, encoding="utf-8")
        (postgres_dir / "configmap.yaml").write_text(POSTGRES_CONFIGMAP, encoding="utf-8")
        (postgres_dir / "service.yaml").write_text(POSTGRES_SERVICE, encoding="utf-8")
        (postgres_dir / "todo_postgres_data.volumeclaim.yaml").write_text(POSTGRES_PVC, encoding="utf-8")
        
        values_content = make_values_yaml(cfg)
        (chart_dir / "values.yaml").write_text(values_content, encoding="utf-8")
        print(f"[ok] Synced {chart_name}")

    # Also update root my-*.yaml files
    (ROOT / "my-local_kind-values.yaml").write_text(make_values_yaml(CONFIGS["getting-started-todo-app-openai-agent.local_kind"]), encoding="utf-8")
    (ROOT / "my-github_kind-values.yaml").write_text(make_values_yaml(CONFIGS["getting-started-todo-app-openai-agent.github_kind"]), encoding="utf-8")
    (ROOT / "my-gcp_gke-values.yaml").write_text(make_values_yaml(CONFIGS["getting-started-todo-app-openai-agent.gcp_gke"]), encoding="utf-8")
    print("[ok] Synced root my-*.yaml files")

if __name__ == "__main__":
    sync()

