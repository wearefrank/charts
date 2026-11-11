{{/*
Expand the name of the chart.
*/}}
{{- define "frank-gateway.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Fully qualified app name, used as prefix for all resources.
*/}}
{{- define "frank-gateway.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "frank-gateway.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Render a value that may contain templates. Strings are rendered as they are, other values are
converted to YAML first. Callers must check that the value is not empty, an empty list renders as "[]".
Usage: include "frank-gateway.tplvalues.render" (dict "value" .Values.path "context" $)
*/}}
{{- define "frank-gateway.tplvalues.render" -}}
{{- $value := typeIs "string" .value | ternary .value (.value | toYaml) -}}
{{- if contains "{{" $value -}}
{{- tpl $value .context -}}
{{- else -}}
{{- $value -}}
{{- end -}}
{{- end }}

{{/*
Labels shared by all selectors, without the component.
*/}}
{{- define "frank-gateway.baseSelectorLabels" -}}
app.kubernetes.io/name: {{ include "frank-gateway.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Selector labels of the gateway pods. The component is part of the selector on purpose: a selector cannot
be changed later, and this keeps Services and the Deployment from matching pods of other components.
*/}}
{{- define "frank-gateway.selectorLabels" -}}
{{ include "frank-gateway.baseSelectorLabels" . }}
app.kubernetes.io/component: gateway
{{- end }}

{{/*
Standard labels and commonLabels of a resource. The standard labels win over commonLabels.
Usage: include "frank-gateway.labelsFor" (dict "context" $ "component" "control")
*/}}
{{- define "frank-gateway.labelsFor" -}}
{{- $ctx := .context -}}
{{- $labels := dict
  "helm.sh/chart" (include "frank-gateway.chart" $ctx)
  "app.kubernetes.io/name" (include "frank-gateway.name" $ctx)
  "app.kubernetes.io/instance" $ctx.Release.Name
  "app.kubernetes.io/version" (toString ($ctx.Values.image.tag | default $ctx.Chart.AppVersion))
  "app.kubernetes.io/component" .component
  "app.kubernetes.io/part-of" "frank-gateway"
  "app.kubernetes.io/managed-by" $ctx.Release.Service -}}
{{- if $ctx.Values.commonLabels -}}
{{- $labels = merge $labels (include "frank-gateway.tplvalues.render" (dict "value" $ctx.Values.commonLabels "context" $ctx) | fromYaml) -}}
{{- end -}}
{{- toYaml $labels -}}
{{- end }}

{{- define "frank-gateway.labels" -}}
{{- include "frank-gateway.labelsFor" (dict "context" . "component" "gateway") -}}
{{- end }}

{{/*
Annotations of a resource: the given annotations and commonAnnotations, the given annotations win.
Renders nothing when there are none, so use it with "with".
Usage: include "frank-gateway.annotations" (dict "annotations" .Values.service.annotations "context" $)
*/}}
{{- define "frank-gateway.annotations" -}}
{{- $ctx := .context -}}
{{- $merged := dict -}}
{{- if .annotations -}}
{{- $merged = include "frank-gateway.tplvalues.render" (dict "value" .annotations "context" $ctx) | fromYaml -}}
{{- end -}}
{{- if $ctx.Values.commonAnnotations -}}
{{- $merged = merge $merged (include "frank-gateway.tplvalues.render" (dict "value" $ctx.Values.commonAnnotations "context" $ctx) | fromYaml) -}}
{{- end -}}
{{- if $merged -}}
{{- toYaml $merged -}}
{{- end -}}
{{- end }}

{{- define "frank-gateway.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "frank-gateway.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Image reference: registry/repository, followed by the digest when set, otherwise by the tag.
*/}}
{{- define "frank-gateway.image" -}}
{{- $reference := printf ":%s" (toString (.Values.image.tag | default .Chart.AppVersion)) -}}
{{- if .Values.image.digest -}}
{{- $reference = printf "@%s" .Values.image.digest -}}
{{- end -}}
{{- if .Values.image.registry -}}
{{- printf "%s/%s%s" .Values.image.registry .Values.image.repository $reference -}}
{{- else -}}
{{- printf "%s%s" .Values.image.repository $reference -}}
{{- end -}}
{{- end }}

{{/*
Name of the ConfigMap or Secret that holds apisix.yaml.
*/}}
{{- define "frank-gateway.standaloneName" -}}
{{- if .Values.standalone.existingSecret }}
{{- include "frank-gateway.tplvalues.render" (dict "value" .Values.standalone.existingSecret "context" .) }}
{{- else if .Values.standalone.existingConfigMap }}
{{- include "frank-gateway.tplvalues.render" (dict "value" .Values.standalone.existingConfigMap "context" .) }}
{{- else }}
{{- printf "%s-apisix-yaml" (include "frank-gateway.fullname" .) }}
{{- end }}
{{- end }}

