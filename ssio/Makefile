install: /usr/local/bin/ssio.py /etc/systemd/system/ssioe.service /etc/systemd/system/ssios.service
	systemctl daemon-reload
	systemctl enable ssioe ssios

/usr/local/bin/ssio.py: ssio.py
	install ssio.py /usr/local/bin

/etc/systemd/system/ssioe.service: ssioe.service
	cp ssioe.service /etc/systemd/system

/etc/systemd/system/ssios.service: ssios.service
	cp ssios.service /etc/systemd/system
