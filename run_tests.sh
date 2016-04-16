pip install -e .
nosetests -s --rednose --with-id --force-color > test_results.txt 2>&1
result=$(diff -U 0 expected_results.txt test_results.txt | grep ^@ | wc -l)

if [ $result -le 4 ];
	then exit 0
fi
diff expected_results.txt test_results.txt
exit 1
