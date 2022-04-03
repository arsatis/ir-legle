echo "String 1: $1";
echo "String 2: $2";
echo "Finding $1 AND $2";

cd training/full
OUTPUT=$(find . -type f -exec grep -q -irnw $1 {} \; -exec grep -l -irnw $2 {} \;)
cd ../..

echo $OUTPUT
