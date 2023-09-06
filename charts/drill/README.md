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
the latest versions of the packages.  You can then run `helm search repo
wearefrank` to see the charts.

To install the ZaakBrug chart:

```shell
helm install zaakbrug wearefrank/zaakbrug
```

To uninstall the chart:

```shell
helm delete zaakbrug
```

### Values

Helm Charts use `values.yaml` for providing default values to 'variables' used in the chart templates. These values may
be overridden either by editing the `values.yaml` file or during `helm install`. For example, such as the namespace,
number of drillbits and more to the `template` files

Please refer to the [values.yaml](values.yaml) file for details on default values for Drill Helm Charts.

### Access Drill Web UI

There is a service that can be used, but this one will jump from pod, which isn't very unfriendly. This will be fixed in
the future. A ingress can be made to the service.

## Chart Structure

Drill Helm charts are organized as a collection of files inside the `drill` directory. As Drill depends on Zookeeper for
cluster co-ordination, a zookeeper chart added as dependency in the [chart definition](Chart.yaml). The Zookeeper chart is maintained by Bitnami.

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
or down as shown above, but can also be autoscaled to simplify cluster management. When enabled, with a higher CPU
utilization, more drill-bits are added automatically and as the cluster load goes down, so do the number of drill-bits
in the Drill Cluster. The drill-bits deemed
excessive [gracefully shut down](https://drill.apache.org/docs/stopping-drill/#gracefully-shutting-down-the-drill-process),
by going into quiescent mode to permit running queries to complete.

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

| Name                                | Description                                              | Value     |
| ----------------------------------- | -------------------------------------------------------- | --------- |
| `replicaCount`                      | Number of Drill replicas to deploy                       | `3`       |
| `livenessProbe.initialDelaySeconds` | Initial delay seconds for livenessProbe                  | `40`      |
| `livenessProbe.periodSeconds`       | Period seconds for livenessProbe                         | `10`      |
| `livenessProbe.timeoutSeconds`      | Timeout seconds for livenessProbe                        | `1`       |
| `livenessProbe.failureThreshold`    | Failure threshold for livenessProbe                      | `6`       |
| `livenessProbe.successThreshold`    | Success threshold for livenessProbe                      | `1`       |
| `resources`                         | Set the resources for the Drill containers               | `{}`      |
| `resources.limits`                  | The resources limits for the Drill containers            | `""`      |
| `resources.requests.memory`         | The requested memory for the Drill containers            | `""`      |
| `resources.requests.cpu`            | The requested cpu for the Drill containers               | `""`      |
| `terminationGracePeriodSeconds`     | Number of seconds after which pods are forcefully killed | `60`      |
| `terminationGracePeriodSeconds`     | Note: Lower values may cause running queries to fail     |           |
| `nodeSelector`                      | Node labels for pod assignment                           | `{}`      |
| `tolerations`                       | Set tolerations for pod assignment                       | `[]`      |
| `affinity`                          | Set affinity for pod assignment                          | `{}`      |
| `timeZone`                          | used for database connection and log timestamps          | `Etc/UTC` |

### Traffic Exposure Parameters

| Name                           | Description                                                                                                                                                                    | Value       |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- |
| `service.type`                 | Drill service type                                                                                                                                                             | `ClusterIP` |
| `service.webPort`              | Needed for the Drill Web UI.                                                                                                                                                   | `80`        |
| `service.userPort`             | User port address. Used between nodes in a Drill cluster. Needed for an external client, such as Tableau, to connect into the cluster nodes. Also needed for the Drill Web UI. | `31010`     |
| `service.controlPort`          | Control port address. Used between nodes in a Drill cluster. Needed for multi-node installation of Apache Drill.                                                               | `31011`     |
| `service.dataPort`             | Data port address. Used between nodes in a Drill cluster. Needed for multi-node installation of Apache Drill.                                                                  | `31012`     |
| `ingress.enabled`              | Enable ingress record generation for Frank!                                                                                                                                    | `false`     |
| `ingress.className`            | IngressClass that will be used to implement the Ingress (Kubernetes 1.18+)                                                                                                     | `""`        |
| `ingress.annotations`          | Additional annotations for the Ingress resource. To enable certificate autogeneration, place here your cert-manager annotations.                                               | `{}`        |
| `ingress.hosts`                | Set hosts for ingress                                                                                                                                                          | `[]`        |
| `ingress.hosts.host`           | Set hostname                                                                                                                                                                   | `""`        |
| `ingress.hosts.paths`          | Set multiple paths                                                                                                                                                             | `[]`        |
| `ingress.hosts.paths.path`     | Set path (context url)                                                                                                                                                         | `""`        |
| `ingress.hosts.paths.pathType` | Set type of path                                                                                                                                                               | `""`        |
| `ingress.tls`                  | Define tls secrets for hosts (implementation not done yet)                                                                                                                     | `[]`        |

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
