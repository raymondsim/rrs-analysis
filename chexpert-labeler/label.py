"""Entry-point script to label radiology reports."""
import pandas as pd
import pdb
from args import ArgParser
from loader import Loader
from stages import Extractor, Classifier, Aggregator
from constants import *

from sklearn.metrics import f1_score
import numpy as np
import json

def df_to_list(df):
    results = []
    for row in df.values.tolist():
        results.append(row[1:])
    return results

# Function to calculate F1 score
def calculate_f1_score(ground_truth, prediction):
    results = []
    for index, row in enumerate(ground_truth):
        f1 = f1_score(ground_truth[index], prediction[index], average='macro')
        results.append(f1)
    return results

def write(reports, labels, output_path, verbose=False):
    """Write labeled reports to specified path."""
    labeled_reports = pd.DataFrame({REPORTS: reports})
    for index, category in enumerate(CATEGORIES):
        labeled_reports[category] = labels[:, index]

    if verbose:
        print(f"Writing reports and labels to {output_path}.")
    labeled_reports[[REPORTS] + CATEGORIES].to_csv(output_path,
                                                   index=False)
    
    return labeled_reports


def label(args):
    """Label the provided report(s)."""

    loader = Loader(args.reports_path,
                    args.sections_to_extract,
                    args.extract_strict,
                    args.num_chunks,
                    args.chunk_id)

    extractor = Extractor(args.mention_phrases_dir,
                          args.unmention_phrases_dir,
                          verbose=args.verbose)
    classifier = Classifier(args.pre_negation_uncertainty_path,
                            args.negation_path,
                            args.post_negation_uncertainty_path,
                            verbose=args.verbose)
    aggregator = Aggregator(CATEGORIES,
                            verbose=args.verbose)

    # Load reports in place.
    loader.load()
    # Extract observation mentions in place.
    extractor.extract(loader.collection)
    # Classify mentions in place.
    classifier.classify(loader.collection)
    # Aggregate mentions to obtain one set of labels for each report.
    labels, sentence_mappings = aggregator.aggregate(loader.collection)

    # Save to JSON file
    with open(f"{args.sentence_mapping_out}", "w") as f:
        json.dump(sentence_mappings, f, indent=4)

    predicted_labels = write(loader.reports, labels, args.output_path, args.verbose)

    if args.ref is not None:

        # F1 evaluation
        pred = df_to_list(predicted_labels.fillna(0))
        ref = df_to_list(pd.read_csv(args.ref).fillna(0))

        if len(pred) != len(ref):
            print("LENGTH OF TWO LISTS ARE NOT IDENTICAL")
            print(len(ref))
            print(len(pred))
            exit(0)

        results = calculate_f1_score(ref, pred)

        print("F1 score: ", np.mean(results))

if __name__ == "__main__":
    parser = ArgParser()
    label(parser.parse_args())

#     manual_args = ["--reports_path", "temp_input.txt",
#                    "--output_path", "temp_output.csv",
#                    "--num_chunks", "4",
#                    "--chunk_id", "0"]

#    label(parser.parse_args_manual(manual_args))
