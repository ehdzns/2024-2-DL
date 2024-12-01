import os
from openai import OpenAI
import base64
import streamlit as st
import pandas as pd
import re
import ast
import copy
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
#####################
#####functions#######
#####################
# Sample text containing the pattern
def ttd(text):
    # Define a regex pattern to match dictionary-like structures
    pattern = r"\{[^}]*\}"  # Matches content inside curly braces

    # Extract matching patterns
    matches = re.findall(pattern, text)
    # If needed, convert the match to a Python dictionary
    if matches:
        # Safely parse the first matched string to a dictionary
        extracted_dict = ast.literal_eval(matches[0])
        return(extracted_dict)     
    else:
        print("No valid dictionary pattern found in the text.")
# image preprocessing
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# API Visual Prompting result
def VPR(IMG_CONTENT,base64_image):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """
            #Persona:Personality Psychologist|MBTI|examine the [image]|suggest respthondent's personality type based on the [reaction] form [image]
            #Domain Knowledge: 
            ## E:Individuals who are energized by external world, social interactions, and outer stimuli.
            ## I:Individuals who are energized by inner world, reflection, and internal thoughts.
            ## S:Focus on concrete, tangible, and present information.Prefer practical, detail-oriented approaches.
            ## N:Focus on abstract, conceptual, and future possibilities.Prefer innovative, big-picture thinking.
            ## T:Decisions based on objective, logical analysis.Prioritize fairness and consistent principles.
            ## F:Decisions based on personal values, empathy, and human impact.Prioritize harmony and individual circumstances.
            ## J:Prefer structured, planned, and organized approaches.Like clear decisions and definitive conclusions.
            ## P:Prefer flexible, spontaneous, and adaptable approaches.Enjoy keeping options open and gathering more information.
            #CONDITION: Consider the [CONTEXT] between [image] and [reaction] 
            ##Output: [python dictionary]and[reasoning]
            ###[python dictionary]format:{'E':n,'I':n,'S':n,'N':n,'T':n,'F':n,'J':n,'P':n}
            ###scoring rule:score 1 to 5 by the intensity
            ###[reasoning] format:[REASONING]:
            # - 'I' (Introversion): n - (reason of scoring)
                - 'S' (Sensing): n - (reason of scoring)
                - 'N' (Intuition): n - (reason of scoring)
                - 'T' (Thinking): n - (reason of scoring)
                - 'F' (Feeling): n - (reason of scoring)
                - 'J' (Judging): n - (reason of scoring)
                - 'P' (Perceiving): n - (reason of scoring)]
            """},
            {"role": "user", "content": [
                {"type": "text", "text": f"reaction of the image:{IMG_CONTENT}"},
                {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{base64_image}"}
                }  
            ]}
        ],
        temperature=1,
    )
    return response
def CMTCH(text,base64_image):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """# you are a worker of Mturk
            #Object:label if the input text is the comment or personal impression
            # Output: Yes or NO"""},
             {"role": "user", "content": [
                {"type": "text", "text":text}
                ]}
            ],
        temperature=1,
     )
    return response
    
def ratcal(a,b):
    ratio1=100*a/(a+b)
    ratio2=100*b/(a+b)
    ratio1.round()
    ratio2.round()
    return(ratio1.round(),ratio2.round())


#####################
#####web site UI#####
#####################

st.set_page_config(
    page_title="MBTI with image",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title('MBTI with image')
st.divider()

di={'E': 0,'I': 0,'S': 0,'N': 0,'T': 0,'F': 0,'J': 0,'P': 0}
if 'img_cmt_df' not in st.session_state:
    st.session_state.img_cmt_df=pd.DataFrame([{'img_1.png':'blank','img_2.png':'blank','img_3.png':'blank','img_4.png':'blank','img_5.png':'blank','img_6.png':'blank','img_7.png':'blank','img_8.png':'blank','img_9.png':'blank','img_10.png':'blank'},
                                              {'img_1.png':di,'img_2.png':di,'img_3.png':di,'img_4.png':di,'img_5.png':di,'img_6.png':di,'img_7.png':di,'img_8.png':di,'img_9.png':di,'img_10.png':di}])

section1 = st.container(border=True)
section1.write("Select the image and write your impression")
img=section1.selectbox('‣ Image list', st.session_state.img_cmt_df.columns, key="comment_date")
with section1:
    st.image(img, caption=None, width=500)

section2 = st.container(border=True)
with section2:
    IMG_CONTENT=st.text_input(f"‣ Write the impression of the image here {img}", "")
    base64_image = encode_image(img)
    cmt_check=CMTCH(IMG_CONTENT,img).choices[0].message.content
    print(cmt_check)
    if st.button('analyze comment', key='generate'):
        if  cmt_check!='NO':
            GPT_R=VPR(IMG_CONTENT,base64_image).choices[0].message.content
            st.success(f"Analysis of {img} comment is done!")
            st.session_state.img_cmt_df[img][0]=GPT_R
            st.session_state.img_cmt_df[img][1]=ttd(GPT_R)
        else:
            st.write('Inscribe the right comment about the image')

    
section3 = st.container(border=True)
with section3:
    st.write(st.session_state.img_cmt_df[img][0])
    
    if st.button('Generate MBTI Result'):
        fin_df=pd.DataFrame(list(st.session_state.img_cmt_df.iloc[1,:]))
        
        E,I=ratcal(fin_df.sum()['E'],fin_df.sum()['I'])
        S,N=ratcal(fin_df.sum()['S'],fin_df.sum()['N'])
        T,F=ratcal(fin_df.sum()['T'],fin_df.sum()['F'])
        J,P=ratcal(fin_df.sum()['J'],fin_df.sum()['P'])
        st.write(f'E: {E} %, I: {I} %') 
        st.write(f'S: {S} %, N: {N} %') 
        st.write(f'T: {T} %, F: {F} %') 
        st.write(f'J: {J} %, P: {P} %')
        st.write(fin_df)
    st.cache_data.clear()
