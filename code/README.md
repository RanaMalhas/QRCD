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

The `qrcd_v1.1_test.json` was released after announcing the winners of the [Quran QA 2022 Shared Task](https://sites.google.com/view/quran-qa-2022/home?authuser=0). 
