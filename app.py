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

prompt = """###Instruction###
Create a comprehensive biography of [individual] detailing the personal background, education, career progression, and other significant appointments or achievements. The biography should be structured as follows:

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

st.set_page_config(page_title="Sherwood Intern", page_icon=":face_with_cowboy_hat:")
st.write("**Sherwood Intern** :face_with_cowboy_hat:")
with st.expander("Click to read documentation"):
  st.write("Sherwood Intern")

#if "keywords" not in st.session_state:
#  st.session_state.keywords = []

#new_keyword = st.text_input("Add a new country:")
#if st.button("Add"):
#  if new_keyword and new_keyword not in st.session_state.keywords:
#    st.session_state.keywords.append(new_keyword)

#if st.session_state.keywords:
#  for keyword in st.session_state.keywords:
#    if st.button(f"Remove '{keyword}'", key = f"remove_{keyword}"):
#      st.session_state.keywords.remove(keyword)

#if st.session_state.keywords:
#  keywords_string = ""
#  for keyword in st.session_state.keywords:
#    keywords_string = keywords_string + keyword + " "  
#  st.info(keywords_string)

Model_Option = st.selectbox("What Large Language Model do I use?", ('Gemini 1.5 Pro'))

Customised_Prompt = st.text_area("You may wish to modify the CV generation prompt below.", prompt)

if st.button("Let\'s Go! :rocket:"):
  try:
    with st.spinner("Running AI Model....."):
    
      start = time.time()
      
      if Model_Option == "Gemini 1.5 Pro":
        gemini = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = gemini.generate_content(Customised_Prompt, safety_settings = safety_settings, generation_config = generation_config, tools = "google_search_retrieval")
        output_text = response.text
        st.write("**Sources**")
        candidates = response.candidates
        grounding_metadata = candidates[0].grounding_metadata
        grounding_chunks = grounding_metadata.grounding_chunks
        for chunk in grounding_chunks:
          uri = chunk.web.uri
          title = chunk.web.title
          st.write(f"[{title}]({uri})")
      
      end = time.time()

    output_container = st.container(border=True)
    output_container.write(output_text)
    output_container.write("Time to generate: " + str(round(end-start,2)) + " seconds")
    bot.send_message(chat_id=recipient_user_id, text="Sherwood CV Gen" + "\n" + Model_Option + "\n" + Country_Option)
    st_copy_to_clipboard(output_text)

  except:
    st.error(" Error occurred when running model", icon="🚨")
