variable "app_name" {
  description = "The name of the application"
  type        = string
}

# TODO: Pass these default through _envcommon ... do not want to loose time on this now
variable "vpc_cidr" {
  description = "value of the vpc cidr block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "azs" {
  description = "value of the availability zones"
  type        = list(string)
  default     = ["ca-central-1a", "ca-central-1b"]
}

variable "public_subnets" {
  description = "value of the public subnets"
  type        = list(string)
  default     = ["10.0.0.0/17", "10.0.128.0/17"]
}

variable "api_fqdn" {
  description = "The FQDN of the domain api"
  type        = string
}

variable "env" {
  description = "Name of the API gateway deployment stage"
  type        = string
}

variable "access_token_validity_hours" {
  description = "The number of hours after which access tokens expire"
  type        = number
  default     = 10
}

variable "allowed_oauth_flows_user_pool_client" {
  description = "Whether the client is allowed to follow the OAuth protocol when interacting with Cognito"
  type        = bool
  default     = true
}

variable "allowed_oauth_flows" {
  description = "The flow of OAuth that is allowed - can be code, implicit, or client_credentials"
  type        = list(string)
  default     = ["code", "implicit"]
}

variable "allowed_oauth_scopes" {
  description = "List of all scopes that are allowed"
  type        = list(string)
  default     = ["email", "openid"]
}

variable "auth_session_validity_hours" {
  description = "The time period after which the authentication session expires"
  type        = number
  default     = 3 // default to 1 hour, adjust as needed
}

variable "callback_url" {
  description = "The URL where users are redirected after they are authenticated"
  type        = string
  default     = "http://localhost:3456" // default to localhost, adjust as needed
}

variable "enable_token_revocation" {
  description = "Whether tokens should be revoked when the respective user logs out"
  type        = bool
  default     = true
}
