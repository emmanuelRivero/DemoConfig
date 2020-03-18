yamllint .
if [ $? -gt 0 ]; then
	echo wrong
else
	echo ok
fi
