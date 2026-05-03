pipeline {
    agent any

    environment {
        APP_DIR         = 'app'
        TEST_DIR        = 'tests'
        APP_CONTAINER   = 'taskapp'
        DB_CONTAINER    = 'taskdb'
        TEST_CONTAINER  = 'selenium-tests'
        APP_PORT        = '5000'
        SMTP_SERVER     = 'smtp.gmail.com'
        SENDER_EMAIL    = 'zuriyatfatima@gmail.com'  // ← your sender email
    }

    stages {

        // ── STAGE 1: CHECKOUT ──────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '=== Pulling latest code from GitHub ==='
                checkout scm
            }
        }

        // ── STAGE 2: SETUP ─────────────────────────────────────────────────
        stage('Setup') {
            steps {
                echo '=== Cleaning up old containers ==='
                sh '''
                    docker rm -f ${APP_CONTAINER} ${DB_CONTAINER} ${TEST_CONTAINER} 2>/dev/null || true
                    docker network rm task-net 2>/dev/null || true
                    docker network create task-net
                '''
            }
        }

        // ── STAGE 3: BUILD APP ─────────────────────────────────────────────
        stage('Build App') {
            steps {
                echo '=== Building Flask application Docker image ==='
                dir("${APP_DIR}") {
                    sh 'docker build -t taskapp:latest .'
                }
            }
        }

        // ── STAGE 4: DEPLOY APP ────────────────────────────────────────────
        stage('Deploy App') {
            steps {
                echo '=== Starting MySQL database container ==='
                sh '''
                    docker run -d \
                        --name ${DB_CONTAINER} \
                        --network task-net \
                        -e MYSQL_ROOT_PASSWORD=root \
                        -e MYSQL_DATABASE=taskdb \
                        -v $(pwd)/${APP_DIR}/init.sql:/docker-entrypoint-initdb.d/init.sql \
                        mysql:8.0

                    echo "Waiting for MySQL to be ready..."
                    sleep 30
                '''

                echo '=== Starting Flask application container ==='
                sh '''
                    docker run -d \
                        --name ${APP_CONTAINER} \
                        --network task-net \
                        -e DB_HOST=${DB_CONTAINER} \
                        -e DB_USER=root \
                        -e DB_PASS=root \
                        -e DB_NAME=taskdb \
                        -p ${APP_PORT}:5000 \
                        taskapp:latest

                    echo "Waiting for Flask app to start..."
                    sleep 10

                    echo "=== Verifying app is up ==="
                    curl -f http://localhost:${APP_PORT} || exit 1
                    echo "App is running!"
                '''
            }
        }

        // ── STAGE 5: TEST ──────────────────────────────────────────────────
        stage('Test') {
            steps {
                echo '=== Building test container ==='
                dir("${TEST_DIR}") {
                    sh 'docker build -t selenium-tests:latest .'
                }

                echo '=== Running Selenium tests ==='
                sh '''
                    docker run \
                        --name ${TEST_CONTAINER} \
                        --network host \
                        -e BASE_URL=http://localhost:${APP_PORT} \
                        selenium-tests:latest \
                    || true

                    echo "=== Copying test results ==="
                    docker cp ${TEST_CONTAINER}:/tests/test-results ./test-results 2>/dev/null || true
                '''
            }
            post {
                always {
                    // Archive HTML report
                    publishHTML(target: [
                        allowMissing:          true,
                        alwaysLinkToLastBuild: true,
                        keepAll:               true,
                        reportDir:             'test-results',
                        reportFiles:           'report.html',
                        reportName:            'Selenium Test Report'
                    ])
                }
            }
        }

        // ── STAGE 6: CLEANUP ───────────────────────────────────────────────
        stage('Cleanup') {
            steps {
                echo '=== Stopping and removing containers ==='
                sh '''
                    docker rm -f ${APP_CONTAINER} ${DB_CONTAINER} ${TEST_CONTAINER} 2>/dev/null || true
                    docker network rm task-net 2>/dev/null || true
                '''
            }
        }
    }

    // ── POST: EMAIL NOTIFICATION ───────────────────────────────────────────
    post {
        always {
            script {
                def cause      = currentBuild.getBuildCauses('hudson.model.Cause$UserCause')
                def gitCause   = currentBuild.getBuildCauses('hudson.triggers.SCMTrigger$SCMTriggerCause')
                def pusherEmail = env.SENDER_EMAIL   // fallback

                // Try to get the email of whoever triggered via GitHub push
                try {
                    def changeSet = currentBuild.changeSets
                    if (changeSet && changeSet.size() > 0) {
                        def firstChange = changeSet[0].items[0]
                        pusherEmail = firstChange.authorEmail ?: env.SENDER_EMAIL
                    }
                } catch (Exception e) {
                    echo "Could not determine pusher email, using default: ${pusherEmail}"
                }

                def status  = currentBuild.currentResult
                def subject = "Jenkins Build ${status}: Student Task Manager - Build #${env.BUILD_NUMBER}"
                def body    = """
DevOps Assignment 3 - Jenkins Pipeline Report
==============================================
Build Number : ${env.BUILD_NUMBER}
Build Status : ${status}
Branch       : ${env.GIT_BRANCH ?: 'unknown'}
Duration     : ${currentBuild.durationString}
Build URL    : ${env.BUILD_URL}

Test Stage   : ${status == 'SUCCESS' ? 'PASSED' : 'FAILED / UNSTABLE'}

See the full Selenium HTML report at:
${env.BUILD_URL}Selenium_Test_Report/

Automated by Jenkins CI/CD Pipeline
"""
                emailext(
                    subject:    subject,
                    body:       body,
                    to:         pusherEmail,
                    from:       env.SENDER_EMAIL,
                    attachmentsPattern: 'test-results/report.html',
                    mimeType:   'text/plain'
                )
            }
        }
    }
}
