pipeline{
    agent any
    // tools {
    //   dockerTool 'docker'
    // }
    stages{
        stage("checkout"){
            steps{
                checkout scm
            }
        }
        stage("push image"){
            steps{
                script{
                   docker.withRegistry('hyeyeon763/ec2','dockerhub-creds'){
                       myapp = docker.build("hyeyeon/ec2:${env.BUILD_ID}")
                       myapp.push()
                    }
                }
            }
        }
    }
}