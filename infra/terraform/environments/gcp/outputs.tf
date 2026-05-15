output "service_uri" {
  value       = google_cloud_run_v2_service.this.uri
  description = "Cloud Run service URI."
}

output "service_account_email" {
  value       = google_service_account.app.email
  description = "Cloud Run runtime service account."
}
