# 🔌Frank!Framework Template Chart

This template Helm Chart can be copied as a start point for a new Frank!.

This chart won't be published because it is not in the `charts` folder.

## Usage

[Helm](https://helm.sh) must be installed to use the charts.  Please refer to
Helm's [documentation](https://helm.sh/docs) to get started.

Once Helm has been set up correctly, add the repo as follows:

```shell
helm repo add frankframework https://frankframework.github.io/charts
```

If you had already added this repo earlier, run `helm repo update` to retrieve
the latest versions of the packages.  You can then run `helm search repo
frankframework` to see the charts.

To install the ff-template chart:

```shell
helm install my-ff-template frankframework/ff-template
```

To uninstall the chart:

```shell
helm delete my-ff-template
```

## Parameters

### Common parameters

| Name               | Description                                                                                  | Value |
| ------------------ | -------------------------------------------------------------------------------------------- | ----- |
| `nameOverride`     | String to partially override common.names.fullname template (will maintain the release name) | `""`  |
| `fullnameOverride` | String to fully override common.names.fullname template                                      | `""`  |

### Frank!Framework image parameters

| Name                | Description                                                | Value              |
| ------------------- | ---------------------------------------------------------- | ------------------ |
| `image.registry`    | Frank!Framework image registry                             | `wearefrank`       |
| `image.repository`  | Frank!Framework image repository                           | `openforms2xxllnc` |
| `image.tag`         | Frank!Framework image tag (immutable tags are recommended) | `""`               |
| `image.pullPolicy`  | Frank!Framework image pull policy                          | `IfNotPresent`     |
| `image.pullSecrets` | Frank!Framework image pull secrets                         | `[]`               |

### Frank! Configuration parameters

| Name                                                         | Description                                                                                                      | Value       |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- | ----------- |
| `frank.memory.percentage`                                    | Set if the values for the memory are in percentages                                                              | `false`     |
| `frank.memory.minimum`                                       | Sets the initial size of the heap that will be used by the Frank!Framework                                       | `1G`        |
| `frank.memory.maximum`                                       | Sets the maximum size of the heap that will be used by the Frank!Framework                                       | `1G`        |
| `frank.dtap.stage`                                           | (Required) Set the `DTAP` stage. Options: `LOC`, `DEV`, `TST`, `ACC`, `PRD`                                      | `""`        |
| `frank.dtap.side`                                            | Set the `DTAP` side of where the instance is running                                                             | `""`        |
| `frank.credentials.secret`                                   | Set the secret name of the existing secret                                                                       | `""`        |
| `frank.credentials.key`                                      | Set the key inside the secret that contains the data (e.g. `credentials.properties`)                             | `""`        |
| `frank.instance.name`                                        | Set the name of the Frank! instance (default is the `fullname`)                                                  | `""`        |
| `frank.configurations.names`                                 | Set the configurations to load. Leave empty to use the default                                                   | `[]`        |
| `frank.security.certificateStores`                           | Define certificate (key/trust) stores to mount in the resources folder of the Frank!                             | `[]`        |
| `frank.security.certificateStores.secretName`                | Name of the secret where the certificate store is located in                                                     | `""`        |
| `frank.security.certificateStores.key`                       | The key in the secret where the certificate store is located in                                                  | `""`        |
| `frank.security.certificateStores.resourceUrl`               | The path to the certificate store in the Resource folder, the key will be used as default value                  | `undefined` |
| `frank.security.http.authentication`                         | Set http authentication for the Frank!                                                                           | `false`     |
| `frank.security.http.localUsers`                             | Set localUsers who can log in on the Frank!                                                                      | `[]`        |
| `frank.security.http.localUsers.username`                    | Set the username of the user                                                                                     | `""`        |
| `frank.security.http.localUsers.password`                    | Set the password of the user                                                                                     | `""`        |
| `frank.security.http.localUsers.roles`                       | Set the roles of the user. Options: `IbisTester`, `IbisDataAdmin`, `IbisAdmin`, `IbisWebService`, `IbisObserver` | `[]`        |
| `frank.security.http.activeDirectory.enabled`                | Enable Active Directory for authentication                                                                       | `false`     |
| `frank.security.http.activeDirectory.url`                    | Set url for Active Directory                                                                                     | `""`        |
| `frank.security.http.activeDirectory.baseDn`                 | Set baseDn for Active Directory users                                                                            | `""`        |
| `frank.security.http.activeDirectory.roleMapping.tester`     | Map the role for Tester                                                                                          | `""`        |
| `frank.security.http.activeDirectory.roleMapping.dataAdmin`  | Map the role for DataAdmin                                                                                       | `""`        |
| `frank.security.http.activeDirectory.roleMapping.admin`      | Map the role for Admin                                                                                           | `""`        |
| `frank.security.http.activeDirectory.roleMapping.webService` | Map the role for WebService                                                                                      | `""`        |
| `frank.security.http.activeDirectory.roleMapping.observer`   | Map the role for Observer                                                                                        | `""`        |
| `frank.server.transactionManager`                            | Set the transaction manager for Tomcat. Options: `NARAYANA`, `BTM`, ``                                           | `""`        |
| `frank.properties`                                           | Set Yaml properties for configuring the Frank!Framework or configurations                                        | `{}`        |
| `frank.environmentVariables`                                 | Set extra environment variables for the Frank!                                                                   | `{}`        |
| `frank.javaOpts`                                             | Append custom options to the `JAVA_OPTS` environment variable for the Frank!                                     | `""`        |

### Frank!Framework Connection parameters

| Name                        | Description                                                                                                                                          | Value  |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| `connections.create`        | Create a `context.xml` and possibly overwrite the existing one, to configure the connections/resources.                                              | `true` |
| `connections.jdbc`          | Set multiple database connections. One connection should have an empty name, so it'll get picked up by default (unless `jdbc.required=false` is set) | `[]`   |
| `connections.jdbc.name`     | Name of the connection (leave empty to use default: `jdbc/${.Values.instance.name}` in lowercase)                                                    | `""`   |
| `connections.jdbc.type`     | DBMS type. Options: `oracle`, `mssql`, `mysql`, `mariadb`, `postgresql`, `db2`, `mongodb`                                                            | `""`   |
| `connections.jdbc.host`     | Host of where the database can be reached (like in the same cluster e.g. `<service>.<namespace>.svc.cluster.local`)                                  | `""`   |
| `connections.jdbc.post`     | Port for the database (leave empty for default)                                                                                                      | `""`   |
| `connections.jdbc.database` | Name of the database to use (default is `.Values.instance.name`)                                                                                     | `""`   |
| `connections.jdbc.username` | Username to connect to the database (or use string template for use with credentials e.g. `${database/username}`)                                    | `""`   |
| `connections.jdbc.password` | Password to connect to the database (or use string template for use with credentials e.g. `${database/password}`)                                    | `""`   |
| `connections.jdbc.ssl`      | Set to `true` is the connection uses SSL, default is `false`                                                                                         | `""`   |
| `connections.jms`           | Set multiple message services                                                                                                                        | `[]`   |
| `connections.jms.name`      | Name of the connection (leave empty to use default: `jms/${.Values.instance.name}` in lowercase)                                                     | `""`   |
| `connections.jms.type`      | MQ type. Options: `artemis`, `activemq`                                                                                                              | `""`   |
| `connections.jms.host`      | Host of where the MQ can be reached (like in the same cluster e.g. `<service>.<namespace>.svc.cluster.local`)                                        | `""`   |
| `connections.jms.post`      | Port for the MQ (leave empty for default)                                                                                                            | `""`   |

### Frank!Framework deployment parameters

The startup probe will enable blue-green deployment, which are great for uptime during upgrades and such.
It (and the liveness probe) will check if the console is accessible, until a better health endpoint is available.
The readiness probe will check if all adapters are running using the server health endpoint

| Name                                 | Description                                                                                                        | Value     |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------ | --------- |
| `replicaCount`                       | Number of Frank!Framework replicas to deploy                                                                       | `1`       |
| `startupProbe.initialDelaySeconds`   | Initial delay seconds for startupProbe                                                                             | `40`      |
| `startupProbe.periodSeconds`         | Period seconds for startupProbe                                                                                    | `10`      |
| `startupProbe.timeoutSeconds`        | Timeout seconds for startupProbe                                                                                   | `1`       |
| `startupProbe.failureThreshold`      | Failure threshold for startupProbe                                                                                 | `12`      |
| `startupProbe.successThreshold`      | Success threshold for startupProbe                                                                                 | `1`       |
| `livenessProbe.initialDelaySeconds`  | Initial delay seconds for livenessProbe                                                                            | `0`       |
| `livenessProbe.periodSeconds`        | Period seconds for livenessProbe                                                                                   | `10`      |
| `livenessProbe.timeoutSeconds`       | Timeout seconds for livenessProbe                                                                                  | `1`       |
| `livenessProbe.failureThreshold`     | Failure threshold for livenessProbe                                                                                | `12`      |
| `livenessProbe.successThreshold`     | Success threshold for livenessProbe                                                                                | `1`       |
| `readinessProbe.initialDelaySeconds` | Initial delay seconds for readinessProbe                                                                           | `0`       |
| `readinessProbe.periodSeconds`       | Period seconds for readinessProbe                                                                                  | `5`       |
| `readinessProbe.timeoutSeconds`      | Timeout seconds for readinessProbe                                                                                 | `1`       |
| `readinessProbe.failureThreshold`    | Failure threshold for readinessProbe                                                                               | `3`       |
| `readinessProbe.successThreshold`    | Success threshold for readinessProbe                                                                               | `1`       |
| `probesEnabled`                      | Toggle probes. This should only be used if a Frank! needs to be kept while in a bad state (for debugging purposes) | `{}`      |
| `probesEnabled.startupProbe`         | Toggle startupProbe                                                                                                | `{}`      |
| `probesEnabled.livenessProbe`        | Toggle livenessProbe                                                                                               | `{}`      |
| `probesEnabled.readinessProbe`       | Toggle readinessProbe                                                                                              | `{}`      |
| `resources`                          | Set the resources for the Frank!Framework containers                                                               | `{}`      |
| `resources.limits`                   | The resources limits for the Frank!Framework containers                                                            | `""`      |
| `resources.requests.memory`          | The requested memory for the Frank!Framework containers                                                            | `""`      |
| `resources.requests.cpu`             | The requested cpu for the Frank!Framework containers                                                               | `""`      |
| `terminationGracePeriodSeconds`      | Number of seconds after which pods are forcefully killed                                                           | `60`      |
| `terminationGracePeriodSeconds`      | Note: Lower values may cause running adapters to fail                                                              |           |
| `nodeSelector`                       | Node labels for pod assignment                                                                                     | `{}`      |
| `tolerations`                        | Set tolerations for pod assignment                                                                                 | `[]`      |
| `affinity`                           | Set affinity for pod assignment                                                                                    | `{}`      |
| `timeZone`                           | used for database connection and log timestamps                                                                    | `Etc/UTC` |

### Traffic Exposure Parameters

| Name                           | Description                                                                                                                      | Value       |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `service.type`                 | Frank!Framework service type                                                                                                     | `ClusterIP` |
| `service.port`                 | Frank!Framework service port                                                                                                     | `80`        |
| `ingress.enabled`              | Enable ingress record generation for Frank!                                                                                      | `false`     |
| `ingress.className`            | IngressClass that will be used to implement the Ingress (Kubernetes 1.18+)                                                       | `""`        |
| `ingress.annotations`          | Additional annotations for the Ingress resource. To enable certificate autogeneration, place here your cert-manager annotations. | `{}`        |
| `ingress.hosts`                | Set hosts for ingress                                                                                                            | `[]`        |
| `ingress.hosts.host`           | Set hostname                                                                                                                     | `""`        |
| `ingress.hosts.paths`          | Set multiple paths                                                                                                               | `[]`        |
| `ingress.hosts.paths.path`     | Set path (context url)                                                                                                           | `""`        |
| `ingress.hosts.paths.pathType` | Set type of path                                                                                                                 | `""`        |
| `ingress.tls`                  | Define tls secrets for hosts (implementation not done yet)                                                                       | `[]`        |

### Other Parameters

| Name                         | Description                                               | Value  |
| ---------------------------- | --------------------------------------------------------- | ------ |
| `serviceAccount.create`      | Enable creation of ServiceAccount for Frank!Framework pod | `true` |
| `serviceAccount.annotations` | Additional custom annotations for the ServiceAccount      | `{}`   |
| `serviceAccount.name`        | The name of the ServiceAccount to use.                    | `""`   |
| `podAnnotations`             | Annotations for Frank!Framework pods                      | `{}`   |
| `podLabels`                  | Extra labels for Frank!Framework pods                     | `{}`   |
| `podSecurityContext`         | Set Frank!Framework pod's Security Context                | `{}`   |
| `securityContext`            | Set Frank!Framework container's Security Context          | `{}`   |

### Persistence

Persistence is used for keeping heap dumps. They can be found at `/heap-dumps` with persistence enabled.
Otherwise, they can be found at `/usr/local/tomcat/logs`

| Name                        | Description                                                                        | Value   |
| --------------------------- | ---------------------------------------------------------------------------------- | ------- |
| `persistence.enabled`       | Enable persistence using Persistent Volume Claims                                  | `false` |
| `persistence.storageClass`  | Persistent Volume storage class                                                    | `""`    |
| `persistence.accessModes`   | Persistent Volume access modes                                                     | `[]`    |
| `persistence.size`          | Persistent Volume size                                                             | `5Gi`   |
| `persistence.dataSource`    | Custom PVC data source                                                             | `{}`    |
| `persistence.existingClaim` | The name of an existing PVC to use for persistence                                 | `""`    |
| `persistence.selector`      | Selector to match an existing Persistent Volume for the Frank!Framework's data PVC | `{}`    |
| `persistence.annotations`   | Persistent Volume Claim annotations                                                | `{}`    |

### Openforms2xxllnc


### Connections

| Name                                                                           | Description                                                                                                       | Value         |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- | ------------- |
| `openforms2xxllnc.connections.beantwoordVraag.endpoint`                        | Endpoint at which the zs-dms BeantwoordVraag binding is served.                                                   | `""`          |
| `openforms2xxllnc.connections.beantwoordVraag.timeout`                         | Timeout used zs-dms BeantwoordVraag calls.                                                                        | `60000`       |
| `openforms2xxllnc.connections.beantwoordVraag.authAlias`                       | AuthAlias used zs-dms BeantwoordVraag calls.                                                                      | `zaakdms-api` |
| `openforms2xxllnc.connections.ontvangAsynchroon.endpoint`                      | Endpoint at which the zs-dms OntvangAsynchroon binding is served.                                                 | `""`          |
| `openforms2xxllnc.connections.ontvangAsynchroon.timeout`                       | Timeout used zs-dms OntvangAsynchroon calls.                                                                      | `60000`       |
| `openforms2xxllnc.connections.ontvangAsynchroon.authAlias`                     | AuthAlias used zs-dms OntvangAsynchroon calls.                                                                    | `zaakdms-api` |
| `openforms2xxllnc.connections.vrijeBerichten.endpoint`                         | Endpoint at which the zs-dms VrijBericht binding is served.                                                       | `""`          |
| `openforms2xxllnc.connections.vrijeBerichten.timeout`                          | Timeout used zs-dms VrijBericht calls.                                                                            | `60000`       |
| `openforms2xxllnc.connections.vrijeBerichten.authAlias`                        | AuthAlias used zs-dms VrijBericht calls.                                                                          | `zaakdms-api` |
| `openforms2xxllnc.connections.notificatiesApi.rootUrl`                         | Root url of the 'Notificaties API' that is used to subscribe at.                                                  | `""`          |
| `openforms2xxllnc.connections.notificatiesApi.timeout`                         | Timeout used in 'Notificaties API' calls.                                                                         | `60000`       |
| `openforms2xxllnc.connections.notificatiesApi.authType`                        | Options: 'jwt', 'basic', 'value'. 'value' uses the password field of the given authAlias as Authorization header. | `""`          |
| `openforms2xxllnc.connections.notificatiesApi.authAlias`                       | Reference to an auth alias to be used as credentials for this api.                                                | `""`          |
| `openforms2xxllnc.connections.notificatiesApi.subscription.callback`           | Fully qualified url to the notification callback of openforms2xxllnc.                                             | `""`          |
| `openforms2xxllnc.connections.notificatiesApi.subscription.authAlias`          | Reference to an auth alias to be used as authorization key for calling the callback endpoint.                     | `""`          |
| `openforms2xxllnc.connections.notificatiesApi.subscription.filters.objectType` | Url of the objecttype to filter the notifications on.                                                             | `""`          |
| `openforms2xxllnc.connections.documentenApi.timeout`                           | Timeout used in 'Documenten API' calls.                                                                           | `60000`       |
| `openforms2xxllnc.connections.documentenApi.authType`                          | Options: 'jwt', 'basic', 'value'. 'value' uses the password field of the given authAlias as Authorization header. | `""`          |
| `openforms2xxllnc.connections.documentenApi.authAlias`                         | Reference to an auth alias to be used as credentials for this api.                                                | `""`          |
| `openforms2xxllnc.connections.objectsApi.timeout`                              | Timeout used in 'Objects API' calls.                                                                              | `60000`       |
| `openforms2xxllnc.connections.objectsApi.authType`                             | Options: 'jwt', 'basic', 'value'. 'value' uses the password field of the given authAlias as Authorization header. | `""`          |
| `openforms2xxllnc.connections.objectsApi.authAlias`                            | Reference to an auth alias to be used as credentials for this api.                                                | `""`          |
| `openforms2xxllnc.connections.noReplySmtp.enabled`                             | Enable connecting to the configured SMTP server/replay.                                                           | `false`       |
| `openforms2xxllnc.connections.noReplySmtp.host`                                | Host of the SMTP server/relay.                                                                                    | `""`          |
| `openforms2xxllnc.connections.noReplySmtp.port`                                | Port of the SMTP server/relay.                                                                                    | `587`         |
| `openforms2xxllnc.connections.noReplySmtp.useSsl`                              | Connect securely to the SMTP server/relay with SSL.                                                               | `true`        |
| `openforms2xxllnc.connections.noReplySmtp.authAlias`                           | Reference to an auth alias to be used as credentials for authorizing with the SMTP server/relay.                  | `""`          |
| `openforms2xxllnc.connections.noReplySmtp.defaultFromName`                     | The default no-reply sender's name that is shown with the no-reply sender's e-mail address.                       | `""`          |
| `openforms2xxllnc.connections.noReplySmtp.defaultFromAddress`                  | The default no-reply sender's e-mail address that used when sending e-mails.                                      | `""`          |
| `openforms2xxllnc.connections.noReplySmtp.signatureFromName`                   | The no-reply sender's name used in the signature of the e-mail body.                                              | `""`          |
| `openforms2xxllnc.connections.noReplySmtp.timeout`                             | Timeout used when sending emails.                                                                                 | `60000`       |
| `openforms2xxllnc.connections.noReplySmtp.authType`                            | Options: 'jwt', 'basic', 'value'. 'value' uses the password field of the given authAlias as Authorization header. | `""`          |

### Mail Templates

| Name                                                   | Description                                                                                | Value |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------ | ----- |
| `openforms2xxllnc.mailTemplates.existingConfigMap`     | The name of the configmap containing the mail templates.                                   | `""`  |
| `openforms2xxllnc.mailTemplates.templates`             | Mail templates that can be referenced by name on a variety of functional error scenario's. | `[]`  |
| `openforms2xxllnc.mailTemplates.templates.name`        | Name of the mail template that can be referenced.                                          | `""`  |
| `openforms2xxllnc.mailTemplates.templates.subject`     | Mail subject text.                                                                         | `""`  |
| `openforms2xxllnc.mailTemplates.templates.messageType` | ContentType of the message. Options: 'text/plain', 'text/html'.                            | `""`  |
| `openforms2xxllnc.mailTemplates.templates.message`     | Mail message body. A limit degree of variable substitution is available.                   | `""`  |

### Workflows

| Name                                                                                   | Description                                                                            | Value   |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------- |
| `openforms2xxllnc.workflows.stuurgegevens.zender.organisatie`                          | Gemeentecode of the gemeente sending the zs-dms requests.                              | `""`    |
| `openforms2xxllnc.workflows.stuurgegevens.zender.applicatie`                           | Application name used when sending the zs-dms requests.                                | `""`    |
| `openforms2xxllnc.workflows.stuurgegevens.ontvanger.organisatie`                       | Gemeentecode of the gemeente receiving the zs-dms requests.                            | `""`    |
| `openforms2xxllnc.workflows.stuurgegevens.ontvanger.applicatie`                        | Application name of the receiving zs-dms application.                                  | `""`    |
| `openforms2xxllnc.workflows.autoRetries.enabled`                                       | Enable automatic retries. For all workflows(unless overriden).                         | `true`  |
| `openforms2xxllnc.workflows.autoRetries.cronExpression`                                | Cron expression used for retry interval/schedule. For all workflows(unless overriden). | `""`    |
| `openforms2xxllnc.workflows.autoRetries.maxRetries`                                    | Maximum amount an errorstore item is retried. For all workflows(unless overriden).     | `5`     |
| `openforms2xxllnc.workflows.autoRetries.workflowSelector.enabled`                      | Enable automatic retries. Override for this specific workflow.                         | `true`  |
| `openforms2xxllnc.workflows.autoRetries.workflowSelector.cronExpression`               | Cron expression used for retry interval/schedule. Override for this specific workflow. | `""`    |
| `openforms2xxllnc.workflows.autoRetries.workflowSelector.maxRetries`                   | Maximum amount an errorstore item is retried. Override for this specific workflow.     | `5`     |
| `openforms2xxllnc.workflows.autoRetries.addDocumentsToCase.enabled`                    | Enable automatic retries. Override for this specific workflow.                         | `true`  |
| `openforms2xxllnc.workflows.autoRetries.addDocumentsToCase.cronExpression`             | Cron expression used for retry interval/schedule. Override for this specific workflow. | `""`    |
| `openforms2xxllnc.workflows.autoRetries.addDocumentsToCase.maxRetries`                 | Maximum amount an errorstore item is retried. Override for this specific workflow.     | `5`     |
| `openforms2xxllnc.workflows.autoRetries.sendNoReplyUserEmail.enabled`                  | Enable automatic retries. Override for this specific workflow.                         | `true`  |
| `openforms2xxllnc.workflows.autoRetries.sendNoReplyUserEmail.cronExpression`           | Cron expression used for retry interval/schedule. Override for this specific workflow. | `""`    |
| `openforms2xxllnc.workflows.autoRetries.sendNoReplyUserEmail.maxRetries`               | Maximum amount an errorstore item is retried. Override for this specific workflow.     | `5`     |
| `openforms2xxllnc.workflows.scheduledStartReceiver.workflowSelector.enabled`           | Enable scheduled start the receiver of this specific workflow.                         | `false` |
| `openforms2xxllnc.workflows.scheduledStartReceiver.workflowSelector.cronExpression`    | Cron expression used to schedule starting the receiver of this specific workflow.      | `""`    |
| `openforms2xxllnc.workflows.scheduledStopReceiver.workflowSelector.enabled`            | Enable scheduled stop the receiver of this specific workflow.                          | `false` |
| `openforms2xxllnc.workflows.scheduledStopReceiver.workflowSelector.cronExpression`     | Cron expression used to schedule stopping the receiver of this specific workflow.      | `""`    |
| `openforms2xxllnc.workflows.onErrorActions.onCaseNotFound.sendEmail`                   | Enable sending a mail to the form initiator when this specific error occurs.           | `false` |
| `openforms2xxllnc.workflows.onErrorActions.onCaseNotFound.templateName`                | Name of the mail template to be used when this specific error occurs.                  | `""`    |
| `openforms2xxllnc.workflows.onErrorActions.onSubjectNotEqualsCaseSubject.sendEmail`    | Enable sending a mail to the form initiator when this specific error occurs.           | `false` |
| `openforms2xxllnc.workflows.onErrorActions.onSubjectNotEqualsCaseSubject.templateName` | Name of the mail template to be used when this specific error occurs.                  | `""`    |
| `openforms2xxllnc.workflows.onErrorActions.onCaseClosed.sendEmail`                     | Enable sending a mail to the form initiator when this specific error occurs.           | `false` |
| `openforms2xxllnc.workflows.onErrorActions.onCaseClosed.templateName`                  | Name of the mail template to be used when this specific error occurs.                  | `""`    |

## Configuration and installation details

### DTAP Stage

The Frank!Framework will start with different settings enabled, depending on what DTAP stage is configured. 

For more information about DTAP stages read: https://frank-manual.readthedocs.io/en/latest/deploying/dtapAndProperties.html

## Notable changes

### 0.1.5

The `.Values.frank.memory` notation has been changed. It is now possible to define a minimum and a maximum, and to set percentages.

### 0.1.4

The `.Values.frank.dtap.stage` and `.Values.frank.dtap.side` are now empty by default.

* `.Values.frank.dtap.stage` is now required and should be set to the right stage. Read more in the [Installation details](#dtap-stage)
* `.Values.frank.dtap.side` will default to the release namespace deployed in.
