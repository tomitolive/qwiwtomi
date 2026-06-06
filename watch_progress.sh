#!/bin/bash
TOTAL=1936
while true; do
  CURRENT=$(ls -1 data/content/*.json 2>/dev/null | wc -l)
  REMAINING=$((TOTAL - CURRENT))
  
  if [ $CURRENT -gt $TOTAL ]; then
     CURRENT=$TOTAL
     REMAINING=0
  fi
  
  PERCENT=$(( CURRENT * 100 / TOTAL ))
  
  # رسم شريط التقدم (طوله 50 حرف)
  FILLED=$(( PERCENT * 50 / 100 ))
  EMPTY=$(( 50 - FILLED ))
  
  BAR=$(head -c $FILLED < /dev/zero | tr '\0' '█')
  EMPTY_BAR=$(head -c $EMPTY < /dev/zero | tr '\0' '░')
  
  echo "==========================================="
  echo "       متابعة تقدم البوت المباشرة"
  echo "==========================================="
  echo ""
  echo "إجمالي الصفحات المطلوبة : $TOTAL"
  echo "تم إنجاز              : $CURRENT"
  echo "متبقي                 : $REMAINING"
  echo ""
  echo "النسبة المئوية: $PERCENT%"
  echo "[$BAR$EMPTY_BAR]"
  echo ""
  echo "- لتوقيف المراقبة، اضغط على CTRL+C"
  echo "==========================================="
  
  sleep 3
done
