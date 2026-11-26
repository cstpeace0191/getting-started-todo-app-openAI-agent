# getting-started-todo-app-openai-agent

A Helm chart for getting-started-todo-app-openai-agent

## Installing the Chart

To install the chart with the release name `my-release`:

```bash
# Standard Helm install
$ helm install  my-release getting-started-todo-app-openai-agent

# To use a custom namespace and force the creation of the namespace
$ helm install my-release --namespace my-namespace --create-namespace getting-started-todo-app-openai-agent

# To use a custom values file
$ helm install my-release -f my-values.yaml getting-started-todo-app-openai-agent
```

See the [Helm documentation](https://helm.sh/docs/intro/using_helm/) for more information on installing and managing the chart.

## Configuration

The following table lists the configurable parameters of the getting-started-todo-app-openai-agent chart and their default values.

| Parameter                                                     | Default                            |
| ------------------------------------------------------------- | ---------------------------------- |
| `backend.imagePullPolicy`                                     | `IfNotPresent`                     |
| `backend.replicas`                                            | `1`                                |
| `backend.repository.image`                                    | `ghcr.io/cstpeace0191/getting-started-todo-app-openai-agent` |
| `backend.repository.tag`                                      | `prod`                             |
| `backend.serviceAccount`                                      | ``                                 |
| `postgres.imagePullPolicy`                                    | `IfNotPresent`                     |
| `postgres.persistence.todo_postgres_data.accessMode[0].value` | `ReadWriteOnce`                    |
| `postgres.persistence.todo_postgres_data.enabled`             | `true`                             |
| `postgres.persistence.todo_postgres_data.size`                | `1Gi`                              |
| `postgres.persistence.todo_postgres_data.storageClass`        | `-`                                |
| `postgres.replicas`                                           | `1`                                |
| `postgres.repository.image`                                   | `postgres`                         |
| `postgres.repository.tag`                                     | `17`                               |
| `postgres.serviceAccount`                                     | ``                                 |


