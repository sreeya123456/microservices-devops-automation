pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        AWS_ACCOUNT_ID = '153106962670'
        ECR_REGISTRY = '153106962670.dkr.ecr.us-east-1.amazonaws.com'
        IMAGE_TAG = "${BUILD_NUMBER}"
        COMPOSE_PROJECT_NAME = 'microservices-devops-automation'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {

        stage('GitHub Checkout') {
            steps {
                checkout scm

                echo 'GitHub checkout completed successfully'
            }
        }

        stage('Validate Environment') {
            steps {
                sh '''
                    set -e

                    echo "Checking required files..."

                    test -f docker-compose.yml
                    test -f nginx/nginx.conf

                    test -f user-service/Dockerfile
                    test -f product-service/Dockerfile
                    test -f order-service/Dockerfile

                    echo "Checking Docker..."

                    docker --version
                    docker compose version

                    echo "Validating Docker Compose..."

                    docker compose config -q

                    echo "Environment validation successful"
                '''
            }
        }

        stage('AWS Authentication') {
            steps {
                sh '''
                    set -e

                    echo "Verifying EC2 IAM role..."

                    aws sts get-caller-identity

                    echo "Authenticating with Amazon ECR..."

                    aws ecr get-login-password \
                        --region ${AWS_REGION} | \
                        docker login \
                        --username AWS \
                        --password-stdin ${ECR_REGISTRY}

                    echo "ECR authentication successful"
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                    set -e

                    echo "Building User Service..."

                    docker build \
                        -t ${ECR_REGISTRY}/user-service:${IMAGE_TAG} \
                        -t ${ECR_REGISTRY}/user-service:latest \
                        ./user-service

                    echo "Building Product Service..."

                    docker build \
                        -t ${ECR_REGISTRY}/product-service:${IMAGE_TAG} \
                        -t ${ECR_REGISTRY}/product-service:latest \
                        ./product-service

                    echo "Building Order Service..."

                    docker build \
                        -t ${ECR_REGISTRY}/order-service:${IMAGE_TAG} \
                        -t ${ECR_REGISTRY}/order-service:latest \
                        ./order-service

                    echo "All Docker images built successfully"
                '''
            }
        }

        stage('Push Images to ECR') {
            steps {
                sh '''
                    set -e

                    echo "Pushing User Service..."

                    docker push ${ECR_REGISTRY}/user-service:${IMAGE_TAG}
                    docker push ${ECR_REGISTRY}/user-service:latest

                    echo "Pushing Product Service..."

                    docker push ${ECR_REGISTRY}/product-service:${IMAGE_TAG}
                    docker push ${ECR_REGISTRY}/product-service:latest

                    echo "Pushing Order Service..."

                    docker push ${ECR_REGISTRY}/order-service:${IMAGE_TAG}
                    docker push ${ECR_REGISTRY}/order-service:latest

                    echo "All images pushed successfully"
                '''
            }
        }

        stage('Deploy Microservices') {
    steps {
        sh '''
            set -e

            export IMAGE_TAG=${BUILD_NUMBER}

            echo "Pulling updated ECR images..."

            docker compose \
                -p ${COMPOSE_PROJECT_NAME} \
                pull user-service product-service order-service

            echo "Deploying updated microservices..."

            docker compose \
                -p ${COMPOSE_PROJECT_NAME} \
                up -d --no-build

            echo "Deployment completed"
        '''
    }
}

        stage('Verify Containers') {
            steps {
                sh '''
                    set -e

                    echo "Checking container status..."

                    docker compose \
                        -p ${COMPOSE_PROJECT_NAME} ps

                    echo "Checking service health..."

                    for endpoint in user product order
                    do
                        echo "Checking ${endpoint} service..."

                        success=false

                        for attempt in $(seq 1 12)
                        do
                            if curl -fsS \
                                http://localhost/health/${endpoint} \
                                > /dev/null
                            then
                                success=true
                                break
                            fi

                            echo "Waiting for ${endpoint} service..."
                            sleep 10
                        done

                        if [ "$success" != "true" ]
                        then
                            echo "${endpoint} health check failed"
                            exit 1
                        fi

                        echo "${endpoint} is healthy"
                    done

                    echo "All three microservices are healthy"
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully'
        }

        failure {
            echo 'CI/CD pipeline failed. Check Console Output.'
        }

        always {
            sh '''
                docker logout ${ECR_REGISTRY} || true
            '''
        }
    }
}
