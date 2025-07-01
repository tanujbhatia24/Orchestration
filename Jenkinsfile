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
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/tanujbhatia24/SampleMERNwithMicroservices.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def dockerContext = ""

                    if (params.APP_TARGET == 'mern-frontend') {
                        dockerContext = 'frontend'
                    } else if (params.APP_TARGET == 'mern-backend-helloservice') {
                        dockerContext = 'backend/helloService'
                    }

                    echo "Building image for ${params.APP_TARGET} from ${dockerContext}"
                    sh """
                        docker build -t ${params.APP_TARGET}:${IMAGE_TAG} ${dockerContext}
                    """
                }
            }
        }

        stage('Login to ECR') {
            steps {
                sh """
                aws ecr get-login-password | \
                docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
                """
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
