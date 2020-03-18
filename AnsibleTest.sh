yamllint .
if [ $? -gt 0 ]
	echo wrong
else
	echo ok
