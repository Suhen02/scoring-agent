

import sys
import os
import argparse
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.pipeline import run_pipeline
from app.utils.logger import log


def parse_args():
    parser = argparse.ArgumentParser(
        description="Candidate Intelligence System - Rank applicants using AI + rules"
    )

    parser.add_argument(
        "--input",
        type=str,
        default=os.environ.get("INPUT_CSV", "data/candidates.csv"),
        help="Path to input CSV file"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=os.environ.get("OUTPUT_CSV", "output/ranked_candidates.csv"),
        help="Path to output CSV file"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (verbose logs)"
    )

    return parser.parse_args()

def main():
    args = parse_args()

    input_csv = args.input
    output_csv = args.output

    log.info("=" * 60)
    log.info("Candidate Intelligence System Starting")
    log.info("=" * 60)

    log.info(f"Input file : {input_csv}")
    log.info(f"Output file: {output_csv}")

    try:
        results = run_pipeline(input_csv, output_csv)

        print("\n" + "=" * 90)
        print(f"{'Name':<25} {'Score':>7} {'Rule':>6} {'LLM':>5} {'Tier':<12} {'Conf':<8}")
        print("-" * 90)

        for r in results:
            print(
                f"{r['name']:<25} "
                f"{r['final_score']:>7.1f} "
                f"{r['rule_score']:>6} "
                f"{r['llm_score']:>5} "
                f"{r['tier']:<12} "
                f"{r.get('confidence', 'N/A'):<8}"
            )

        print("=" * 90)

        print("\nSummary Stats:")

        tier_counts = {}
        for r in results:
            tier_counts[r["tier"]] = tier_counts.get(r["tier"], 0) + 1

        for tier, count in sorted(tier_counts.items()):
            print(f"  {tier:<12}: {count}")

        print("\nPipeline completed successfully")

    except Exception as e:
        log.error("Pipeline failed!")
        log.error(str(e))

        if args.debug:
            traceback.print_exc()

        sys.exit(1)


if __name__ == "__main__":
    main()