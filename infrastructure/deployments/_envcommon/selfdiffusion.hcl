terraform {
    source = "../../..//stacks/selfdiffusion"
}

inputs = {
    app_name = "selfdiffusion"
    access_token_validity_hours = 10
    allowed_oauth_flows_user_pool_client = true
    allowed_oauth_flows = ["code", "implicit"]
    allowed_oauth_scopes = ["email","openid"]
    auth_session_validity_hours = 5
    callback_url = "https://localhost:3456"
    enable_token_recovation = true
}