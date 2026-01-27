pipeline{
    agent any
    environment{
        IMAGE = "devraq-agent-backend-service"
        KUBE_NAMESPACE="thinkcloud"

        INFLUXDB_URL="http://172.16.0.103:8086"
        INFLUXDB_TOKEN="3K0iKC2-0FhOaRFI_kQN-3tCAUYacTXpuiJ9Uts5pzH9ZkplCuc7xxhdj5A01dXxPEG7BLE58QJLpshIZIB03w=="
        INFLUXDB_ORG="RCV-Vamanit-ORG"
    }

    stages{
        stage('checkout'){
            steps{
                git branch: 'main', url: 'https://github.com/thinkcloud-in/DevRaQ-Agent-Backend-Service.git'
            }
        }

        stage('build docker'){
            steps{
                script{
                    sh "docker build -t ${IMAGE}:latest ."
                    // sh "docker push ${IMAGE}:latest"
                }
            }
        }

        stage('Deploy to k8s'){
            steps{
                script{
                    sh "kubectl apply -f k8s/backend-2-deployment.yaml -n ${KUBE_NAMESPACE}"
                }
            }
        }
    }

    post{
        success{
            echo "Agent Deployed successfully!"
        }
        failure{
            echo "Agent Deployment failed. Please check the logs."
        }
    }
}

