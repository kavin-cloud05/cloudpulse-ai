#!/usr/bin/env bash
# CloudPulse AI - Linux server health check
# Exit code: 0 = all OK, 1 = warning found, 2 = critical found

# Thresholds (percent)
CPU_WARN=70;  CPU_CRIT=90
MEM_WARN=75;  MEM_CRIT=90
DISK_WARN=70; DISK_CRIT=85

# Compare a value with warn/crit limits and print OK, WARNING or CRITICAL
level() {
  if [ "$1" -ge "$3" ]; then echo "CRITICAL"
  elif [ "$1" -ge "$2" ]; then echo "WARNING"
  else echo "OK"
  fi
}

# CPU usage: read /proc/stat twice, one second apart
cpu_usage() {
  read -r _ u1 n1 s1 i1 w1 q1 sq1 _ < /proc/stat
  sleep 1
  read -r _ u2 n2 s2 i2 w2 q2 sq2 _ < /proc/stat
  local idle=$(( (i2 + w2) - (i1 + w1) ))
  local total=$(( (u2+n2+s2+i2+w2+q2+sq2) - (u1+n1+s1+i1+w1+q1+sq1) ))
  [ "$total" -eq 0 ] && echo 0 || echo $(( 100 * (total - idle) / total ))
}

CPU=$(cpu_usage)
MEM=$(free | awk '/Mem:/ {printf "%d", $3/$2*100}')
DISK=$(df / | awk 'NR==2 {gsub("%","",$5); print $5}')

CPU_L=$(level "$CPU" $CPU_WARN $CPU_CRIT)
MEM_L=$(level "$MEM" $MEM_WARN $MEM_CRIT)
DISK_L=$(level "$DISK" $DISK_WARN $DISK_CRIT)

echo "===== CloudPulse AI Server Health ====="
echo "Time:    $(date '+%Y-%m-%d %H:%M:%S')"
echo "Host:    $(hostname)"
echo "Uptime:  $(uptime -p)"
echo "CPU:     ${CPU}%  [$CPU_L]"
echo "Memory:  ${MEM}%  [$MEM_L]"
echo "Disk /:  ${DISK}%  [$DISK_L]"

if command -v docker > /dev/null 2>&1; then
  echo "Docker:  $(systemctl is-active docker)"
else
  echo "Docker:  not installed"
fi

echo
echo "Top 5 processes by CPU:"
ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -6

# Set the exit code from the worst level
if [ "$CPU_L" = "CRITICAL" ] || [ "$MEM_L" = "CRITICAL" ] || [ "$DISK_L" = "CRITICAL" ]; then
  exit 2
elif [ "$CPU_L" = "WARNING" ] || [ "$MEM_L" = "WARNING" ] || [ "$DISK_L" = "WARNING" ]; then
  exit 1
fi
exit 0
