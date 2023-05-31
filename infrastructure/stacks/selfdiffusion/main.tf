# TODO: 
# 1. send cognito email from a custom domain

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

resource "aws_dynamodb_table" "user_information" {
  name         = "user_info"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "email"

  attribute {
    name = "email"
    type = "S"
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.app_name}_lambda_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
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
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_role_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${var.app_name}_api"
  description   = "Handler for ${var.app_name} backend"
  handler       = "index.lambda_handler"
  runtime       = "python3.10"

  # TODO: fix this to be relative path ...
  source_path = "/Users/jonathanpelletier/Projects/selfdiffusion/services/selfdiffusion-api"

  tags = {
    Name = "${var.app_name}_lambda"
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
  name        = "api-gateway"
  description = "API Gateway for managing user information and triggering ML jobs"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "api_gateway_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part   = "balance"
}


# adding cognito authorizer
resource "aws_api_gateway_authorizer" "authorizer" {
  name          = "CognitoUserPoolAuthorizer"
  type          = "COGNITO_USER_POOLS"
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  provider_arns = [aws_cognito_user_pool.user_pool.arn]
}

resource "aws_api_gateway_method" "api_gateway_method" {
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  resource_id   = aws_api_gateway_resource.api_gateway_resource.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.authorizer.id

  request_parameters = {
    "method.request.path.proxy" = true
  }

}

resource "aws_api_gateway_integration" "api_gateway_integration" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  resource_id = aws_api_gateway_resource.api_gateway_resource.id
  http_method = aws_api_gateway_method.api_gateway_method.http_method

  integration_http_method = aws_api_gateway_method.api_gateway_method.http_method
  type                    = "AWS_PROXY"
  uri                     = module.lambda_function.lambda_function_invoke_arn
}

resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_function.lambda_function_name
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

resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "${var.app_name}_API_Gateway_Logs"
  retention_in_days = 14
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
