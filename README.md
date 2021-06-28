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

   ```bash
   docker build . -t iris_classifier:latest
   docker run -p 9000:8080 iris_classifier
   
   # to test the endpoints
   curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"body": "[[1, 2, 2, 3]]"}'
   
   #Login, Tag and Push to ECR
   aws ecr get-login-password | docker login --username AWS --password-stdin 213386773652.dkr.ecr.ap-south-1.amazonaws.com
   docker tag iris_classifier 213386773652.dkr.ecr.ap-south-1.amazonaws.com/irisclassifier
   docker push 213386773652.dkr.ecr.ap-south-1.amazonaws.com/irisclassifier
   ```

   This is the manual version but with the `deploy.py` script it becomes easier. 
   This script takes care of building, tagging and pushing the bento-bundle
   image and also creates the SAM template file so you can push it to AWS
   services using SAM deploy.
   ```
   python deploy.py <bento-bundle-path>
   ```

4. Build Cloudformation template. We have to create the template that we will
   use to build infrastructure in AWS (API gateway for all the endpoints and
   Lambda functions). 
   
   Right now, I'm using a custom template file. *TODO* Check out AWS SAM Cli and
   creation of endpoints and template files using that (this is what is
   currently used in bentoml lambda deployment).

   ```bash
   aws cloudformation deploy \
    --stack-name lambda-api \
    --template-file lambda2.yml \
    --capabilities CAPABILITY_IAM
   ```


## Tasks
- [x] Write down the steps to deploy Lambda function
- [ ] Create a bento with multiple api functions and setup CF config for that 
- [ ] checkout aws sam cli and see can it be used for deployment
- [ ] investigate image config on cf template. and allow it to set run_command on the template rather than in entry.sh.  https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-imageconfig


## Resources
- [Lambda Container Images](https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/)
- [Setting up API Gateways for Lambda](https://nickolaskraus.org/articles/creating-an-amazon-api-gateway-with-a-lambda-integration-using-cloudformation/)
- [Deploying custom Docker Image with SAM](https://github.com/philschmid/aws-lambda-with-docker-image)
