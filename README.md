# Bad_Soup

### Example Scoring and Analysis for a Mock Machine Learning Annotation

This demonstrates scoring and analysis for a fabricated machine learning annotation scenario.

For demonstration purposes, I created a `dummy_data.jsonl` file containing mock data, including:
- A unique alphanumeric `dataItemId`. All alphanumeric values were randomly generated. 
- A `Final Label` representing the ground truth yes/no annotation.
- Mock rule ID instances: `BAD_SOUP`, `CABLE_SALAD`, and `OVERSTIMULATED`.

- This scenario involves a basic yes/no triple annotation and six fictitious annotators: Alice, Bob, Charlie, David, Eve, and Frank.
- One mock task includes a labeling error, resulting in only two annotators submitting responses.

The Python script `dummy.py` generates an Excel file named `dummy_output.xlsx` containing the following:
- A main sheet with a Pandas DataFrame organized into these columns: `dataItemId`, `rule_id`, `Final Label`, annotator columns (one for each annotator), and `agreement_count`. The annotator columns display each annotator's selections.

- Individual annotator sheets, each with these columns: `dataItemId`, `rule_id`, `Final Label`, `Decision`, and `Matches Final Label`. `Matches Final Label` indicates whether the annotator's `Decision` matches the `Final Label`.
- The individual annotator sheets exclude `dataItemId` instances that the respective annotator did not annotate, achieved by filtering: `annotator_df = annotator_df[annotator_df['Decision'] != 'N/A']`.

- Calculates the majority decision and agreement count and prints it to a new column: `df['majority_decision'], df['agreement_count'] = zip(*df.apply(lambda row: get_majority_agreement([row[annotator] for annotator in all_annotators]), axis=1))`

- Creates a new column `Matches Final Label`and uses a lambda function to checks if the annotator's decision matches the final label:  `annotator_df['Matches Final Label'] = annotator_df.apply(lambda row: int(row['Decision'] == row['Final Label']) if row['Decision'] != 'N/A' else 'N/A', axis=1)`
 
In the terminal, it prints the following: 
- Total Annotations
- Full Agreement (3/3) Count
- Full Agreement (3/3) Percentage
- Majority Agreement (2+/3) Count
- Majority Agreement (2+/3) Percentage
- Annotator Participation Counts

A warning for items that were not triple annotated.
