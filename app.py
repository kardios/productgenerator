import streamlit as st
import os
import time
import telebot
import google.generativeai as genai
from openai import OpenAI
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from st_copy_to_clipboard import st_copy_to_clipboard

# Set up Telegram Bot
recipient_user_id = os.environ['RECIPIENT_USER_ID']
bot_token = os.environ['BOT_TOKEN']
bot = telebot.TeleBot(bot_token)

# Retrieve the API keys from the environment variables
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
client_sonar = OpenAI(api_key=os.environ['PERPLEXITY_API_KEY'], base_url="https://api.perplexity.ai")
client_openai = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

safety_settings = {
  HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
  HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
  HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
  HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

generation_config = genai.GenerationConfig(
  candidate_count = 1,
  temperature = 0.5,
)

def generate_cv_prompt(individual):
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

def generate_developments_prompt(country):
  prompt = f"""# CONTEXT #
You are an expert political and economic analyst.

# OBJECTIVE #
Write a comprehensive and detailed political report on the current political and economic situation of {country}.

# STYLE #
Use a formal writing style, adhering to the linguistic norms and conventions of British English and spelling. Back arguments up with supporting facts, statistics, and quotes; avoid overgeneralizations and sweeping statements. Where possible, structure each paragraph in the following manner: a) thesis sentence; b) sentence elaborating thesis; c) supporting details (e.g., data, research, quotes); d) more supporting details (if applicable); e) concluding sentence.

# TONE #
The tone should be neutral and professional. Avoid normative statements, and passing value judgements.

# AUDIENCE #
The report is intended for Ministers and senior officials in the Ministry of Foreign Affairs.

# RESPONSE #
The report should be structured as follows:

1. **DEVELOPMENTS IN {country}>**

2. A succinct one-paragraph summary highlighting the most salient recent political, social or economic developments in {country}.

3. **Political Developments**. Describe in detail the political standing of the government of the day. Mention any cabinet reshuffles, coups, infighting or intrigue in the last 6 months that may affect the government's stability or priorities. Describe the government's policy priorities.

4. Two to Five subsections highlighting other key recent trends and developments in {country} over the past year that have not already been covered under **Political Developments**. Each sub-section should be parked under a header that describes the topic discussed. There is no need to have a dedicated subsection on human rights issues/abuses.

5. **Economic Developments**. Describe in detail the latest GDP growth figure of {country}, and compare it to the previous year. Cite reputable sources such as the World Bank, UN, IMF. Note key macroeconomic trends and projections. Note the main economic opportunities and challenges facing {country}.

6. **International Relations**. Describe in detail the foreign policy orientation of {country}. Summarise the foreign relations of {country} with key international partners, with particular attention to ASEAN, its neighbouring countries, and Singapore."""
  return prompt 

st.set_page_config(page_title="Sherwood Generator", page_icon=":face_with_cowboy_hat:")
st.write("**Sherwood Generator** :face_with_cowboy_hat:")
with st.expander("Click to read documentation", expanded = True):
  st.write("Productivity tool for generating **CV** and **Developments** papers")
  st.write("Choose from the following Large Language Models:")
  st.write("- **sonar-pro** by Perplexity")
  st.write("- **sonar-reasoning** using DeepSeek R1")
  st.write("- **gemini-1.5-pro-002** by Google")
  st.write("Comparison of generated CVs using **o1** model by OpenAI")

Model_Select = st.multiselect("What Large Language Model do I use?", ['sonar-pro', 'sonar-reasoning', 'gemini-1.5-pro-002'], ['sonar-pro', 'sonar-reasoning', 'gemini-1.5-pro-002'])
Product_Option = st.selectbox("What product do you want to generate?", ('CV', 'Developments'))

if Product_Option == "CV":
  input = st.text_input("What is the name of the individual?")
  Customised_Prompt = generate_cv_prompt(input)
elif Product_Option == "Developments":
  input = st.text_input("What is the name of the country or region?")
  Customised_Prompt = generate_developments_prompt(input)

if st.button("Let\'s Go! :rocket:") and input.strip() != "" and Model_Select != []:
  try:
    with st.spinner("Running AI Model....."):

      combined_output = ""
      for Model_Option in Model_Select:
      
        if Model_Option == "sonar-reasoning" or Model_Option == "sonar-pro":
          start = time.time()
          response = client_sonar.chat.completions.create(model=Model_Option, messages=[{ "role": "user", "content": Customised_Prompt }], temperature = 0.5)
          output_text = response.choices[0].message.content 
          end = time.time()

          with st.expander(input + " " + Product_Option + " " + Model_Option, expanded = True):
            st.markdown(output_text.replace('\n','\n\n'))
            st_copy_to_clipboard(output_text)
            combined_output = combined_output + "<answer_" + Model_Option + ">\n\n" + output_text + "\n\n</answer_" + Model_Option + ">\n\n" 
            st.write("Time to generate: " + str(round(end-start,2)) + " seconds")
            st.write("Sources:")
            for citation in response.citations:
              st.write(citation)
      
        elif Model_Option == "gemini-1.5-pro-002":
          start = time.time()
          gemini = genai.GenerativeModel(Model_Option)
          response = gemini.generate_content(Customised_Prompt, safety_settings = safety_settings, generation_config = generation_config, tools = "google_search_retrieval")
          output_text = response.text
          end = time.time()
        
          with st.expander(input + " " + Product_Option + " " + Model_Option, expanded = True):
            st.markdown(output_text)
            combined_output = combined_output + "<answer_" + Model_Option + ">\n\n" + output_text + "\n\n</answer_" + Model_Option + ">\n\n" 
            st_copy_to_clipboard(output_text)
            st.write("Time to generate: " + str(round(end-start,2)) + " seconds")
            st.write("Sources:")
            candidates = response.candidates
            grounding_metadata = candidates[0].grounding_metadata
            grounding_chunks = grounding_metadata.grounding_chunks
            for chunk in grounding_chunks:
              uri = chunk.web.uri
              title = chunk.web.title
              st.write(f"[{title}]({uri})")
          
        st.snow()
        bot.send_message(chat_id=recipient_user_id, text="Sherwood Generator" + "\n" + Model_Option + "\n" + Product_Option + "\n" + input)

      st_copy_to_clipboard(combined_output)
      if Product_Option == "CV" and len(Model_Select) > 1:
        start = time.time()
        response = client_openai.chat.completions.create(model="o1", messages=[{"role": "user", "content": "Compare the answers: \n\n" + combined_output}])
        compare_text = response.choices[0].message.content
        end = time.time() 
        with st.expander("Comparison with o1", expanded = True):
          st.write(compare_text.replace('\n','\n\n')
          st.write("Time to generate: " + str(round(end-start,2)) + " seconds")
          st_copy_to_clipboard(compare_text)
        st.balloons()
                     
  except:
    st.error(" Error occurred when running model", icon="🚨")