{{/*
Service ports: a missing targetPort is the name of the port, which is the name of a container port,
and a missing protocol is TCP.
*/}}
{{- define "frank-gateway.servicePorts" -}}
{{- $ports := list -}}
{{- range .Values.service.ports -}}
{{- $port := deepCopy . -}}
{{- if not $port.targetPort -}}{{- $_ := set $port "targetPort" $port.name -}}{{- end -}}
{{- if not $port.protocol -}}{{- $_ := set $port "protocol" "TCP" -}}{{- end -}}
{{- $ports = append $ports $port -}}
{{- end -}}
{{- toYaml $ports -}}
{{- end }}

{{/*
Deployment strategy. A rolling update without settings starts a new pod before it stops an old one.
*/}}
{{- define "frank-gateway.strategy" -}}
{{- $strategy := deepCopy .Values.strategy -}}
{{- if eq (toString ($strategy.type | default "RollingUpdate")) "RollingUpdate" -}}
{{- $rolling := $strategy.rollingUpdate | default dict -}}
{{- if not (hasKey $rolling "maxUnavailable") -}}{{- $_ := set $rolling "maxUnavailable" 0 -}}{{- end -}}
{{- if not (hasKey $rolling "maxSurge") -}}{{- $_ := set $rolling "maxSurge" 1 -}}{{- end -}}
{{- $_ := set $strategy "rollingUpdate" $rolling -}}
{{- end -}}
{{- toYaml $strategy -}}
{{- end }}

{{/*
Resolve the name of a port in service.ports to its port number.
Usage: include "frank-gateway.servicePortNumber" (dict "root" . "port" "https")
*/}}
{{- define "frank-gateway.servicePortNumber" -}}
{{- $port := .port -}}
{{- $found := "" -}}
{{- range .root.Values.service.ports -}}
{{- if eq .name $port -}}{{- $found = .port -}}{{- end -}}
{{- end -}}
{{- if not $found -}}
{{- fail (printf "service.ports has no port named %q" $port) -}}
{{- end -}}
{{- int $found -}}
{{- end }}

{{/*
Backend reference for Gateway API routes, pointing at the gateway Service.
Usage: include "frank-gateway.routeBackendRefs" (dict "root" . "port" .Values.httpRoute.defaultBackendPort)
*/}}
{{- define "frank-gateway.routeBackendRefs" -}}
- name: {{ include "frank-gateway.fullname" .root }}
  port: {{ include "frank-gateway.servicePortNumber" . }}
{{- end }}

{{/*
Complete config.yaml: the user supplied config with the chart managed keys forced.
*/}}
{{- define "frank-gateway.config" -}}
{{- $config := deepCopy .Values.config -}}
{{- $apisix := dict
  "node_listen" (list .Values.containerPorts.http)
  "enable_admin" false
  "enable_control" .Values.control.enabled
  "ssl" (dict "enable" true "listen" (list (dict "port" .Values.containerPorts.https))) -}}
{{- if .Values.control.enabled -}}
{{- $_ := set $apisix "control" (dict "ip" "0.0.0.0" "port" .Values.control.port) -}}
{{- end -}}
{{- $managed := dict
  "apisix" $apisix
  "deployment" (dict "role" "data_plane" "role_data_plane" (dict "config_provider" "yaml")) -}}
{{- if .Values.metrics.enabled -}}
{{- $_ := set $managed "plugin_attr" (dict "prometheus" (dict
  "export_addr" (dict "ip" "0.0.0.0" "port" .Values.metrics.port)
  "export_uri" .Values.metrics.path)) -}}
{{- end -}}
{{- toYaml (mustMergeOverwrite $config $managed) -}}
{{- end }}

{{/*
Complete apisix.yaml, always terminated with the #END marker APISIX requires.
*/}}
{{- define "frank-gateway.apisixYaml" -}}
{{- $content := .Values.standalone.apisixYaml | trimSuffix "\n" -}}
{{- if hasSuffix "#END" (trim $content) -}}
{{- $content -}}
{{- else -}}
{{- $content }}
#END
{{- end -}}
{{- end }}

{{/*
Writable emptyDir mounts. APISIX writes to these paths while the root filesystem is read-only.
*/}}
{{- define "frank-gateway.writablePaths" -}}
- name: conf
  path: /usr/local/apisix/conf
- name: logs
  path: /usr/local/apisix/logs
- name: client-body-temp
  path: /usr/local/apisix/client_body_temp
- name: proxy-temp
  path: /usr/local/apisix/proxy_temp
- name: fastcgi-temp
  path: /usr/local/apisix/fastcgi_temp
- name: uwsgi-temp
  path: /usr/local/apisix/uwsgi_temp
- name: scgi-temp
  path: /usr/local/apisix/scgi_temp
- name: tmp
  path: /tmp
{{- end }}

{{/*
Checks the values and fails with all problems at once. Rendered by templates/validate.yaml.
*/}}
{{- define "frank-gateway.validateValues" -}}
{{- $errors := list -}}
{{- $portNames := list -}}
{{- range .Values.service.ports -}}
{{- $portNames = append $portNames .name -}}
{{- end -}}

