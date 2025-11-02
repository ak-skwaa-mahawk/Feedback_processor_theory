{{- define "synara.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "synara.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "synara.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "synara.labels" -}}
app.kubernetes.io/name: {{ include "synara.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: Helm
{{- end -}}

{{- define "synara.selectorLabels" -}}
app.kubernetes.io/name: {{ include "synara.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}