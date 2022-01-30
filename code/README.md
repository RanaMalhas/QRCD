To run the evaluation script:

```
python eval_qrcd.py
  --dataset_file= .../qrcd_dev_gold.json
  --nbest_prediction_file=.../nbest_predictions.json 
  --cutoff_rank=10
```

You can use part of the qrcd_v1.1_train.json as a development set for evaluation. \
As the qrcd_v1.1_test.json will be released without its answers, a leaderboard is being developed on CodaLab to receive a system's submission for evaluation.
