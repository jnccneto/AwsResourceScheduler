import os
import sys
import pprint

def lambda_handler(event, context):
	print('############# EVENT #################')
	print(event)
	if 'source' in event:
		if event['source'] == 'aws.events':
			print("GetAllResourcesList###########################")
			AllResources = Scheduler_Functions.GetAllResourcesList()
			print("CheckResourcesStateAndApplyChanges###########################")      
			Scheduler_Functions.CheckResourcesStateAndApplyChanges(AllResources)
        
OnAws = True
if os.environ.get("AWS_EXECUTION_ENV") == None:
	print("Not On AWS")
	OnAws = False
	sys.path.append('python')
	import Scheduler_Functions
	lambda_handler({'source':'aws.events'},None)
else:
	print("On AWS")
	import Scheduler_Functions
