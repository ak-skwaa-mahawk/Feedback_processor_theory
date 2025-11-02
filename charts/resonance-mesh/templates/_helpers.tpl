{{- define "resonance-mesh.fullname" -}}
{{- include "resonance-mesh.name" . }}-{{ .Release.Name }}
{{- end -}}

{{- define "resonance-mesh.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "resonance-mesh.labels" -}}
app.kubernetes.io/name: {{ include "resonance-mesh.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: Helm
{{- end -}}