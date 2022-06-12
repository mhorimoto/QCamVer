install: /usr/local/bin/buttons.py /usr/lib/systemd/system/buttons.service

/usr/local/bin/buttons.py: buttons.py
	install -m 700 buttons.py /usr/local/bin

/usr/lib/systemd/system/buttons.service: buttons.service
	cp buttons.service /usr/lib/systemd/system
	systemctl daemon-reload
	systemctl start buttons
	systemctl enable buttons

