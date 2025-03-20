import json
import pandas as pd
from collections import Counter
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

def get_majority_agreement(annotations):
    valid_annotations = [a for a in annotations if a != 'N/A']
    if not valid_annotations:
        return "No valid annotations", 0
    counts = Counter(valid_annotations)
    majority = counts.most_common(1)[0]
    return majority[0], majority[1]

data_item_ids = []
rule_ids = []
final_labels = []
annotator_decisions = {}
item_annotators = {}

with open('dummy_data.jsonl', 'r') as file: #This is my input file
    for line in file:
        data = json.loads(line)
        
        data_item_id = data['dataItemId']
        data_item_ids.append(data_item_id)
        
        rule_id = next(iter(data['humanLabelData']['submissions'].values()))['metadata']['rule_id']
        rule_ids.append(rule_id)
        
        final_label = data['finalLabel']['rule_violation']
        final_labels.append(final_label)

        item_annotators[data_item_id] = []
        for annotator, submission in data['humanLabelData']['submissions'].items():
            if annotator not in annotator_decisions:
                annotator_decisions[annotator] = {}
            annotator_decisions[annotator][data_item_id] = submission['rule_violation']
            item_annotators[data_item_id].append(annotator)

df = pd.DataFrame({
    'dataItemId': data_item_ids,
    'rule_id': rule_ids,
    'Final Label': final_labels # This is our Ground Truth
})

all_annotators = sorted(set(annotator for annotators in item_annotators.values() for annotator in annotators))
for annotator in all_annotators:
    df[annotator] = df['dataItemId'].map(annotator_decisions[annotator]).fillna('N/A')

# Calculate majority agreement
df['majority_decision'], df['agreement_count'] = zip(*df.apply(lambda row: get_majority_agreement([row[annotator] for annotator in all_annotators]), axis=1))

wb = Workbook()

main_sheet = wb.active
main_sheet.title = "All Data"

for r in dataframe_to_rows(df, index=False, header=True):
    main_sheet.append(r)

for annotator in all_annotators:
    sheet = wb.create_sheet(title=annotator)
    
    annotator_df = df[['dataItemId', 'rule_id', 'Final Label', annotator, 'agreement_count']]
    annotator_df.columns = ['dataItemId', 'rule_id', 'Final Label', 'Decision', 'Agreement Count']
    
    annotator_df['Matches Final Label'] = annotator_df.apply(
        lambda row: int(row['Decision'] == row['Final Label']) if row['Decision'] != 'N/A' else 'N/A', 
        axis=1
    )
    
    annotator_df = annotator_df[annotator_df['Decision'] != 'N/A']
    
    for r in dataframe_to_rows(annotator_df, index=False, header=True):
        sheet.append(r)

output_file_name = 'dummy_output.xlsx' #Output file
wb.save(output_file_name)

print(f"Excel file '{output_file_name}' has been created successfully with individual sheets for each annotator.")

#Will only show in terminal
total_annotations = len(df)
full_agreement_count = sum(df['agreement_count'] == 3)
majority_agreement_count = sum(df['agreement_count'] >= 2)
full_agreement_percentage = (full_agreement_count / total_annotations) * 100
majority_agreement_percentage = (majority_agreement_count / total_annotations) * 100

print(f"\nTotal Annotations: {total_annotations}")
print(f"Full Agreement (3/3) Count: {full_agreement_count}")
print(f"Full Agreement (3/3) Percentage: {full_agreement_percentage:.2f}%")
print(f"Majority Agreement (2+/3) Count: {majority_agreement_count}")
print(f"Majority Agreement (2+/3) Percentage: {majority_agreement_percentage:.2f}%")

print("\nAnnotator Participation Counts:")
annotator_counts = Counter([annotator for annotators in item_annotators.values() for annotator in annotators])
for annotator, count in annotator_counts.items():
    print(f"{annotator}: {count}")

# Check for any items that are not triple annotated
items_with_different_annotators = {item_id: annotators for item_id, annotators in item_annotators.items() if len(annotators) != 3}
if items_with_different_annotators:
    print("\nWarning: The following items are not triple annotated:")
    for item_id, annotators in items_with_different_annotators.items():
        print(f"Data Item ID: {item_id}, Number of Annotators: {len(annotators)}, Annotators: {', '.join(annotators)}")
else:
    print("\nNo labeling errors.")