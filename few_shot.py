import numpy as np
import pandas as pd
import json
class FewShot:
    def __init__(self,file_path="Data/processed_posts.json"):
        self.df=None
        self.unique_tags=None
        self.load_posts(file_path="Data/processed_posts.json")
    def load_posts(self,file_path):
        with open(file_path,encoding='utf-8') as f:
            posts=json.load(f)
            df=pd.json_normalize(posts)
            df['length']=df['line_count'].apply(self.categorize_length)
            self.df=df
            all_tags = self.df['tags'].apply(lambda x: x).sum()
            unique_tags = list(set(all_tags))
            self.unique_tags=unique_tags
    def get_tags(self):
        return self.unique_tags
    def get_filtered_posts(self,length,language,tag):
        df_filtered=self.df[
            (self.df['language']==language)&
            (self.df['length']==length)&
            (self.df['tags'].apply(lambda tags:tag in tags))##this gives true if jobserach in [sapna,jobsearch]
        ]
        return df_filtered.to_dict(orient="records")
    def categorize_length(self, line_count):
        if line_count < 5:
            return "Short"
        elif 5 <= line_count <= 10:
            return "Medium"
        else:
            return "Long"
if __name__=="__main__":
    fs=FewShot()
    posts=fs.get_filtered_posts("Short","Hinglish","Influencer")
    print(posts)


