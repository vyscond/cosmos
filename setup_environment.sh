moon_service="[Unit]\nDescription=Moon Server\nAfter=network.target\n\n[Service]\nPIDFile=/root/moon/pid\nExecStart=/usr/bin/python2 /usr/bin/moon.py /root/moon/moon.cfg start &> /dev/null &\nExecStop=/usr/bin/python2 /usr/bin/moon.py /root/moon/moon.cfg stop &> /dev/null &\n\n[Install]\nWantedBy=multi-user.target\n"

moon_cfg="{\n    \n    \"name\" : \"$1\" ,\n    \"ip\"   : \"$2\" ,\n    \"port\" : \"$3\" ,\n    \"pid\"  : \"$4/moon/pid\" ,\n    \"stream\" : \n    {        \"stdin\"  : \"default\" ,\n        \"stdout\" : \"$4/moon/moonserver.std\" ,\n        \"stderr\" : \"$4/moon/moonserver.std\"\n    }\n    \n    ,\n    \n    \"directorys\" :\n    {\n        \"applications\"     : \"$4/moon/apps\" ,\n        \"application_profiles\" : \"$4/moon/app_profiles\"\n    }\n\n}\n"

echo '[cosmos]['`pwd`'][creating folder hierarchy]'

echo '[cosmos]['`pwd`'][creating moon folder]'
echo "mkdir moon"
mkdir moon

cd moon
echo '[cosmos]['`pwd`'][creating app_profiles folder]'
echo "mkdir app_profiles"
mkdir app_profiles

echo '[cosmos]['`pwd`'][creating apps folder]'
echo "mkdir apps"
mkdir apps

echo '[cosmos]['`pwd`'][creating moon.cfg file]'
echo "touch moon.cfg"
touch moon.cfg

echo '[cosmos]['`pwd`'][filling up moon.cfg with]'
echo "echo -e \$moon_cfg"
echo -e $moon_cfg > $4/moon/moon.cfg

cd /usr/lib/systemd/system/
echo '[cosmos]['`pwd`'][installing moon.service file]'
echo "echo -e \$moon_service > moon.service"
echo -e $moon_service > moon.service

cd
echo '[cosmos]['`pwd`'][enabling moon service at boot]'
echo "systemctl enable moon.service"
systemctl enable moon.service



