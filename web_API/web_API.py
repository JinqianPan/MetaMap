import pandas as pd
import datetime
import re
from tqdm import tqdm
from skr_web_api import Submission, METAMAP_INTERACTIVE_URL
import argparse
import sys
import os
from timeout_decorator import timeout
# Set every print as print(flush=True)
import functools
print = functools.partial(print, flush=True)
# ignore warnings
import warnings
warnings.filterwarnings('ignore')

# ------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--save_num', type=int, default=500)
parser.add_argument('--num_machine', type=int, default=1)
parser.add_argument('--total_machine', type=int, default=1)
parser.add_argument('--begin_num', type=int, default=-1)
parser.add_argument('--finish_num', type=int, default=-1)
parser.add_argument('--chunks', type=int, default=0)
args = parser.parse_args()
print(args, '\n\n')

# ------------------------------------------------------------
@timeout(400)
def get_info(serviceurl, email, apikey, inputtext, loop_times=1):
    """
    Get the information from Metamap API
    :param:
        serviceurl, email, apikey: API requirement
        inputtext: str/list(length no more than 5), input text
    """
    for i in range(loop_times):
        inst = Submission(email, apikey)
        if serviceurl:
            inst.set_serviceurl(serviceurl)
        inst.init_mm_interactive(inputtext, args='-N')
        response = inst.submit()
        lines = response.content.decode().strip().split('\n')[1:]
        if len(lines) >= 1:
            return lines
            break
        elif (i == loop_times-1) & (len(lines) == 0):
            # https://lhncbc.nlm.nih.gov/ii/tools/MetaMap.html
            print('     Failed get information from NIH.')
            return lines

def extract_info(lines):
    """
    Extract information from 'lines'
    :return: dataframe
        columns: concept, classify_abbreviation, trigger_conditions, extracted_text
    """
    def extract_quoted_text(s):
        # Extract text in double quotation mark
        return re.findall(r'"(.*?)"', s)

    data = []
    for line in lines:
        parts = line.split('|')
        if parts[1] == 'MMI':
            concept = parts[3]
            classify_abbreviation = parts[5].split('[')[1].split(']')[0]
            trigger_conditions = parts[6].split('[')[1].split(']')[0]
            data.append([concept, classify_abbreviation, trigger_conditions])

    df = pd.DataFrame(data, columns=['concept', 'classify_abbreviation', 'trigger_conditions'])

    df['extracted_text'] = df['trigger_conditions'].apply(extract_quoted_text)
    df['extracted_text'] = df['extracted_text'].apply(lambda x: list(set([item.lower() for item in x])))
    return df

# ------------------------------------------------------------
if __name__ == '__main__':
    serviceurl = METAMAP_INTERACTIVE_URL
    email = ''
    apikey = ''
    semanticTypes_path = '../support_data/SemanticTypes_2018AB.txt'
    working = 5
    data_load_folder = ''
    save_folder = ''
    saving_path = save_folder + 'finish_data/'
    checkpoint_saving_path = save_folder + f'check_point/check_point_imp_{args.num_machine}/'
    saving_file_name = f'label_data_impression_{args.num_machine}.csv'

    try:
        if not os.path.exists(saving_path):
            os.makedirs(saving_path)
        print('Create saving_path')
    except Exception as e:
        print('failed to create saving_path\n', e)

    try:
        if not os.path.exists(checkpoint_saving_path):
            os.makedirs(checkpoint_saving_path)
        print('Create checkpoint_saving_path')
    except Exception as e:
        print('failed to create checkpoint_saving_path\n', e)

    print(saving_file_name)

# ------------------------------------------------------------
# Loading data
    time1 = datetime.datetime.now()
    notes_text = []
    for i in range(1, 5):
        notes = pd.read_csv(data_load_folder + f'/raw_data/order_narratives_{i}.tsv', sep='\t')
        notes.dropna(subset=['note_text'], inplace=True)
        notes = notes[notes['note_text'] != "Ordered by an unspecified provider."]
        notes = notes.reset_index(drop=True)
        notes_text += list(notes['note_text'])
    time2 = datetime.datetime.now()
    print('Read note from original data:', len(notes_text), '(time:', (time2-time1).seconds, ')')
    print('#####################')

# ------------------------------------------------------------
# Get running begin and finish thresholds
    if (args.begin_num == -1) & (args.finish_num == -1):
        intermediate = len(notes_text) // args.total_machine + 1
        begin_num = (args.num_machine - 1) * intermediate
        finish_num = args.num_machine * intermediate
    else:
        begin_num = args.begin_num
        finish_num = args.finish_num

    if finish_num > len(notes_text):
        finish_num = len(notes_text)
    
    print('begin_num:', begin_num)
    print('finish_num:', finish_num)

    if args.chunks == 1:
        finish_num = finish_num + args.total_machine
        chunks = [notes_text[i:i+working] for i in range(begin_num, finish_num, working)]

    df = pd.DataFrame()
    error_line = []

    print('Connect to API to get the infomation...')
    threshold = 0

    if args.chunks == 1:
        begin_num_tmp = 0
        finish_num_tmp = len(chunks)
    elif args.chunks == 0:
        begin_num_tmp = begin_num
        finish_num_tmp = finish_num

# ------------------------------------------------------------
# Running
    for i in range(begin_num_tmp, finish_num_tmp):
        try:
            time3 = datetime.datetime.now()
            # print(time3)
            lines = []
            try:
                if args.chunks == 1:
                    lines = get_info(serviceurl, email, apikey, chunks[i])
                elif args.chunks == 0:
                    lines = get_info(serviceurl, email, apikey, notes_text[i])
            except Exception as e:
                print('Timeout for the loop', i, '.', e)
            time4 = datetime.datetime.now()
            # print(time4)
            print(lines[0])
            if len(lines) != 0:
                new_df = extract_info(lines)
                print(i, '/', finish_num_tmp-1, ':', 
                      'Line:', new_df.shape[0], 
                      ', loop time:', (time4-time3).seconds, 
                      ', total time:', (time4-time1).seconds)
                df = pd.concat([df, new_df])
            else:
                print(i, '/', finish_num_tmp-1, ': Do not get information.')
            threshold += 1
            if threshold == args.save_num:
                df.to_csv(checkpoint_saving_path+f'checkpoint_imp_{args.num_machine}_{i}.csv', index=False)
                sys.stdout.flush()
                threshold = 0
        except Exception as e:
            error_line.append(i)
            print('Error:', i, '.', e)

    if len(error_line) > 0:
        print(error_line)
    else:
        print('Do not have error.')

# ------------------------------------------------------------
# Save data
    print('#####################')
    print('Finish connect to API')
    df['extracted_text'] = df['extracted_text'].apply(lambda x: ', '.join(x))
    df = df.drop_duplicates()
    df.to_csv(saving_path+saving_file_name, index=False)
    sys.stdout.flush()
    print('Done')