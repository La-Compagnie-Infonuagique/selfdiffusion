# TODO: 
# 1. send cognito email from a custom domain

locals {
  namespace = "${var.app_name}_${var.env}"
}

data "aws_iam_policy_document" "job_bucket_policy" {
  statement {
    sid = "AllowReadToall"
    actions = [
      "s3:GetObject"
    ]
    resources = [
      "${aws_s3_bucket.job_results.arn}/*"
    ]

    principals {
      type = "*"
      identifiers = [
        "*"
      ]
    }
  }
}

# Create S3 bucket to store customer job results
resource "aws_s3_bucket" "job_results" {
  bucket = "${var.app_name}-${var.env}-job-results"

  tags = {
    Name        = "${var.app_name}-${var.env}-job-results"
    Environment = var.env
  }
}

# SQS Queue for job scheduling
## NOTE: Add DLQ later.
resource "aws_sqs_queue" "job_processing_queue" {
  name = "${var.app_name}-${var.env}-jobs-queue"

  tags = {
    Environment = var.env
  }
}

resource "aws_s3_bucket_policy" "job_bucket_policy" {
  bucket = aws_s3_bucket.job_results.id
  policy = data.aws_iam_policy_document.job_bucket_policy.json
}

# NOTE: Bad, replace with relative path.
locals {
  examples_path = "/Users/jonathanpelletier/Projects/selfdiffusion/infrastructure/stacks/selfdiffusion/examples/4910499e-3356-4b4d-a872-5c6ebd64b819"
  prefix        = "4910499e-3356-4b4d-a872-5c6ebd64b819"
}

# Upload the example images to the S3 bucket
resource "aws_s3_object" "example_images" {

  for_each = fileset(local.examples_path, "*")
  bucket   = aws_s3_bucket.job_results.bucket
  key      = "${local.prefix}/${each.value}"
  source   = "${local.examples_path}/${each.value}"
}


# Get data about AWS region
data "aws_region" "current" {}

# Runpod API Key SSM Param
resource "aws_ssm_parameter" "runpod_api_key_param" {
  name  = "/${var.app_name}/${var.env}/runpdod_api_key"
  type  = "SecureString"
  value = "REPLACE-ME-BY-AN-ACTUAL-KEY"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_route53_zone" "fqdn_zone" {
  name = var.api_fqdn
}

# obtenir un certificat pour le domaine
module "acm" {

  providers = {
    aws = aws.us-east-1
  }

  source = "terraform-aws-modules/acm/aws"

  domain_name = aws_route53_zone.fqdn_zone.name
  zone_id     = aws_route53_zone.fqdn_zone.zone_id

  wait_for_validation = true
}

resource "aws_cognito_user_pool" "user_pool" {
  name = "${var.app_name}_user_pool"

  auto_verified_attributes = ["email"]

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }
}

resource "aws_cognito_user_pool_domain" "amazon_domain" {
  domain       = var.app_name
  user_pool_id = aws_cognito_user_pool.user_pool.id
}

resource "aws_cognito_user_pool_client" "client" {
  name = "${var.app_name}_user_pool_client"

  user_pool_id = aws_cognito_user_pool.user_pool.id

  access_token_validity                = var.access_token_validity_hours
  allowed_oauth_flows_user_pool_client = var.allowed_oauth_flows_user_pool_client

  allowed_oauth_flows   = var.allowed_oauth_flows
  allowed_oauth_scopes  = var.allowed_oauth_scopes
  auth_session_validity = var.auth_session_validity_hours

  callback_urls           = [var.callback_url]
  default_redirect_uri    = var.callback_url
  enable_token_revocation = var.enable_token_revocation

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]
}

# Persistance for user information
resource "aws_dynamodb_table" "user_information" {
  name         = "user_info"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "username"

  attribute {
    name = "username"
    type = "S"
  }
}

# Persistance for job processing
resource "aws_dynamodb_table" "jobs" {
  name         = "jobs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "job_id"
  range_key    = "username"

  attribute {
    name = "job_id"
    type = "S"
  }

  attribute {
    name = "username"
    type = "S"
  }

  global_secondary_index {
    name            = "username_job_index"
    hash_key        = "username"
    range_key       = "job_id"
    projection_type = "ALL"
  }

}

