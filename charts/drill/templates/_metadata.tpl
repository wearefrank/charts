{{/*
drill.metadata creates a standard metadata header.
It creates a 'metadata:' section with name and labels.
*/}}
{{- define "drill.metadata" -}}
metadata:
  name: {{ template "drill.fullname" . }}
  labels:
{{ include "drill.labels" . | indent 4 -}}
{{- end -}}
