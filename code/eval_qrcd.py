""" Official evaluation script for v1.1 of the QRCD dataset. """

from __future__ import print_function
from farasa.segmenter import FarasaSegmenter #added on June 1, 2021

import collections
from collections import Counter
import string
import re
import argparse
import json
import sys
import tensorflow as tf

#global variables
stopWords={'من','الى','إلى','عن','على','في','حتى'}

def _is_punctuation(c):
    exclude = set(string.punctuation)
    exclude.add('،')
    exclude.add('؛')
    exclude.add('؟')
    if c in exclude:
        return True
    return False

def normalize_answer_wAr(s):
    """remove punctuation, some stopwords and extra whitespace."""
    def remove_stopWords(text):
        terms = []
        # must take care of the prefixes before removing stopwords
        # stopWords = {'من', 'الى', 'إلى', 'عن', 'على', 'في', 'حتى'} ## defined globally
        for term in text.split():
            if term not in stopWords:
                terms.append(term)
        return " ".join(terms)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc_wAr(text):
        exclude = set(string.punctuation)
        exclude.add('،')
        exclude.add('؛')
        exclude.add('؟')
        return ''.join(ch for ch in text if ch not in exclude)

    return white_space_fix(remove_stopWords(remove_punc_wAr(s)))

def normalize_answers_wAr(ss):
    """remove punctuation, some stopwords and extra whitespace."""
    cleaned_ss=[]
    for s in ss:
        s = normalize_answer_wAr(s)
        cleaned_ss.append(s)
    return cleaned_ss

def exact_match_score(matching_at1):
    if matching_at1 == 1:
        return 1
    else:
        return 0

def f1_score(prediction_tokensIds, ground_truth_tokensIds):
    common = Counter(prediction_tokensIds) & Counter(ground_truth_tokensIds)
    num_same = sum(common.values())
    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(prediction_tokensIds)
    recall = 1.0 * num_same / len(ground_truth_tokensIds)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1

def pAP_score(mScores, ranks, gold_spans_set):
    ## Computing partial average precision
    score = 0.0
    partialHits = 0.0
    for mScore, rank in zip(mScores, ranks):
        if mScore != 0:
            partialHits = partialHits + mScore
            score += partialHits / rank
    return score / len(gold_spans_set) # pAP

def construct_char_to_word_offset(paragraph_text):
    doc_tokens = paragraph_text.strip().split()
    char_to_word_offset = []
    for i, token in enumerate(doc_tokens):
        for c in token:
            char_to_word_offset.append(i)
        char_to_word_offset.append(i) # for the whitespace
    return char_to_word_offset

def remove_prefixes_in_text(text):
    text_tokens = farasa_segmenter.segment(text).split()
    tokens = []
    for token in text_tokens:
        token = re.sub(r'^و[+]', '', token)  # only begining of words
        token = re.sub(r'^ف[+]', '', token)
        token = re.sub(r'^ب[+]', '', token)
        token = re.sub(r'^ك[+]', '', token)
        token = re.sub(r'^ل[+]', '', token)
        token = re.sub(r'^لل[+]', '', token)
        token = re.sub(r'^ال[+]', '', token)

        # defragment by removing pluses
        token = re.sub(r'[+]', '', token)
        tokens.append(token)
    return " ".join(tokens)

def remove_prefixes(answers):
    farasa_answers = []
    for answer in answers:
        answerToAppend = remove_prefixes_in_text(answer)
        farasa_answers.append(answerToAppend)
    return farasa_answers

# should get rid of all adjust methods and normalize both pred and gold on the fly, if possible (verify)
def adjust_start(org_text, org_word_start):
    '''
    :param org_text: must receive org_text after removing prefixes
    :param org_start:
    :return:
    '''
    start = org_word_start
    text_terms = org_text.split()
    lastIsPunct = False
    lastIsStopWord = False
    for i, term in enumerate(text_terms):
        if i > org_word_start:
            if lastIsPunct or lastIsStopWord:
                start = start + 1
            break
        #check if stopword
        if term in stopWords:
            start = start - 1
            lastIsStopWord = True
        else:
            lastIsStopWord = False

        if _is_punctuation(term):
            start = start - 1
            lastIsPunct = True
        else:
            lastIsPunct = False
    return start

