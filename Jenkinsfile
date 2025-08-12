pipeline {
  agent any
  environment {
    IMAGE = "hyeyeon763/ec2"          // docker.io 생략해도 OK (자동으로 붙음)
    TAG   = "${env.BUILD_ID}"
  }
  stages {
    stage('checkout') {
      steps { checkout scm }
    }
    stage('push image') {
      steps {
        script {
          // ✅ Docker Hub는 이 엔드포인트가 정답
          docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-creds') {
            def app = docker.build("${IMAGE}:${TAG}")   // ✅ def 붙이기
            app.push()
            // latest도 같이 밀고 싶으면:
            sh "docker tag ${IMAGE}:${TAG} ${IMAGE}:latest"
            sh "docker push ${IMAGE}:latest"
          }
        }
      }
    }
  }
}