{{- if and .Values.standalone.existingConfigMap .Values.standalone.existingSecret -}}
{{- $errors = append $errors "standalone.existingConfigMap and standalone.existingSecret are mutually exclusive" -}}
{{- end -}}

{{- if not (has .Values.service.type (list "ClusterIP" "NodePort" "LoadBalancer")) -}}
{{- $errors = append $errors (printf "service.type must be ClusterIP, NodePort or LoadBalancer, got %q" .Values.service.type) -}}
{{- end -}}

{{- if regexMatch "^[^/]*[.:][^/]*/" .Values.image.repository -}}
{{- $errors = append $errors (printf "image.repository %q must not contain the registry host, set it in image.registry" .Values.image.repository) -}}
{{- end -}}

{{- $ports := list .Values.containerPorts.http .Values.containerPorts.https -}}
{{- if .Values.control.enabled -}}{{- $ports = append $ports .Values.control.port -}}{{- end -}}
{{- if .Values.metrics.enabled -}}{{- $ports = append $ports .Values.metrics.port -}}{{- end -}}
{{- if ne (len $ports) (len (uniq $ports)) -}}
{{- $errors = append $errors "containerPorts.http, containerPorts.https, control.port and metrics.port must all be different" -}}
{{- end -}}

{{- if .Values.ingress.enabled -}}
{{- if not .Values.ingress.rules -}}
{{- $errors = append $errors "ingress.enabled is true but ingress.rules is empty" -}}
{{- end -}}
{{- $needsDefault := false -}}
{{- range .Values.ingress.rules -}}
{{- range ((.http).paths | default list) -}}
{{- if not .backend -}}{{- $needsDefault = true -}}{{- end -}}
{{- end -}}
{{- end -}}
{{- if and $needsDefault (not (has .Values.ingress.defaultBackendPort $portNames)) -}}
{{- $errors = append $errors (printf "ingress.defaultBackendPort %q is not the name of a port in service.ports" .Values.ingress.defaultBackendPort) -}}
{{- end -}}
{{- if and $needsDefault (gt (len (toString .Values.ingress.defaultBackendPort)) 15) -}}
{{- $errors = append $errors (printf "ingress.defaultBackendPort %q is longer than 15 characters, the name of an Ingress backend port is an IANA service name" .Values.ingress.defaultBackendPort) -}}
{{- end -}}
{{- end -}}

{{- if .Values.httpRoute.enabled -}}
{{- if not .Values.httpRoute.parentRefs -}}
{{- $errors = append $errors "httpRoute.enabled is true but httpRoute.parentRefs is empty, the route would not attach to a Gateway" -}}
{{- end -}}
{{- $needsDefault := false -}}
{{- range .Values.httpRoute.rules -}}
{{- if not .backendRefs -}}{{- $needsDefault = true -}}{{- end -}}
{{- end -}}
{{- if and $needsDefault (not (has .Values.httpRoute.defaultBackendPort $portNames)) -}}
{{- $errors = append $errors (printf "httpRoute.defaultBackendPort %q is not the name of a port in service.ports" .Values.httpRoute.defaultBackendPort) -}}
{{- end -}}
{{- end -}}

{{- if .Values.tlsRoute.enabled -}}
{{- if not .Values.tlsRoute.parentRefs -}}
{{- $errors = append $errors "tlsRoute.enabled is true but tlsRoute.parentRefs is empty, the route would not attach to a Gateway" -}}
{{- end -}}
{{- if not .Values.tlsRoute.hostnames -}}
{{- $errors = append $errors "tlsRoute.enabled is true but tlsRoute.hostnames is empty, a TLSRoute needs at least one SNI hostname" -}}
{{- end -}}
{{- $needsDefault := false -}}
{{- range .Values.tlsRoute.rules -}}
{{- if not .backendRefs -}}{{- $needsDefault = true -}}{{- end -}}
{{- end -}}
{{- if and $needsDefault (not (has .Values.tlsRoute.defaultBackendPort $portNames)) -}}
{{- $errors = append $errors (printf "tlsRoute.defaultBackendPort %q is not the name of a port in service.ports" .Values.tlsRoute.defaultBackendPort) -}}
{{- end -}}
{{- end -}}

{{- if and .Values.metrics.serviceMonitor.enabled (not .Values.metrics.enabled) -}}
{{- $errors = append $errors "metrics.serviceMonitor.enabled is true but metrics.enabled is false, there is no metrics Service to monitor" -}}
{{- end -}}

{{- if and .Values.autoscaling.enabled (gt (int .Values.autoscaling.minReplicas) (int .Values.autoscaling.maxReplicas)) -}}
{{- $errors = append $errors "autoscaling.minReplicas must not be greater than autoscaling.maxReplicas" -}}
{{- end -}}

{{- if $errors -}}
{{- fail (printf "\nVALUES VALIDATION:\n- %s" (join "\n- " $errors)) -}}
{{- end -}}
{{- end }}
