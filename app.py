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

st.set_page_config(page_title="Sherwood Intern", page_icon=":face_with_cowboy_hat:",)

with st.expander("Click to read documentation"):
  st.write("Sherwood Intern)

prompt = """
# CONTEXT # You are an expert political and economic analyst.

# OBJECTIVE # Write a comprehensive and detailed political report on the current political and economic situation of <INPUT_COUNTRY>.

# STYLE # Use a formal writing style, adhering to the linguistic norms and conventions of British English and spelling. Back arguments up with supporting facts, statistics, and quotes; avoid overgeneralizations and sweeping statements. Where possible, structure each paragraph in the following manner: 
(a) thesis sentence; 
(b) sentence elaborating thesis; 
(c) supporting details (e.g., data, research, quotes); 
(d) more supporting details (if applicable); 
(e) concluding sentence.

# TONE # The tone should be neutral and professional. Avoid normative statements, and passing value judgements. 

# AUDIENCE # The report is intended for Ministers and senior officials in the Ministry of Foreign Affairs. 

# RESPONSE # The report should be structured as follows: 

1. **DEVELOPMENTS IN <INPUT_COUNTRY>** 

2. A succinct one-paragraph summary highlighting the most salient recent political, social or economic developments in the country. 

3. **Political Developments**. Describe in detail the political standing of the government of the day. Mention any cabinet reshuffles, coups, infighting or intrigue in the last 6 months that may affect the government's stability or priorities. Describe the government's policy priorities. 

4. Two to Five subsections highlighting other key recent trends and developments in the country over the past year that have not already been covered under **Political Developments**. Each sub-section should be parked under a header that describes the topic discussed. There is no need to have a dedicated subsection on human rights issues/abuses. 

5. **Economic Developments**. Describe in detail the country's latest GDP growth figure, and compare it to the previous year. Cite reputable sources such as the World Bank, UN, IMF. Note key macroeconomic trends and projections. Note the country's main economic opportunities and challenges. 

6. **International Relations**. Describe in detail the country's foreign policy orientation. Summarise the country's foreign relations with key international partners, with particular attention to ASEAN, its neighbouring countries, and Singapore.
"""

Model_Option = st.selectbox("What Large Language Model do I use?", ('Gemini 1.5 Pro', 'Llama 3.1 Sonar'))

Country_Option = st.text_input("What is the name of the country?", "Lao People\'s Democratic Republic")

Customised_Prompt = st.text_area("You may wish to modify the prompt below.", prompt) + "\n# INPUT COUNTRY\n<INPUT_COUNTRY>\n" + Country_Option + "\n</INPUT_COUNTRY>\n"

if st.button("Let\'s Go! :rocket:"):
  try:
    with st.spinner("Running AI Model....."):
    
      start = time.time()
      
      if Model_Option == "Gemini 1.5 Pro (G)":
        gemini = genai.GenerativeModel("gemini-1.5-pro-002")
        response = gemini.generate_content(prompt, safety_settings = safety_settings, generation_config = generation_config, tools = "google_search_retrieval")
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
    bot.send_message(chat_id=recipient_user_id, text="Sherwood Lab" + "\n" + Option_Input + "\n" + Model_Option + "\n" + Prompt_Option)
    st_copy_to_clipboard(output_text)

  except:
    st.error(" Error occurred when running model", icon="🚨")
