# Helm Charts for Apache Drill

> [!NOTE]
> This project was originally forked from [Agirish/drill-helm-charts](https://github.com/Agirish/drill-helm-charts), but
> was moved to this repo for automated build and discoverability.

## Overview

This repository contains a collection of files that can be used to deploy [Apache Drill](http://drill.apache.org/) on
Kubernetes using Helm Charts. Supports single-node
and [cluster](http://drill.apache.org/docs/installing-drill-in-distributed-mode/) modes.

### What are Helm and Charts?

[Helm](https://helm.sh/) is a package manager
for [Kubernetes](https://kubernetes.io/). [Charts](https://helm.sh/docs/topics/charts/) are a packaging format in Helm
that can simplify deploying Kubernetes applications such as Drill Clusters.

## Pre-requisites

- A Kubernetes Cluster (this project is tested on a [K3s](https://k3s.io/) cluster)
- [Helm](https://github.com/helm/helm#install) version 3 or greater
- [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) version 1.16.0 or greater

## Usage

[Helm](https://helm.sh) must be installed to use the charts.
Please refer to Helm's [documentation](https://helm.sh/docs) to get started.

Once Helm has been set up correctly, add the repo as follows:

```shell
helm repo add wearefrank https://wearefrank.github.io/charts
```

If you had already added this repo earlier, run `helm repo update` to retrieve
the latest versions of the packages. You can then run `helm search repo
wearefrank` to see the charts.

To install the Drill chart:

```shell
helm install drill wearefrank/drill
```

To uninstall the chart:

```shell
helm delete drill
```

### Values

Helm Charts use `values.yaml` for providing default values to 'variables' used in the chart templates. These values may
be overridden either by editing the `values.yaml` file or during `helm install`. For example, such as the namespace,
number of drillbits and more to the `template` files

Please refer to the [values.yaml](values.yaml) file for details on default values for Drill Helm Charts.

### Access Drill Web UI

There is a service that can be used, but this one will jump from pod, which isn't very friendly. Depending on ingress
class you can make this sticky with annotations. You could also change the

## Chart Structure

Drill Helm charts are organized as a collection of files inside the `drill` directory. As Drill depends on Zookeeper for
cluster co-ordination, a zookeeper chart added as dependency in the [chart definition](Chart.yaml). The Zookeeper chart
is maintained by Bitnami.

```shell
drill/   
  Chart.yaml    # A YAML file with information about the chart
  Chart.lock    # A YAML file containing information about the fetched dependencies
  values.yaml   # The default configuration values for this chart
  charts/       # A directory containing the ZK charts
  templates/    # A directory of templates, when combined with values, will generate valid Kubernetes manifest files
  docs/			# A directory containing files for the documentation
```

### Templates

Helm Charts contain `templates` which are used to generate Kubernetes manifest files. These are YAML-formatted resource
descriptions that Kubernetes can understand. These templates contain 'variables', values for which are picked up from
the `values.yaml` file.

Drill Helm Charts contain the following templates:

## Autoscaling Drill Clusters

The size of the Drill cluster (number of Drill Pod replicas / number of drill-bits) can not only be manually scaled up
or down, but can also be autoscaled to simplify cluster management. When enabled, with a higher CPU
utilization, more drill-bits are added automatically and as the cluster load goes down, so do the number of drill-bits
in the Drill Cluster. The drill-bits deemed
excessive [gracefully shut down](https://drill.apache.org/docs/stopping-drill/#gracefully-shutting-down-the-drill-process),
by going into quiescent mode to permit running queries to complete.

> [!IMPORTANT]
> For the graceful shutdown to succeed, a sigfile is made in the `$DRILL_HOME` folder. This requires running as `root` (
> uid 0). If the application is run as `drilluser` the `stop` commando will be used.

Enable autoscaling by editing the autoscale section in `drill/values.yaml` file.

## Parameters

### Common parameters

| Name               | Description                                                                                  | Value |
| ------------------ | -------------------------------------------------------------------------------------------- | ----- |
| `nameOverride`     | String to partially override common.names.fullname template (will maintain the release name) | `""`  |
| `fullnameOverride` | String to fully override common.names.fullname template                                      | `""`  |

### Drill image parameters

| Name                | Description                                      | Value          |
| ------------------- | ------------------------------------------------ | -------------- |
| `image.registry`    | Drill image registry                             | `""`           |
| `image.repository`  | Drill image repository                           | `apache/drill` |
| `image.tag`         | Drill image tag (immutable tags are recommended) | `""`           |
| `image.pullPolicy`  | Drill image pull policy                          | `IfNotPresent` |
| `image.pullSecrets` | Drill image pull secrets                         | `[]`           |

### Drill deployment parameters

| Name                                 | Description                                              | Value     |
| ------------------------------------ | -------------------------------------------------------- | --------- |
| `replicaCount`                       | Number of Drill replicas to deploy                       | `1`       |
| `startupProbe.initialDelaySeconds`   | Initial delay seconds for livenessProbe                  | `10`      |
| `startupProbe.periodSeconds`         | Period seconds for livenessProbe                         | `10`      |
| `startupProbe.timeoutSeconds`        | Timeout seconds for livenessProbe                        | `1`       |
| `startupProbe.failureThreshold`      | Failure threshold for livenessProbe                      | `6`       |
| `startupProbe.successThreshold`      | Success threshold for livenessProbe                      | `1`       |
| `readinessProbe.initialDelaySeconds` | Initial delay seconds for livenessProbe                  | `0`       |
| `readinessProbe.periodSeconds`       | Period seconds for livenessProbe                         | `5`       |
| `readinessProbe.timeoutSeconds`      | Timeout seconds for livenessProbe                        | `1`       |
| `readinessProbe.failureThreshold`    | Failure threshold for livenessProbe                      | `3`       |
| `readinessProbe.successThreshold`    | Success threshold for livenessProbe                      | `1`       |
| `livenessProbe.initialDelaySeconds`  | Initial delay seconds for livenessProbe                  | `0`       |
| `livenessProbe.periodSeconds`        | Period seconds for livenessProbe                         | `10`      |
| `livenessProbe.timeoutSeconds`       | Timeout seconds for livenessProbe                        | `1`       |
| `livenessProbe.failureThreshold`     | Failure threshold for livenessProbe                      | `6`       |
| `livenessProbe.successThreshold`     | Success threshold for livenessProbe                      | `1`       |
| `resources`                          | Set the resources for the Drill containers               | `{}`      |
| `resources.limits`                   | The resources limits for the Drill containers            | `""`      |
| `resources.requests.memory`          | The requested memory for the Drill containers            | `""`      |
| `resources.requests.cpu`             | The requested cpu for the Drill containers               | `""`      |
| `terminationGracePeriodSeconds`      | Number of seconds after which pods are forcefully killed | `25`      |
| `terminationGracePeriodSeconds`      | Note: Lower values may cause running queries to fail     |           |
| `nodeSelector`                       | Node labels for pod assignment                           | `{}`      |
| `tolerations`                        | Set tolerations for pod assignment                       | `[]`      |
| `affinity`                           | Set affinity for pod assignment                          | `{}`      |
| `timeZone`                           | used for database connection and log timestamps          | `Etc/UTC` |

### Traffic Exposure Parameters

| Name                           | Description                                                                                                                       | Value       |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `service.web.type`             | Drill Web service type                                                                                                            | `ClusterIP` |
| `service.web.port`             | Drill Web service port                                                                                                            | `80`        |
| `service.user.type`            | Drill User Api service type                                                                                                       | `ClusterIP` |
| `service.user.port`            | Drill User Api service port                                                                                                       | `31010`     |
| `ingress.enabled`              | Enable ingress record generation for Drill                                                                                        | `false`     |
| `ingress.className`            | IngressClass that will be used to implement the Ingress (Kubernetes 1.18+)                                                        | `""`        |
| `ingress.annotations`          | Additional annotations for the Ingress resource. To enable certificate auto-generation, place here your cert-manager annotations. | `{}`        |
| `ingress.hosts`                | Set hosts for ingress                                                                                                             | `[]`        |
| `ingress.hosts.host`           | Set hostname                                                                                                                      | `""`        |
| `ingress.hosts.paths`          | Set multiple paths                                                                                                                | `[]`        |
| `ingress.hosts.paths.path`     | Set path (context url)                                                                                                            | `""`        |
| `ingress.hosts.paths.pathType` | Set type of path                                                                                                                  | `""`        |
| `ingress.tls`                  | Define tls secrets for hosts (implementation not done yet)                                                                        | `[]`        |

### Other Parameters

| Name                         | Description                                          | Value  |
| ---------------------------- | ---------------------------------------------------- | ------ |
| `serviceAccount.create`      | Enable creation of ServiceAccount for Drill pod      | `true` |
| `serviceAccount.annotations` | Additional custom annotations for the ServiceAccount | `{}`   |
| `serviceAccount.name`        | The name of the ServiceAccount to use.               | `""`   |
| `podAnnotations`             | Annotations for Drill pods                           | `{}`   |
| `podLabels`                  | Extra labels for Drill pods                          | `{}`   |
| `podSecurityContext`         | Set Drill pod's Security Context                     | `{}`   |
| `securityContext`            | Set Drill container's Security Context               | `{}`   |

### Drill configuration

Configuring Drill can be done with override files or in the web ui, although some properties can only be set in the override file.
When using the web ui, ZooKeeper will be used to store the values. Make sure that the storage of ZooKeeper is persistent if you intend to configure this way.

This is an example where the web ui and authentication for local (plain) users is enabled.

```hocon
drill.exec: {
http.enabled: true,
impersonation: {
enabled: true,
max_chained_user_hops: 3
},
security: {
auth.mechanisms: ["PLAIN"]
},
security.user.auth: {
enabled: true,
packages += "org.apache.drill.exec.rpc.user.security",
impl: "pam4j",
pam_profiles: [ "sudo", "login" ]
}
}
```

For more options refer to the [Apache Drill documentation](https://drill.apache.org/docs/configuration-options-introduction/).

| Name                                            | Description                                                                                                               | Value |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ----- |
| `drill.drivers`                                 | JDBC Drivers can be configured to download here. This can be used if the Docker image doesn't contain the correct drivers | `[]`  |
| `drill.drivers.name`                            | The name of the driver, will be used as filename (with `.jar` appended) and as name for initContainer                     | `""`  |
| `drill.drivers.url`                             | The URL to download the driver from                                                                                       | `""`  |
| `drill.drivers.noCheckCertificate`              | Skip certificate check                                                                                                    | `""`  |
| `drill.overrideConfiguration.existingConfigMap` | The name of the configmap, containing configuration files to override                                                     | `""`  |
| `drill.overrideConfiguration.drill`             | Multiline value for drill-override.conf                                                                                   |       |
| `drill.overrideConfiguration.drillMetastore`    | Multiline value for drill-metastore-override.conf                                                                         | `""`  |
| `drill.overrideConfiguration.drillOnYarn`       | Multiline value for drill-on-yarn-override.conf                                                                           | `""`  |
| `drill.overrideConfiguration.drillSqlLine`      | Multiline value for drill-sqlline-override.conf                                                                           | `""`  |
| `drill.overrideConfiguration.storagePlugins`    | Multiline value for storage-plugins-override.conf Can also be configured in the Web UI and saved by persistent ZooKeeper  | `""`  |
| `drill.authentication.existingSecret`           | Name of the secret containing a passwd file                                                                               | `""`  |
| `drill.authentication.users`                    | Users to create on the system                                                                                             | `[]`  |
| `drill.authentication.users.name`               | Username for the user                                                                                                     | `""`  |
| `drill.authentication.users.password`           | Password for the user                                                                                                     | `""`  |
| `drill.authentication.users.admin`              | Configures if the user should be admin                                                                                    | `""`  |

### Persistence

Persistence is used for logging and for JDBC drivers. These can be configured separately.

Configuration for Drill will be saved in ZooKeeper.
Make sure that ZooKeeper is persistent if you want to keep changes in the Web UI.

| Name                                   | Description                                                              | Value   |
| -------------------------------------- | ------------------------------------------------------------------------ | ------- |
| `persistence.enabled`                  | Enable persistence using Persistent Volume Claims                        | `false` |
| `persistence.storageClass`             | Persistent Volume storage class                                          | `""`    |
| `persistence.accessModes`              | Persistent Volume access modes                                           | `[]`    |
| `persistence.size`                     | Persistent Volume size                                                   | `2Gi`   |
| `persistence.dataSource`               | Custom PVC data source                                                   | `{}`    |
| `persistence.existingClaim`            | The name of an existing PVC to use for persistence                       | `""`    |
| `persistence.selector`                 | Selector to match an existing Persistent Volume for Drill's data PVC     | `{}`    |
| `persistence.annotations`              | Persistent Volume Claim annotations                                      | `{}`    |
| `persistence.dataLogDir.size`          | PVC Storage Request for Drill's dedicated data log directory             | `2Gi`   |
| `persistence.dataLogDir.existingClaim` | The name of an existing PVC to use for persistence                       | `""`    |
| `persistence.dataLogDir.selector`      | Selector to match an existing Persistent Volume for Drill's data log PVC | `{}`    |

## Notable changes

### 1.2.7

The notation for `.Values.service` has been changed. This makes it possible to configure `web` and `user` services separately.

### 1.2.6

`.Values.replicaCount` has been changed from `3` to `1`. This is to default to a less complex install. 
Having three replicas introduces some complexity regarding, authentication, logging and how queries will be executed. 
Until features have been added to simple this, the user needs to take these things into account. 

The notation for `.Values.persistence` has changed so storage for logs and data can be configured secretly. 
The values for persistent logging are now located at `.Values.persistence.dataLogDir`.
