import streamlit as st
import os
import time
import telebot
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from st_copy_to_clipboard import st_copy_to_clipboard

# Set up Telegram Bot
recipient_user_id = os.environ['RECIPIENT_USER_ID']
bot_token = os.environ['BOT_TOKEN']
bot = telebot.TeleBot(bot_token)

# Retrieve the API keys from the environment variables
GEMINI_API_KEY = os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

safety_settings = {
  HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
  HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
  HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
  HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

generation_config = genai.GenerationConfig(
  candidate_count = 1,
  temperature = 0,
)

def generate_prompt(individual):
    prompt = f"""###Instruction###
Create a comprehensive biography of {individual} detailing the personal background, education, career progression, and other significant appointments or achievements. The biography should be structured as follows:

1. **NAME**: Full name of the individual.
2. **GOVERNMENT POSITION**: Current or most recent government position held.
3. **COUNTRY**: The official name of the country they serve or have served.
4. **BORN**: Date of birth.
5. **AGE**: Current age. Calculate the difference between the current date and the date of birth.
6. **MARITAL STATUS**: Information on marital status, including spouse and children if applicable. String format.
7. **EDUCATION**: Chronological list of educational achievements, including institutions attended and degrees or qualifications obtained. Give the breakdown in the form of PERIOD, INSTITUTION, DEGREE.
8. **CAREER**: Detailed account of the individual's career, including positions held, dates of service, and any promotions or notable responsibilities. This section can be continued as needed (e.g., "Career (cont’d)"). Do not miss the details of all promotions and double hatting positions. Give the breakdown in the form of YEAR and POSITION.
9. **OTHER APPOINTMENTS**: List of other significant appointments, roles, or contributions outside of their main career path.
10. **AWARDS and DECORATIONS**: List of awards and decorations received.
11. **LANGUAGES**: Languages spoken.
12. **REMARKS**: Any additional noteworthy information or personal achievements, including familial connections to other notable figures if relevant.

This format is designed to provide a clear and detailed overview of an individual's professional and personal life, highlighting their contributions and achievements in a structured manner.

###Information###
[INFO]

###Biography###"""
    return prompt

st.set_page_config(page_title="Sherwood CV Generator", page_icon=":face_with_cowboy_hat:")
st.write("**Sherwood CV Generator** :face_with_cowboy_hat:")
#with st.expander("Click to read documentation"):
#  st.write("Sherwood CV Generator")

Model_Option = st.selectbox("What Large Language Model do I use?", ('Gemini 1.5 Pro'))
Name_of_Person = st.text_input("Enter the name of the person whose CV you would like to generate:")
Customised_Prompt = generate_prompt(Name_of_Person)

if st.button("Let\'s Go! :rocket:") and Name_of_Person.strip()!="":
  try:
    with st.spinner("Running AI Model....."):
    
      start = time.time()
      if Model_Option == "Gemini 1.5 Pro":
        gemini = genai.GenerativeModel("gemini-1.5-pro-002")
        response = gemini.generate_content(Customised_Prompt, safety_settings = safety_settings, generation_config = generation_config, tools = "google_search_retrieval")
        output_text = response.text
        with st.expander("Sources for " + Name_of_Person):
          st.write("Sources for " + Name_of_Person)
          candidates = response.candidates
          grounding_metadata = candidates[0].grounding_metadata
          grounding_chunks = grounding_metadata.grounding_chunks
          for chunk in grounding_chunks:
            uri = chunk.web.uri
            title = chunk.web.title
            st.write(f"[{title}]({uri})")
        
        #st.write("Sources for " + Name_of_Person)
        #candidates = response.candidates
        #grounding_metadata = candidates[0].grounding_metadata
        #grounding_chunks = grounding_metadata.grounding_chunks
        #for chunk in grounding_chunks:
        #  uri = chunk.web.uri
        #  title = chunk.web.title
        #  st.write(f"[{title}]({uri})")
      end = time.time()

      with st.expander("CV of " + Name_of_Person):
        st.write(output_text)
        st.write("Time to generate: " + str(round(end-start,2)) + " seconds")
        st_copy_to_clipboard(output_text)

      st.snow()
      bot.send_message(chat_id=recipient_user_id, text="Sherwood CV Gen" + "\n" + Model_Option + "\n" + Name_of_Person)
      
  except:
    st.error(" Error occurred when running model", icon="🚨")
