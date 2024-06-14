from pymetamap import MetaMap
import pandas as pd
from tqdm import tqdm
import argparse
import re
import os
import sys
# Set every print as print(flush=True)
import functools
print = functools.partial(print, flush=True)
# ignore warnings
import warnings
warnings.filterwarnings('ignore')

# ------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--save_num', type=int, default=100)
parser.add_argument('--num_machine', type=int, default=1)
parser.add_argument('--total_machine', type=int, default=1)
parser.add_argument('--begin_num', type=int, default=-1)
parser.add_argument('--finish_num', type=int, default=-1)
parser.add_argument('--data_name', type=str, default='order_narratives_1.tsv')
args = parser.parse_args()
print('\n\n', args, '\n\n')

# ------------------------------------------------------------
METAMAP_PATH = ''
DATA_PATH = ''
SAVE_FOLDER = ''

data_name = args.data_name
doc_type = data_name.split('.')[0].split('_')[1]
num = data_name.split('.')[0].split('_')[2]

SAVING_PATH = SAVE_FOLDER + f'finish_data/{doc_type}_{num}/'
CHECKPOINT_SAVING_PATH = SAVE_FOLDER + f'check_point/check_point_{doc_type}/{doc_type}_{num}/'
saving_file_name = f'label_data_{doc_type}_{num}_{args.num_machine}.csv'
checkpoint_name = f'checkpoint_{doc_type}_{num}_{args.num_machine}.csv'

print('Saving Path:')
print('METAMAP_PATH:', METAMAP_PATH)
print('DATA_PATH:', DATA_PATH)
print('SAVE_FOLDER:', SAVE_FOLDER)
print('data_name:', data_name)
print('doc_type:', doc_type)
print('num:', num)
print('CHECKPOINT_SAVING_PATH:', CHECKPOINT_SAVING_PATH)
print('saving_file_name:', saving_file_name)
print('checkpoint_name:', checkpoint_name, '\n\n')

# ------------------------------------------------------------
try:
    if not os.path.exists(SAVING_PATH):
        os.makedirs(SAVING_PATH)
    print('Create saving_path')
except Exception as e:
    print('failed to create saving_path\n', e)

try:
    if not os.path.exists(CHECKPOINT_SAVING_PATH):
        os.makedirs(CHECKPOINT_SAVING_PATH)
    print('Create checkpoint_saving_path')
except Exception as e:
    print('failed to create checkpoint_saving_path\n', e)

print(saving_file_name)

# ------------------------------------------------------------
def load_data():
    notes_text = []
    notes = pd.read_csv(DATA_PATH + data_name, sep='\t')
    notes.dropna(subset=['note_text'], inplace=True)
    notes = notes[notes['note_text'] != "Ordered by an unspecified provider."]
    notes = notes.reset_index(drop=True)
    notes_text = list(notes['note_text'])
    return notes_text

def remove_non_ascii_from_list(strings):
    # Remove non-ASCII characters from each string in the list
    return [''.join(char for char in text if ord(char) < 128) for text in strings]

# ------------------------------------------------------------
def extract_info(concept):
    def extract_quoted_text(s):
        # Extract text in double quotation mark
        return re.findall(r'"(.*?)"', s)
    def remove_brackets(lst):
        return ', '.join(lst)

    data = []
    if hasattr(concept, 'mm'):
        concept_name = concept.preferred_name
        classify_abbreviation = concept.semtypes.split('[')[1].split(']')[0]
        trigger_conditions = concept.trigger.split('[')[1].split(']')[0]
        data.append([concept_name, classify_abbreviation, trigger_conditions])

    df = pd.DataFrame(data, columns=['concept', 'classify_abbreviation', 'trigger_conditions'])

    df['extracted_text'] = df['trigger_conditions'].apply(extract_quoted_text)
    df['extracted_text'] = df['extracted_text'].apply(lambda x: list(set([item.lower() for item in x])))
    df['extracted_text'] = df['extracted_text'].apply(remove_brackets)
    
    return df

# ------------------------------------------------------------
def running_part(sents, df, save_num, max_length=5000):
    def split_long_strings(string_list, max_length=5000):
        new_list = []
        for item in string_list:
            if len(item) > max_length:
                words = item.split()
                current_string = ""
                for word in words:
                    if len(current_string) + len(word) + 1 > max_length:
                        new_list.append(current_string)
                        current_string = word
                    else:
                        if current_string:
                            current_string += " " + word
                        else:
                            current_string = word
                if current_string:
                    new_list.append(current_string)
            else:
                new_list.append(item)
        return new_list

    def pair_elements_non_repeating(lst):
        return [lst[i:i+2] for i in range(0, len(lst), 2)]
    
    sents = split_long_strings(sents, max_length=max_length)
    sents = pair_elements_non_repeating(sents)
    print('This part data len:', len(sents))

    threshold = 0
    error_line = []

    for i in tqdm(sents):
        try:
            concepts, error = mm.extract_concepts(i)
            for concept in concepts:
                new_df = extract_info(concept)
                df = pd.concat([df, new_df])

            if threshold % save_num == save_num - 1:
                df = df.drop_duplicates()
                df.to_csv(CHECKPOINT_SAVING_PATH + checkpoint_name, index=False)
                sys.stdout.flush()
                
        except Exception as e:
            error_line.append(i)
            print('Error:', i, '.', e)

        threshold += 1
    
    print(df.shape)
    df.to_csv(SAVING_PATH + saving_file_name, index=False)
    sys.stdout.flush()
    print('Done')

    if len(error_line) > 0:
        print(error_line)
    else:
        print('Do not have error.')
    return error_line

# ------------------------------------------------------------
if __name__ == '__main__':

# ------------------------------------------------------------
    mm = MetaMap.get_instance(METAMAP_PATH)
    df = pd.DataFrame()

    sents = load_data()
    print('Original data len:', len(sents))
    sents = remove_non_ascii_from_list(sents)

# ------------------------------------------------------------
# Get running begin and finish thresholds
    if (args.begin_num == -1) & (args.finish_num == -1):
        intermediate = len(sents) // args.total_machine + 1
        begin_num = (args.num_machine - 1) * intermediate
        finish_num = args.num_machine * intermediate
    else:
        begin_num = args.begin_num
        finish_num = args.finish_num

    if finish_num > len(sents):
        finish_num = len(sents)
    
    print('begin_num:', begin_num)
    print('finish_num:', finish_num, '\n')

# ------------------------------------------------------------

    max_len_list = [5000, 2000, 500, 100, 10, 1]

    for i in max_len_list:
        print('max_length:', i)
        if i == 5000:
            input_set = sents[begin_num: finish_num]
        else:
            if len(error_line) > 0:
                input_set = [item for sublist in error_line for item in sublist]
            else:
                print(f'Break before {i}.')
                break
        error_line = running_part(input_set, df, args.save_num, max_length=i)