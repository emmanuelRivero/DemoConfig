import requests
import json
import urllib
import os
import subprocess
import sys
import time

#ARG1 = sys.argv[1]

AWXurl = 'http://35.237.194.234'
AWXuser = 'emmait'
AWXpassword = 'emmanuelrf1234'
TemplateName = 'DemoBanorte'
CopyName = 'Dry-run ' + TemplateName
TemplateID = 9

### check connectivity to the AWX and if there is an other test running for this template 
r = requests.get(AWXurl + '/api/v2/job_templates/?search='+ CopyName, auth=(AWXuser,AWXpassword))
searchResult = json.loads(r.text)
if r.status_code == 200:	
	if searchResult["count"] != 0:
		print ("There is a test running please wait until its done")
		sys.exit(1)
else:
	print ("there was a problem connecting the AWX server please contact an adminstrator")
	sys.exit(1)

print ('Starting automatic YAML-Ansible test')
print ('=============================================')
### running tests ###
print ('YAML structure test:')
process = subprocess.Popen(['yamllint', '.'],
           stdout=subprocess.PIPE,
           stderr=subprocess.PIPE,
           universal_newlines=True)
stdout, stderr = process.communicate()

structureResults = stdout
structureCode = process.poll()

if structureCode != 0:
        print (structureResults)
else:
        print ('OK')

print ('=============================================')
print ('Ansible best practices test:')

process = subprocess.Popen(['ansible-lint'],
           stdout=subprocess.PIPE,
           stderr=subprocess.PIPE,
           universal_newlines=True)
stdout, stderr = process.communicate()

practicesResults = stdout
practicesCode = process.poll()

if practicesCode != 0:
        print (practicesResults)
else:
        print ('OK')

### Dry run test ###

print ('=============================================')
print ('starting check test')

Header = {'content-type': 'application/json'}
copyNameJson = {'name': CopyName}
updateData = {'job_type':'check'}
r = requests.post(AWXurl + '/api/v2/job_templates/'+ str(TemplateID) + '/copy/', data=json.dumps(copyNameJson), headers=Header, auth=(AWXuser,AWXpassword))

if r.status_code == 201:
	print ("Copying...")
else:
	print ("Ups, something happend, can't copy the template")
	error = json.loads(r.text)
	print (error)

r = requests.get(AWXurl + '/api/v2/job_templates/?search='+ CopyName, auth=(AWXuser,AWXpassword))

copyTemplate = {}
copyID = 0
if r.status_code == 200:
	print ("Found template...")
	copyTemplate = json.loads(r.text)
	copyID = copyTemplate["results"][0]["id"]
else:
	print ("Ups, something happend, can't find the copy")
	error = json.loads(r.text)
	print (error)

r = requests.patch(AWXurl + '/api/v2/job_templates/'+ str(copyID) +'/', data=json.dumps(updateData), auth=(AWXuser,AWXpassword), headers=Header)

if r.status_code == 200:
	print ("Check enable...")
else:
	print ("Ups, something happend, cant update the dopy")
	error = json.loads(r.text)
	print (error)

r = requests.post(AWXurl + '/api/v2/job_templates/'+ str(copyID) +'/launch/', data=json.dumps({}), auth=(AWXuser,AWXpassword), headers=Header)

jobStdout = ''
jobFinalStatus = 0
if r.status_code == 201:
	LaunchTemplate = json.loads(r.text)
	JobID = LaunchTemplate["job"]
	print ("Running job: " + str(JobID))
	while True:
		r = requests.get(AWXurl + '/api/v2/jobs/'+ str(JobID) +'/', auth=(AWXuser,AWXpassword))
		jobData = json.loads(r.text)
		status = jobData["status"]
		if status == "running" or status == "pending" :
			print ("Please wait, the test is running...")

		else:
			print ("Test finished status: " + status)
			
			r = requests.get(AWXurl + '/api/v2/jobs/'+ str(JobID) +'/stdout?format=txt', auth=(AWXuser,AWXpassword), headers={'content-type': 'text/plain ;utf-8'})
			dryResult = r.text
			if status == "successful":
				jobFinalStatus = 0
			else: 
				jobFinalStatus =1
			break
		time.sleep(5)
else:
	print ("Ups, something happend, can't launch the template")
	error = json.loads(r.text)
	print (r.status_code)
	print (error)

r = requests.delete(AWXurl + '/api/v2/job_templates/'+ str(copyID) +'/', auth=(AWXuser,AWXpassword))

if r.status_code == 204:
	print ("Copy deleted...")
else:
	print ("Ups, something happend, cant update the dopy")
	error = json.loads(r.text)
	print (error)

print ("test logs:")
print (dryResult)

### Summary ###

print (" Test Summary:")
print ("=============================================")

if structureCode != 0:
        print ("YAML structure test: Fail")
else:
        print ("YAML structure test: OK")

if practicesCode != 0:
        print ("Ansible best practices test: Fail")
else:
        print ("Ansible best practices test: OK")

if jobFinalStatus != 0:
		print ("Ansible check run: Fail")
else: 
		print ("Ansible check run: OK")
print("=============================================")

### generting results.txt ###
try:
	os.remove("results.txt")
except:
	print ("results.txt was not found creating a file")

f = open("results.txt", "a")
f.write("Automatic YAML-Ansible test results:\n\n")

f.write("=============================================\n")
f.write("### Test summary ###\n\n")

if structureCode != 0:
        f.write("YAML structure test: Fail\n")
else:
        f.write("YAML structure test: OK\n")

if practicesCode != 0:
        f.write ("Ansible best practices test: Fail\n")
else:
        f.write ("Ansible best practices test: OK\n")

if jobFinalStatus != 0:
		f.write ("Ansible check run: Fail\n\n")
else: 
		f.write ("Ansible check run: OK\n\n")
f.write("=============================================\n")
if structureCode != 0:
        f.write("\n###  YAML structure test results:  ###\n\n")
        f.write(structureResults)
        f.write("=============================================\n")

if structureCode != 0:
        f.write("\n### Ansible best practice test results: ###\n\n")
        f.write(practicesResults)
        f.write("=============================================\n")

f.write("\nCheck run logs:\n")
f.write(dryResult)
f.close()
print ("results.txt genereted")

if structureResults != 0 or practicesResults != 0 or dryResult !=0:
	sys.exit(1)


