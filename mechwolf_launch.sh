#!/bin/bash
# Basic for loop

#Set the mechwolf client directories. Default is /home/pi/
directory="/home/pi"

for filename in /boot/*.yml.* 
do
	[ -e "$filename" ] || continue	# check if the list is empty
	echo $filename
	short=${filename##*/} # remove leading path
	base=${short%%.yml*} # filename without numbers or extension
	number=${filename##*.}
	echo $short
	echo $base
	echo $number
	echo "making directory $directory/client_$number"
	mkdir $directory/client_$number
	echo "copying $filename to $directory/client_$number/$base.yml"
	cp $filename $directory/client_$number/$base.yml	
	echo "launching mechwolf client"
	(cd $directory/client_$number; tmux new-session -d -s client$number "mechwolf client -vvv")
done

echo All done
