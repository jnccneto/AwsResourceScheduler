# AWS Scheduler Info
 

## Install 

Two step instalation is needed

First Gateway API / Lambda / Cognito resources and next the Javascript/HTML

The Username Password is generated in the GitHb Action. It echoes in the github output console


Issue this comands to trigger an instalation 

1. Instalation of Gateway API / Lambda / Cognito

Date=$(date +%D_%T); echo "infra_deploy $Date" > DeployTriggerFile.txt ; git add DeployTriggerFile.txt;git commit -m "Actions: infra_deploy ENV:LEARNING $Date";git push origin master

2. Instalation of S3 / Javascript code for DashBoard

Date=$(date +%D_%T); echo "DashBoard_setup $Date" > DeployTriggerFile.txt ; git add DeployTriggerFile.txt;git commit -m "Actions: DashBoard_setup ENV:LEARNING $Date";git push origin master


## SetUp Resources

Tags have to be added to resources so that scheduler app can start/stop at defined schedules.
TAGS:

        Key: "Name"
        Value: "Resource Name Used in DashBoard Listing/Debuging"      

        Key: "Project"
        Value: "Resource Project Group Used in DashBoard for grouping resources"

        Key: "Scheduler:Flag"
        Value: True|False 
        If True Resources is managed by Scheduler. If False or non existant, no action is taken

        Key: "Scheduler:Timings"
        Value: "0600:2000"
        time interval when resource should be running. Configured Values:
        "0600:2000","0900:1900","2000:0600"
        
        Key: "Scheduler:WeekDays"
        Value: "weekworkdays"
        week days when resource should be running. Configured Values:        
        "all","weekworkdays","sat,sun"

        Key: "Scheduler:OverRide"
        Value: ""
        Flag to overide the normal start/stop.
        Must be set in DashBoard WebConsole and with a Date




Below examples for adding to CloudFormation stacks



AWS::AutoScaling::AutoScalingGroup TAGS


      Tags: 
      - 
        Key: "Name"
        Value: "AsGroupNightShift"   
        PropagateAtLaunch: False 
      - 
        Key: "Project"
        Value: "App2_NightShift"
        PropagateAtLaunch: True 
      - 
        Key: "Scheduler:Flag"
        Value: True
        PropagateAtLaunch: True      
      - 
        Key: "Scheduler:Timings"
        Value: "2000:0600"
        PropagateAtLaunch: True         
      - 
        Key: "Scheduler:WeekDays"
        Value: "weekworkdays"
        PropagateAtLaunch: True         
      - 
        Key: "Scheduler:OverRide"
        Value: ""
        PropagateAtLaunch: True   
        
        
        
        
AWS::EC2::Instance TAGS

      Tags: 
      - 
        Key: "Name"
        Value: "Ec2_MultipleProjects_Night"      
      - 
        Key: "Project"
        Value: "App_Ec2Only,App2_NightShift"
      - 
        Key: "Scheduler:Flag"
        Value: True
      -         
        Key: "Scheduler:Timings"
        Value: "2000:0600"
      - 
        Key: "Scheduler:WeekDays"
        Value: "weekworkdays"
      - 
        Key: "Scheduler:OverRide"
        Value: ""        
        
        
        
        
AWS::RDS::DBInstance TAGS

     Tags: 
      - 
        Key: "Name"
        Value: "Rds_Day"      
      - 
        Key: "Project"
        Value: "App1_DayShift"
      - 
        Key: "Scheduler:Flag"
        Value: True
      -         
        Key: "Scheduler:Timings"
        Value: "0600:2000"
      - 
        Key: "Scheduler:WeekDays"
        Value: "weekworkdays"
      - 
        Key: "Scheduler:OverRide"
        Value: ""           
