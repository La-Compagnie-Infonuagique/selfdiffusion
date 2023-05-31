locals {

    region = "ca-central-1"
    env_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))

    env = local.env_vars.locals.env
    account = local.env_vars.locals.account

    aws_role_arn = "arn:aws:iam::${local.account}:role/AccountAdminDeploymentRole"
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF

provider "aws" {
  region = "${local.region}"

  assume_role {
    role_arn = "${local.aws_role_arn}"
    session_name = "devops_deployment"
  }
}

EOF
}

# Configuration de l'état terraform.
remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    bucket = "tfbackend-bucket-${local.account}"

    key = "inference/${path_relative_to_include()}/terraform.tfstate"
    region         = "${local.region}"
    encrypt        = true
    dynamodb_table = "tfbackend-dynamodb-table-${local.account}"
  }
}

inputs = {
  env = local.env
}
