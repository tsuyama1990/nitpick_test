echo "Testing files..."
if [ -d "src" ]; then
  echo "src found"
else
  echo "src missing"
fi
if [ -d "tests" ]; then
  echo "tests found"
else
  echo "tests missing"
fi
