pipeline {
    agent any

    parameters {
        choice(
            name: 'APP_TARGET',
            choices: ['mern-frontend', 'mern-backend-helloservice'],
            description: 'Select which app to build and push'
        )
    }

    environment {
        AWS_REGION = 'ap-south-1'
        AWS_ACCOUNT_ID = '975050024946'
        IMAGE_TAG = "${GIT_COMMIT}"
        CODE_REPO = 'https://github.com/tanujbhatia24/SampleMERNwithMicroservices.git'
        CODE_BRANCH = 'main'
    }

    stages {
        stage('Clone App Code') {
            steps {
                dir('app-code') {
                    git branch: "${env.CODE_BRANCH}", url: "${env.CODE_REPO}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def dockerContext = ''
                    if (params.APP_TARGET == 'mern-frontend') {
                        dockerContext = 'frontend'
                    } else if (params.APP_TARGET == 'mern-backend-helloservice') {
                        dockerContext = 'backend/helloService'
                    }

                    echo "Building Docker image from: app-code/${dockerContext}"

                    sh """
                        docker build -t ${params.APP_TARGET}:${IMAGE_TAG} app-code/${dockerContext}
                    """
                }
            }
        }

        stage('Login to ECR') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'tanuj-aws-ecr-creds'
                ]]) {
                    sh "echo 'Trying to log in to AWS ECR in region $AWS_REGION for account $AWS_ACCOUNT_ID'"
                    sh """
                        aws ecr get-login-password | \
                        docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
                    """
        }
    }
}


        stage('Tag & Push Docker Image') {
            steps {
                script {
                    def ecr_uri = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${params.APP_TARGET}"
                    sh """
                    docker tag ${params.APP_TARGET}:${IMAGE_TAG} ${ecr_uri}:${IMAGE_TAG}
                    docker push ${ecr_uri}:${IMAGE_TAG}
                    """
                }
            }
        }
    }
}
