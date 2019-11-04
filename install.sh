rm -rf /opt/retropie/configs/all/AutoPivot/
mkdir /opt/retropie/configs/all/AutoPivot/
cp -f -r ./AutoPivot /opt/retropie/configs/all/

sudo chmod 755 /opt/retropie/configs/all/AutoPivot/*sh

sudo sed -i '/AutoPivot.py/d' /opt/retropie/configs/all/autostart.sh
sudo sed -i '/emulationstation/d' /opt/retropie/configs/all/autostart.sh
echo '#LANG=ko_KR.UTF-8 emulationstation #auto' >> /opt/retropie/configs/all/autostart.sh
echo '/opt/retropie/configs/all/AutoPivot/AutoPivot.py' >> /opt/retropie/configs/all/autostart.sh

python ./AutoPivot/setup.py

echo
echo "Setup Completed. Reboot after 3 Seconds."
sleep 3
reboot
