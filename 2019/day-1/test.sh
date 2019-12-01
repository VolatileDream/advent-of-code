#!/bin/bash

echo "Testing part 1"
diff <(./main.py --by-line --part 1 test.1.in) test.1.out
echo "Testing part 2"
diff <(./main.py --by-line --part 2 test.2.in) test.2.out
