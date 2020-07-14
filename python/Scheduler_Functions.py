"""
Copyright (c) <2019> <jose neto jose.neto@liber4e.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""



import boto3
import pprint
import datetime
import os
import dateutil.tz
import re

Debug = False

ec2_session = boto3.client('ec2')
autoscaling_sessions = boto3.client('autoscaling')
rds_session = boto3.client('rds')

########################################################

## SETTINGS ############################################
SchedulerFlagTagName = 'Scheduler:Flag'
SchedulerFlagTagNameOk = 'Exec'
SchedulerTimingsTagName = 'Scheduler:Timings'
SchedulerWeekDaysTagName = 'Scheduler:WeekDays'
SchedulerOverRideTagName = 'Scheduler:OverRide'
SchedulerActionsTagName = 'Scheduler:Actions'
SchedulerActionsStartBy = 'StartedBy:Scheduler'
SchedulerActionsStopBy = 'StopedBy:Scheduler'


defaultStartTime = '0700'
defaultStopTime = '1900'
defaultTimeZone = 'utc'
defaultDaysActive = 'all'
defaultTimingsTagName = "default"
TimingsSeparator = ":"

AllDaysTag = "all"
AllWeekWorkDaysTag = "weekworkdays"
WeekDaysList = ['mon', 'tue', 'wed', 'thu', 'fri','sat', 'sun']
WeekDaysSeparator = ","

WeekDaysValidateList = WeekDaysList
WeekDaysValidateList.append(AllDaysTag)
WeekDaysValidateList.append(AllWeekWorkDaysTag)


ResourceTypeEc2 = "ec2"
ResourceTypeAsGroup = "AsGrp"
ResourceTypeRDS = "rds"

Luxembourg = dateutil.tz.gettz('Europe/Luxembourg')
now = datetime.datetime.now(tz=Luxembourg).strftime("%H%M")
nowDay = datetime.datetime.today().strftime("%a").lower()


if Debug is True:
	print(defaultStartTime,defaultStopTime)
	print(defaultDaysActive)
	print("time: ",now )
	print("Day: ",nowDay )




## State and Timings ###################################################
########################################################################


def GetDayTime():
	return { 'Day': nowDay, 'Time': now} 

def CheckDesiredState(TimeIn,daysActiveIn):
	TimeInCheck = False
	daysActiveInCheck = False

	if Debug is True:
		print("CheckDesiredState ################## ")
		print("TimeIn: ",TimeIn )
		print("daysActiveIn: ",daysActiveIn )

	TimeIn_regex = r"[0-9]{4}" + re.escape(TimingsSeparator) + r"[0-9]{4}\b"
	if re.search(TimeIn_regex, TimeIn): 
		#print("TimeIn Macth OK")
		TimeInCheck = True
	else:
		print("TimeIn Format Error (TimeIn_regex) ",TimeIn,TimeIn_regex)

	daysActiveIn_regex = r"[a-z]{3}" + re.escape(WeekDaysSeparator) + r"[a-z]{3}\b"
	if re.search(daysActiveIn_regex, daysActiveIn): 
		#print("daysActiveIn multiple")
		daysActiveCheck = daysActiveIn.split(WeekDaysSeparator)
		for DayToCheck in daysActiveCheck:
			if DayToCheck.lower() in WeekDaysValidateList:
				#print("daysActiveIn OK: ",DayToCheck)
				daysActiveInCheck = True
			else:
				print("daysActiveIn Format Error: ",daysActiveIn,daysActiveIn_regex)
	else:
		#print("daysActiveIn Single Value")
		if daysActiveIn in WeekDaysValidateList:
			#print("daysActiveIn OK")
			daysActiveInCheck = True
		else:
			print("daysActiveIn Format Error:",daysActiveIn,daysActiveIn_regex)
			daysActiveInCheck = False

	if Debug is True:
		if TimeInCheck == True and daysActiveInCheck == True:
			print("TimeIn,daysActiveIn OK ")
		else:
			print("TimeIn,daysActiveIn Errors ")

	if TimeInCheck == True and daysActiveInCheck == True:
		if 	TimeIn.lower() == defaultTimingsTagName:
			startTimeIn = defaultStartTime
			stopTimeIn = defaultStopTime
		else:
			Timings = TimeIn.split(TimingsSeparator)
			startTimeIn = Timings[0]
			stopTimeIn = Timings[1]
	
		# Days Interpreter #############################
		isActiveDay = False
		if daysActiveIn.lower() == AllDaysTag:
			isActiveDay = True
		elif daysActiveIn.lower() == AllWeekWorkDaysTag:
			if (nowDay in WeekDaysList):
				isActiveDay = True
		else:
			daysActive = daysActiveIn.split(WeekDaysSeparator)
			for d in daysActive:
				if d.lower() == nowDay:
					isActiveDay = True
		# EndDays Interpreter #############################
	
		isActiveTime = False
	
		if startTimeIn < stopTimeIn:
			if startTimeIn <= str(now) and stopTimeIn >= str(now):
				isActiveTime = True
			elif startTimeIn >= str(now) or stopTimeIn <= str(now):
				isActiveTime = False
		elif startTimeIn > stopTimeIn:
			if startTimeIn <= str(now):
				isActiveTime = True
			elif startTimeIn > str(now) and stopTimeIn >= str(now):
				isActiveTime = True
			elif startTimeIn > str(now) and stopTimeIn < str(now):
				isActiveTime = False
		elif startTimeIn == stopTimeIn:
			isActiveTime = True
		
		
		if Debug is True:
			print("daysActiveIn: ",daysActiveIn )
			print("isActiveDay: ",isActiveDay )
			print("startTime ",startTimeIn)
			print("stopTime ",stopTimeIn)
			print("str(now) ",str(now))
			print("isActiveTime ",isActiveTime)
						
		if  isActiveTime == False or ( isActiveTime == True and isActiveDay == False):
			return "stopped"
		elif isActiveTime == True and isActiveDay == True:
			return "running"
	else:
		return None
## EndOfState and Timings ##############################################
########################################################################



def ProcessTags(TagsIn):
	#print("ProcessTags TagsIn #########################################")
	#print(TagsIn)
	InfoToReturn = {}

	if isinstance(TagsIn, list): 
		InfoToReturn['ResourceName'] = next((item['Value'] for item in TagsIn if item["Key"] == "Name"), None)
		InfoToReturn['Project'] = next((item['Value'] for item in TagsIn if item["Key"] == "Project"), None)
		InfoToReturn['Schedule'] = next((item['Value'] for item in TagsIn if ( item["Key"] == SchedulerFlagTagName )), None)
		InfoToReturn['SchedulerActions'] = next((item['Value'] for item in TagsIn if ( item["Key"] == SchedulerActionsTagName )), None)

		if next((item['Value'] for item in TagsIn if item["Key"] == SchedulerTimingsTagName), None) != None and next((item['Value'] for item in TagsIn if item["Key"] == SchedulerWeekDaysTagName), None) != None:
			InfoToReturn['ScheduleTimings'] = next((item['Value'] for item in TagsIn if ( item["Key"] == SchedulerTimingsTagName )), None)
			InfoToReturn['ScheduleWeekDays'] = next((item['Value'] for item in TagsIn if ( item["Key"] == SchedulerWeekDaysTagName )), None)
			InfoToReturn['ScheduleDesiredState'] = CheckDesiredState(InfoToReturn['ScheduleTimings'],InfoToReturn['ScheduleWeekDays'])
			InfoToReturn['ScheduleOverRide'] = next((item['Value'] for item in TagsIn if ( item["Key"] == SchedulerOverRideTagName )), None)

		if next((item['Value'] for item in TagsIn if item["Key"] == "aws:autoscaling:groupName"), None) != None:
			InfoToReturn['ResourceAsGroup'] = next((item['Value'] for item in TagsIn if item["Key"] == "aws:autoscaling:groupName"))

	#print("########################")
	#print("InfoToReturn: ",InfoToReturn)
	return InfoToReturn





## EC2 #################################################################
########################################################################
def GetAllEc2Instances():
	ec2_list = ec2_session.get_paginator('describe_instances')
	Ec2InfoToReturn = []

	for page in ec2_list.paginate(
			Filters=[
					{
						'Name': 'tag-key',
						'Values': [SchedulerFlagTagName]
					},
					{
						'Name': 'tag-value',
						'Values': [SchedulerFlagTagNameOk]
					}
			]		
	):
			for res in page['Reservations']:
					for Instance in res['Instances']:
							#print( Instance['InstanceId'])
							if Debug is True:
								pprint.pprint(Instance)
								
							InstanceInfo = {'ResourceType':'ec2','resourceId':Instance['InstanceId']}
							InstanceInfo['CurrentState'] = Instance['State']['Name']
							
							if('Tags' in Instance):
								InstanceInfoFromTags = ProcessTags(Instance['Tags'])
								InstanceInfo.update(InstanceInfoFromTags)
							else:
								InstanceInfo.update({'Schedule':False})
							if Debug is True:
								InstanceInfo['TAGS'] = []
								if('Tags' in Instance):
									for Tag in Instance['Tags']:
										InstanceInfo['TAGS'].append({Tag['Key']:Tag['Value']})
					
							Ec2InfoToReturn.append(InstanceInfo)
							#pprint.pprint(Instance['Instances'])
	return Ec2InfoToReturn


def UpdateEc2Schedule(resourceId,ScheduleTimings,ScheduleDays,OverRide):
	response = ec2_session.create_tags(
		DryRun=False,
		Resources=[resourceId],
		Tags=[
        {
            'Key': SchedulerTimingsTagName,
            'Value': ScheduleTimings
        },
        {
            'Key': SchedulerWeekDaysTagName,
            'Value': ScheduleDays
        },
        {
            'Key': SchedulerOverRideTagName,
            'Value': OverRide
        }
    ]
	)
	return ProcessAwsReply(response)

def StartEc2(resourceId):
	response = ec2_session.start_instances(
    InstanceIds=[resourceId],
    DryRun=False
	)
	if ProcessAwsReply(response) is True:
		ec2_session.create_tags(
		DryRun=False,
		Resources=[resourceId],
		Tags=[
			{
				'Key': SchedulerActionsTagName,
				'Value': SchedulerActionsStartBy,
			},
		]
	)	
	return ProcessAwsReply(response)


def StopEc2(resourceId):
	response = ec2_session.stop_instances(
		InstanceIds=[resourceId],
		DryRun=False,
		Hibernate=False,
		Force=False
	)
	if ProcessAwsReply(response) is True:
		ec2_session.create_tags(
		DryRun=False,
		Resources=[resourceId],		
		Tags=[
			{
				'Key': SchedulerActionsTagName,
				'Value': SchedulerActionsStopBy,
			},
		]
	)	
	return ProcessAwsReply(response)

def StopTerminateEc2(resourceId):
	response = ec2_session.terminate_instances(
		InstanceIds=[resourceId],
		DryRun=False,
	)
	if ProcessAwsReply(response) is True:
		ec2_session.create_tags(
		DryRun=False,
		Resources=[resourceId],		
		Tags=[
			{
				'Key': SchedulerActionsTagName,
				'Value': SchedulerActionsStopBy,
			},
		]
	)	
	return ProcessAwsReply(response)

def CheckIfEc2Exists(Ec2Id):
	response = ec2_session.describe_instances(
			Filters=[
					{
							'Name': 'instance-id',
							'Values': [Ec2Id]
					},
			],
	)
	if(len(response['Reservations']) > 0):
		Ec2Status = True
	else:
		Ec2Status = False
	return Ec2Status



## EndofEC2 ############################################################
########################################################################


## RDS #################################################################
########################################################################
def GetAllRdsInstances():
	RdsInfoToReturn = []
	ec2_list = rds_session.get_paginator('describe_db_instances')

	for page in ec2_list.paginate():
	
			for Instance in page['DBInstances']:
				#print(Instance['DbiResourceId'])
				if Debug is True:
					pprint.pprint(Instance)
					
				InstanceInfo = {'ResourceType':'rds','resourceId':Instance['DbiResourceId']}
				InstanceInfo['CurrentState'] = Instance['DBInstanceStatus']
				InstanceInfo['ResourceArn'] = Instance['DBInstanceArn']
				InstanceInfo['DBInstanceIdentifier'] = Instance['DBInstanceIdentifier']
				InstanceInfo['CurrentState'] = Instance['DBInstanceStatus']
				Tags = rds_session.list_tags_for_resource(ResourceName=Instance['DBInstanceArn'])['TagList']
				#pprint.pprint(Tags)


				if any(d['Key'] == SchedulerFlagTagName and d['Value'] == SchedulerFlagTagNameOk for d in Tags):
						#print('Exists!')					
						InstanceInfoFromTags = ProcessTags(Tags)
						InstanceInfo.update(InstanceInfoFromTags)
						
						if Debug is True:
							InstanceInfo['TAGS'] = []
							if('Tags' in Instance):
								for Tag in Instance['Instances'][0]['Tags']:
									InstanceInfo['TAGS'].append({Tag['Key']:Tag['Value']})
				
						InstanceInfo['ResourceName'] = Instance['DBInstanceIdentifier']
						RdsInfoToReturn.append(InstanceInfo)
	return RdsInfoToReturn

def GetRdsArn(resourceId):
	RdsInfo = GetAllRdsInstances()
	RdsInfoFiltered = [d for d in RdsInfo if d['resourceId'] == resourceId]
	return RdsInfoFiltered[0]['ResourceArn']

def GetRdsInstanceIdentifier(resourceId):
	RdsInfo = GetAllRdsInstances()
	RdsInfoFiltered = [d for d in RdsInfo if d['resourceId'] == resourceId]
	print(RdsInfoFiltered)
	return RdsInfoFiltered[0]['DBInstanceIdentifier']
		

def UpdateRdsSchedule(resourceId,ScheduleTimings,ScheduleDays,OverRide):

	RdsArn = GetRdsArn(resourceId)

	response = rds_session.add_tags_to_resource(
		ResourceName=RdsArn,
		Tags=[
        {
            'Key': SchedulerTimingsTagName,
            'Value': ScheduleTimings
        },
        {
            'Key': SchedulerWeekDaysTagName,
            'Value': ScheduleDays
        },
        {
            'Key': SchedulerOverRideTagName,
            'Value': OverRide
        }
    ]
	)
	return ProcessAwsReply(response)

def StartRds(resourceId):
	RdsArn = GetRdsArn(resourceId)
	RdsIdentifier = GetRdsInstanceIdentifier(resourceId)
	
	response = rds_session.start_db_instance(
		DBInstanceIdentifier=RdsIdentifier,
	)
	if ProcessAwsReply(response) is True:
		rds_session.add_tags_to_resource(
		ResourceName=RdsArn,
		Tags=[
			{
				'Key': SchedulerActionsTagName,
				'Value': SchedulerActionsStopBy,
			},
		]
	)	
	return ProcessAwsReply(response)


def StopRds(resourceId):
	RdsArn = GetRdsArn(resourceId)
	RdsIdentifier = GetRdsInstanceIdentifier(resourceId)
	print("STOPING ",resourceId,RdsIdentifier)
	response = rds_session.stop_db_instance(
		DBInstanceIdentifier=RdsIdentifier,
	)
	if ProcessAwsReply(response) is True:
		rds_session.add_tags_to_resource(
		ResourceName=RdsArn,
		Tags=[
			{
				'Key': SchedulerActionsTagName,
				'Value': SchedulerActionsStopBy,
			},
		]
	)	
	return ProcessAwsReply(response)


## EndofRDS ############################################################
########################################################################


## AutoScallingGroups ##################################################
########################################################################
    
def GetAutoScallingGroups(GroupId):
	
	if GroupId is "All":
   
		paginator = autoscaling_sessions.get_paginator('describe_auto_scaling_groups')
		page_iterator = paginator.paginate(
				PaginationConfig={'PageSize': 100}
		)
		filtered_asgs = page_iterator.search(
				'AutoScalingGroups[] | [?contains(Tags[?Key==`{}`].Value, `{}`)]'.format(SchedulerFlagTagName, SchedulerFlagTagNameOk)
		)
		AsGroups = {}
		AsGroups['AutoScalingGroups'] = []

		for asg in filtered_asgs:
				#print (asg['AutoScalingGroupName'])
				AsGroups['AutoScalingGroups'].append(asg)

		#pprint.pprint(AsGroups)

	else:
		AsGroups = autoscaling_sessions.describe_auto_scaling_groups(AutoScalingGroupNames=[GroupId])

	AsGroupsInfoToReturn = []
	for AsGrp in AsGroups['AutoScalingGroups']:
		#pprint.pprint(AsGrp)
		AsGrpInfo = {
			'ResourceType':'AsGrp',
			'resourceId':AsGrp['AutoScalingGroupName'],
			'AutoScalingGroupName':AsGrp['AutoScalingGroupName'],
			'AsGrpMinSize':AsGrp['MinSize'],
			'AsGrpMaxSize':AsGrp['MaxSize'],
			'AsGrpDesiredCapacity':AsGrp['DesiredCapacity'],
			}		
		if AsGrp['MinSize'] > 0:
			AsGrpInfo['CurrentState'] = "running"
		else:
			AsGrpInfo['CurrentState'] = "stopped"

		GroupInfoFromTags = ProcessTags(AsGrp['Tags'])
		AsGrpInfo.update(GroupInfoFromTags)
		AsGrpInfo['SuspendedLaunch'] = next(('true' for item in AsGrp['SuspendedProcesses'] if item["ProcessName"] == 'Launch'), None)
		AsGrpInfo['instances_ids'] = [item['InstanceId'] for item in AsGrp['Instances']]
		AsGrpInfo['ResourceAsGroup'] = AsGrp['AutoScalingGroupName']
		if Debug is True:
			AsGrpInfo['TAGS'] = [Tag for Tag in AsGrp['Tags']]

		AsGroupsInfoToReturn.append(AsGrpInfo)
		
	return AsGroupsInfoToReturn



def SuspendLaunchAutoScallingGroup(GroupId):
	print("Suspend GroupId ",GroupId)
	response = autoscaling_sessions.suspend_processes(
		AutoScalingGroupName=GroupId,
		ScalingProcesses=['Launch']
	)
	pprint.pprint(response)

def ResumeLaunchAutoScallingGroup(GroupId):
	print("Resume GroupId ",GroupId)
	response = autoscaling_sessions.resume_processes(
    AutoScalingGroupName=GroupId,
    ScalingProcesses=['Launch']
	)
	pprint.pprint(response)

def StopWithSuspendAutoScallingGroup(GroupId):
	print("Stop GroupId ",GroupId)
	SuspendLaunchAutoScallingGroup(GroupId)
	AsGroupDetails = GetAutoScallingGroups(GroupId)
	print("AsGroupDetails ",AsGroupDetails)
	print("instances_ids ",AsGroupDetails[0]['instances_ids'])
	if len(AsGroupDetails[0]['instances_ids']) > 0:
		for InstID in AsGroupDetails[0]['instances_ids']:
			ec2_session.terminate_instances(InstanceIds=[InstID],DryRun=False)
	else:
		print("no instances to stop ",len(AsGroupDetails[0]['instances_ids']))



def StartAutoScallingGroup(resourceId):
	response = autoscaling_sessions.update_auto_scaling_group(
				AutoScalingGroupName=resourceId,
				MinSize=1,
				MaxSize=1,
				DesiredCapacity=1,
			)
			
	if ProcessAwsReply(response) is True:
		autoscaling_sessions.create_or_update_tags(
		Tags=[
			{
				'Key': SchedulerActionsTagName,
				'Value': SchedulerActionsStartBy,
				'PropagateAtLaunch': True,
				'ResourceId': resourceId,
				'ResourceType': 'auto-scaling-group',
			},
		]
	)
	return ProcessAwsReply(response)
				
def StopAutoScallingGroup(resourceId):
	response = autoscaling_sessions.update_auto_scaling_group(
				AutoScalingGroupName=resourceId,
				MinSize=0,
				MaxSize=1,
				DesiredCapacity=0,
			)
	if ProcessAwsReply(response) is True:
		autoscaling_sessions.create_or_update_tags(
		Tags=[
			{
				'Key': SchedulerActionsTagName,
				'Value': SchedulerActionsStopBy,
				'PropagateAtLaunch': True,
				'ResourceId': resourceId,
				'ResourceType': 'auto-scaling-group',
			},
		]
	)
	return ProcessAwsReply(response)

def UpDateAutoScallingGroupSchedule(resourceId,ScheduleTimings,ScheduleDays,OverRide):
	print("UpDateAutoScallingGroupSchedule resourceId :", resourceId )  
	AsGrpIdInfo = GetAutoScallingGroups(resourceId)
	
	print("AsGrpIdInfo :")  
	print(AsGrpIdInfo)
	print("AsGrpIdInfo InstanceId :", AsGrpIdInfo[0]['instances_ids'] )
	for Instance in AsGrpIdInfo[0]['instances_ids']:
		## Check if instace exists 
		if CheckIfEc2Exists(Instance) is True:
			UpdateEc2Schedule(Instance,ScheduleTimings,ScheduleDays,OverRide)
		
			response = autoscaling_sessions.create_or_update_tags(
				Tags=[
					{
						'Key': SchedulerTimingsTagName,
						'Value': ScheduleTimings,
						'PropagateAtLaunch': True,
						'ResourceId': resourceId,
						'ResourceType': 'auto-scaling-group',
					},
					{
						'Key': SchedulerWeekDaysTagName,
						'Value': ScheduleDays,
						'PropagateAtLaunch': True,
						'ResourceId': resourceId,
						'ResourceType': 'auto-scaling-group',
					}
				]
			)
			FeedBack=ProcessAwsReply(response)
		else:
			FeedBack=False
	return FeedBack

## EndOfAutoScallingGroups ##################################################
#############################################################################

#SchedulerActionsStopdBy = 'StopedBy:Scheduler'


def ProcessAwsReply(InResponse):
	if InResponse['ResponseMetadata']['HTTPStatusCode'] == 200:
		print("ProcessAwsReply: ", True)
		return True
	else:
		print ("ERRORS in AWS PROCESS")
		print(InResponse)
		return False



def UpdateResourceSchedule(resourceId,ResourceType,ScheduleTimings,ScheduleDays,OverRide):
	print("UpdateResource ID: " ,resourceId)
	if ResourceType == ResourceTypeEc2:
		print("Resource: " ,ResourceTypeEc2)
		return UpdateEc2Schedule(resourceId,ScheduleTimings,ScheduleDays,OverRide)
	elif ResourceType == ResourceTypeAsGroup:
		print("Resource: " ,ResourceTypeAsGroup)
		return UpDateAutoScallingGroupSchedule(resourceId,ScheduleTimings,ScheduleDays,OverRide)
	elif ResourceType == ResourceTypeRDS:
		print("Resource: " ,ResourceTypeRDS)
		return UpdateRdsSchedule(resourceId,ScheduleTimings,ScheduleDays,OverRide)


def StartResource(resourceId,ResourceType):
	print("StartResource ID: " ,resourceId)
	if ResourceType == ResourceTypeEc2:
		print("Resource: " ,ResourceTypeEc2)
		return StartEc2(resourceId)
	elif ResourceType == ResourceTypeAsGroup:
		print("Resource: " ,ResourceTypeAsGroup)
		return StartAutoScallingGroup(resourceId)
	elif ResourceType == ResourceTypeRDS:
		print("Resource: " ,ResourceTypeRDS)
		return StartRds(resourceId)


def StopResource(resourceId,ResourceType):
	print("StopResource ID: " ,resourceId)
	if ResourceType == ResourceTypeEc2:
		print("Resource: " ,ResourceTypeEc2)
		return StopEc2(resourceId)
	elif ResourceType == ResourceTypeAsGroup:
		print("Resource: " ,ResourceTypeAsGroup)
		return StopAutoScallingGroup(resourceId)
	elif ResourceType == ResourceTypeRDS:
		print("Resource: " ,ResourceTypeRDS)
		return StopRds(resourceId)


def CheckScheduleOverRide(OverRideIn):
  if(OverRideIn is not None):
    OverRideIn_regex = r"[0-9]{2}-[0-9]{2}-[0-9]{4}"
    if re.search(OverRideIn_regex, OverRideIn):
      print("OverRideIn:", OverRideIn, "RegEx OK")
      if datetime.datetime.strptime(OverRideIn, '%d-%m-%Y') > datetime.datetime.now():
        print("OverRideIn After Today:")
        return True
      else:
        print("OverRideIn Before or Today:")
      return False
  return False




def CheckResourcesStateAndApplyChanges(ResourcesList):
	for Resource in ResourcesList:
		print("\n\n")
		print("#########################################")
		if(Resource['Schedule'] is not None and Resource['Schedule'] is not False):
			print("Checking Resource : ", Resource)
			print("ID : ", Resource['resourceId'])
			if 'ResourceName' in Resource:
				print("ResourceName : ", Resource['ResourceName'])
			print("ResourceType : ", Resource['ResourceType'])
			print("CurrentState : ", Resource['CurrentState'] , "Desired State", Resource['ScheduleDesiredState'])
			print("ScheduleOverRide : ", Resource['ScheduleOverRide'])
			ResourceOverRide = CheckScheduleOverRide(Resource['ScheduleOverRide'])
			print("CheckScheduleOverRide : ", ResourceOverRide)
			
			if ResourceOverRide == False:
				if Resource['ResourceType'] == 'rds':
					if Resource['CurrentState'] == "available" and Resource['ScheduleDesiredState'] == "stopped":
						print ("Stoping Resource")
						print (StopResource(Resource['resourceId'],Resource['ResourceType']))
					elif Resource['CurrentState'] == "stopped" and Resource['ScheduleDesiredState'] == "running":
						print ("Starting Resource")
						print (StartResource(Resource['resourceId'],Resource['ResourceType']))
				else:
					if Resource['ResourceType'] == 'ec2' and 'ResourceAsGroup' in Resource:
						print ("ec2 in AsGroup Ignoring")
					elif Resource['CurrentState'] == "running" and Resource['ScheduleDesiredState'] == "stopped":
						print ("Stoping Resource")
						print (StopResource(Resource['resourceId'],Resource['ResourceType']))
					elif Resource['CurrentState'] == "stopped" and Resource['ScheduleDesiredState'] == "running":
						print ("Starting Resource")
						print (StartResource(Resource['resourceId'],Resource['ResourceType']))
					elif Resource['CurrentState'] == "terminated":
						print ("Ignoring terminated")
					elif Resource['CurrentState'] == "pending":
						print ("Ignoring pending")
					else:
						print ("Resource State Ok")
			elif ResourceOverRide == True:
				print ("Resource Is on OverRide Status")
		else:
			if 'ResourceName' in Resource:
				print("ResourceName : ", Resource['ResourceName'])
			print("ID : ", Resource['resourceId'])
			print ("Resource Not Under Schedule")


def GetAllResourcesList():
	Ec2Info = GetAllEc2Instances()
	AsGroupsInfo = GetAutoScallingGroups("All")
	RdsInfo = GetAllRdsInstances()
	return AsGroupsInfo + Ec2Info + RdsInfo
