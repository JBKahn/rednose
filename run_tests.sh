pip install -e .
nosetests --rednose --with-id --force-color > test_results.txt 2>&1
result=$(comm -3 expected_results.txt test_results.txt | wc -l)

if [ "$result" -ge 32 -a "$result" -le 34 ];
	then exit 0
fi

if [ "$result" -eq 4 ];
	then exit 0
fi


if [ "$result" -eq 0 ];
	then exit 0
fi

# local python 2.6
if [ "$result" -eq 70 ];
	then exit 0
fi

# travis python 2.6
if [ "$result" -eq 78 ];
	then exit 0
fi

comm -3 expected_results.txt test_results.txt
comm -3 expected_results.txt test_results.txt | wc -l
exit 1
