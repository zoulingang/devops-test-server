// Jenkins 声明式流水线：和 .github/workflows/ci.yml 跑同样的 Dagger 命令（lint、test、end-to-end）。
//
// Jenkins 侧的前提（需要在 Jenkins 机器上准备好，本仓库不负责安装 Jenkins）：
// 1. 运行这条流水线的 agent 是 Linux 或 macOS，装有 Docker，并且 Jenkins 运行用户能直接执行 `docker`
//    （Linux 上把 jenkins 用户加入 docker 组）。Dagger CLI 会自动用 Docker 启动 Dagger engine 容器。
// 2. agent 上有 curl 和 sh，并且能访问 dl.dagger.io、registry.dagger.io、Docker Hub、mcr.microsoft.com、
//    PyPI、npm registry 和 github.com（end-to-end 要从 GitHub 拉前端仓库的 Dagger 模块）。
// 3. Dagger CLI 不需要预装：下面的 "Install Dagger CLI" 阶段会把 DAGGER_VERSION 指定的版本装到
//    $WORKSPACE_TMP/bin（工作区之外，不会混进 --server=. 的目录），已装好同版本时跳过。
// 4. 插件：Pipeline、Git，推荐用 Multibranch Pipeline + GitHub Branch Source 来构建 PR 和 main。
//
// 版本号 0.21.11 同时写在 dagger.json、ci.yml 和这里，升级时一起改。
pipeline {
    // TODO：确定 Jenkins agent 的标签后改成 agent { label '...' }
    agent any

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20', artifactDaysToKeepStr: '14'))
    }

    environment {
        DAGGER_VERSION = '0.21.11'
        // E2E 用例在前端仓库，这里加载前端仓库 main 分支的 Dagger 模块。
        // 需要前后端一起改接口时，临时改成前端的对应分支，例如 github.com/zoulingang/devops-test-web@my-branch
        WEB_MODULE = 'github.com/zoulingang/devops-test-web@main'
    }

    stages {
        stage('Install Dagger CLI') {
            steps {
                sh '''
                    mkdir -p "$WORKSPACE_TMP/bin"
                    if ! "$WORKSPACE_TMP/bin/dagger" version 2>/dev/null | grep -q "v$DAGGER_VERSION"; then
                        curl -fsSL https://dl.dagger.io/dagger/install.sh | BIN_DIR="$WORKSPACE_TMP/bin" sh
                    fi
                    "$WORKSPACE_TMP/bin/dagger" version
                '''
            }
        }

        // 三个阶段并行运行，在 Jenkins 界面上各自显示为一个分支，对应 GitHub Actions 的三个 job。
        stage('CI') {
            parallel {
                stage('lint') {
                    steps {
                        sh '"$WORKSPACE_TMP/bin/dagger" call lint'
                    }
                }
                stage('test') {
                    steps {
                        sh '"$WORKSPACE_TMP/bin/dagger" call test'
                    }
                }
                stage('end-to-end') {
                    steps {
                        // 先导出报告：测试失败时这一步也成功，保证报告和截图一定能拿到。
                        // 报告导出到工作区之外（$WORKSPACE_TMP），否则下一步 --server=. 的内容变了，缓存失效会重跑测试
                        sh '''
                            rm -rf "$WORKSPACE_TMP/playwright-report"
                            "$WORKSPACE_TMP/bin/dagger" call -m "$WEB_MODULE" end-to-end-report --server=. export --path="$WORKSPACE_TMP/playwright-report"
                        '''
                        // 再判定结果：输入相同，Dagger 命中缓存不会重跑测试；有用例失败时这一步变红
                        sh '"$WORKSPACE_TMP/bin/dagger" call -m "$WEB_MODULE" end-to-end --server=.'
                    }
                    post {
                        // 不论成败都归档报告。archiveArtifacts 只能归档工作区里的文件，
                        // 所以两次 dagger call 都结束后，再把报告拷回工作区
                        always {
                            sh '''
                                rm -rf playwright-report
                                if [ -d "$WORKSPACE_TMP/playwright-report" ]; then
                                    cp -R "$WORKSPACE_TMP/playwright-report" playwright-report
                                fi
                            '''
                            archiveArtifacts artifacts: 'playwright-report/**', allowEmptyArchive: true
                            // 归档后删掉，免得下次构建时混进 --server=. 的目录
                            sh 'rm -rf playwright-report'
                        }
                    }
                }
            }
        }
    }
}
