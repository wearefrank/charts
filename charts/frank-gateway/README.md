## Parameters

### General

These are all overrides for the `apisix` subchart dependency, so everything must be
nested under the `apisix:` key (otherwise it never reaches the subchart, see
apache/apisix-helm-chart's values.yaml). Chart version 2.14.0 no longer has a separate
dashboard subchart/dependency, so there is no key for that.

Gotcha: the subchart itself also has its own top-level `apisix:` key (a 1-to-1 mirror
of the APISIX `config.yaml` `apisix:` section, which includes `deployment:` among
others). To override something in there you need `apisix.apisix.*` from our
values.yaml — the first `apisix:` is the dependency, the second is their own config
section.


### Image

| Name                      | Description                                                 | Value                              |
| ------------------------- | ----------------------------------------------------------- | ---------------------------------- |
| `apisix.image.repository` | APISIX container image repository                           | `ghcr.io/wearefrank/frank-gateway` |
| `apisix.image.tag`        | APISIX container image tag (immutable tags are recommended) | `1.0.0`                            |

### Deployment mode

| Name                                                        | Description                                                                                     | Value         |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------------- |
| `apisix.apisix.deployment.mode`                             | APISIX deployment mode (we run standalone, without etcd)                                        | `standalone`  |
| `apisix.apisix.deployment.role_traditional.config_provider` | Configuration provider used in standalone mode                                                  | `yaml`        |
| `apisix.apisix.deployment.standalone.config`                | Inline APISIX routes configuration (YAML string); customers override this with their own routes | `routes: []
` |

### Custom plugins

| Name                                  | Description                                                                                                                                                                                                                               | Value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `apisix.apisix.customPlugins.enabled` | Enable custom (WeAreFrank) Lua plugins baked into the image                                                                                                                                                                               | `true`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `apisix.apisix.customPlugins.luaPath` | Lua module search path pattern used to locate custom plugin code                                                                                                                                                                          | `/usr/local/apisix/custom-plugins/?.lua`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `apisix.apisix.customPlugins.plugins` | Custom plugin definitions: each entry has `name` (must match its Lua module name), `attrs` (passed through to the APISIX plugin config), and an optional `configMap` (`name`/`mounts`) to mount plugin config from an existing ConfigMap. |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `apisix.apisix.plugins`               | Enabled APISIX plugin list; custom plugins (see `customPlugins.plugins` above) must also be listed here, or APISIX won't load them                                                                                                        | `["real-ip","client-control","proxy-control","request-id","opentelemetry","ext-plugin-pre-req","fault-injection","mocking","serverless-pre-function","cors","ip-restriction","ua-restriction","referer-restriction","csrf","uri-blocker","request-validation","chaitin-waf","multi-auth","openid-connect","cas-auth","authz-casbin","authz-casdoor","wolf-rbac","ldap-auth","hmac-auth","basic-auth","jwt-auth","jwe-decrypt","key-auth","consumer-restriction","forward-auth","opa","authz-keycloak","proxy-cache","body-transformer","proxy-mirror","proxy-rewrite","workflow","api-breaker","limit-conn","limit-count","limit-req","response-extractor","gzip","server-info","traffic-split","redirect","response-rewrite","degraphql","grpc-transcode","grpc-web","public-api","prometheus","datadog","loki-logger","elasticsearch-logger","echo","loggly","http-logger","splunk-hec-logging","skywalking-logger","google-cloud-logging","sls-logger","tcp-logger","kafka-logger","rocketmq-logger","syslog","udp-logger","file-logger","clickhouse-logger","inspect","example-plugin","cert-auth","frank-sender","generic-oauth-client","jwt-client","limit-size","soap-action-router","openid-connect-client","fsc","serverless-post-function","ext-plugin-post-req","ext-plugin-post-resp"]` |

### etcd

We use standalone/yaml mode and don't talk to etcd at all (internal or external).

| Name                       | Description                                                                                          | Value   |
| -------------------------- | ---------------------------------------------------------------------------------------------------- | ------- |
| `apisix.etcd.enabled`      | Enable the bundled etcd subchart                                                                     | `false` |
| `apisix.externalEtcd.user` | External etcd username, emptied to avoid an unused etcd secret/env var since `etcd.enabled` is false | `""`    |

### Ingress controller

| Name                                | Description                                           | Value   |
| ----------------------------------- | ----------------------------------------------------- | ------- |
| `apisix.ingress-controller.enabled` | Enable the bundled APISIX ingress-controller subchart | `false` |

## Troubleshooting: `helm dependency update` fails

This chart depends on the official `apisix` chart via `https://apache.github.io/apisix-helm-chart`.
This URL occasionally has DNS resolution issues (see [apache/apisix-helm-chart#959](https://github.com/apache/apisix-helm-chart/issues/959)).

If you get an error like:

    Error: looks like "..." is not a valid chart repository or cannot be reached:
    Get "https://apache.github.io/apisix-helm-chart/index.yaml": dial tcp: lookup apache.github.io: no such host

use the alternative repo hosted by API7.ai instead:

    helm repo add apisix https://charts.apiseven.com --force-update
    helm repo update
    helm dependency update .

> **Note:** these two repos have not always been exactly in sync in the past
> ([apache/apisix-helm-chart#610](https://github.com/apache/apisix-helm-chart/issues/610)).
> After falling back, always double-check the chart version with `helm dependency list`.

## Gotcha: nesting of values.yaml overrides for the `apisix` subchart

All overrides for the `apisix` dependency must be nested under the `apisix:`
key in our `values.yaml` — otherwise they never reach the subchart.

Extra gotcha: the subchart itself also has its own top-level `apisix:` key in
its own `values.yaml` (a 1-to-1 mirror of the APISIX `config.yaml` `apisix:`
section, which includes `deployment:` among others). So to override e.g.
`deployment.mode` from our chart you need `apisix.apisix.deployment.mode` —
the first `apisix:` is the dependency, the second is their own config
section. Keys like `image`, `etcd` and `ingress-controller` do sit directly
at the top level of the subchart, so those are simply `apisix.image`,
`apisix.etcd`, etc. (no double nesting).

Always verify values changes with `helm template frank-gateway . --debug`
and specifically check `deployment.role_traditional.config_provider` and the
container `command`/volumes in the rendered Deployment — with incorrect
nesting, Helm silently swallows the override and falls back to the
subchart's defaults (traditional mode + etcd), without an error message.

Separate gotcha: with `etcd.enabled: false`, the chart by default assumes
you're using an *external* etcd (`externalEtcd.user` defaults to `"root"`),
and generates an unused etcd secret + `APISIX_ETCD_PASSWORD` env var in the
Deployment. For standalone/yaml mode without etcd (internal or external),
set `apisix.externalEtcd.user: ""` to avoid that.