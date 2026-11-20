
import json
import sys
from pathlib import Path

# Load the production JobShield engine.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "artifacts" / "jobshield"))

from analysis_engine import analyze_text

DATASET = Path(__file__).with_name("dataset.json")


def main():
    examples = json.loads(DATASET.read_text(encoding="utf-8"))

    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0

    print("\nJOBSHIELD ACCURACY EVALUATION")
    print("=" * 55)

    for example in examples:
        result = analyze_text(example["text"])
        signals = ", ".join(f.key for f in result.findings) or "none"
        print(f"  Detected warning signals: {signals}")

        # Initial evaluation threshold: score 20 or higher.
        predicted_scam = result.score >= 20
        actual_scam = example["label"] == "scam"

        if predicted_scam and actual_scam:
            true_positive += 1
            outcome = "CORRECT SCAM"
        elif predicted_scam and not actual_scam:
            false_positive += 1
            outcome = "FALSE POSITIVE"
        elif not predicted_scam and not actual_scam:
            true_negative += 1
            outcome = "CORRECT LEGITIMATE"
        else:
            false_negative += 1
            outcome = "MISSED SCAM"

        print(
            f'{example["id"]}: score={result.score:3} '
            f'expected={example["label"]:10} {outcome}'
        )

    total = len(examples)

    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative
    legitimate_denominator = true_negative + false_positive

    precision = (
        true_positive / precision_denominator
        if precision_denominator else 0
    )
    recall = (
        true_positive / recall_denominator
        if recall_denominator else 0
    )
    false_positive_rate = (
        false_positive / legitimate_denominator
        if legitimate_denominator else 0
    )
    accuracy = (
        (true_positive + true_negative) / total
        if total else 0
    )

    print("\nCONFUSION MATRIX")
    print(f"True positives:  {true_positive}")
    print(f"False positives: {false_positive}")
    print(f"True negatives:  {true_negative}")
    print(f"False negatives: {false_negative}")

    print("\nMETRICS AT SCORE >= 20")
    print(f"Precision:           {precision:.1%}")
    print(f"Recall:              {recall:.1%}")
    print(f"False-positive rate: {false_positive_rate:.1%}")
    print(f"Accuracy:            {accuracy:.1%}")
    print(f"Examples evaluated:  {total}")


if __name__ == "__main__":
    main()
