# coding=utf-8
#
# This script applies AraBERT's cleaning process and segmentation to ARCD or
# any SQUAD-like structured files and "naively" re-alligns the answers start positions

'''
The original script name is "arcd_preprocessing.py" as published with the AraBERT paper initially in 2020.
We tailored it and renamed it as "qrcd_preprocessing.py" to be used in preprocessing the QRCD dataset
or any SQUAD-like structured files to re-allign the answers start positions more accurately.

Main changes/updates:
- Stripping the last char from the answer if it was a full stop to facilitate finding the answer in
  the accompanying passage.
- All answers to a question were considered (rather than only one/first answer)
- Re-alignment of answer-start taking into consideration the punctuations retained (e.g. full stops).
  The method adj_answer_start() was added to adjust answer-start
'''
import tensorflow as tf
from preprocess_arabert import preprocess, never_split_tokens
from tokenization import BasicTokenizer, _is_punctuation

import json

flags = tf.flags
FLAGS = flags.FLAGS

## Required parameters
flags.DEFINE_string(
    "input_file", None, "The input json file with a SQUAD like structure."
)

flags.DEFINE_string(
    "output_file", None, "The ouput json file with AraBERT preprocessing applied."
)

flags.DEFINE_bool(
    "do_farasa_tokenization", None, "True for AraBERTv1 and False for AraBERTv0.1"
)

## Other parameters
flags.DEFINE_bool(
    "use_farasapy",
    True,
    "True if you want to use farsasapy instead of FarasaSegmenterJar.jar",
)

flags.DEFINE_string(
    "path_to_farasa",
    None,
    "path to the FarasaSegmenterJar.jar file required when "
    "do_farasa_tokenization is enabled will be ignore if use_farasapy is set to True",
)

bt = BasicTokenizer()

def clean_preprocess(text, do_farasa_tokenization, farasa, use_farasapy):
    text = " ".join(
        bt._run_split_on_punc(
            preprocess(
                text,
                do_farasa_tokenization=do_farasa_tokenization,
                farasa=farasa,
                use_farasapy=use_farasapy,
            )
        )
    )
    text = " ".join(text.split())  # removes extra whitespaces
    return text

def adjust_answer_start(orig_text, orig_answer_start):
    '''
    :param orig_text: raw paragraph text
    :param orig_start: character position at which the answer starts
    :return:
    '''
    start = orig_answer_start
    chars= list(orig_text)
    i = 0
    while i < len(chars):
        if i > orig_answer_start:
            break
        char = chars[i]
        if _is_punctuation(char):
            start = start + 1
        i += 1
    return start

def main(_):
    tf.logging.set_verbosity(tf.logging.INFO)

    if FLAGS.do_farasa_tokenization and (FLAGS.path_to_farasa == None):
        raise ValueError(
            "do_farasa_tokenization is enabled, please provide the path_to_farasa"
        )

    if FLAGS.do_farasa_tokenization:
        if FLAGS.use_farasapy:
            from farasa.segmenter import FarasaSegmenter

            farasa_segmenter = FarasaSegmenter(interactive=True)
        else:
            from py4j.java_gateway import JavaGateway

            gateway = JavaGateway.launch_gateway(classpath=FLAGS.path_to_farasa)
            farasa_segmenter = gateway.jvm.com.qcri.farasa.segmenter.Farasa()
    else:
        farasa = None
        farasa_segmenter = None ## inserted on Dec 28, 2020

    with tf.gfile.Open(FLAGS.input_file, "r") as reader:
        input_data = json.load(reader)["data"]

    for entry in input_data:
        for paragraph in entry["paragraphs"]:
            orig_paragraph_context = paragraph["context"]
            paragraph["context"] = clean_preprocess(
                paragraph["context"],
                do_farasa_tokenization=FLAGS.do_farasa_tokenization,
                farasa=farasa_segmenter,
                use_farasapy=FLAGS.use_farasapy,
            )
            for qas in paragraph["qas"]:
                qas["question"] = clean_preprocess(
                    qas["question"],
                    do_farasa_tokenization=FLAGS.do_farasa_tokenization,
                    farasa=farasa_segmenter,
                    use_farasapy=FLAGS.use_farasapy,
                )
                ground_truth_answers = list(map(lambda x: x['text'], qas['answers']))
                for i, answer in enumerate(ground_truth_answers):
                    orig_answer_start = qas["answers"][i]["answer_start"]
                    adj_answer_start = adjust_answer_start(orig_paragraph_context, orig_answer_start)

                    qas['answers'][i]['answer_start'] = adj_answer_start
                    qas["answers"][i]["text"] = clean_preprocess(
                        qas["answers"][i]["text"],
                        do_farasa_tokenization=FLAGS.do_farasa_tokenization,
                        farasa=farasa_segmenter,
                        use_farasapy=FLAGS.use_farasapy,
                    )

    input_data = {
        "data": input_data,
        "version": "1.1",
        "preprocess": "True",
    }
    with tf.gfile.Open(FLAGS.output_file, "w") as writer:
        json.dump(input_data, writer)

if __name__ == "__main__":
    flags.mark_flag_as_required("input_file")
    flags.mark_flag_as_required("output_file")
    flags.mark_flag_as_required("do_farasa_tokenization")
    tf.app.run()
