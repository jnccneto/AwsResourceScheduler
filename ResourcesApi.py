import json
import os
import sys
import pprint



def lambda_handler(event, context):
	print('############# EVENT #################')
	print(event)
	if 'resource' in event:
	#if event['resource'] is not None:
		print("API CALL   ################################")
		if event['resource'] == '/list':
			print("List ####################################")
			
			
			RdsInfo = Scheduler_Functions.GetAllRdsInstances()
			RdsInfoFiltered = [d for d in RdsInfo if d['Schedule'] in ['True','true']]

			Ec2Info = Scheduler_Functions.GetAllEc2Instances()
			Ec2InfoFiltered = [d for d in Ec2Info if d['Schedule'] in ['True','true'] and d['CurrentState'] != "terminated" ]

			AsGroupsInfo = Scheduler_Functions.GetAutoScallingGroups("All")
			AsGroupsFiltered = [d for d in AsGroupsInfo if d['Schedule'] in ['True','true']]

			DayTimeOnService = Scheduler_Functions.GetDayTime()
			ResourcesInfo = AsGroupsFiltered + Ec2InfoFiltered + RdsInfoFiltered + [DayTimeOnService]
			
			
			if OnAws == False:
				pprint.pprint(ResourcesInfo)
			return {
				'statusCode': 200,
				'headers': {
					"Access-Control-Allow-Origin" : "*", ## Required for CORS support to work
					## "Access-Control-Allow-Credentials" : True ## Required for cookies, authorization headers with HTTPS
				},
				'body': json.dumps(ResourcesInfo),
			}
		if event['resource'] == '/updateschedule':
			print("updateschedule ####################################")
			if  ( event['queryStringParameters']['resourceId'] and event['queryStringParameters']['ResourceType'] and event['queryStringParameters']['ScheduleTimings'] and event['queryStringParameters']['ScheduleWeekDays'] and event['queryStringParameters']['ScheduleOverRide'] ) is not None:
					response = Scheduler_Functions.UpdateResourceSchedule(event['queryStringParameters']['resourceId'],event['queryStringParameters']['ResourceType'],event['queryStringParameters']['ScheduleTimings'],event['queryStringParameters']['ScheduleWeekDays'],event['queryStringParameters']['ScheduleOverRide'])
					if(response is True):
						HtmlFeedBack = "ProcessOk"
					else:
						HtmlFeedBack = response
					return {
						'statusCode': 200,
						'headers': {
							"Access-Control-Allow-Origin" : "*", ## Required for CORS support to work
						},
						'body': json.dumps(HtmlFeedBack),
						}

       
        
OnAws = True
if os.environ.get("AWS_EXECUTION_ENV") == None:
	print("Not On AWS")
	OnAws = False
	import argparse
	sys.path.append('python')

	#from testcase import TestCase
	import Scheduler_Functions
	
	parser = argparse.ArgumentParser(description='A tutorial of argparse!')
	parser.add_argument("--action")
	parser.add_argument("--resourceId")
	parser.add_argument("--ScheduleTimings")
	parser.add_argument("--ScheduleWeekDays")
	parser.add_argument("--ScheduleOverRide")
	parser.add_argument("--ResourceType")

	args = parser.parse_args()
	action = args.action
	resourceId = args.resourceId
	ScheduleTimings = args.ScheduleTimings
	ScheduleWeekDays = args.ScheduleWeekDays
	ScheduleOverRide = args.ScheduleOverRide
	ResourceType = args.ResourceType
	if action == "update" and ( resourceId and ScheduleTimings and ScheduleWeekDays and ScheduleOverRide ) is not None:
		print("ACTIONS: ", resourceId,  ScheduleTimings,  ScheduleWeekDays,  ScheduleOverRide )
		event = {}
		event['queryStringParameters'] = {}
		event['queryStringParameters']['resourceId'] = resourceId
		event['queryStringParameters']['ScheduleTimings'] = ScheduleTimings
		event['queryStringParameters']['ScheduleWeekDays'] = ScheduleWeekDays
		event['queryStringParameters']['ScheduleOverRide'] = ScheduleOverRide
		event['queryStringParameters']['ResourceType'] = ResourceType
		
		event['resource'] = '/updateschedule'
		lambda_handler(event, None)


	elif action == "list":
		lambda_handler({'resource':'/list'},None)
else:
	print("On AWS")
	import Scheduler_Functions
