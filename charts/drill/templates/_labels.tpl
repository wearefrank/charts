{{/*
Common labels
*/}}
{{- define "drill.labels" -}}
helm.sh/chart: {{ include "drill.chart" . }}
{{ include "drill.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "drill.selectorLabels" -}}
app.kubernetes.io/name: {{ include "drill.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
