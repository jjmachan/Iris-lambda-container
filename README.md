# Bentoml Bundle for Lambda Deployment

The prototype for lambda deployment using containers. The steps for preping the
Bento Bundle are

1. Modify Docker Image. You have to add both Runtime Interface Client and the
   Runtime Interface Emulator to the Image. We have to also change the
   `ENTRYPOINT` to use another script to start the RIC when the container is
   started. 

2. Add Lambda API Function. This code handles the actual request and calls the
   bento service to serve the response of the model. *TODO* Here one thing to add is
   support for multiple API endpoints. 

3. Build the image. With all these changes, the service is ready to run on
   Lambda, tag and push the docker image into ECR. 

4. Build Cloudformation template. We have to create the template that we will
   use to build infrastructure in AWS (API gateway for all the endpoints and
   Lambda functions). 
   
   Right now, I'm using a custom template file. *TODO* Check out AWS SAM Cli and
   creation of endpoints and template files using that (this is what is
   currently used in bentoml lambda deployment).


## Tasks
[ ] Write down the steps to deploy Lambda function
[ ] Create a bento with multiple api functions and setup CF config for that
[ ] checkout aws sam cli and see can it be used for deployment
[ ] investigate image config on cf template. and allow it to set run_command on the template rather than in entry.sh.  https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-imageconfig
