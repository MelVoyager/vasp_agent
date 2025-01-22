homo=`awk '/NELECT/ {print $3/2}' $1`
lumo=`awk '/NELECT/ {print $3/2+1}' $1`
nkpt=`awk '/NKPTS/ {print $4}' $1`

e1=`grep "     $homo     " $1 | tail -$nkpt | sort -n -k 3 | tail -1 | awk '{print $3}'`
e2=`grep "     $lumo     " $1 | tail -$nkpt | sort -n -k 3 | head -1 | awk '{print $3}'`

echo "HOMO: band:" $homo " E=" $e1
echo "LUMO: band:" $lumo " E=" $e2
