# *QRCD* (Qur'anic Reading Comprehension Dataset)
*QRCD_v1.2* is released! It can be downloaded from the [Qur'an QA 2023 repo](https://gitlab.com/bigirqu/quran-qa-2023/-/tree/main) at [this link](https://gitlab.com/bigirqu/quran-qa-2023/-/tree/main/Task-B).

This repository contains information about [*QRCD_v1.1*](https://github.com/RanaMalhas/QRCD/tree/main/dataset), [CL-AraBERT](https://github.com/RanaMalhas/QRCD/blob/main/README.md#cl-arabert-pre-trained-language-model) (**CL**assical **AraBERT**) pre-trained model and [code](https://github.com/RanaMalhas/QRCD/tree/main/code) for evaluating results on *QRCD*.

*QRCD_v1.1* is composed of 1,093 tuples of question-passage pairs that are coupled with their extracted answers to constitute 1,337 question-passage-answer triplets. The distribution of the dataset into training and test sets is shown below. The dataset in this repo adopts the [SQuAD v1.1 format](https://github.com/facebookresearch/DrQA#format-b). 

A *QRCD_v1.1* version in JSONL (JSON lines) format is also available. It can be downloaded from the [Qur'an QA 2022 repo](https://gitlab.com/bigirqu/quranqa/-/tree/main/datasets). 

<!-- | **Dataset** | **%** | **# Question-Passage  Pairs** | **# Question-Passage-Answer  Triplets** |
|-------------|:-----:|:-----------------------------:|:---------------------------------------:|
| Training    |  65%  |              710              |                   861                   |
| Development |  10%  |              109              |                   128                   |
| Test        |  25%  |              274              |                   348                   |
| All         |  100% |              1,093            |                  1,337                  |
 -->

| QRCD_v1.1 Dataset          |**# Question-Passage Pairs**|**# QPA\* triplets for All Questions**|**# QPA triplets for Single-answer Questions**|**#QPA triplets for Multi-answer Questions**|
|------------------|:--------------------------:|:-------------------------:|:---------------------------:|:----------------------------:|       
| All              |            1093            |        1337               |          949          |             388            |
| Training         |            819             |        989                |          722          |             268            |
| Test / Holdout   |            274             |        348                |          227          |             121            |

\* QPA stands for question-passage-pair

<!-- | **Dataset**    | **%** |**# Question-Passage Pairs** |               **# Question-passage-answer triplets**                          |
|----------------|:-----:|:---------------------------:|:------------------:|-----------------------------|----------------------------|
|                |       |                             | **All  Questions** | **Single-answer Questions** | **Multi-answer Questions** |
| All            | 100%  |          1,093              |     1,337          |          949                |           388              |
| Training       | 75%   |          819                |     989            |          722                |           268              |
| Test / Holdout*| 25%   |          274                |     348            |          227                |           121              | -->


Each Qur’anic passage in QRCD may have more than one occurrence; and each passage occurrence is paired with a different question. Likewise, each question in QRCD may have more than one occurrence; and each question occurrence is paired with a different Qur’anic passage.

The source of the Qur'anic text in *QRCD* is the [Tanzil project download page](https://tanzil.net/download/), which provides verified versions of the Holy Qur'an in several scripting styles. We have chosen the simple-clean text style of Tanzil version 1.0.2.

# CL-AraBERT Pre-trained Language Model
Download [CL-AraBERTv0.1](https://www.dropbox.com/sh/9zazklvmtzkg1sv/AADiJuZlfUca-mCJZIELQpwta?dl=0); an AraBERT-based model that is further pre-trained using about 1.05B-word Classical Arabic dataset taken from the [OpenITI corpus](https://github.com/OpenITI/RELEASE).  

## How to use CL-AraBERT
Although CL-AraBERT was initially pre-trained for the purpose of developing a machine reading comprehension (MRC) model on the Holy Qur'an, it can easily be exploited for developing *other* NLP tasks on the Holy Qur'an and CA text, such as detecting semantic similarity between Qur'anic verses, and question answering (QA) on Hadith or Exegeses of Qur'an, among others.  

You can easily use CL-AraBERT since it is almost fully compatible with the official AraBERT and BERT codebases. The two minor differences with the offical BERT are in:

* tokenization.py: since we have used the AraBERT codebase, the only difference between AraBERT and BERT is in the tokenization.py file where the function \_is_punctuation was modified to make it compatible the "+" symbol and the "[" and "]" characters as explained [here](https://github.com/aub-mind/arabert/tree/master/arabert#how-to-use).

* run_squad.py: since our [evaluation script](https://github.com/RanaMalhas/QRCD/blob/main/code/eval_qrcd.py) is based on the start/end token positions of the predicted answer(s), we modified run_squad.py such that it writes out the start/end token positions of each predicted answer span to the answer predictions file (nbest_predictions.json) as well. The modified version is named [run_squad_qrcd.py](https://github.com/RanaMalhas/QRCD/blob/main/code/arabert/run_squad_qrcd.py). 

### Using CL-AraBERT with *QRCD*
1. Reformat the train dataset.

Reformatting (or unpooling) is needed for the answer spans of multi-answer questions so that each answer span with its corresponding question and passage (question-passage-answer triplet) is considered a training eample. 

```
python ./code/data_util/transform_to_unpooled_answers_format.py
  --input_file=.../qrcd_v1.1_train.json 
  --output_file=.../qrcd_v1.1_train_reformatted.json
```

2. Preprocess the train and test datasets.

```
python ./code/arabert/qrcd_preprocessing.py
  --input_file= .../qrcd_v1.1_train_reformatted.json \
  --output_file= .../qrcd_v1.1_train_reformatted_pre.json \ 
  --do_farasa_tokenization=False \ 
  --use_farasapy=False 
```
```
python ./code/arabert/qrcd_preprocessing.py \
  --input_file= .../qrcd_v1.1_test.json \
  --output_file= .../qrcd_v1.1_test_pre.json \ 
  --do_farasa_tokenization=False \ 
  --use_farasapy=False 
```

3. Fine-tune the model for the QA/MRC task.

```
python ./code/arabert/run_squad_qrcd.py \  
  --vocab_file= .../PATH_TO_PRE-TRAINED_TF_CKPT/vocab.txt \
  --bert_config_file= .../PATH_TO_PRE-TRAINED_TF_CKPT/config.json \
  --init_checkpoint= .../PATH_TO_PRE-TRAINED_TF_CKPT/cl-arabert01_model.ckpt.data \
  --do_train=True \
  --train_file= .../qrcd_v1.1_train_reformatted_pre.json \
  --do_predict=True \
  --predict_file=.../qrcd_v1.1_test_pre.json \ 
  --train_batch_size=32 \
  --predict_batch_size=24 \
  --learning_rate=3e-5 \
  --num_train_epochs=4 \
  --max_seq_length=384 \
  --doc_stride=128 \
  --do_lower_case=False \
  --output_dir= .../PATH_TO_OUTPUT_PATH   
```
Note: If you have access to a Cloud TPU that you want to fine-tune/train on, just add the following additional flags to run_squad_qrcd.py:

```
  --use_tpu=True \
  --tpu_name=$TPU_NAME
```

## How to Cite
If you use the QRCD dataset and/or the CL-AraBERT model, please cite us as:

@article{malhas2022arabic,  
  title={Arabic machine reading comprehension on the {H}oly {Q}ur’an using {CL-AraBERT}},  
  author={Malhas, Rana and Elsayed, Tamer},  
  journal={Information Processing \\& Management},  
  volume={59},  
  number={6},  
  pages={103068},  
  year={2022},  
  publisher={Elsevier}  
}

## Acknowledgments
We would like to thank all the Qur’an specialists who contributed to annotating/rating the question-answer pairs, especially Dr. Ahmad Shukri, Professor of Tafseer and Qur’anic Sciences at Qatar University, for his scholarly advice throughout the annotation process of the answers extracted from the Holy Qur'an.
