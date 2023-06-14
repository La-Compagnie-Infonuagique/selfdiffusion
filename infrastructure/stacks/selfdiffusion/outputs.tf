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

output "aws_access_key_id" {
  value       = aws_iam_access_key.worker_access_key.id
  description = "value of the AWS access key ID"
}

output "aws_secret_key_id" {
  value       = nonsensitive(aws_iam_access_key.worker_access_key.secret)
  description = "value of the AWS secret key"
}

output "job_queue_url" {
  value       = aws_sqs_queue.job_processing_queue.id
  description = "ARN of the job queue"
}

output "result_bucket" {
  value       = aws_s3_bucket.job_results.id
  description = "Name of the bucket where the results are stored"
}

output "job_queue_results_url" {
  value       = aws_sqs_queue.job_processing_queue_results.id
  description = "SQS queue where worker will post confirmation of job complete"
}

