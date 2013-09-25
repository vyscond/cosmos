echo '[setup] coping moon.service to /etc/systemd/system/'
cp moon.service /etc/systemd/system/
echo '[setup] refreshing daemons'
systemctl --system daemon-reload


