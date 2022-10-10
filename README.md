# *QRCD* (Qur'anic Reading Comprehension Dataset)
This repository contains information about [*QRCD*](https://github.com/RanaMalhas/QRCD/tree/main/dataset), [CL-AraBERT](https://github.com/RanaMalhas/QRCD/blob/main/README.md#cl-arabert-pre-trained-language-model) (**CL**assical **AraBERT**) pre-trained model and [code](https://github.com/RanaMalhas/QRCD/tree/main/code) for evaluating results on *QRCD*.

*QRCD* is composed of 1,093 tuples of question-passage pairs that are coupled with their extracted answers to constitute 1,337 question-passage-answer triplets. The distribution of the dataset into training and test sets is shown below. The dataset in this repo adopts the [SQuAD v1.1 format](https://github.com/facebookresearch/DrQA#format-b). A version in JSONL (JSON lines) format is also available. It can be downloaded from the [Qur'an QA 2022 repo](https://gitlab.com/bigirqu/quranqa/-/tree/main/datasets). 

<!-- | **Dataset** | **%** | **# Question-Passage  Pairs** | **# Question-Passage-Answer  Triplets** |
|-------------|:-----:|:-----------------------------:|:---------------------------------------:|
| Training    |  65%  |              710              |                   861                   |
| Development |  10%  |              109              |                   128                   |
| Test        |  25%  |              274              |                   348                   |
| All         |  100% |              1,093            |                  1,337                  |
 -->

| Dataset          |**# Question-Passage Pairs**|**# QPA\* triplets for All Questions**|**# QPA triplets for Single-answer Questions**|**#QPA triplets for Multi-answer Questions**|
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

### Using CL-AraBERT with *QRCD*

1. Preprocess the train and test datasets using [qrcd_preprocessing.py](https://github.com/RanaMalhas/QRCD/blob/main/code/arabert/qrcd_preprocessing.py).

```
python qrcd_preprocessing.py
  --input_file= .../qrcd_v1.1_train.json \
  --output_file= .../qrcd_v1.1_train_pre.json \ 
  --do_farasa_tokenization=False \ 
  --use_farasapy=False 
```
```
python qrcd_preprocessing.py \
  --input_file= .../qrcd_v1.1_test.json \
  --output_file= .../qrcd_v1.1_test_pre.json \ 
  --do_farasa_tokenization=False \ 
  --use_farasapy=False 
```

2. Fine-tune the model for the QA/MRC task

Since our [evaluation script](https://github.com/RanaMalhas/QRCD/blob/main/code/eval_qrcd.py) is based on the start/end token positions of the predicted answer(s), you will need to use [run_squad_qrcd.py](https://github.com/RanaMalhas/QRCD/blob/main/code/arabert/run_squad_qrcd.py) in fine-tuning (instead of using the original [run_squad.py](https://github.com/google-research/bert/blob/master/run_squad.py) script released with the original [BERT paper](https://arxiv.org/abs/1810.04805)).  Though, the only change that we have introduced to the original script is to write out the start/end token positions of each predicted answer span to the answer predictions file (nbest_predictions.json) as well. 

```
python run_squad_qrcd.py \  
  --vocab_file= .../PATH_TO_PRE-TRAINED_TF_CKPT/vocab.txt \
  --bert_config_file= .../PATH_TO_PRE-TRAINED_TF_CKPT/config.json \
  --init_checkpoint= .../PATH_TO_PRE-TRAINED_TF_CKPT/cl-arabert01_model.ckpt.data \
  --do_train=True \
  --train_file= .../qrcd_v1.1_train_pre.json \
  --do_predict=True \
  --predict_file=.../qrcd_v1.1_test_pre.json \ 
  --train_batch_size=32 \
  --predict_batch_size=24 \
  --learning_rate=3e-5 \
  --num_train_epochs=4 \
  --max_seq_length=384 \
  --doc_stride=128 \
  --do_lower_case=False \
  --output_dir= .../PATH_TO_OUTPUT_PATH \
  --use_tpu=True \
  --tpu_name=$TPU_NAME
  
```
