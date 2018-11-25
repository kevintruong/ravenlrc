#! /usr/bin/env bash

a=$(cat $1|sed -E '/\[0.*\]/!d'|awk -F"\n" '{print NR"*"$1}'|sed 's#\]#*#g'|sed 's#\[#00:#g')
b=$(echo "$a"|awk -F"*" '{print $1}')
c=$(echo "$a"|awk -F"*" '{print $2}'|sed 's#\.#,#g'|sed 's/$/0/g'|cut -c-12)
d=$(echo "$a"|awk -F"*" '{print $2}'|sed '1d'|sed 's#\.#,#g'|sed 's/$/0/g')
e=$(echo "$c"|sed -n '$p'|awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')
f=$(expr $e + 10)
#g=$(date -r $f|awk '{print $4}'|awk -F: '{ print "00:"$2":"$3",000"}')         #the date command may only works for OS X
h=$(echo -e "$d""\n""$g"|cut -c-12)
j=$(echo "$a"|awk -F"*" '{print $3}')
k=$(paste -d"-" <(printf "%s" "$c") <(printf "%s" "$h")|sed 's#-# --> #g')
paste -d "\n" <(printf "%s" "$b") <(printf "%s" "$k") <(printf "%s" "$j") |awk -v n=3 '1; NR % n == 0 {print ""}'>lrc.srt
