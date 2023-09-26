# :bridge_at_night: ZaakBrug

An app for Dutch municipalities that supports the transition from "zaak- en documentatieservices" (zds) to "zaakgericht werken" (zgw).

[ZaakBrug source on GitHub](https://github.com/ibissource/zaakbrug)

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

## Parameters

### Common parameters

| Name               | Description                                                                               | Value |
| ------------------ | ----------------------------------------------------------------------------------------- | ----- |
| `nameOverride`     | String to partially override ff-common.fullname template (will maintain the release name) | `""`  |
| `fullnameOverride` | String to fully override ff-common.fullname template                                      | `""`  |

### Frank!Framework image parameters

| Name                | Description                                                | Value          |
| ------------------- | ---------------------------------------------------------- | -------------- |
| `image.registry`    | Frank!Framework image registry                             | `wearefrank`   |
| `image.repository`  | Frank!Framework image repository                           | `zaakbrug`     |
| `image.tag`         | Frank!Framework image tag (immutable tags are recommended) | `""`           |
| `image.pullPolicy`  | Frank!Framework image pull policy                          | `IfNotPresent` |
| `image.pullSecrets` | Frank!Framework image pull secrets                         | `[]`           |

### Frank! Configuration parameters

| Name                                                         | Description                                                                                                      | Value   |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- | ------- |
| `frank.memory`                                               | Sets the initial and maximum size of the heap that will be used by the Frank!Framework                           | `4G`    |
| `frank.dtap.stage`                                           | (Required) Set the `DTAP` stage. Options: `LOC`, `DEV`, `TST`, `ACC`, `PRD`                                      | `""`    |
| `frank.dtap.side`                                            | Set the `DTAP` side of where the instance is running                                                             | `""`    |
| `frank.credentials.secret`                                   | Set the secret name of the existing secret                                                                       | `""`    |
| `frank.credentials.key`                                      | Set the key inside the secret that contains the data (e.g. `credentials.properties`)                             | `""`    |
| `frank.instance.name`                                        | Set the name of the Frank! instance (default is the `fullname`)                                                  | `""`    |
| `frank.configurations.names`                                 | Set the configurations to load. Leave empty to use the default                                                   | `[]`    |
| `frank.security.http.authentication`                         | Set http authentication for the Frank!                                                                           | `false` |
| `frank.security.http.localUsers`                             | Set localUsers who can log in on the Frank!                                                                      | `[]`    |
| `frank.security.http.localUsers.username`                    | Set the username of the user                                                                                     | `""`    |
| `frank.security.http.localUsers.password`                    | Set the password of the user                                                                                     | `""`    |
| `frank.security.http.localUsers.roles`                       | Set the roles of the user. Options: `IbisTester`, `IbisDataAdmin`, `IbisAdmin`, `IbisWebService`, `IbisObserver` | `[]`    |
| `frank.security.http.activeDirectory.enabled`                | Enable Active Directory for authentication                                                                       | `false` |
| `frank.security.http.activeDirectory.url`                    | Set url for Active Directory                                                                                     | `""`    |
| `frank.security.http.activeDirectory.baseDn`                 | Set baseDn for Active Directory users                                                                            | `""`    |
| `frank.security.http.activeDirectory.roleMapping.tester`     | Map the rol for Tester                                                                                           | `""`    |
| `frank.security.http.activeDirectory.roleMapping.dataAdmin`  | Map the rol for DataAdmin                                                                                        | `""`    |
| `frank.security.http.activeDirectory.roleMapping.admin`      | Map the rol for Admin                                                                                            | `""`    |
| `frank.security.http.activeDirectory.roleMapping.webService` | Map the rol for WebService                                                                                       | `""`    |
| `frank.security.http.activeDirectory.roleMapping.observer`   | Map the rol for Observer                                                                                         | `""`    |
| `frank.server.transactionManager`                            | Set the transaction manager for Tomcat. Options: `NARAYANA`, `BTM`, ``                                           | `""`    |
| `frank.environmentVariables`                                 | Set extra environment variables for the Frank!                                                                   | `{}`    |

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
| `connections.jms`           | Set multiple massage services                                                                                                                        | `[]`   |
| `connections.jms.name`      | Name of the connection (leave empty to use default: `jms/${.Values.instance.name}` in lowercase)                                                     | `""`   |
| `connections.jms.type`      | MQ type. Options: `artemis`, `activemq`                                                                                                              | `""`   |
| `connections.jms.host`      | Host of where the MQ can be reached (like in the same cluster e.g. `<service>.<namespace>.svc.cluster.local`)                                        | `""`   |
| `connections.jms.post`      | Port for the MQ (leave empty for default)                                                                                                            | `""`   |

### Frank!Framework deployment parameters

| Name                                | Description                                             | Value     |
| ----------------------------------- | ------------------------------------------------------- | --------- |
| `replicaCount`                      | Number of Frank!Framework replicas to deploy            | `1`       |
| `livenessProbe.initialDelaySeconds` | Initial delay seconds for livenessProbe                 | `40`      |
| `livenessProbe.periodSeconds`       | Period seconds for livenessProbe                        | `10`      |
| `livenessProbe.timeoutSeconds`      | Timeout seconds for livenessProbe                       | `1`       |
| `livenessProbe.failureThreshold`    | Failure threshold for livenessProbe                     | `6`       |
| `livenessProbe.successThreshold`    | Success threshold for livenessProbe                     | `1`       |
| `resources`                         | Set the resources for the Frank!Framework containers    | `{}`      |
| `resources.limits`                  | The resources limits for the Frank!Framework containers | `""`      |
| `resources.requests.memory`         | The requested memory for the Frank!Framework containers | `""`      |
| `resources.requests.cpu`            | The requested cpu for the Frank!Framework containers    | `""`      |
| `nodeSelector`                      | Node labels for pod assignment                          | `{}`      |
| `tolerations`                       | Set tolerations for pod assignment                      | `[]`      |
| `affinity`                          | Set affinity for pod assignment                         | `{}`      |
| `timeZone`                          | used for database connection and log timestamps         | `Etc/UTC` |

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

### ZaakBrug

Following sections are about the configuration for the ZaakBrug

| Name                                                              | Description                                                                                    | Value                                                  |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `zaakbrug.zds.timezone`                                           | The timezone of the receiving zds service                                                      | `Etc/UTC`                                              |
| `zaakbrug.soap.beantwoordVraag.endpoint`                          | Set the endpoint the service should be available at                                            | `translate/generic/zds/BeantwoordVraag`                |
| `zaakbrug.soap.beantwoordVraag.validationSoftFail`                | Incoming messages are validated, if set to `true` the message still gets processed if it fails | `false`                                                |
| `zaakbrug.soap.beantwoordVraag_v2.endpoint`                       | Set the endpoint the service should be available at                                            | `translate/generic/zds/v2/BeantwoordVraag`             |
| `zaakbrug.soap.beantwoordVraag_v2.validationSoftFail`             | Incoming messages are validated, if set to `true` the message still gets processed if it fails | `false`                                                |
| `zaakbrug.soap.ontvangAsynchroon.endpoint`                        | Set the endpoint the service should be available at                                            | `translate/generic/zds/OntvangAsynchroon`              |
| `zaakbrug.soap.ontvangAsynchroon.validationSoftFail`              | Incoming messages are validated, if set to `true` the message still gets processed if it fails | `false`                                                |
| `zaakbrug.soap.ontvangAsynchroonMutatie_v2.endpoint`              | Set the endpoint the service should be available at                                            | `translate/generic/zds/v2/OntvangAsynchroonMutatie`    |
| `zaakbrug.soap.ontvangAsynchroonMutatie_v2.validationSoftFail`    | Incoming messages are validated, if set to `true` the message still gets processed if it fails | `false`                                                |
| `zaakbrug.soap.ontvangAsynchroonOverdragen_v2.endpoint`           | Set the endpoint the service should be available at                                            | `translate/generic/zds/v2/OntvangAsynchroonOverdragen` |
| `zaakbrug.soap.ontvangAsynchroonOverdragen_v2.validationSoftFail` | Incoming messages are validated, if set to `true` the message still gets processed if it fails | `false`                                                |
| `zaakbrug.soap.vrijeBerichten.endpoint`                           | Set the endpoint the service should be available at                                            | `translate/generic/zds/VrijBericht`                    |
| `zaakbrug.soap.vrijeBerichten.validationSoftFail`                 | Incoming messages are validated, if set to `true` the message still gets processed if it fails | `false`                                                |
| `zaakbrug.soap.vrijeBerichten_v2.endpoint`                        | Set the endpoint the service should be available at                                            | `translate/generic/zds/v2/VrijBericht`                 |
| `zaakbrug.soap.vrijeBerichten_v2.validationSoftFail`              | Incoming messages are validated, if set to `true` the message still gets processed if it fails | `false`                                                |

### Identificatie Templates

Templates used for generating zaak- and documentidentificatie<br/>
The syntax for variable substitution is as follows {[variable-name][:formatting-string]}

Variables:
- id          Auto-incrementing identifier with 'D' as formatting option, indicating the amount of digits.
example: {id:D5} with id-123 will result in '00123'
- datetime    The current date and time with '[Y' as formatting option, according to
(https://www.oreilly.com/library/view/xslt-2nd-edition/9780596527211/ch04s05.html).
Only the '[Y0001]' is currently implemented
example: {datetime:[Y001]} with datetime=14-03-2023 produces '2023'

| Name                                         | Description                        | Value                          |
| -------------------------------------------- | ---------------------------------- | ------------------------------ |
| `zaakbrug.zgw.zaakIdentificatieTemplate`     | Template for zaakidentificatie     | `ZK{datetime:[Y0001]}-{id:D5}` |
| `zaakbrug.zgw.documentIdentificatieTemplate` | Template for documentidentificatie | `DC{datetime:[Y0001]}-{id:D5}` |
| `zaakbrug.zgw.besluitIdentificatieTemplate`  | Template for besluitidentificatie  | `BS{datetime:[Y0001]}-{id:D5}` |

### Api Endpoints

Make sure that all Url's contain two "parts" e.g. `openzaak-nginx.zaakbrug`. Openzaak can't use a single part domain.

| Name                                   | Description                                                                                                      | Value                                 |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| `zaakbrug.zgw.zakenApi.rootUrl`        | Endpoint for the zaken API                                                                                       | `http://open-zaak/zaken/api/v1/`      |
| `zaakbrug.zgw.zakenApi.authType`       | Options: 'jwt', 'basic', 'value'. 'value' uses the password field of the given authAlias as Authorization header | `jwt`                                 |
| `zaakbrug.zgw.zakenApi.authAlias`      | Reference to an auth alias configured in credentials.properties                                                  | `zaken-api.jwt`                       |
| `zaakbrug.zgw.catalogiApi.rootUrl`     | Endpoint for the catalogi API                                                                                    | `http://open-zaak/catalogi/api/v1/`   |
| `zaakbrug.zgw.catalogiApi.authType`    | Options: 'jwt', 'basic', 'value'. 'value' uses the password field of the given authAlias as Authorization header | `jwt`                                 |
| `zaakbrug.zgw.catalogiApi.authAlias`   | Reference to an auth alias configured in credentials.properties                                                  | `zaken-api.jwt`                       |
| `zaakbrug.zgw.documentenApi.rootUrl`   | Endpoint for the documenten API                                                                                  | `http://open-zaak/documenten/api/v1/` |
| `zaakbrug.zgw.documentenApi.authType`  | Options: 'jwt', 'basic', 'value'. 'value' uses the password field of the given authAlias as Authorization header | `jwt`                                 |
| `zaakbrug.zgw.documentenApi.authAlias` | Reference to an auth alias configured in credentials.properties                                                  | `zaken-api.jwt`                       |
| `zaakbrug.zgw.besluitenApi.rootUrl`    | Endpoint for the besluiten API                                                                                   | `http://open-zaak/besluiten/api/v1/`  |
| `zaakbrug.zgw.besluitenApi.authType`   | Options: 'jwt', 'basic', 'value'. 'value' uses the password field of the given authAlias as Authorization header | `jwt`                                 |
| `zaakbrug.zgw.besluitenApi.authAlias`  | Reference to an auth alias configured in credentials.properties                                                  | `zaken-api.jwt`                       |

### Globals

| Name                                          | Description                       | Value |
| --------------------------------------------- | --------------------------------- | ----- |
| `zaakbrug.globals.organizations`              | Map gemeentecode and RSIN         | `[]`  |
| `zaakbrug.globals.organizations.gemeenteNaam` | Name for organisation             | `""`  |
| `zaakbrug.globals.organizations.gemeenteCode` | Gemeentecode to map to RSIN       | `""`  |
| `zaakbrug.globals.organizations.RSIN`         | RSIN to be mapped to gemeentecode | `""`  |

### Profiles

| Name                                                                     | Description                                | Value       |
| ------------------------------------------------------------------------ | ------------------------------------------ | ----------- |
| `zaakbrug.profiles.profile`                                              | Translation profile, specific per zaakType | `[]`        |
| `zaakbrug.profiles.profile.zaakTypeIdentificatie`                        | Zaaktype the profile is for                | `""`        |
| `zaakbrug.profiles.profile.endCaseEndDate`                               |                                            | `undefined` |
| `zaakbrug.profiles.profile.endCaseEndDate.coalesceResultaat`             | Options: `Onbekend`, `Toegekend`           | `""`        |
| `zaakbrug.profiles.profile.endDateAndResultLastStatus`                   |                                            | `undefined` |
| `zaakbrug.profiles.profile.endDateAndResultLastStatus.coalesceResultaat` | Options: `Onbekend`, `Toegekend`           | `""`        |

### Staging

Staging is needed if you want to use zgw-to-zds.

Following sections are about configuring OpenZaak (used as staging zaaksysteem) and the API proxy.<br />
Ref: https://open-zaak.readthedocs.io/en/stable/installation/kubernetes.html

OpenZaak needs a Postgres database with PostGIS<br />
ref: https://open-zaak.readthedocs.io/en/stable/installation/prerequisites.html#postgresql-with-postgis

| Name                                            | Description                                                                                                                      | Value                                                                                                                                                      |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `staging.enabled`                               | Enable the staging environment                                                                                                   | `false`                                                                                                                                                    |
| `staging.zakenApi.rootUrl`                      | Endpoint of the zaken API of the staging zaaksysteem                                                                             | `http://zaakbrug-staging-nginx.zaakbrug/zaken/api/v1/`                                                                                                     |
| `staging.documentenApi.rootUrl`                 | Endpoint of the documenten API of the staging zaaksysteem                                                                        | `http://zaakbrug-staging-nginx.zaakbrug/documenten/api/v1/`                                                                                                |
| `staging.catalogiApi.rootUrl`                   | Endpoint of the catalogi API of the staging zaaksysteem                                                                          | `http://zaakbrug-staging-nginx.zaakbrug/catalogi/api/v1/`                                                                                                  |
| `staging.besluitenApi.rootUrl`                  | Endpoint of the besluiten API of the staging zaaksysteem                                                                         | `http://zaakbrug-staging-nginx.zaakbrug/besluiten/api/v1/`                                                                                                 |
| `staging.extraEnvVars`                          | Extra environment variables that should be set on the zaaksysteem                                                                | `[]`                                                                                                                                                       |
| `staging.extraEnvVars`                          | The notifications should be disabled                                                                                             |                                                                                                                                                            |
| `staging.extraEnvVars.name`                     | Name of the variable                                                                                                             | `""`                                                                                                                                                       |
| `staging.extraEnvVars.value`                    | Value of the variable                                                                                                            | `undefined`                                                                                                                                                |
| `staging.settings.useXForwardedHost`            | Add `X-Forwarded-Host` to proxy header                                                                                           | `false`                                                                                                                                                    |
| `staging.settings.useXForwardedHost`            | Leave this to false, so absolute URL's make their way though te reverse proxies.                                                 |                                                                                                                                                            |
| `staging.settings.debug`                        | Set the debug mode of the zaaksysteem                                                                                            | `false`                                                                                                                                                    |
| `staging.settings.allowedHosts`                 | Set the (v)hosts that need to be accessible for OpenZaak                                                                         | `zaakbrug-staging.zaakbrug,zaakbrug-staging-nginx.zaakbrug,zaakbrug-staging.zaakbrug.svc.cluster.local,zaakbrug-staging-nginx.svc.cluster.local,localhost` |
| `staging.settings.allowedHosts`                 | Add the ingress route if you have one. Change the service names and include namespace                                            |                                                                                                                                                            |
| `staging.settings.secretKey`                    | Secret key that’s used for certain cryptographic utilities. Use [Djecrety](https://djecrety.ir/) to generate one                 | `""`                                                                                                                                                       |
| `staging.settings.database.host`                | Host for the database                                                                                                            | `""`                                                                                                                                                       |
| `staging.settings.database.port`                | Port for the database                                                                                                            | `5432`                                                                                                                                                     |
| `staging.settings.database.username`            | User to log in to the database                                                                                                   | `""`                                                                                                                                                       |
| `staging.settings.database.password`            | Password for the user                                                                                                            | `""`                                                                                                                                                       |
| `staging.settings.database.name`                | Name of the database                                                                                                             | `""`                                                                                                                                                       |
| `staging.settings.database.sslmode`             | Configure SSLMode                                                                                                                | `prefer`                                                                                                                                                   |
| `staging.persistence.enabled`                   | Toggle persistence for the staging zaaksysteem                                                                                   | `true`                                                                                                                                                     |
| `staging.persistence.storageClassName`          | Configure which storage class should be used                                                                                     | `""`                                                                                                                                                       |
| `staging.apiProxy.nameOverride`                 | String to partially override zaakbrug.apiProxyFullname template (will maintain the release name)                                 | `""`                                                                                                                                                       |
| `staging.apiProxy.fullnameOverride`             | String to fully override zaakbrug.apiProxyFullname template                                                                      | `""`                                                                                                                                                       |
| `staging.apiProxy.replicaCount`                 | Number of API proxy replicas to deploy                                                                                           | `1`                                                                                                                                                        |
| `staging.apiProxy.podAnnotations`               | Annotations for API proxy pods                                                                                                   | `{}`                                                                                                                                                       |
| `staging.apiProxy.podLabels`                    | Extra labels for API proxy pods                                                                                                  | `{}`                                                                                                                                                       |
| `staging.apiProxy.securityContext`              | Set API proxy container's Security Context                                                                                       | `{}`                                                                                                                                                       |
| `staging.apiProxy.image.registry`               | API proxy image registry                                                                                                         | `""`                                                                                                                                                       |
| `staging.apiProxy.image.repository`             | API proxy image repository                                                                                                       | `nginxinc/nginx-unprivileged`                                                                                                                              |
| `staging.apiProxy.image.tag`                    | API proxy image tag (immutable tags are recommended)                                                                             | `stable`                                                                                                                                                   |
| `staging.apiProxy.image.pullPolicy`             | API proxy image pull policy                                                                                                      | `IfNotPresent`                                                                                                                                             |
| `staging.apiProxy.image.pullSecrets`            | API proxy image pull secrets                                                                                                     | `[]`                                                                                                                                                       |
| `staging.apiProxy.resources`                    | Set the resources for the API proxy containers                                                                                   | `{}`                                                                                                                                                       |
| `staging.apiProxy.resources.limits`             | The resources limits for the API proxy containers                                                                                | `""`                                                                                                                                                       |
| `staging.apiProxy.resources.requests.memory`    | The requested memory for the API proxy containers                                                                                | `""`                                                                                                                                                       |
| `staging.apiProxy.resources.requests.cpu`       | The requested cpu for the API proxy containers                                                                                   | `""`                                                                                                                                                       |
| `staging.apiProxy.existingConfigmap`            | Set the name of an existing config-map to use as configuration for the API proxy                                                 | `""`                                                                                                                                                       |
| `staging.apiProxy.service.type`                 | API proxy service type                                                                                                           | `ClusterIP`                                                                                                                                                |
| `staging.apiProxy.service.port`                 | API proxy service port                                                                                                           | `80`                                                                                                                                                       |
| `staging.apiProxy.service.annotations`          | Annotations for the API proxy service                                                                                            | `{}`                                                                                                                                                       |
| `staging.apiProxy.ingress.enabled`              | Enable ingress record generation for Frank!                                                                                      | `false`                                                                                                                                                    |
| `staging.apiProxy.ingress.className`            | IngressClass that will be used to implement the Ingress (Kubernetes 1.18+)                                                       | `""`                                                                                                                                                       |
| `staging.apiProxy.ingress.annotations`          | Additional annotations for the Ingress resource. To enable certificate autogeneration, place here your cert-manager annotations. | `{}`                                                                                                                                                       |
| `staging.apiProxy.ingress.hosts`                | Set hosts for ingress                                                                                                            | `[]`                                                                                                                                                       |
| `staging.apiProxy.ingress.hosts.host`           | Set hostname                                                                                                                     | `""`                                                                                                                                                       |
| `staging.apiProxy.ingress.hosts.paths`          | Set multiple paths                                                                                                               | `[]`                                                                                                                                                       |
| `staging.apiProxy.ingress.hosts.paths.path`     | Set path (context url)                                                                                                           | `""`                                                                                                                                                       |
| `staging.apiProxy.ingress.hosts.paths.pathType` | Set type of path                                                                                                                 | `""`                                                                                                                                                       |
| `staging.apiProxy.ingress.tls`                  | Define tls secrets for hosts (implementation not done yet)                                                                       | `[]`                                                                                                                                                       |

## Configuration and installation details

### DTAP Stage

The Frank!Framework will start with different settings enabled, depending on what DTAP stage is configured.

For more information about DTAP stages read: https://frank-manual.readthedocs.io/en/latest/deploying/dtapAndProperties.html

## Notable changes

### 2.0.10

The `.Values.frank.dtap.stage` and `.Values.frank.dtap.side` are now empty by default.

* `.Values.frank.dtap.stage` is now required and should be set to the right stage. Read more in the [Installation details](#dtap-stage)
* `.Values.frank.dtap.side` will default to the release namespace deployed in.
