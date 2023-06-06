output "cognito_domain_prefix" {
  value       = aws_cognito_user_pool.user_pool.domain
  description = "aws cognito domain associated with the user pool"
}

output "cognito_app_client_id" {
  value       = aws_cognito_user_pool_client.client.id
  description = "aws cognito app client id"
}

output "cognito_user_pool_id" {
  value       = aws_cognito_user_pool.user_pool.id
  description = "aws cognito user pool id"
}

output "api_execution_arn" {
  value       = aws_api_gateway_rest_api.api_gateway.execution_arn
  description = "execution arn"
}

output "zone_info" {
  value       = aws_route53_zone.fqdn_zone.name_servers
  description = "NS for the public hosted zone"
}

output "api_gateway_endpoint" {
  value       = aws_route53_record.api_endpoint.fqdn
  description = "The API Gateway endpoint"
}

output "runpod_api_key_param" {
  value       = aws_ssm_parameter.runpod_api_key_param.name
  description = "The name of the SSM parameter containing the Runpod API key"
}
