# AWS Scheduler Info
 

## Install 

Issue this comands to trigger an instalation 

1. Instalation of Gateway API / Lambda / Cognito

Date=$(date +%D_%T); echo "infra_deploy $Date" > DeployTriggerFile.txt ; git add DeployTriggerFile.txt;git commit -m "Actions: infra_deploy ENV:LEARNING $Date";git push origin master

2. Instalation of S3 / Javascript code for DashBoard

Date=$(date +%D_%T); echo "DashBoard_setup $Date" > DeployTriggerFile.txt ; git add DeployTriggerFile.txt;git commit -m "Actions: DashBoard_setup ENV:LEARNING $Date";git push origin master


