#!/bin/bash
while true; do
  clear
  echo "============================================="
  echo " 🤖 AI FAQ GENERATION PROGRESS MONITOR 🚀"
  echo "============================================="
  
  TOTAL=$(ls data/content | grep "\.json$" | wc -l)
  # Check for files still containing the generic fallback question
  REMAINING=$(grep -rl '"متى يتوفر' data/content/ | wc -l)
  REMAINING_TV=$(grep -rl '"متى تتوفر' data/content/ | wc -l)
  
  LET_TOTAL=$((REMAINING + REMAINING_TV))
  DONE=$((TOTAL - LET_TOTAL))
  
  echo "Total Pages: $TOTAL"
  echo "Pages rewritten by AI: $DONE"
  echo "Pages left to process: $LET_TOTAL"
  echo "---------------------------------------------"
  echo ">> Latest Logs from AI Bot:"
  tail -n 5 faq_ai.log
  echo "---------------------------------------------"
  echo "Press [CTRL + C] to exit this monitor."
  sleep 3
done
