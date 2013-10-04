echo '[creating base dir]'
mkdir -p /home/moonserver/
rm -r /home/moonserver/*
echo '[coping file to dir]'
cp daemon.py  /home/moonserver/
cp moon.py    /home/moonserver/
cp vysocket.py /home/moonserver/
cp moon.config /home/moonserver/

cp -R applications /home/moonserver/
cp -R applications_map /home/moonserver/

echo '[coping service file to systemctl folder]'
#cp moonserver.service /usr/lib/systemd/system/

echo '[enable daemon at boot]'
#systemctl enable moonserver.service

echo '[setup done!]'