# Persistance for GPU runtime lifecycle management
resource "aws_dynamodb_table" "runtimes" {
  name         = "runtimes"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "runtime_id"
  range_key    = "username"

  attribute {
    name = "runtime_id"
    type = "S"
  }

  attribute {
    name = "username"
    type = "S"
  }

  global_secondary_index {
    name            = "username_runtime_index"
    hash_key        = "username"
    range_key       = "runtime_id"
    projection_type = "ALL"
  }
}
resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda_policy"
  description = "Policy for allowing lambda to access required services"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "dynamodb:*",
        "ssm:*",
        "s3:*",
        "sqs:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

module "lambda_api" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${var.app_name}_api"
  description   = "Handler for ${var.app_name} backend"
  handler       = "index.lambda_handler"
  runtime       = "python3.10"
  attach_policy = true
  policy        = aws_iam_policy.lambda_policy.arn

  # TODO: fix this to be relative path ...
  source_path = "/Users/jonathanpelletier/Projects/selfdiffusion/services/selfdiffusion-api"

  # ENV variables for the lambda function
  environment_variables = {
    ClientId              = aws_cognito_user_pool_client.client.id
    UserPoolId            = aws_cognito_user_pool.user_pool.id
    Region                = data.aws_region.current.name
    UserInfoTableName     = aws_dynamodb_table.user_information.id
    RunpodApiKeyParamName = aws_ssm_parameter.runpod_api_key_param.name
    JobResultBucketName   = aws_s3_bucket.job_results.id
    JobQueueUrl           = aws_sqs_queue.job_processing_queue.id
    JobTableName          = aws_dynamodb_table.jobs.id
  }

  tags = {
    Name = "${var.app_name}_lambda_api"
  }
}

resource "aws_iam_user" "worker" {
  name = "${var.app_name}_${var.env}_runpod_worker"
}

resource "aws_iam_access_key" "worker_access_key" {
  user = aws_iam_user.worker.name
}

data "aws_iam_policy_document" "worker_iam_policy" {
  statement {
    sid = "AllowRunpodWorkerToAccessJobQueue"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes"
    ]
    resources = [aws_sqs_queue.job_processing_queue.arn]
    effect    = "Allow"
  }

  statement {
    sid       = "AllowWorkerWriteS3"
    actions   = ["s3:PutObject"]
    resources = [aws_s3_bucket.job_results.arn]
    effect    = "Allow"
  }
}

resource "aws_iam_policy" "worker_policy" {
  name   = "${var.app_name}_${var.env}_worker_policy"
  policy = data.aws_iam_policy_document.worker_iam_policy.json

  tags = {
    Name        = "${var.app_name}_${var.env}_worker_policy"
    Environment = var.env
  }

}

resource "aws_iam_user_policy_attachment" "worker_policy_attachment" {
  user       = aws_iam_user.worker.name
  policy_arn = aws_iam_policy.worker_policy.arn
}


module "lambda_scheduler" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${var.app_name}_scheduler"
  description   = "Handler for ${var.app_name} GPU runtime scheduler"
  handler       = "index.lambda_handler"
  runtime       = "python3.10"
  attach_policy = true
  policy        = aws_iam_policy.lambda_policy.arn

  # TODO: fix this to be relative path ...
  source_path = "/Users/jonathanpelletier/Projects/selfdiffusion/services/scheduler"

  # ENV variables for the lambda function
  environment_variables = {
    Region                = data.aws_region.current.name
    UserInfoTableName     = aws_dynamodb_table.user_information.id
    RunpodApiKeyParamName = aws_ssm_parameter.runpod_api_key_param.name
    JobResultBucketName   = aws_s3_bucket.job_results.id
    JobQueueUrl           = aws_sqs_queue.job_processing_queue.id
    JobTableName          = aws_dynamodb_table.jobs.id
    RuntimeTableName      = aws_dynamodb_table.runtimes.id
  }

  tags = {
    Name = "${var.app_name}_lambda_scheduler"
  }
}


# set permissions for API gateway logging at the account level:
resource "aws_iam_role" "api_gateway_cloudwatch" {
  name = "api_gateway_cloudwatch_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "api_gateway_cloudwatch_policy" {
  name = "api_gateway_cloudwatch_policy"
  role = aws_iam_role.api_gateway_cloudwatch.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "logs:PutLogEvents",
        "logs:GetLogEvents",
        "logs:FilterLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_api_gateway_account" "account" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch.arn
}

