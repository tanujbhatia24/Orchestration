pipeline {
    agent any

    parameters {
        string(name: 'APP_TARGET', defaultValue: '', description: 'Leave blank to auto-detect based on changed folders')
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

        stage('Detect Changed Folder') {
            when {
                expression { return !params.APP_TARGET?.trim() }
            }
            steps {
                dir('app-code') {
                    script {
                        def changedFiles = sh(
                            script: "git diff-tree --no-commit-id --name-only -r \$(git rev-parse HEAD)",
                            returnStdout: true
                        ).trim().split("\n")

                        echo "Changed files: ${changedFiles}"

                        if (changedFiles.any { it.startsWith("frontend/") }) {
                            env.APP_TARGET = "mern-frontend"
                        } else if (changedFiles.any { it.startsWith("backend/helloService/") }) {
                            env.APP_TARGET = "mern-backend-helloservice"
                        } else {
                            error("No recognized folder changes detected. Please check your commit.")
                        }

                        echo "Auto-detected APP_TARGET: ${env.APP_TARGET}"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def target = params.APP_TARGET?.trim() ? params.APP_TARGET : env.APP_TARGET
                    def dockerContext = target == 'mern-frontend' ? 'frontend' :
                                        target == 'mern-backend-helloservice' ? 'backend/helloService' : ''

                    if (!dockerContext) {
                        error "Invalid APP_TARGET value: '${target}'"
                    }

                    echo "Building Docker image from: app-code/${dockerContext}"

                    sh """
                        docker build -t ${target}:${IMAGE_TAG} app-code/${dockerContext}
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
                    sh """
                        echo 'Logging into AWS ECR in region ${env.AWS_REGION}'
                        aws ecr get-login-password --region ${env.AWS_REGION} | \
                        docker login --username AWS --password-stdin ${env.AWS_ACCOUNT_ID}.dkr.ecr.${env.AWS_REGION}.amazonaws.com
                    """
                }
            }
        }

        stage('Tag & Push Docker Image') {
            steps {
                script {
                    def target = params.APP_TARGET?.trim() ? params.APP_TARGET : env.APP_TARGET
                    def ecr_uri = "${env.AWS_ACCOUNT_ID}.dkr.ecr.${env.AWS_REGION}.amazonaws.com/${target}"

                    sh """
                        docker tag ${target}:${IMAGE_TAG} ${ecr_uri}:${IMAGE_TAG}
                        docker push ${ecr_uri}:${IMAGE_TAG}
                    """
                }
            }
        }
    }
}
