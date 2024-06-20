include .env

deploy: clean
	sudo docker build --tag scrum-dashboard-server .  && sudo docker run  -p 3000:3000 -v `pwd`.:/app scrum-dashboard-server

clean:
	sudo docker rmi scrum-dashboard-server -f

stop:
	sudo docker stop

jira-cli:
 	jirashell -s https://zadara.atlassian.net -u ${JIRA_USERNAME} -p ${JIRA_API_KEY}

show-env:
	echo ${JIRA_USERNAME}
	echo ${JIRA_API_KEY}