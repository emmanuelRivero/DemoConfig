#!/bin/bash
### removing results files ###
rm -f results.txt
rm -f yml-structure.txt
rm -f ansible-practice.txt

### running tests ###
echo Starting YAML-Ansible playbook tests:
echo YAML auto check results:

yamllint .
if [ $? -gt 0 ]; then
        STRUCTURE=1
else
        STRUCTURE=0
fi

ansible-lint *.yml *.yaml
if [ $? -gt 0 ]; then
        PRACTICE=1
else
        PRACTICE=0
fi

### generating report ###
echo YAML auto check results: >> results.txt
echo ============================== >> results.txt
if [ $STRUCTURE -eq 0 ]; then
		echo YAML structure: OK >> results.txt
else
		echo YAML structure: Fail >> results.txt

        echo YAML structure Test:> yaml-structure.txt
        echo ============================== >> yaml-structure.txt
        yamllint . >> yaml-structure.txt
fi
if [ $PRACTICE -eq 0 ]; then
		echo Ansible practice: OK  >> results.txt
else
		echo Ansible practice: Fail >> results.txt

        echo Ansible practice Test results: >> ansible-practice.txt
        echo ============================== >> ansible-practice.txt
        ansible-lint *.yml *.yaml >> ansible-practice.txt
fi
echo ============================== >> results.txt

### priting report to main I/O ###
echo Test results:
echo ==============================
if [ $STRUCTURE -eq 0 ]; then
		echo YAML structure: OK
else
		echo YAML structure: Fail	
fi

if [ $PRACTICE -eq 0 ]; then
		echo Ansible practice: OK
else
		echo Ansible practice: Fail
fi
echo ==============================