resource "aws_api_gateway_rest_api" "api_gateway" {
  depends_on  = [aws_api_gateway_account.account]
  name        = "${var.app_name}_api"
  description = "API Gateway for managing user information and triggering ML jobs"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Proxy resource
resource "aws_api_gateway_resource" "api_gateway_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part   = "{proxy+}"
}

# adding cognito authorizer to rest_api
resource "aws_api_gateway_authorizer" "authorizer" {
  name          = "CognitoUserPoolAuthorizer"
  type          = "COGNITO_USER_POOLS"
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  provider_arns = [aws_cognito_user_pool.user_pool.arn]
}

# Adding ANY mothod to API.
resource "aws_api_gateway_method" "api_gateway_method" {
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  resource_id   = aws_api_gateway_resource.api_gateway_resource.id
  http_method   = "ANY"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.authorizer.id

  request_parameters = {
    "method.request.path.proxy" = true
  }
}

# FWD all methods to lambda with POST
resource "aws_api_gateway_integration" "api_gateway_integration" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  resource_id = aws_api_gateway_resource.api_gateway_resource.id
  http_method = aws_api_gateway_method.api_gateway_method.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.lambda_api.lambda_function_invoke_arn
}

# Permission for API gateway to invoke lambda.
resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_api.lambda_function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*"
}


resource "aws_api_gateway_deployment" "api_gateway_deployment" {
  depends_on  = [aws_api_gateway_method.api_gateway_method]
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.api_gateway.body))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "stage" {
  deployment_id = aws_api_gateway_deployment.api_gateway_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  stage_name    = "${var.app_name}_${var.env}"

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
    format          = "$context.identity.sourceIp $context.status $context.responseLength $context.requestId $context.integrationErrorMessage $context.error.message"
  }
}

resource "aws_api_gateway_base_path_mapping" "path_mapping" {
  domain_name = aws_api_gateway_domain_name.fqdn.domain_name
  api_id      = aws_api_gateway_rest_api.api_gateway.id
  stage_name  = aws_api_gateway_stage.stage.stage_name
}

# Logging for the API.
resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "${var.app_name}_API_Gateway_Logs"
  retention_in_days = 14
}


resource "aws_api_gateway_domain_name" "fqdn" {
  certificate_arn = module.acm.acm_certificate_arn
  domain_name     = aws_route53_zone.fqdn_zone.name
}

resource "aws_route53_record" "api_endpoint" {
  zone_id = aws_route53_zone.fqdn_zone.zone_id
  name    = aws_route53_zone.fqdn_zone.name
  type    = "A"

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.fqdn.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.fqdn.cloudfront_zone_id
  }
}


## Networking for users gpu instances.
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "${var.app_name}_vpc"
  cidr = var.vpc_cidr

  azs            = var.azs
  public_subnets = var.public_subnets

  tags = {
    env = var.env
  }
}

## Create the Gateway S3 Endpoint and DynamoDB endpoints.
### S3
resource "aws_vpc_endpoint" "s3_endpoint" {
  vpc_id       = module.vpc.vpc_id
  service_name = "com.amazonaws.${data.aws_region.current.name}.s3"

  route_table_ids   = module.vpc.public_route_table_ids
  vpc_endpoint_type = "Gateway"
}

### DynamoDB
resource "aws_vpc_endpoint" "dynamodb_endpoint" {
  vpc_id       = module.vpc.vpc_id
  service_name = "com.amazonaws.${data.aws_region.current.name}.dynamodb"

  route_table_ids   = module.vpc.public_route_table_ids
  vpc_endpoint_type = "Gateway"
}

## Security Group the customer instance will use.
resource "aws_security_group" "outbound_only" {
  name        = "${local.namespace}_sg"
  description = "Only allow outbound traffic"

  vpc_id = module.vpc.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

## Store the security group id in a SSM parameter store
resource "aws_ssm_parameter" "outbound_only_sg" {
  name = "/${var.app_name}/${var.env}/outbound_only_sg"

  type  = "String"
  value = aws_security_group.outbound_only.id
}

## Allow sign in with SSM
resource "aws_iam_instance_profile" "base_instance_profile" {
  name = "base_instance_profile"
  role = aws_iam_role.ec2_role.name
}

resource "aws_iam_role" "ec2_role" {
  name               = "${local.namespace}_ec2_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "attachement" {
  name       = "${local.namespace}_policy_attachement"
  roles      = [aws_iam_role.ec2_role.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

