A=1; while [ $A -lt 1001 ]; do echo python main.py --seed $A; A=`expr ${A} + 1`; done >> run.sh

