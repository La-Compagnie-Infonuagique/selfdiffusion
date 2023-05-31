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

output "api_gateway_endpoint" {
  value       = aws_api_gateway_deployment.api_gateway_deployment.invoke_url
  description = "aws api gateway endpoint"
}

output "api_execution_arn" {
  value       = aws_api_gateway_rest_api.api_gateway.execution_arn
  description = "execution arn"

}
