## Troubleshooting: `helm dependency update` faalt

De chart hangt af van de officiële `apisix` chart via `https://apache.github.io/apisix-helm-chart`.
Deze URL heeft af en toe DNS-resolutieproblemen (zie [apache/apisix-helm-chart#959](https://github.com/apache/apisix-helm-chart/issues/959)).

Als je een foutmelding krijgt zoals:

    Error: looks like "..." is not a valid chart repository or cannot be reached:
    Get "https://apache.github.io/apisix-helm-chart/index.yaml": dial tcp: lookup apache.github.io: no such host

gebruik dan de alternatieve, door API7.ai gehoste repo:

    helm repo add apisix https://charts.apiseven.com --force-update
    helm repo update
    helm dependency update .

Of draai `./scripts/update-deps.sh`, die dit automatisch afhandelt.

> **Let op:** deze twee repo's zijn in het verleden niet altijd exact synchroon gebleken
> ([apache/apisix-helm-chart#610](https://github.com/apache/apisix-helm-chart/issues/610)).
> Controleer na een fallback altijd de chart-versie met `helm dependency list`.

## Gotcha: nesting van values.yaml overrides voor de `apisix` subchart

Alle overrides voor de `apisix`-dependency moeten genest staan onder de `apisix:`
key in onze `values.yaml` — anders komen ze de subchart niet in.

Extra addertje: de subchart heeft in zijn *eigen* `values.yaml` óók weer een
top-level `apisix:` key (1-op-1 spiegel van de APISIX `config.yaml`
`apisix:`-sectie, met daaronder o.a. `deployment:`). Om bv. `deployment.mode`
te overriden vanuit onze chart heb je dus `apisix.apisix.deployment.mode`
nodig — de eerste `apisix:` is de dependency, de tweede hun eigen
config-sectie. Keys als `image`, `etcd` en `ingress-controller` zitten wél
direct op het top-level van de subchart, dus die zijn gewoon `apisix.image`,
`apisix.etcd`, etc. (geen dubbele nesting).

Verifieer values-wijzigingen altijd met `helm template frank-gateway . --debug`
en controleer specifiek `deployment.role_traditional.config_provider` en de
container `command`/volumes in de gerenderde Deployment — bij een verkeerde
nesting slikt Helm de override stilletjes in en val je terug op de defaults
van de subchart (traditional mode + etcd), zonder foutmelding.

Losstaand addertje: met `etcd.enabled: false` gaat de chart er standaard van
uit dat je een *externe* etcd gebruikt (`externalEtcd.user` default is
`"root"`), en genereert dan een ongebruikte etcd-secret +
`APISIX_ETCD_PASSWORD` env var in de Deployment. Voor standalone/yaml mode
zonder etcd (intern of extern) zet je `apisix.externalEtcd.user: ""` om dat
te voorkomen.