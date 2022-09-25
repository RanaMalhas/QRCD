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


