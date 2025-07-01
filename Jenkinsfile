pipeline {
    agent any

    parameters {
        choice(
        string(name: 'APP_TARGET', defaultValue: '', description: '...'),
        name: 'APP_TARGET',
        choices: ['mern-frontend', 'mern-backend-helloservice'],
        description: '...'
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

        stage('Detect Changed Files') {
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

                        // You can put any condition here if needed, but for now we just decide to build both
                        env.BUILD_ALL = 'true'
                    }
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

        stage('Build and Push Docker Images') {
            steps {
                script {
                    def targets = []
                    if (params.APP_TARGET?.trim()) {
                        targets = [params.APP_TARGET.trim()]
                    } else if (env.BUILD_ALL == 'true') {
                        targets = ['mern-frontend', 'mern-backend-helloservice']
                    }

                    for (app in targets) {
                        def dockerContext = app == 'mern-frontend' ? 'frontend' :
                                            app == 'mern-backend-helloservice' ? 'backend/helloService' : null

                        if (!dockerContext) {
                            error "Unknown app target: ${app}"
                        }

                        def image = "${app}:${IMAGE_TAG}"
                        def ecr_uri = "${env.AWS_ACCOUNT_ID}.dkr.ecr.${env.AWS_REGION}.amazonaws.com/${app}"

                        echo "Building: ${image} from context: app-code/${dockerContext}"
                        sh "docker build -t ${image} app-code/${dockerContext}"

                        echo "Tagging and pushing: ${ecr_uri}:${IMAGE_TAG}"
                        sh """
                            docker tag ${image} ${ecr_uri}:${IMAGE_TAG}
                            docker push ${ecr_uri}:${IMAGE_TAG}
                        """
                    }
                }
            }
        }
    }
}
