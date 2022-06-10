# *QRCD* (Qur'anic Reading Comprehension Dataset)
This repository contains information about *QRCD*, CL-AraBERT (**CL**assical **AraBERT**) pre-trained model and code for evaluating results on *QRCD*.

*QRCD* is composed of 1,093 tuples of question-passage pairs that are coupled with their extracted answers to constitute 1,337 question-passage-answer triplets. The distribution of the dataset into training and test sets is shown below.

| **Dataset** | **%** | **# Question-Passage  Pairs** | **# Question-Passage-Answer  Triplets** |
|-------------|:-----:|:-----------------------------:|:---------------------------------------:|
| Training    |  65%  |              710              |                   861                   |
| Development |  10%  |              109              |                   128                   |
| Test        |  25%  |              274              |                   348                   |
| All         |  100% |              1,093            |                  1,337                  |


|     Dataset          | ** # Question-Passage Pairs** | **   # Question-passage-answer triplets** |                                 |                                |
|----------------------|:-----------------------------:|:-----------------------------------------:|---------------------------------|--------------------------------|
|                      |                               |           **   All  Questions**           | **   Single-answer  Questions** | **   Multi-answer  Questions** |
|     All              |                1093           |                      1337                 |                 949             |                 388            |
|     Training         |               819             |                      989                  |                722              |                 268            |
|     Test / Holdout   |                274            |                      348                  |                 227             |                121             |

| **Dataset**    | **%** |**# Question-Passage Pairs** |               **# Question-passage-answer triplets**                          |
|----------------|:-----:|:---------------------------:|:------------------:|-----------------------------|----------------------------|
|                |       |                             | **All  Questions** | **Single-answer Questions** | **Multi-answer Questions** |
| All            | 100%  |          1,093              |     1,337          |          949                |           388              |
| Training       | 75%   |          819                |     989            |          722                |           268              |
| Test / Holdout*| 25%   |          274                |     348            |          227                |           121              |
*The test will released soon

Each Qur’anic passage in QRCD may have more than one occurrence; and each passage occurrence is paired with a different question. Likewise, each question in QRCD may have more than one occurrence; and each question occurrence is paired with a different Qur’anic passage.

The source of the Qur'anic text in *QRCD* is the [Tanzil project download page](https://tanzil.net/download/), which provides verified versions of the Holy Qur'an in several scripting styles. We have chosen the simple-clean text style of Tanzil version 1.0.2.

# CL-AraBERT Pre-trained Language Model
Download [CL-AraBERTv0.1](https://www.dropbox.com/s/ekkgoj2yrkhgtez/CL-AraBERTv0.1-base.zip?dl=0); an AraBERT-based model that is further pre-trained using about 1.05B-word Classical Arabic dataset taken from the [OpenITI corpus](https://github.com/OpenITI/RELEASE).  


