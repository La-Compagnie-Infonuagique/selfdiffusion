# Sprint 0
Objective:
1. have an MVP that replicates 1 basic function of
https://neural.love/ai-art-generator
2. See if we can work together as a team.

Starting on Tuesday June 6th 2023 until june 13th 2023.

## Summary
See if we can make progress on an MVP that is a simple replica of https://neural.love/ai-art-generator.

## User should be
1. Able to sign up.
2. Able to log in.
3. Trigger the creation of images based on a prompt.
4. Get some feedback on the generation process on the UI (can be a generic spinner for the MVP).
5. Have the generated image displayed on the screen.

## Notes
1. User signup and login will be available through AWS Cognito.
2. Inference API will be available:
    a. Example invocation: 
    curl --request POST \
     --url https://api.dev.selfdiffusion.net/generate \
     --header 'Authorization: Bearer <TOKEN>' \ # See NOTE on TOKEN
     --header 'Accept: application/json' \
     --header 'Content-Type: application/json' \
     --data '{
     "prompt": "a picture of a developper coding",
     "samples": 1,
}'
    b. This will return a job id in a json payload (e.g: {'job_id':'e9095add-b72e-4a93-8472-eb878d150bfb'} )
    c. This ID can be used to poll for the result of the job and get the resulting image location. Example
    curl --request POST \
     --url https://api.dev.selfdiffusion.net/result \
     --header 'Authorization: Bearer <TOKEN>' \ # See NOTE on TOKEN
     --header 'Accept: application/json' \
     --header 'Content-Type: application/json' \
     --data '{
     "job_id": "e9095add-b72e-4a93-8472-eb878d150bfb"
}'
    d. This will return a json payload with the location of the images (e.g:)
    {'images': ['https://s3.amazonaws.com/selfdiffusion/userid/results/e9095add-b72e-4a93-8472-eb878d150bfb/0.png']}
    e. You can use the AWS Cognito user pool token as TOKEN to authenticate to the API.
    f. You can exchange the user pool token for an identity token to get the images directly from S3.
    g. see the AWS Cognito documentation here for details: https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html

    ## Backlog
    1. Create a Client App ID for AWS cognito user login/signup (Jonathan).
    2. Create a mock of generate API endpoint and deploy to dev (Jonathan).
    3. Create a mock of the result API endpoint and deploy to dev (Jonathan).




