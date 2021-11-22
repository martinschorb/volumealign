#!/bin/bash
echo This is the hostname:
sleep 5
hostname
sleep 5
echo this is the input file
echo $1
sleep 5
cp $1 out.jpg
echo Now we go on...
sleep 15
echo and another hostname
sleep 30
hostname
