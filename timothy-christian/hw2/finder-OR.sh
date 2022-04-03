echo "String 1: $1";
echo "String 2: $2";
echo "Finding $1 OR $2";

cd training/full
OUTPUT=$(grep -irnlw "$1\|$2")
cd ../..

echo $OUTPUT

