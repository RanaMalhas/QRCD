## How to use the evaluation script?

1. Preprocess the qrcd_v1.1_test.json using [qrcd_preprocessing.py](https://github.com/RanaMalhas/QRCD/blob/main/code/arabert/qrcd_preprocessing.py)

```
python qrcd_preprocessing.py
	--input_file= .../qrcd_v1.1_test.json \
	--output_file= .../qrcd_v1.1_test_pre.json \ 
	--do_farasa_tokenization=False \ 
	--use_farasapy=False 
```

2. Run the evaluation script

```
python eval_qrcd.py
  --dataset_file= .../qrcd_v1.1_test_pre.json
  --nbest_prediction_file=.../nbest_predictions.json 
  --cutoff_rank=10
```
The nbest_predictions.json file is the output of the [run_squad.py](https://github.com/google-research/bert/blob/master/run_squad.py) script released with the original [BERT paper](https://arxiv.org/abs/1810.04805). Though, the only change that we have introduced to the original script is to write out the start/end token positions of each predicted answer span to the nbest_predictions.json file as well. This is essential because our adopted answer matching scheme (between a system's predicted answer to a given question, and its corresponding gold answers) is based on token *positions* in the accompanying Qur'anic passage, rather than any  arbitrary matching bag-of-tokens from that passage. In this way, a predicted answer will be rewarded only if it was extracted from the proper verse/context. We have named the slightly updated version [run_squad_qrcd.py]().

