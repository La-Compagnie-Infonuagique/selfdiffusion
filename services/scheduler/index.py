import json
import boto3
import os

def lambda_handler(event, _):
    # Makes decision about the number of worker that process jobs

    # pull out average arrival rate.
    # pull out average processing time per job.
    # pull out the number of workers.

    # compute ro = lambda / (mu * m)

    # if ro < 1, then we are underutilized, so we can reduce the number of workers.
    # if ro > 1, then we are overutilized, so we can increase the number of workers.

    print('hello world')

