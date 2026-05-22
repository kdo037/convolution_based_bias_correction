#! /bin/bash
startdate=20100101
enddate=20101231
next=$startdate
numberOfDayPerCore=100
count=1

read -p "Enter the day: " date
echo "This is the $date"

delimiter="_"
IFS="$delimiter" read -r -a name_split <<< "$date"
model_first_day=${name_split[6]:0:8}

echo "model first day: $model_first_day"

# calculate number of core needed
firstDay=$(date +%Y%m%d -ud "$next")
lastDay=$(date +%Y%m%d -ud "$enddate")
#days=$((lastDay-firstDay+1))

let days=($(date +%s -d $lastDay)-$(date +%s -d $firstDay))/86400

days=$((days+1))
remainderDay=$((days % numberOfDayPerCore))
dividerDay=$((days/numberOfDayPerCore))

#echo $days
#echo $remainderDay
#echo $lastDay
#echo $dividerDay

export dir=/home/khanh/Documents/biasCorrection/gaussianFilter/test_scripts/

#echo $next
while [ "$next" -le "$enddate" ]
do
        if [ $count -le $dividerDay ]
        then
                yr="${next:0:4}"
                mo="${next:4:2}"
                dy="${next:6:2}"
                echo "before " $next
                
                nextday=$(date +%Y%m%d -ud "$next $((numberOfDayPerCore-1)) day")
                sed -e 's/syyyymmdd/'$next'/g' -e 's/eyyyymmdd/'$nextday'/g' -e 's/iyyyymmdd/'$model_first_day'/g' $dir/gaussianBiasSSP_final.py >& $dir/p_$count.py
                chmod 777 $dir/p_$count.py

                #next=$((nextday+1))
                next=$(date +%Y%m%d -ud "$nextday 1 day")
                count=$((count+1))
                echo $next
        else
                yr="${next:0:4}"
                mo="${next:4:2}"
                dy="${next:6:2}"


                nextday=$(date +%Y%m%d -ud "$next $((remainderDay)) day")
                echo "remainding day"
                if [ $remainderDay -eq 1 ]
                then
                        sed -e 's/syyyymmdd/'$next'/g' -e 's/eyyyymmdd/'$next'/g' -e 's/iyyyymmdd/'$model_first_day'/g' $dir/gaussianBiasSSP_final.py >& $dir/p_$count.py
                else
                        remain=$(date +%Y%m%d -ud "$next $((remainderDay-1)) day")
                        sed -e 's/syyyymmdd/'$next'/g' -e 's/eyyyymmdd/'$remain'/g' -e 's/iyyyymmdd/'$model_first_day'/g' $dir/gaussianBiasSSP_final.py >& $dir/p_$count.py
                fi

                chmod 777 $dir/p_$count.py
                next=$nextday
                count=$((count+1))
                #echo "test"
        fi
done

# run processes
i=1
#echo $count
while [ $i -lt $count ]
do
        #qsub -v runs=$i qsub.sh
        python3 $dir/p_$i.py "$date" &
        i=$((i+1))
        #echo $i
done
wait