def adjust_end(org_text, org_word_end):
    '''
    :param org_text: must receive org_text after removing prefixes to match punctuation
    :param org_end:
    :return:
    '''
    end = org_word_end
    text_terms = org_text.split()
    for i, term in enumerate(text_terms):
        if i > org_word_end:
            break
        if term in stopWords or _is_punctuation(term):
            end = end - 1
    return end

def construct_text_from_range(span_range, parag_text):
    doc_tokens = parag_text.strip().split()
    span_tokenIds = list(span_range)
    span_tokens =[]
    for indx in span_tokenIds:
        span_tokens.append(doc_tokens[indx])
    return " ".join(span_tokens)

def compute_matchingScores_withSplitting(gold_spans_ranges, pred_spans_ranges, cutoff_rank, context, cntxt_qid):

    splitMatching_f1Scores = []
    matching_f1Scores_at1 = []
    split_PredSpans = []

    #needed to construct the answer spans from corresponding ranges
    paragraph_text = context
    paragraph_text = remove_prefixes_in_text(paragraph_text)
    paragraph_text = normalize_answer_wAr(paragraph_text)

    pre_split_PredSpans = collections.defaultdict(list)

    pred_spans, probs, pred_word_start_postions, pred_word_end_positions = zip(*pred_spans_ranges)
    gold_spans_list, gold_word_start_postions, gold_word_end_positions = zip(*gold_spans_ranges)

    # 0. Compute matching score @rank1 for EM and F1@1
    pred_span = pred_spans[0]
    maxf1_at1 = 0.0
    maxMatched_gold_span = None
    pred_span_tokenIds = list(range(pred_word_start_postions[0], pred_word_end_positions[0] + 1))

    for i, gold_span in enumerate(gold_spans_list):
            gold_span_tokenIds = set(range(gold_word_start_postions[i], gold_word_end_positions[i] + 1))

            f1_at1 = f1_score(pred_span_tokenIds, gold_span_tokenIds)
            if f1_at1 > maxf1_at1:
                maxf1_at1 = f1_at1
                maxMatched_gold_span = gold_span
    matching_f1Scores_at1.append((pred_span, maxMatched_gold_span, maxf1_at1))
    #-------------------------------------------------------
    # 1. for each pred_span find all overlaps with gold_spans
    overallRank = 0
    for i, pred_span in enumerate(pred_spans):
        rank = i + 1
        if rank > int(cutoff_rank):
            break
        overallRank += 1

        if pred_span==None:
            pre_split_PredSpans[pred_span].append((None, None , range(0), range(0), overallRank))
            continue

        pred_range = range(pred_word_start_postions[i], pred_word_end_positions[i] + 1)
        gold_span_matches=0
        for j, gold_span in enumerate(gold_spans_list):
            gold_range = range(gold_word_start_postions[j], gold_word_end_positions[j] + 1)

            # Compute the range overlap between the prediction and each gold answer
            #overlap = pred_range_set & gold_range_set # set intersection using &
            #overlap = pred_range_set.intersection(gold_range_set) # set intersection using method intersection
            pred_gold_overlap = range(max(pred_range[0], gold_range[0]), min(pred_range[-1], gold_range[-1]) + 1)
            if len(pred_gold_overlap)!=0:
                pre_split_PredSpans[pred_span].append((pred_range, gold_span, gold_range, pred_gold_overlap, overallRank))
                gold_span_matches+=1
        if gold_span_matches==0:
            # Avoid adding a None match if the pred_span happens to match a span in the gold-answer
            # but it is not in the correct position in the context
            if pred_span not in  pre_split_PredSpans:
                pre_split_PredSpans[pred_span].append((pred_range, None, range(0), range(0), overallRank))

    #2. for each pred_span that match multiple gold_spans make breaks and make sure to store the rank
    for pred_span1, ranges1 in pre_split_PredSpans.items():
        pred_ranges1, gold_spans1, gold_ranges1, pred_gold_overlaps1, ranks1 = zip(*ranges1)

        # 2.1. pred_span matches only one gold_span => no splitting needed
        if len(gold_spans1) == 1 and gold_spans1[0] is not None:
            split_PredSpans.append(
                (pred_span1, pred_ranges1[0], gold_spans1[0], gold_ranges1[0], pred_gold_overlaps1[0], float(ranks1[0])))
            continue

        # 2.2 split pred_span across matched gold_spans (horizontally)
        # overlap1 is the pred_gold_overlap with current encountered gold_span
        # overlap2 is the pred_gold_overlap with next encountered gold_span

        # rank_offset is used to give temporary ranks to predictions to be split
        rank_original = float(ranks1[0])
        rank_offset = 1.0/(len(gold_spans1)+1)
        pred_ranges1_crnt = list(pred_ranges1)

        pred_span_1st_range = range(0)
        pred_span_2nd_range = range(0)
        pred_span_1st_text = None
        pred_span_2nd_text = None
        for k, overlap1 in enumerate(pred_gold_overlaps1):
            #case when pred_span has no match with any gold-span
            if gold_spans1[k] is None:
                split_PredSpans.append(
                    (pred_span1, pred_ranges1[k], None, range(0), range(0), float(ranks1[k])))
                continue
            l = k+1
            if l >= len(pred_gold_overlaps1):
                continue

            # case when two predicted spans become the same after processing e.g. 27:20-28\t232 سبا
            # Each predicted answer has its own rank
            if gold_spans1[k] == gold_spans1[l]: # another case for not splitting
                split_PredSpans.append(
                    (pred_span1, pred_ranges1[k], gold_spans1[k], gold_ranges1[k], pred_gold_overlaps1[k],
                     float(ranks1[k])))
                split_PredSpans.append(
                    (pred_span1, pred_ranges1[l], gold_spans1[l], gold_ranges1[l], pred_gold_overlaps1[l],
                     float(ranks1[l])))
                continue

            # When pred_span1 matches more than 2 gold_spans, slide pred_ranges1_crnt
            if pred_span_2nd_text != None:
                split_PredSpans.pop()
                pred_ranges1_crnt[l-1] = pred_span_2nd_range # l-1 is k
                rank_offset = rank_offset + 0.05

            overlap2 = pred_gold_overlaps1[l]
            # print("overlap2 = %s" % overlap2 )
            #
            # for gld_span, gld_range in zip(gold_spans1, gold_ranges1):
            #     print ("gld_range=%s, gld_span=%s " %(gld_range, gld_span))

            # Another case for no splitting:
            # when the same predicted answer partially matches two overlapping gold answers
            # print(len(range(max(overlap1[0], overlap2[0]), min(overlap1[-1], overlap2[-1]) + 1)))
            # assert len(range(max(overlap1[0], overlap2[0]), min(overlap1[-1], overlap2[-1]) + 1))==0
            if len(range(max(overlap1[0], overlap2[0]), min(overlap1[-1], overlap2[-1]) + 1)) != 0:
                # print("Warning: For cntxt_qid=%s, predicted span@%d: %s \nOverlap between gold answers exists,"
                #       " the predicted answer will not be split. Match with better matched gold answer" % (cntxt_qid, ranks1[k], pred_span1))
                # gold_spans_set = set(gold_spans1)
                # print("%s\tpredicted span@%d\t%s\t%d\t%d\t%s\t%s" % (cntxt_qid, ranks1[k], pred_span1, len(gold_spans_set), len(gold_spans1), gold_spans1[k], gold_ranges1[k]))

                # Decide which is a better match using F1 over range overlap and append the better one on the fly
                prdTokens = list(pred_ranges1[k])
                gldTokens1st = list(gold_ranges1[k])
                gldTokens2nd = list(gold_ranges1[l])
                f1_w1st_gold = f1_score(prdTokens, gldTokens1st)
                f1_w2nd_gold = f1_score(prdTokens, gldTokens2nd)
                if f1_w1st_gold >= f1_w2nd_gold:
                    split_PredSpans.append(
                    (pred_span1, pred_ranges1[k], gold_spans1[k], gold_ranges1[k], pred_gold_overlaps1[k],
                     float(ranks1[k])))
                else:
                    split_PredSpans.append(
                    (pred_span1, pred_ranges1[l], gold_spans1[l], gold_ranges1[l], pred_gold_overlaps1[l],
                     float(ranks1[l])))
                continue

            # split pred_span into two parts in every loop-round at a time
            # compute range in between pred_gold_overlaps1 (overlap1 and overlap2)
            range_in_between = range(overlap1[-1]+1, overlap2[0])
            if len(range_in_between)==0:
                pred_span_1st_range = range(pred_ranges1_crnt[k][0], overlap1[-1] + 1)
                pred_span_2nd_range = range(overlap2[0], pred_ranges1_crnt[l][-1]+1)
            else:
                tokens_in_between = list(range_in_between)
                #tokens_in_between = sorted(tokens_in_between) # verify if needed
                m = (len(tokens_in_between) // 2)   # integer division

                pred_span_1st_range = range(pred_ranges1_crnt[k][0], tokens_in_between[m])
                pred_span_2nd_range = range(tokens_in_between[m], pred_ranges1_crnt[l][-1] + 1)

            # print("paragraph: %s" %paragraph_text)
            pred_span_1st_text = construct_text_from_range(pred_span_1st_range, paragraph_text)
            pred_span_2nd_text = construct_text_from_range(pred_span_2nd_range, paragraph_text)

            # New temporary ranks to be used in re-ranking pred_spans
            rank_1st = rank_original + rank_offset
            rank_2nd = rank_1st + rank_offset

            split_PredSpans.append(
                        (pred_span_1st_text, pred_span_1st_range, gold_spans1[k], gold_ranges1[k], pred_gold_overlaps1[k], rank_1st))
            split_PredSpans.append(
                        (pred_span_2nd_text,pred_span_2nd_range, gold_spans1[l], gold_ranges1[l], pred_gold_overlaps1[l], rank_2nd))

    #3.1 Sort by rank (verify if needed because the ranks are assigned in order)
    sortByKeyOrder = 5
    #split_PredSpans = mySort(split_PredSpans, sortByKeyOrder)
    split_PredSpans.sort(key=lambda i: i[sortByKeyOrder]) #verify if I should re-assign the list

    #3.2 rerank converting float ranks into consecutive integer ranks
    #To convert the above code, no need to introduce another list except the reranked one
    split_PredSpans_reranked = []
    for rnk, split_PredSpan  in enumerate(split_PredSpans):
        v1, v2, v3, v4, v5, rankflt = split_PredSpan
        newRank = rnk + 1
        split_PredSpans_reranked.append((v1, v2, v3, v4, v5, newRank))

    #3.3 For each split pred_span find maxMatched gold span (as before) but using F1 over range overlap
    #    Since the stored gold_span information have not been used (so far), verify if they need to be removed from the tuple
    split_pred_spans1, split_pred_ranges1, _, _, _, splitRanks1 = zip(*split_PredSpans_reranked)

    # Next: Max match each split pred_answer with a gold-answer
    #       and remove all occurrences of that matched gold answer (must verify)
    unmatched_gold_word_start_postions = list(gold_word_start_postions).copy()
    unmatched_gold_word_end_positions = list(gold_word_end_positions).copy()
    unmatched_gold_spans = list(gold_spans_list).copy()
    for indx, split_pred_span1 in enumerate(split_pred_spans1):
        rank = splitRanks1[indx]
        maxf1 = 0.0
        maxMatched_gold_span = None

        #verify if needed
        if split_pred_span1==None:
            splitMatching_f1Scores.append(
                (None, None, 0.0, rank))
            continue

        split_pred_span1_tokenIds = list(split_pred_ranges1[indx])
        for indy, gold_span in enumerate(unmatched_gold_spans):
            # gold_ranges1 can be used instead of the start and end positions
            gold_span_tokenIds = set(range(unmatched_gold_word_start_postions[indy], unmatched_gold_word_end_positions[indy]+1))
            f1 = f1_score(split_pred_span1_tokenIds, gold_span_tokenIds)
            if f1 > maxf1:
                maxf1 = f1
                maxMatched_gold_span = gold_span

        if maxf1!=0:
            # Remove all occurences of a gold_span, if applicable
            for gold in gold_spans_list:
                if gold == maxMatched_gold_span and gold in unmatched_gold_spans:
                    indg = unmatched_gold_spans.index(maxMatched_gold_span)
                    unmatched_gold_spans.pop(indg)
                    unmatched_gold_word_start_postions.pop(indg)
                    unmatched_gold_word_end_positions.pop(indg)

        splitMatching_f1Scores.append((split_pred_span1, maxMatched_gold_span, maxf1, rank))
    return matching_f1Scores_at1, splitMatching_f1Scores

def evaluate(dataset, nbest_predictions, cutoff_rank, eval_scores_file, qtypes_file):
    f1_at1_all_s = 0.0
    em_all_s = 0.0
    pAP_all_s = 0.0
    s_questions = 0  # single_answer questions
    s_qa_pairs = 0

    pAP_all_m = 0.0  # partial Average precision
    m_questions = 0  # multi_answer questions
    m_qa_pairs = 0
    all_qa_pairs = 0

    for article in dataset:
        for paragraph in article['paragraphs']:
            org_paragraph_text = paragraph['context']
            char_to_word_offset = construct_char_to_word_offset(org_paragraph_text)

            for qa in paragraph['qas']:
                gold_spans_ranges = []
                cntxt_qid = qa['id']
                context_4cntxt_qid = org_paragraph_text
                org_paragraph_text = remove_prefixes_in_text(org_paragraph_text)

                if qa['id'] not in nbest_predictions:
                    message = 'Unanswered question ' + cntxt_qid + \
                              ' will receive score 0.'
                    print(message, file=sys.stderr)
                    continue

                ground_truths = list(map(lambda x: x['text'], qa['answers']))
                all_qa_pairs = all_qa_pairs + len(ground_truths)
                gold_span_offsets = list(map(lambda x: x['answer_start'], qa['answers']))
                for gold_span, gold_span_offset in zip(ground_truths, gold_span_offsets):
                    org_word_start_position = char_to_word_offset[gold_span_offset] # word-start-position in pargraph/context
                    org_word_end_position = char_to_word_offset[gold_span_offset + len(gold_span) - 1] # word-end-position

                    # adjust the start/end token positions to cater for stopwords removal
                    adj_word_start_position = adjust_start(org_paragraph_text, org_word_start_position)
                    adj_word_end_position = adjust_end(org_paragraph_text, org_word_end_position)
                    gold_span = remove_prefixes_in_text(gold_span)
                    gold_span = normalize_answer_wAr(gold_span)
                    gold_spans_ranges.append((gold_span, adj_word_start_position, adj_word_end_position))
                sortByKeyOrder = 1  # sort tuple by start_position of gold answer
                gold_spans_ranges.sort(key=lambda i: i[sortByKeyOrder])

                nbest_predictions_4cntxt_qid = nbest_predictions[qa['id']]
                pred_spans_ranges = []
                for nbest_prediction in nbest_predictions_4cntxt_qid:
                    span = nbest_prediction['text']
                    span = remove_prefixes_in_text(span)
                    span = normalize_answer_wAr(span)

                    #get the start/end token positions predicted in nbest_predictions
                    org_word_start_index = nbest_prediction['orig_start_index']
                    org_word_end_index = nbest_prediction['orig_end_index']

                    # adjust start/end token positions to cater for stopwords removal
                    adj_word_start_position = adjust_start(org_paragraph_text, org_word_start_index)
                    adj_word_end_position = adjust_end(org_paragraph_text, org_word_end_index)
                    if len(span.split()) == 0 or adj_word_start_position > adj_word_end_position:
                        # Although noisy showing all paragraph, keep it
                        # print("\nWarning for %s: could not find original predicted answer %s in \nparagraph after removing prefixes and stopwords %s" % (
                        #     cntxt_qid, org_span, paragraph_text))
                        # less noisy
                        # print("\nWarning for %s: could not find original predicted answer %s" % (
                        #     cntxt_qid, org_span))
                        continue

                    # Use the actual returned start/end token positions of predicted answer from nbest_predictions file after adjusting
                    word_start_position = adj_word_start_position
                    word_end_position = adj_word_end_position

                    prob = nbest_prediction['probability']
                    pred_spans_ranges.append(
                    (span, prob, word_start_position, word_end_position))

                # steps 0 through 3 are in compute_matchingScores_withSplitting
                matching_f1Scores_at1, splitMatching_f1Scores = compute_matchingScores_withSplitting(
                    gold_spans_ranges, pred_spans_ranges, cutoff_rank, context_4cntxt_qid, cntxt_qid)

                # 4. compute pAP@k, F1@1 and EM with matching using F1 over ranges (i.e., token positions) with splitting, if needed
                pred_spans, maxMatched_gold_spans, maxf1s, ranks = zip(*splitMatching_f1Scores)
                pred_span_at1, maxMatched_gold_span_at1, maxf1_at1 = zip(*matching_f1Scores_at1)
                gold_spans_list, gold_word_start_postions, gold_word_end_positions = zip(*gold_spans_ranges)
                gold_spans_set = set(gold_spans_list)  # this is a set

                maxf1_at1 = maxf1_at1[0]
                mScores = list(maxf1s)

                ### Evaluating single answer questions ###
                if len(gold_spans_set) == 1 or len(gold_spans_list) == 1:
                    qtype = 's'
                    s_questions += 1
                    s_qa_pairs = s_qa_pairs + len(gold_spans_list)

                    ## Compute f1@1
                    f1_at1 = maxf1_at1
                    f1_at1_all_s += f1_at1

                    # Compute EM Exact Match
                    em = exact_match_score(maxf1_at1)
                    em_all_s += em

                    ## Computing partial average precision for single-answer question
                    pAP = pAP_score(mScores, ranks, gold_spans_set)
                    pAP_all_s += pAP

                    qtypes_file.write("\t".join((cntxt_qid, qtype)) + "\n")
                    eval_scores_file.write("\t".join((cntxt_qid, "s", str(pAP), str(f1_at1), str(em))) + "\n")

                if len(gold_spans_set) > 1:
                    m_questions += 1
                    m_qa_pairs = m_qa_pairs + len(gold_spans_list)
                    qtype = 'm'

                    ## Computing partial average precision for multi_answer question
                    pAP = pAP_score(mScores, ranks, gold_spans_set)
                    pAP_all_m += pAP

                    qtypes_file.write("\t".join((cntxt_qid, qtype)) + "\n")
                    eval_scores_file.write("\t".join((cntxt_qid, "m", str(pAP))) + "\n")

    print('\ns_questions=%d, s_qa_pairs=%d' % (s_questions, s_qa_pairs))
    print('m_questions=%d, m_qa_pairs=%d' % (m_questions, m_qa_pairs))
    print("all_questions=%d, all_qa_pairs=%d" % (s_questions + m_questions, all_qa_pairs))

    if s_questions != 0:
         avg_f1At1 = 100.0 * f1_at1_all_s / s_questions
         avg_em = 100.0 * em_all_s / s_questions
         avg_pAP = 100.0 * pAP_all_s / s_questions

         print('\n==> Single-answer questions: F1@1: %.3f, EM=%0.3f, pAP@%s= %0.3f' % (
            avg_f1At1, avg_em, cutoff_rank, avg_pAP))

    if m_questions != 0:
         avg_pAP = 100.0 * pAP_all_m / m_questions
         print('==> Multi-answer questions: \t\t\t\t\t\t  pAP@%s: %0.3f' % (cutoff_rank, avg_pAP))

    overall_pAP = 100.0 * (pAP_all_s + pAP_all_m) / (
                        s_questions + m_questions)
    print('==> All questions: \t\t\t\t\t\t\t\t\t  pAP@%s= %0.3f ' % (cutoff_rank, overall_pAP))

if __name__ == '__main__':
    version = '1.1'
    parser = argparse.ArgumentParser(
        description='Evaluation for QRCD ' + version)
    parser.add_argument('--dataset_file', help='Dataset file')
    parser.add_argument('--nbest_prediction_file', help='nbest_Prediction file', required=True)
    parser.add_argument('--cutoff_rank', help='Cutoff rank at which to prune nbest_predictions, default=10',
                        required=False, default='10')
    args = parser.parse_args()
    farasa_segmenter = FarasaSegmenter(interactive=True)

    #with open(args.dataset_file) as dataset_file: # use if tenserflow is not imported
    with tf.io.gfile.GFile(args.dataset_file, "r") as dataset_file:
        dataset_json = json.load(dataset_file)
        dataset = dataset_json['data']

    #with open(args.nbest_prediction_file) as nbest_prediction_file: # use if tenserflow is not imported
    with tf.io.gfile.GFile(args.nbest_prediction_file, "r") as nbest_prediction_file:
        nbest_predictions = json.load(nbest_prediction_file)

    #for writing evaluation scores to a file
    path_to_eval_scores_file = args.nbest_prediction_file[:-22] + "trial_byRfctrd_eval_scores_at" + args.cutoff_rank +".txt"
    #eval_scores_file = open(path_to_eval_scores_file, 'w') # use if tenserflow is not imported
    eval_scores_file = tf.io.gfile.GFile(path_to_eval_scores_file, "w")

    path_to_qtypes_file = args.nbest_prediction_file[:-22] + "trial_byRfctrd_eval_qtypes_by_span_num.txt"
    #qtypes_file = open(path_to_qtypes_file, 'w') # use if tenserflow is not imported
    qtypes_file = tf.io.gfile.GFile(path_to_qtypes_file, "w")

    evaluate(dataset, nbest_predictions, args.cutoff_rank, eval_scores_file, qtypes_file )