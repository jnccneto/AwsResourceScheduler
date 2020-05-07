Install /////////////////////////////////////////
Infra	////////////////////////////////////////
Date=$(date +%D_%T); echo "infra_deploy $Date" > DeployTriggerFile.txt ; git add DeployTriggerFile.txt;git commit -m "Actions: infra_deploy ENV:LEARNING $Date";git push origin master
DashBoard	///////////////////////////////////
Date=$(date +%D_%T); echo "DashBoard_setup $Date" > DeployTriggerFile.txt ; git add DeployTriggerFile.txt;git commit -m "Actions: DashBoard_setup ENV:LEARNING $Date";git push origin master

