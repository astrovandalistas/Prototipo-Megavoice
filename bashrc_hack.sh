# run aeffect lab stuff
isrun=`ps -u tgh | grep python | wc -l`
if [ $isrun -lt 1 ] 
then 
    cd /home/pi/Dev/Megavoice
while [ 1 -le 20 ]
do
    python megavoice.py --inport=8989 --localnetport=8900 --localnet=aeffect07.local --inip=aeffect02.local &
    killpid=$!
    sleep 110
    kill -9 $killpid
done
fi
