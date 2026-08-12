read -p "What region are you running? " region
# # echo $region
# cd busbar_arc
# echo "Running 'drive_arc_bar.py'..."
# echo
# python drive_arc_bar.py -r $region
# cd ../busbar_straight
# echo "Running 'drive_straight_bar.py'..."
# python drive_straight_bar.py -r $region
# echo
# cd ../coil_interlayer
# echo "Running 'drive_interlayer.py'..."
# echo
# python drive_interlayer.py -r $region
# echo
# cd ../../SolCalc
# echo "Running 'calculate_Mau13_single_region.py'..."
# echo
# python calculate_Mau13_single_region.py -r $region
# echo
cd ../helicalc_drive/coil
echo "Running 'drive_helicalc.py'..."
echo
python drive_helicalc.py -r $region