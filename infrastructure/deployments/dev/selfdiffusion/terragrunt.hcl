include "root" {
  path = find_in_parent_folders()
}

# Inclure ce qui est commun aux environnements.
include "envcommon" {
  path   = "${dirname(find_in_parent_folders())}/_envcommon/selfdiffusion.hcl"
}
