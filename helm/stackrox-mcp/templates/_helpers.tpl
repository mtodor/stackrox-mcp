{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "stackrox-mcp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "stackrox-mcp.selectorLabels" -}}
app.kubernetes.io/name: stackrox-mcp
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "stackrox-mcp.labels" -}}
helm.sh/chart: {{ include "stackrox-mcp.chart" . }}
{{ include "stackrox-mcp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
