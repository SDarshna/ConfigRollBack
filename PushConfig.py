#!/usr/bin/env python3 


###############################################################
#### Module to push the config in PA and monitor the result 
#### Author: Darshna Subashchandran
################################################################



import logging
from time import sleep


def push_candidate_config(folder_list, desc, sdk):
    #Push the candidate config
    url = "https://api.sase.paloaltonetworks.com/sse/config/v1/config-versions/candidate:push"
    payload = {
        "description": desc,
        "folders": folder_list
    }
    resp = sdk.rest_call(url=url, data=payload, method="POST")
    #sdk.set_debug(3)

    #Extract the job ID from the response
    job_id = resp.json().get('job_id')

    #Poll the status of the Job ID
    job_complete = False
    while job_complete is False:
        url = "https://api.sase.paloaltonetworks.com/sse/config/v1/jobs/"+job_id
        resp = sdk.rest_call(url=url, method="GET")
        #sdk.set_debug(3)
        if resp.status_code == 200:
            status = resp.json()['data'][0]['status_str']
            logging.info('Polling job [{}]: {}'.format(job_id, status))
            if status == 'FIN':
                job_complete = True
            elif status == 'PEND' or status == 'ACT':
                job_complete = False
            else:
                job_complete = True
        else:
            logging.error('API call failure!')
            break
        sleep(5)

