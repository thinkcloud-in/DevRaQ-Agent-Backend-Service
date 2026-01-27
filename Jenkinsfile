pipeline {
    agent any

    environment {
        APP_NAME       = "devraq-agent-backend-service"
        IMAGE_TAG      = "latest"

        WORKDIR        = "/home/admin-01/Desktop/rcv/agent-backend"
        TAR_DIR        = "/home/admin-01/Desktop/rcv/tar"
        TAR_FILE       = "devraq-agent-backend_latest.tar"

        REMOTE_HOST    = "172.16.0.101"      // K8s VM
        REMOTE_USER    = "root"              // User on K8s VM that can run kubectl
        REMOTE_TAR_DIR = "/home/rcv/daas_installer/daas_tar"
        SSH_KEY        = "/root/.ssh/id_ed25519" // Existing SSH key mounted in Jenkins
    }

    stages {

        stage('Prepare Directories') {
            steps {
                sh 'mkdir -p ${TAR_DIR}'
            }
        }

        stage('Checkout Backend Code') {
            steps {
                dir("${WORKDIR}") {
                    deleteDir()
                    git branch: 'main',
                        url: 'https://github.com/thinkcloud-in/DevRaQ-Agent-Backend-Service.git',
                        credentialsId: 'github_token'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir("${WORKDIR}") {
                    sh '''
                        docker image prune -a -f
                        docker build -t ${APP_NAME}:${IMAGE_TAG} .
                    '''
                }
            }
        }

        stage('Save Docker Image as TAR') {
            steps {
                sh '''
                    docker save -o ${TAR_DIR}/${TAR_FILE} ${APP_NAME}:${IMAGE_TAG}
                    ls -lh ${TAR_DIR}
                '''
            }
        }

        stage('Copy TAR to Remote K8s VM') {
            steps {
                sh '''
                    ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no \
                        ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_TAR_DIR}"

                    scp -i ${SSH_KEY} -o StrictHostKeyChecking=no \
                        ${TAR_DIR}/${TAR_FILE} \
                        ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_TAR_DIR}/
                '''
            }
        }

        stage('Deploy Backend on Remote K8s VM') {
            steps {
                sh """
                    echo "➡️ Loading Docker image and applying K8s deployment on remote VM..."
                    ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} bash -s <<ENDSSH
                        # Load Docker image
                        docker load -i ${REMOTE_TAR_DIR}/${TAR_FILE}

                        # Apply Kubernetes deployment
                        kubectl apply -f /home/rcv/daas_installer/daas_v2/k8s/backend-2-deployment.yaml -n thinkcloud
ENDSSH
                """
            }
        }

    }

    post {
        success {
            echo '✅ Agent Backend Build → TAR → Copy → Deploy Successful!'
        }
        failure {
            echo '❌ Agent Backend Pipeline Failed!'
        }
    }
}
