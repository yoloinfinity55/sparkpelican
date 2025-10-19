"""
Main automation entrypoint for SparkPelican.
Example:
    python -m src.main process_youtube "https://youtube.com/watch?v=..."
"""
import sys
from src.utils.logger import get_logger

logger = get_logger()

def main():
    logger.info("SparkPelican automation starting...")
    if len(sys.argv) > 1:
        task = sys.argv[1]
        logger.info(f"Running task: {task}")
        # future: add subcommands like 'process_youtube', 'generate_ai_post', etc.
    else:
        logger.info("No task specified.")
        print("Usage: python -m src.main [task]")

if __name__ == "__main__":
    main()
