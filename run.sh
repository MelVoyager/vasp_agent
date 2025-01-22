export OPENAI_BASE_URL=https://api.claudeshop.top/v1
export OPENAI_API_KEY=sk-quJAzB28WxqweFevx5cn5GWKxu4IAzwbih6p864uA7Mvs5hF

# check python name
if [ "$#" -lt 1 ]; then
    echo "用法: $0 <python_file> [args...]"
    exit 1
fi

PYTHON_FILE="$1"
shift

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
WORKSPACE="logs/${TIMESTAMP}"
LOG_FILE="${PYTHON_FILE}_${TIMESTAMP}.log"

mkdir $WORKSPACE
# python "$PYTHON_FILE".py --ws "$WORKSPACE" "$@"
python "$PYTHON_FILE".py --ws "$WORKSPACE" "$@" 2>&1 | tee "$WORKSPACE/$LOG_FILE"

echo "check out log at: $WORKSPACE/$LOG_FILE"