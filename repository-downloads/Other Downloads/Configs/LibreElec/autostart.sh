(
echo performance > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor    
echo 750 > /sys/devices/pci0000:00/0000:00:02.0/drm/card0/gt_min_freq_mhz
) &
nohup script.sh &
