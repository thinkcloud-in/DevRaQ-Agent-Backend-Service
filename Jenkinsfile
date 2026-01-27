pipeline {
    agent any

    environment {
        APP_NAME       = "devraq-agent-backend-service"
        IMAGE_TAG      = "latest"

        WORKDIR        = "/home/admin-01/Desktop/rcv/agent-backend"
        TAR_DIR        = "/home/admin-01/Desktop/rcv/tar"
        TAR_FILE       = "devraq-agent-backend_latest.tar"

        REMOTE_HOST    = "172.16.0.101"
        REMOTE_USER    = "root"
        REMOTE_TAR_DIR = "/home/rcv/daas_installer/daas_tar"
        REMOTE_BASE_DIR = "/home/rcv/daas_installer/daas_v1/agent-backend"
        SCRIPT_DIR     = "/home/rcv/Desktop/scrpit"
        DEPLOY_SCRIPT  = "agent_backend.sh"
        SSH_KEY        = "/root/.ssh/id_ed25519"
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

        stage('Copy TAR & YAMLs to Remote Server') {
            steps {
                sh """
                    # Create remote directories
                    ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no \
                        ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_TAR_DIR} ${REMOTE_BASE_DIR}"

                    # Copy TAR file
                    scp -i ${SSH_KEY} -o StrictHostKeyChecking=no \
                        ${TAR_DIR}/${TAR_FILE} \
                        ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_TAR_DIR}/

                    # Copy Kubernetes YAML files (from repo) to BASE_DIR
                    scp -i ${SSH_KEY} -o StrictHostKeyChecking=no \
                        ${WORKDIR}/k8s/*.yaml \
                        ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BASE_DIR}/
                """
            }
        }

        stage('Deploy Backend on Remote Server') {
            steps {
                sh """
                    echo "➡️ Deploying backend on remote server..."

                    # Ensure the deployment script exists on remote server
                    ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} \
                        "test -f ${SCRIPT_DIR}/${DEPLOY_SCRIPT}" || { echo '❌ Deployment script not found on remote host!'; exit 1; }

                    # Run everything in a single SSH session (corrected heredoc)
                    ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no -q -T ${REMOTE_USER}@${REMOTE_HOST} <<ENDSSH
set -e
echo "🔹 Making deployment script executable..."
chmod +x ${SCRIPT_DIR}/${DEPLOY_SCRIPT}

echo "🔹 Running deployment script..."
bash ${SCRIPT_DIR}/${DEPLOY_SCRIPT}
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
