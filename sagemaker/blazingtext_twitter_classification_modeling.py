import sagemaker
from sagemaker import get_execution_role
import json
import boto3
import pandas as pd
from random import shuffle
import multiprocessing
from multiprocessing import Pool
import csv
import nltk

sess = sagemaker.Session()

role = get_execution_role()
print(role) # This is the role that SageMaker would use to leverage AWS resources (S3, CloudWatch) on your behalf

bucket = "mehdi-datalake" # Replace with your own bucket name if needed
print(bucket)
data_key = 'twitter-data/hashtags/aws/2019-01-04/labeled.csv/hashtag-labeled-only-tweet.csv'
data_location = 's3://{}/{}'.format(bucket, data_key)

tweets = pd.read_csv(data_location)

tweets.to_csv('tweets-labeled.csv', sep=',', header=None, index=False)

prefix = 'twitter-data/marketing-model'

index_to_label = {}
#with open("dbpedia_csv/classes.txt") as f:
#    for i,label in enumerate(f.readlines()):
#        index_to_label[str(i+1)] = label.strip()
index_to_label = {
    "0": "technical",
    "1": "marketing"
}
print(index_to_label)

nltk.download('punkt')

def transform_instance(row):
    cur_row = []
    label = "__label__" + index_to_label[row[0]]  #Prefix the index-ed label with __label__
    cur_row.append(label)
    cur_row.extend(nltk.word_tokenize(row[1].lower()))
    return cur_row

def preprocess(input_file, output_file, keep=1):
    all_rows = []
    with open(input_file, 'r') as csvinfile:
        csv_reader = csv.reader(csvinfile, delimiter=',')
        for row in csv_reader:
            all_rows.append(row)
    shuffle(all_rows)
    all_rows = all_rows[:int(keep*len(all_rows))]
    pool = Pool(processes=multiprocessing.cpu_count())
    transformed_rows = pool.map(transform_instance, all_rows)
    pool.close()
    pool.join()

    with open(output_file, 'w') as csvoutfile:
        csv_writer = csv.writer(csvoutfile, delimiter=' ', lineterminator='\n')
        csv_writer.writerows(transformed_rows)

# Preparing the training dataset

# Since preprocessing the whole dataset might take a couple of mintutes,
# we keep 20% of the training dataset for this demo.
# Set keep to 1 if you want to use the complete dataset
#preprocess('dbpedia_csv/train.csv', 'dbpedia.train', keep=.2)
preprocess('tweets-labeled.csv', 'tweets.train', keep=.8)

# Preparing the validation dataset
#preprocess('dbpedia_csv/test.csv', 'dbpedia.validation')
preprocess('tweets-labeled.csv', 'tweets.validation')

train_channel = prefix + '/train'
validation_channel = prefix + '/validation'

sess.upload_data(path='tweets.train', bucket=bucket, key_prefix=train_channel)
sess.upload_data(path='tweets.validation', bucket=bucket, key_prefix=validation_channel)

s3_train_data = 's3://{}/{}'.format(bucket, train_channel)
s3_validation_data = 's3://{}/{}'.format(bucket, validation_channel)

s3_output_location = 's3://{}/{}/output'.format(bucket, prefix)

region_name = boto3.Session().region_name
container = sagemaker.amazon.amazon_estimator.get_image_uri(region_name, "blazingtext", "latest")
print('Using SageMaker BlazingText container: {} ({})'.format(container, region_name))

bt_model = sagemaker.estimator.Estimator(container,
                                         role,
                                         train_instance_count=1,
                                         train_instance_type='ml.c4.4xlarge',
                                         train_volume_size = 30,
                                         train_max_run = 360000,
                                         input_mode= 'File',
                                         output_path=s3_output_location,
                                         sagemaker_session=sess)
bt_model.set_hyperparameters(mode="supervised",
                            epochs=10,
                            min_count=2,
                            learning_rate=0.05,
                            vector_dim=10,
                            early_stopping=True,
                            patience=4,
                            min_epochs=5,
                            word_ngrams=2)

train_data = sagemaker.session.s3_input(s3_train_data, distribution='FullyReplicated',
                        content_type='text/plain', s3_data_type='S3Prefix')
validation_data = sagemaker.session.s3_input(s3_validation_data, distribution='FullyReplicated',
                             content_type='text/plain', s3_data_type='S3Prefix')
data_channels = {'train': train_data, 'validation': validation_data}
bt_model.fit(inputs=data_channels, logs=True)


