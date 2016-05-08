cd /bolt/bolt/apps/
find . -name "*.py" -type f -exec cat {} + | wc -l
find ./articles -name "*.py" -type f -exec cat {} + | wc -l
find ./core -name "*.py" -type f -exec cat {} + | wc -l
find ./common -name "*.py" -type f -exec cat {} + | wc -l
find ./jobs -name "*.py" -type f -exec cat {} + | wc -l
find ./comments -name "*.py" -type f -exec cat {} + | wc -l
find ./orgs -name "*.py" -type f -exec cat {} + | wc -l
find ./ratings -name "*.py" -type f -exec cat {} + | wc -l
find ./tasks -name "*.py" -type f -exec cat {} + | wc -l
find ./users -name "*.py" -type f -exec cat {} + | wc -l
find ./newspaper -name "*.py" -type f -exec cat {} + | wc -l
