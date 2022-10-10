"""
Date: Jan 20, 2022

To adapt the QRCD dataset to the CL-AraBERT model (or any other BERT-like model), the part of the dataset
to be used for fine-tuning/training should be preprocessed (or reformatted) such that a question-passage-answer triplet
is created for each answer span. I.e., answer spans of multi-answer questions are unpooled.
For SQuAD v1.1, this step is not needed prior to fine-tuning/training because it does not include multi-answer questions.

"""
import argparse
import json

def read_to_json_file(qrcd_file):

    with open(qrcd_file, 'r', encoding='utf-8') as json_file:
        qrcd_dict = json.load(json_file)
    json_file.close()

    return qrcd_dict

def write_to_json_file(squad_formatted_content, output_file):
    with open(output_file, 'w', encoding='utf-8') as fp:
        json.dump(squad_formatted_content, fp, separators=(',', ':'), ensure_ascii=False)
    fp.close()

def get_answer_id(passage_id, context, answer):
    """get answer id"""
    passage_id_start = int(passage_id.split(':')[1].split('-')[0]) 
    passage_id_end = int(passage_id.split(':')[1].split('-')[1].split('\t')[0])
    splitted_text = context.split('. ')
    splitted_answer = answer.split('. ')

    idxs = {}
    for idx in range(len(splitted_text)):
        if splitted_answer[0] in splitted_text[idx] and 'start_idx' not in idxs and idx in range(0,passage_id_end-passage_id_start+1):
            idxs['start_idx'] = str(idx + passage_id_start)
                
        if splitted_answer[-1] in splitted_text[idx] and 'end_idx' not in idxs and idx in range(0,passage_id_end-passage_id_start+1):
            idxs['end_idx'] = str(idx + passage_id_start)

    splitted_id_2 = passage_id.split(':')[0] + ':' + idxs['start_idx'] + '-' + idxs['end_idx']

    return splitted_id_2

def reproduce_new_train_data(qrcd_dict_train):

    quest_ids_dict = {}
    for paragraphs_idx in range(len(qrcd_dict_train['data'])):
        for paragraph_idx in range(len(qrcd_dict_train['data'][paragraphs_idx]['paragraphs'])):
            #Intialize a new list of questions
            list_quests = []
            context = qrcd_dict_train['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['context']
            for quest_idx in range(len(qrcd_dict_train['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'])):
                id = qrcd_dict_train['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'][quest_idx]['id']
                quest = qrcd_dict_train['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'][quest_idx]
                question = qrcd_dict_train['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'][quest_idx]['question']
                #split id by \t
                splitted_id = id.split('\t')
                
                #get answer occurence to be used in constructing the train question id format
                quest_id = splitted_id[1]
    
                if quest_id in quest_ids_dict:
                    quest_ids_dict[quest_id] += 1
                else:
                    quest_ids_dict[quest_id] = 1

                #get all answers
                answers = qrcd_dict_train['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'][quest_idx]['answers'].copy()
                
                k = 1
                for answer_idx in range(len(answers)):
                    new_quest = {}
                    answer = answers[answer_idx]
                    answer_text = answer['text']

                    #get answer_id
                    splitted_id_final = get_answer_id(id, context, answer_text)

                    #construct new id
                    new_qid = splitted_id[0] + '\t' + quest_id + '-' + str(quest_ids_dict[quest_id]) + '-' + str(k) + '\t' + splitted_id_final

                    new_quest['answers'] = [answer]
                    new_quest['id'] = new_qid
                    new_quest['question'] = question
                    k += 1
                    #add the question with the updated id
                    list_quests += [new_quest]
            #assign a new list of questions
            qrcd_dict_train['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'] = list_quests

    return qrcd_dict_train

def remove_no_span_answers(qrcd_dict):

    paragraph_indexes_to_remove = []

    for paragraphs_idx in range(len(qrcd_dict['data'])):
        for paragraph_idx in range(len(qrcd_dict['data'][paragraphs_idx]['paragraphs'])):
            list_quests = qrcd_dict['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'].copy()
            for quest_idx in range(len(qrcd_dict['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'])):
                list_anwers = qrcd_dict['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'][quest_idx]['answers'].copy()
                for answer_idx in range(len(qrcd_dict['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'][quest_idx]['answers'])):
                    answer_start =  qrcd_dict['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'][quest_idx]['answers'][answer_idx]['answer_start']
                    if answer_start == -1:
                        answer_to_remove = qrcd_dict['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'][quest_idx]['answers'][answer_idx].copy()
                        list_anwers.remove(answer_to_remove)
                        
                        if list_anwers == []:
                            quest_to_remove = qrcd_dict['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'][quest_idx].copy()
                            list_quests.remove(quest_to_remove)
            
                        if list_quests == []:
                            paragraph_indexes_to_remove += [paragraphs_idx]
                qrcd_dict['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'][quest_idx]['answers'] = list_anwers
        qrcd_dict['data'][paragraphs_idx]['paragraphs'][paragraph_idx]['qas'] = list_quests

    #remove all indexes in paragraph_indexes_to_remove from qrcd_dict file
    for index in sorted(paragraph_indexes_to_remove, reverse=True):
        del qrcd_dict['data'][index]

    return qrcd_dict

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''Generating qrcd in SQuAD's format...''')

    parser.add_argument('--input_file', required=True,
                        help='QRCD json file with answer spans pooled')

    parser.add_argument('--output_file', required=True,
                        help='Name of QRCD json file with answer spans unpooled')

    parser.add_argument("--no_span", type=str2bool, nargs='?',
                        const=True, default=False,
                        help="If False then we remove all nospan answers")

    args = parser.parse_args()

    qrcd_dict = read_to_json_file(args.input_file)
    qrcd_dict_train = reproduce_new_train_data(qrcd_dict)

    if args.no_span == False:
        qrcd_dict_train = remove_no_span_answers(qrcd_dict_train)

    write_to_json_file(qrcd_dict_train, args.output_file)
    
