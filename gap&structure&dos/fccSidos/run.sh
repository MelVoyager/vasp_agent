# https://www.bilibili.com/opus/744205995937366052
# Step 1: a DFT groundstate calculation
cp INCAR1 INCAR
mpirun -np 8 vasp_std

# # Step 2: obtain DFT virtual orbitals
cp INCAR2 INCAR
mpirun -np 8 vasp_std


# Step 3: the actual GW calculation
cp INCAR3 INCAR
mpirun -np 8 vasp_std

# Step 4:gather dos data
awk 'BEGIN{i=1} /dos>/,\
                /\/dos>/ \
                 {a[i]=$2 ; b[i]=$3 ; i=i+1} \
     END{for (j=12;j<i-5;j++) print a[j],b[j]}' vasprun.xml > dos.dat

ef=`awk '/efermi/ {print $3}' vasprun.xml`

# Step 5：plot dos with python
python plot.py