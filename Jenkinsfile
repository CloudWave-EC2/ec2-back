pipeline{
    agent any
    // tools {
    //   dockerTool 'docker'
    // }fdfdf
    stages{
        stage("checkout"){
            steps{
                checkout scm
            }
        }
        stage("push image"){
            steps{
                script{
                   docker.withRegistry('https://docker.io/hyeyeon763/ec2','dockerhub-creds'){
                       myapp = docker.build("docker.io/hyeyeon763/ec2:${env.BUILD_ID}")
                       myapp.push()
                    }
                }
            }
        }
    }
}