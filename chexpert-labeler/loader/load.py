"""Define report loader class."""
import warnings
import re
import bioc
import pandas as pd
from negbio.pipeline import text2bioc, ssplit, section_split
from tqdm import tqdm
import json

from constants import *

import sys

class Loader(object):
    """Report impression loader."""
    def __init__(self, reports_path, sections_to_extract, extract_strict):
        self.reports_path = reports_path
        self.sections_to_extract = sections_to_extract
        self.extract_strict = extract_strict
        self.punctuation_spacer = str.maketrans({key: f"{key} "
                                                 for key in ".,"})
        self.splitter = ssplit.NegBioSSplitter(newline=False)
        # === ADDED PARAMETERS ===
        self.num_chunks = num_chunks
        self.chunk_id = chunk_id
        # ========================

    def load(self):
        """Load and clean the reports."""
        collection = bioc.BioCCollection()

        if str(self.reports_path).endswith(".csv"):
            reports = pd.read_csv(self.reports_path,
                              header=None,
                              names=[REPORTS])[REPORTS].tolist()
        elif str(self.reports_path).endswith(".txt") or str(self.reports_path).endswith(".target") or str(self.reports_path).endswith(".tok"):
            print("READING IN TXT FILE")
            reports = [line.strip() for line in open(self.reports_path, encoding="utf-8").readlines()]
            # reports = [" ".join(doc.split()[1:]) for doc in reports] # Remove prepend image ID
            if self.num_chunks and self.chunk_id is not None:
                print(f"CHUNKING TXT INPUT INTO {self.num_chunks} CHUNKS. PROCESSING CHUNK {self.chunk_id}.")
                n = len(reports)
                chunk_size = (n + self.num_chunks - 1) // self.num_chunks
                start = chunk_size * self.chunk_id
                end = min(chunk_size * (self.chunk_id + 1), n)
                reports = reports[start:end]
                print(f"PROCESSING REPORTS FROM {start} TO {end}. TOTAL {len(reports)} REPORTS.")
            print("NUMBER OF TEST SAMPLES: ", len(reports))
        elif "temp_input" not in str(self.reports_path) and str(self.reports_path).endswith(".json"):
            print("READING IN JSON FILE", self.reports_path)
            data = json.loads(open(self.reports_path, 'r').read())
            data = data["test"]
            reports = [item["findings"] for item in data]
        elif "temp_input" in str(self.reports_path):
            print("READING IN JSON FILE", self.reports_path)
            data = json.loads(open(self.reports_path, 'r').read())
            # flatten_data = data["train"] + data["test"] + data["val"]
            reports = [item["findings"] for item in data] 
        else:
            sys.exit("Error: Input not in correct format")

        print("START READING AND EXTRACT SECTIONS ... ")
        for i, report in tqdm(enumerate(reports)):
            # print(report[:20], type(report[:20]))

            clean_report = self.clean(report)
            document = text2bioc.text2document(str(i), clean_report)

            if self.sections_to_extract:
                document = self.extract_sections(document)

            split_document = self.splitter.split_doc(document)

            assert len(split_document.passages) == 1,\
                ('Each document must be given as a single passage.')

            collection.add_document(split_document)

        self.reports = reports
        self.collection = collection

    def extract_sections(self, document):
        """Extract the Impression section from a Bioc Document."""
        split_document = section_split.split_document(document)
        passages = []
        for i, passage in enumerate(split_document.passages):
            if 'title' in passage.infons:
                if (passage.infons['title'] in self.sections_to_extract and
                    len(split_document.passages) > i+1):
                    next_passage = split_document.passages[i+1]
                    if 'title' not in next_passage.infons:
                        passages.append(next_passage)
        
        if passages or self.extract_strict:
            extracted_passages = bioc.BioCPassage()
            if passages:
                extracted_passages.offset = passages[0].offset
                extracted_passages.text = ' '.join(map(lambda x: x.text, passages))
            else:
                extracted_passages.offset = 0
                extracted_passages.text = ''
            split_document.passages = [extracted_passages]
            return split_document
        else:
            warnings.warn('Loader found document containing none of the ' + 
                          'provided sections to extract. Returning original ' + 
                          'document.')
            return document

    def clean(self, report):
        """Clean the report text."""
        # Remove numbers
        no_number_report = ''.join(char for char in report if not char.isnumeric()) 
        # Lower casing
        lower_report = no_number_report.lower()
        # Change `and/or` to `or`.
        corrected_report = re.sub('and/or',
                                  'or',
                                  lower_report)
        # Change any `XXX/YYY` to `XXX or YYY`.
        corrected_report = re.sub('(?<=[a-zA-Z])/(?=[a-zA-Z])',
                                  ' or ',
                                  corrected_report)
        # Clean double periods
        clean_report = corrected_report.replace("..", ".")
        # Insert space after commas and periods.
        clean_report = clean_report.translate(self.punctuation_spacer)
        # Convert any multi white spaces to single white spaces.
        clean_report = ' '.join(clean_report.split())
        # Remove empty sentences
        clean_report = re.sub(r'\.\s+\.', '.', clean_report)

        return clean_report
