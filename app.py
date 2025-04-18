import streamlit as st
import os
import time
import telebot
import google.generativeai as gen_ai
from openai import OpenAI
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google import genai
from google.genai import types
from st_copy_to_clipboard import st_copy_to_clipboard

# Set up Telegram Bot
recipient_user_id = os.environ['RECIPIENT_USER_ID']
bot_token = os.environ['BOT_TOKEN']
bot = telebot.TeleBot(bot_token)

# Retrieve the API keys from the environment variables
gen_ai.configure(api_key=os.environ["GOOGLE_API_KEY"])
client_sonar = OpenAI(api_key=os.environ['PERPLEXITY_API_KEY'], base_url="https://api.perplexity.ai")
client_openai = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
client_thinker = genai.Client(
    api_key=os.environ["GOOGLE_API_KEY"],
    # Use `v1alpha` so you can see the `thought` flag.
    http_options={'api_version':'v1alpha'},
    )

safety_settings = {
  HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
  HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
  HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
  HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

generation_config = gen_ai.GenerationConfig(
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

def generate_factsheet_prompt(country):
  prompt = f"""### Instruction ###
You are an amazing research intern. I would like you to help me generate a factsheet of {country}. Use the format below.

### Response ###
FACTSHEET ON [NAME OF COUNTRY]
Total Area: [Total Area in square kilometres]
Population: [Population size]
Ethnic Group: [List of ethnic groups, and percentage composition]
Languages: [List of official and other languages]
Government:
Type: [Government Type]
National Capital: [Name of National Capital]
Administrative Division: [Nomenclature and Number of Administrative Divisions]
Independence: [Date of Independence]
Executive Branch:
[name of chief of state]
[name of head of governement]
[cabinet list]
[list of elections/appointments]
Legislative Branch:
[Description]
Elections: [Type of Elections]
Judicial Branch:
Highest courts: [Name of Highest Courts]
Judge Selections and Term of Office: [Description]
Main Political Parties and Leaders: [List of main political parties and leaders]
Economy:
Real GDP (PPP): [Real GDP Purchasing Power Parity in US dollars]
GDP - Real Growth Rate: [Real Growth Rate in %]
Real GDP per capita (PPP): [Real GDP per capital (Purchasing Power Parity) in US dollars]
Inflation Rate: [Inflation Rate in %]
Exports:
[List of main exports]
[List of main exports partners]
Imports:
[List of main imports]
[List of main imports partners]
External Debt: [External Debt in US dollars and as % of GDP]"""
  return prompt

def generate_response_prompt(country):
  prompt = f"""### Task ###
You are a top-tier research analyst. Your goal is to generate a list of up-to-date, high-quality headlines related to the response of {country} to the US reciprocal tariffs announced by the Trump Administration since Liberation Day.
### Format ###
For each headline:
- Begin with a **bolded summary sentence** that captures the essence of the headline.
- Follow with a brief contextual paragraph (2–3 sentences) explaining the significance or background of the story.
- End with a direct link to a reputable source or article for further reading."""
  return prompt

st.set_page_config(page_title="Sherwood Generator", page_icon=":earth_asia:")
st.write("**Sherwood Generator** :earth_asia:")
with st.expander("Click to read documentation", expanded = True):
  st.write("Experimental tool to support drafting of products. Put Large Language Models (LLMs) to work as your personal research team!")
  st.write("- Generate **CV**, **Factsheet**, **Developments** paper and custom products")
  st.write("Deploy up to three **interns** to independently generate the first cut from online sources:")
  st.write("- **Sonar** (sonar-pro by Perplexity)")
  st.write("- **Deepseek** (sonar-reasoning by Perplexity)")
  st.write("- **Gemini** (gemini-1.5-pro-002 by Google)")
  st.write("Deploy up to two **reviewers** to independently compare the answers drafted by the interns:")
  st.write("- **Oscar** (o1 by OpenAI)")
  st.write("- **Graham** (gemini-2.0-flash-thinking-exp-01-21 by Google)")
  st.write("The reviewers do not have access to internet but will compare the answers drafted by the interns to highlight where they agree, where they differ, whether there are claims that raise questions of factual accuracy, and whether there are any other relevant perspectives that are not covered in the answers.")
  
Intern_Select = st.multiselect("Which **interns** would you like to deploy?", ['Sonar', 'Deepseek', 'Gemini'], ['Sonar', 'Deepseek', 'Gemini'])
Compare_Select = st.multiselect("Which **reviewers** would you like to deploy?", ['Graham', 'Oscar'], ['Graham', 'Oscar']) 
Product_Option = st.selectbox("What **product** would like them to work on?", ('CV', 'Factsheet', 'Developments', 'Response to US Reciprocal Tariffs', 'Custom'))

if Product_Option == "CV":
  input_text = st.text_input("What is the name of the individual? Consider adding details like country and designation.")
  Customised_Prompt = generate_cv_prompt(input_text)
if Product_Option == "Factsheet":
  input_text = st.text_input("What is the name of the country on which you wish to create a factsheet?")
  Customised_Prompt = generate_factsheet_prompt(input_text)
elif Product_Option == "Developments":
  input_text = st.text_input("What is the name of the country or region?")
  Customised_Prompt = generate_developments_prompt(input_text)
elif Product_Option == "Response to US Reciprocal Tariffs":
  input_text = st.text_input("What is the name of the country?")
  Customised_Prompt = generate_response_prompt(input_text)
elif Product_Option == "Custom":
  input_text = "Custom"
  Customised_Prompt = st.text_area("Please provide the details of the product for the team.")

if st.button("Let\'s Go! :rocket:") and input_text.strip() != "" and Customised_Prompt.strip() != "" and Intern_Select != []:
  
  if input_text == "Custom":
    response = client_openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Summarise into a short phrase, not more than a few words:\n\n" + Customised_Prompt}])
    key_phrase = response.choices[0].message.content
  else:
    key_phrase = input_text
  
  st.divider()    
  
  try:
    with st.spinner("Running AI Model....."):

      combined_output = ""
      for Intern in Intern_Select:
      
        if Intern == "Sonar":
          start = time.time()
          response = client_sonar.chat.completions.create(model="sonar-pro", messages=[{ "role": "user", "content": Customised_Prompt }], temperature = 0.5)
          output_text = response.choices[0].message.content 
          end = time.time()
          with st.expander("**Sonar**, " + Product_Option + ", " + key_phrase, expanded = True):
            st.markdown(output_text.replace('\n','\n\n'))
            st.write("*Click* :clipboard: *to copy to clipboard*")
            st_copy_to_clipboard(output_text)
            combined_output = combined_output + "<answer_" + Intern + ">\n\n" + output_text + "\n\n</answer_" + Intern + ">\n\n" 
            st.write("*Time to generate:* " + str(round(end-start,2)) + " seconds")
            st.write("Sources:")
            for citation in response.citations:
              st.write(citation)

        elif Intern == "Deepseek":
          start = time.time()
          response = client_sonar.chat.completions.create(model="sonar-reasoning", messages=[{ "role": "user", "content": Customised_Prompt }], temperature = 0.5)
          output_text = response.choices[0].message.content 
          end = time.time()
          with st.expander("**Deepseek**, " + Product_Option + ", " + key_phrase, expanded = True):
            st.markdown(output_text.replace('\n','\n\n'))
            st.write("*Click* :clipboard: *to copy to clipboard*")
            st_copy_to_clipboard(output_text)
            combined_output = combined_output + "<answer_" + Intern + ">\n\n" + output_text + "\n\n</answer_" + Intern + ">\n\n" 
            st.write("*Time to generate:* " + str(round(end-start,2)) + " seconds")
            st.write("Sources:")
            for citation in response.citations:
              st.write(citation)
      
        elif Intern == "Gemini":
          start = time.time()
          gemini = gen_ai.GenerativeModel("gemini-1.5-pro-002")
          response = gemini.generate_content(Customised_Prompt, safety_settings = safety_settings, generation_config = generation_config, tools = "google_search_retrieval")
          output_text = response.text
          end = time.time()
          with st.expander("**Gemini**, " + Product_Option + ", " + key_phrase, expanded = True):
            st.markdown(output_text)
            st.write("*Click* :clipboard: *to copy to clipboard*")
            st_copy_to_clipboard(output_text)
            combined_output = combined_output + "<answer_" + Intern + ">\n\n" + output_text + "\n\n</answer_" + Intern + ">\n\n" 
            st.write("*Time to generate:* " + str(round(end-start,2)) + " seconds")
            st.write("Sources:")
            candidates = response.candidates
            grounding_metadata = candidates[0].grounding_metadata
            grounding_chunks = grounding_metadata.grounding_chunks
            for chunk in grounding_chunks:
              uri = chunk.web.uri
              title = chunk.web.title
              st.write(f"[{title}]({uri})")
          
        st.snow()
        bot.send_message(chat_id=recipient_user_id, text="Sherwood Generator" + "\n" + Intern + "\n" + Product_Option + "\n" + key_phrase)

      st.write("*Click* :clipboard: *to copy all answers to clipboard*")
      st_copy_to_clipboard(combined_output)
      st.divider()
        
      if len(Intern_Select) > 1 and len(Compare_Select) > 0:
          
        compare_prompt = "Your task is to do a point-by-point comparison of the answers below, highlighting (A) where they agree; (B) where they differ; (C) whether any claims raise questions about factual accuracy; (D) any other relevant perspectives not covered in the answers. No need to have a summary table of the similarities and differences.\n\n" 

        if Product_Option == "Response to US Reciprocal Tariffs":
          compare_prompt = (
          "# Task:\n"
          "You are my intelligent reading assistant. Your job is to analyze the provided answers and organize the items into meaningful thematic clusters. Please ignore the text in the <think> tags.\n\n"
          "# Format:\n"
          "Group items under clearly labeled **themes**. For each item:\n"
          "- Start with a **bolded topic sentence** that summarizes the item.\n"
          "- Include a detailed summary if available (2–4 sentences).\n"
          "- Add a link to the original source, where applicable.\n\n")
          
        compare_prompt = compare_prompt + "The answers are contained in the tags below.\n\n"
        tags = ""
        for Intern in Intern_Select:
          tags = tags + "<answer_" + Intern + "> (Refer to this answer as **" + Intern + "** in your output)\n\n"
        compare_prompt = compare_prompt + tags + "Here are the answers:\n\n"
        st.write(compare_prompt)
          
        if "Graham" in Compare_Select:
          start = time.time()
          response = client_thinker.models.generate_content(model="gemini-2.0-flash-thinking-exp-01-21", config={'thinking_config': {'include_thoughts': True}}, contents = compare_prompt + combined_output)
          compare_text = response.text
          end = time.time() 
          with st.expander("**Graham**, " + Product_Option + ", " + key_phrase, expanded = True):
            st.write(compare_text.replace('\n','\n\n'))
            st.write("*Click* :clipboard: *to copy to clipboard*")
            st_copy_to_clipboard(compare_text)
            st.write("*Time to generate:* " + str(round(end-start,2)) + " seconds")
          st.balloons()
          bot.send_message(chat_id=recipient_user_id, text="Sherwood Generator" + "\n" + "Graham" + "\n" + Product_Option + "\n" + key_phrase)

        if "Oscar" in Compare_Select:
          start = time.time()
          response = client_openai.chat.completions.create(model="o1", messages=[{"role": "user", "content": compare_prompt + combined_output}])
          compare_text = response.choices[0].message.content
          end = time.time() 
          with st.expander("**Oscar**, " + Product_Option + ", " + key_phrase, expanded = True):
            st.write(compare_text.replace('\n','\n\n'))
            st.write("*Click* :clipboard: *to copy to clipboard*")
            st_copy_to_clipboard(compare_text)
            st.write("*Time to generate:* " + str(round(end-start,2)) + " seconds")
          st.balloons()
          bot.send_message(chat_id=recipient_user_id, text="Sherwood Generator" + "\n" + "Oscar" + "\n" + Product_Option + "\n" + key_phrase)
    
  except:
    st.error(" Error occurred when running model", icon="🚨")
