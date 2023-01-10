#!/usr/bin/env python3 

###############################################################
#### PA Config Rollback Script (Reset of SC, RN and GP )
#### Author: Darshna Subashchandran
################################################################

import PushConfig
import yaml
from time import sleep
import argparse
import prisma_sase

####################################################
#### Login to the tenant with the client secret
###################################################
def sdk_login_to_controller(filepath):
    with open(filepath) as f:
        client_secret_dict = yaml.safe_load(f)
        client_id = client_secret_dict["client_id"]
        client_secret = client_secret_dict["client_secret"]
        tsg_id_str = client_secret_dict["scope"]
        global tsgid
        tsgid = tsg_id_str.split(":")[1]
        #print(client_id, client_secret, tsgid)
    
    global sdk 
    sdk = prisma_sase.API(controller="https://sase.paloaltonetworks.com/", ssl_verify=False)
    sdk.set_debug(3) 
    sdk.interactive.login_secret(client_id, client_secret, tsgid)
    
    return sdk

####################################################
#### Rollback candidate config to a Specific Version
###################################################
def rollback_candidate_config_to_ver(tsgid,ver):

    #Load a previous version you want to rollback to
    url = "https://api.sase.paloaltonetworks.com/sse/config/v1/config-versions:load"
    payload = {
        "version": ver
    }
    resp = sdk.rest_call(url=url, data=payload, method="POST")
    sdk.set_debug(3)
    #print(resp)

####################################################
#### Reading tenant version info 
###################################################
def read_tenant_ver_info(input_filepath):
    with open(input_filepath) as f:
        tenant_ver_dict = yaml.full_load(f)
    return tenant_ver_dict

if __name__ == "__main__":
    
    #Parsing the arguments to the script
    parser = argparse.ArgumentParser(description='Onboarding the LocalUsers, Service Connection and Security Rules.')
    parser.add_argument('-f', '--InputFilePath', help='Input secret file in .yml format for the tenant(T1) from which the security rules have to be replicated.')  
    parser.add_argument('-t1', '--T1Secret', help='Input secret file in .yml format for the tenant(T1) from which the security rules have to be replicated.')  

    args = parser.parse_args()
    T1_secret_filepath = args.T1Secret
    input_filepath = args.InputFilePath

    global sdk
    sdk = sdk_login_to_controller(T1_secret_filepath)   
     
    #Read subtenant version info from file
    tenant_ver_dict = read_tenant_ver_info(input_filepath)
    #print(tenant_ver_dict)
   
 
    for tsgid,ver_str in tenant_ver_dict.items():

        #Split the version string
        mu_ver,rn_ver,sc_ver = tenant_ver_dict[int(tsgid)].split(",")
        rollback_ver = min(mu_ver,rn_ver,sc_ver)
    
	#Rollback candidate config to version
        rollback_candidate_config_to_ver(tsgid, rollback_ver)
               
        PushConfig.push_candidate_config(["Service Connections"], "push to Service Connections", sdk)
        sleep(10)
        PushConfig.push_candidate_config(["Remote Networks"], "push to Remote Networks", sdk)
        sleep(10)
        PushConfig.push_candidate_config(["Mobile Users"], "push to Mobile Users", sdk)
        sleep(10)


