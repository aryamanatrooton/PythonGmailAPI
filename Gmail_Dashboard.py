from __future__ import print_function
import pandas as pd
import streamlit as st
import os
import time
# Import Libraries
import math
import os.path
from re import sub
from typing import List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import json
class GmailException(Exception):
    	"""gmail base exception class"""

class NoEmailFound(GmailException):
	"""no email found"""

def load_credentials(filename='credentials.json'):
    creds=None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif filename:
                # print("ues")
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                    filename, SCOPES)
                    creds = flow.run_local_server(port=0)
                except:
                    print("No File Found")
        # with open('token.json', 'w') as token:
        #     token.write(creds.to_json())
        return creds
def convert_base64_file(filename):
    file = open(filename, 'rb')
    byte = file.read()
    file.close()
    with open(os.path.join(os.getcwd(), filename[:-4]), 'wb') as _f:
        _f.write(byte)
    print("Attached file  {0} is saved at".format(filename),os.getcwd())

def get_gmail_api():
    print("Calling Again")
    # progress_text = "Operation in progress. Please wait."
    # st.text(progress_text)
    # st.empty()
    
    cnt=0
    my_bar = st.progress(cnt)
    df = pd.DataFrame(columns = ['ID','Labels','To', 'From','Subject','Date','Message','Location'])
    results=service.users().messages().list(userId='me').execute()
    messages=results.get('messages',[])
    if not messages:
        print("You have no new messages")
    else:
        for message in messages:
            message_gmail={}
            increment=(100/len(messages))
            cnt=cnt+int(math.ceil(increment))
            if cnt>=100:
                cnt=100
            my_bar.progress(cnt)

            # print(message['id'])
        
            msg=service.users().messages().get(userId='me',id=message['id']).execute()
            message_gmail['ID']=message['id']
            message_gmail['Labels']=",".join(msg['labelIds'])  
            email_data=msg['payload']['headers']
            for values in email_data:
                name=values["name"]
                # print(name) 
                if name=="From":
                    from_name=values['value']
                    message_gmail['From']=from_name

                if name=="Date":
                    from_name=values['value']
                    message_gmail['Date']=from_name
                
                if name=="Subject":
                    subject=values['value']
                    message_gmail['Subject']=subject
                if name=="To":
                    if len(message_gmail['Labels'])>1 and message_gmail['Labels'].__contains__("INBOX"):
                        Username=values['value']
                        message_gmail["To"]=values['value']
                else:
                     message_gmail["To"]=values['value']
                if name=="Cc":
                    message_gmail["Cc"]=values['value']
                    
            message_gmail['Message']=msg['snippet']
            messageDetail = get_message_detail(message['id'], msg_format='full', metadata_headers=['parts'])
            messageDetailPayload = messageDetail.get('payload')
            if 'parts' in messageDetailPayload:
                for msgPayload in messageDetailPayload['parts']:
                    file_name = msgPayload['filename']
                    body = msgPayload['body']
                    save_location = os.getcwd()
                    if 'attachmentId' in body:
                        attachment_id = body['attachmentId']
                        attachment_content = get_file_data(message['id'], attachment_id, file_name, save_location)
                        filename=file_name+".bin"
                        with open(os.path.join(save_location, filename), 'wb') as _f:
                            _f.write(attachment_content)
                            # print(f'Atfile  {file_name} is saved at {save_location}')
                            message_gmail['Location']=os.path.join(save_location, filename)
            # if len(message_gmail['Location'])==0:
            message_gmail['Location']=None
            # response_gmail[message['id']]=message_gmail
            df.loc[len(df)]=message_gmail
            # print(df.shape)
    return df,Username
            # exit()

def get_file_data(message_id, attachment_id, file_name, save_location):
    response = service.users().messages().attachments().get(userId='me',messageId=message_id,id=attachment_id).execute()
    file_data = base64.urlsafe_b64decode(response.get('data').encode('UTF-8'))
    return file_data

def get_message_detail(message_id, msg_format='metadata', metadata_headers: List=None):
	message_detail = service.users().messages().get(
		userId='me',
		id=message_id,
		format=msg_format,
		metadataHeaders=metadata_headers
	).execute()
	return message_detail

if __name__ == '__main__':
    # try:
    FilterPass=False
    SCOPES = ['https://mail.google.com/']
    
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    st.title("Welcome to Gmail Dashboard")
    
    userlist=[]
    userlist.append('--Select Gmail ID---')
    userlist.append('Add New +')
    getlist=[var for var in os.listdir("./") if  var.endswith(".json") and var not in ('credentials.json','sample.json')]
    for user in getlist:
        userlist.append(user[:-5])
    # set3 = set_option.union(userlist)
    # set_option.add(userlist)
#     import streamlit as st


    
    option = st.selectbox('Gmail INBOX',userlist,index=0)
    
    if option!='--Select Gmail ID---':
        if option in userlist:
             Username=option
             if os.path.exists('{0}.json'.format(Username)):
                    creds_file = Credentials.from_authorized_user_file('{0}.json'.format(Username), SCOPES)
             else:
                    creds_file=load_credentials()
        service = build('gmail', 'v1', credentials=creds_file)
        # if FilterPass==False:
        output,current_user=get_gmail_api()
        if FilterPass:
            st.download_button(
                "Download Gmail Message",
                csv,
                "Gmail_Message.csv",
                "text/csv",
                key='download-csv'
            )
        
        # for percent_complete in range(100):
        #     time.sleep(0.1)
            
        # st.spinner(text="In progress...")
        # CSS to inject contained in a string
        def convert_df(df):
            return df.to_csv(index=False).encode(encoding = 'raw_unicode_escape')
        #    return df.to_csv(index=False).encode('utf-8')


        
        
        if output.shape[0]>1:
            csv = convert_df(output)
            FilterPass=True
            filter_list=output['Labels'].unique()
            option_filter=[]
            option_filter.append('--Select Category--')
            for i in filter_list:
                 temp_list=i.split(',')
                 for j in temp_list:
                        option_filter.append(j)
            option_filter=set(option_filter)
            option_filter=list(option_filter) 
            selected_filter=st.selectbox('Filter',set(option_filter),index=option_filter.index('--Select Category--'))
            if selected_filter!="--Select Category--":
                output=output.loc[output['Labels'].str.contains(selected_filter)]
                st.dataframe(output,width=1200)
            else:
                 st.dataframe(output,width=1200)
            st.download_button(
                "Download Gmail Message",
                csv,
                "Gmail_Message.csv",
                "text/csv",
                key='download-csv'
            )
            
        else:
             st.wrte("No Data Found!")
            
        st.markdown("<h6 style='text-align: center; color: red;'>Copyright reserved by Twinnet Technologies </h6>", unsafe_allow_html=True)
        if not os.path.exists('{0}.json'.format(Username)):
            with open("{0}.json".format(current_user), "w") as outfile:
                outfile.write(creds_file.to_json())
