include "root" {
  path = find_in_parent_folders()
}

# Inclure ce qui est commun aux environnements.
include "envcommon" {
  path   = "${dirname(find_in_parent_folders())}/_envcommon/selfdiffusion.hcl"
}

# Read env specific configuration
locals {
  env_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))

  env = local.env_vars.locals.env
}

inputs = {
  api_fqdn = "api.${local.env}.selfdiffusion.net"
}
