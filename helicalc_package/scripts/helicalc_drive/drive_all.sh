cd busbar_arc
python drive_arc_bar.py -r DSTracker
cd ../busbar_straight
python drive_straight_bar.py -r DSTracker
cd ../coil_interlayer
python drive_interlayer.py -r DSTracker
cd ../../SolCalc
python calculate_Mau13_single_region.py -r DSTracker
cd ../helicalc_drive/coil
python drive_helicalc.py -r DSTracker