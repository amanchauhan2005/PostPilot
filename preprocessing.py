import json
from llm_helper import llm
import re
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
def extract_json_from_text(text):
    """Extract JSON from text that might contain preamble or postamble."""
    # Find JSON-like content between curly braces
    json_match = re.search(r'(\{.*\})', text, re.DOTALL)
    if json_match:
        try:
            json_str = json_match.group(1)
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    return None
def get_unified_tags(post_meta_data):
    unique_tags=set()
    for posts in post_meta_data:
        unique_tags.update(posts['tags'])
    unique_tags_list=','.join(unique_tags)
    safe_tags_list = str(unique_tags_list).encode('ascii', 'ignore').decode('ascii')
    template =  '''I will give you a list of tags. You need to unify tags with the following requirements,
    1. Tags are unified and merged to create a shorter list. 
       Example 1: "Jobseekers", "Job Hunting" can be all merged into a single tag "Job Search". 
       Example 2: "Motivation", "Inspiration", "Drive" can be mapped to "Motivation"
       Example 3: "Personal Growth", "Personal Development", "Self Improvement" can be mapped to "Self Improvement"
       Example 4: "Scam Alert", "Job Scam" etc. can be mapped to "Scams"
    2. Each tag should be follow title case convention. example: "Motivation", "Job Search"
    3. Output should be a JSON object, No preamble
    3. Output should have mapping of original tag and the unified tag. 
       For example: {{"Jobseekers": "Job Search",  "Job Hunting": "Job Search", "Motivation": "Motivation}}
    
    Here is the list of tags: 
    {tags}
    '''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"tags": str(safe_tags_list)})
    extracted_json = extract_json_from_text(response.content)
    if extracted_json:
        return extracted_json

    # If we couldn't extract JSON, print the response for debugging and raise an error
    print(f"Failed to extract JSON. Response content: {response.content[:500]}...")
    raise OutputParserException(f"Failed to extract JSON from LLM response")
def extract_metadata(post):
    template = '''
        You are given a LinkedIn post. You need to extract number of lines, language of the post and tags.
        Give only a valid json without any text .Do not add text key and engagement key in json object .Must have only three keys.
        1. Return a valid JSON. No preamble. 
        2. JSON object only have exactly three keys: line_count, language and tags. 
        3.Do not add text and engagement key in json object.
        2.JSON object must  have exactly three keys: line_count, language and tags. 
        3. tags is an array of text tags. Extract maximum two tags.
        4. Language should be English or Hinglish (Hinglish means hindi + english)
        Here is the actual post on which you need to perform this task:  
        {post}
        '''
    pt=PromptTemplate.from_template(template)
    chain=pt|llm
    safe_post = str(post).encode('ascii', 'ignore').decode('ascii')
    response=chain.invoke(input={'post':safe_post})
    extracted_json = extract_json_from_text(response.content)
    if extracted_json:
        return extracted_json

    # If we couldn't extract JSON, print the response for debugging and raise an error
    print(f"Failed to extract JSON. Response content: {response.content[:500]}...")
    raise OutputParserException(f"Failed to extract JSON from LLM response")
def process_post(raw_file_path,processed_file_path):
    with open(raw_file_path,encoding='utf-8') as file:
        posts=json.load(file)
        enriched_posts=[]
        for post in posts:
             meta_data=extract_metadata(post['text'])
             post_meta_data=meta_data | post
             enriched_posts.append(post_meta_data)
    unified_tags=get_unified_tags(enriched_posts)
    for post in enriched_posts:
        current_tags=post['tags']
        new_tags={unified_tags[tag] for tag in current_tags}
        post['tags']=list(new_tags)
    with open(processed_file_path,encoding='utf-8',mode="w")as outfile:
        json.dump(enriched_posts,outfile,indent=4)

if __name__=="__main__":
    process_post('Data/raw_posts.json','Data/processed_posts.json')