# 🔌Frank2PodiumD Chart

This Helm Chart contains the Frank!Framework configured for integration with PodiumD.

The Frank! is preconfigured with H2, but can be used with any other supported database.

## Usage

[Helm](https://helm.sh) must be installed to use the charts. Please refer to Helm's [documentation](https://helm.sh/docs) to get started.

Once Helm has been set up correctly, add the repo as follows:

```shell
helm repo add wearefrank https://wearefrank.github.io/charts
```

If you had already added this repo earlier, run `helm repo update` to retrieve the latest versions of the packages. 
You can then run `helm search repo wearefrank` to see the charts.

To install the frank2podiumd chart:

```shell
helm install my-frank2podiumd wearefrank/frank2podiumd
```

To uninstall the chart:

```shell
helm delete my-frank2podiumd
```

## Parameters

### Frank!Framework parameters

This chart is a wrapper for the Frank!Framework chart.
See the documentation for the Frank!Framework chart for more information.

| Name                                                    | Description                                                 | Value           |
| ------------------------------------------------------- | ----------------------------------------------------------- | --------------- |
| `frankframework.image.registry`                         | frank2podiumd image registry                                | `wearefrank`    |
| `frankframework.image.repository`                       | frank2podiumd image repository                              | `frank2podiumd` |
| `frankframework.image.tag`                              | frank2podiumd image tag (immutable tags are recommended)    | `1.0.0`         |
| `frankframework.image.pullPolicy`                       | frank2podiumd image pull policy                             | `IfNotPresent`  |
| `frankframework.image.pullSecrets`                      | frank2podiumd image pull secrets                            | `[]`            |
| `frankframework.replicaCount`                           | Number of Frank!Framework replicas to deploy                | `1`             |
| `frankframework.securityContext.readOnlyRootFilesystem` | Set the security context for the Frank!Framework containers | `true`          |

## Configuration and installation details

### DTAP Stage

The Frank!Framework will start with different settings enabled, depending on what DTAP stage is configured. 

For more information about DTAP stages read: https://docs.frankframework.org/docs/manual/deployment/dtap/

## Notable changes

See the notable changes in the [Frank!Framework chart](https://github.com/frankframework/charts/tree/master/charts/frankframework).
