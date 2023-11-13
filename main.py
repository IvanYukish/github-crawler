import argparse
import json
import logging
import os

from app.models import GithubModel
from app.settings import DEFAULT_PATH
from app.crawlers import GitHubCrawler


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--input_path', type=str, nargs=1,
                        help='path to dir that contains all input files inside current project, default "app/data"')
    parser.add_argument('--output_path', type=str, nargs=1,
                        help='path to dir that contains all output files inside current project, default "app/data"')

    args = parser.parse_args()
    input_path = args.input_path.pop(0) if args.input_path else DEFAULT_PATH
    output_path = args.output_path.pop(0) if args.output_path else DEFAULT_PATH

    files = [file for file in os.listdir(input_path) if file.startswith("input")]

    for index, file in enumerate(sorted(files)):
        with open(os.path.join(input_path, file), "r") as f:
            data = json.load(f)

        # validate data
        GithubModel(**data)

        collected_data = GitHubCrawler(**data).run()
        output_file_name = os.path.join(output_path, f"output_example{index + 1}.json")

        with open(output_file_name, "w") as f:
            json.dump(collected_data, f, indent=4)

        logger.warning(f"{output_file_name}, was populated by data")
