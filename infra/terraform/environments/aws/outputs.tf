output "alb_dns_name" {
  value       = aws_lb.this.dns_name
  description = "Application load balancer DNS name."
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.this.name
  description = "ECS cluster name."
}
