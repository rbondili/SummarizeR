# SummarizeR

Summarizes Articles, Saves Browsing Time.

# Installation

Install the extension with pip:

Step 1 :- Run code "pip install -r requirements.txt"

Step 2:- Run code "python -m spacy download en_core_web_md"
  
# Running the App

Run "Stream run app.py" 

If encounter this error "module 'google.protobuf.descriptor' has no attribute '_internal_create_key'" on your ubuntu machine 
Stakcoverflow :- https://stackoverflow.com/questions/61922334/how-to-solve-attributeerror-module-google-protobuf-descriptor-has-no-attribu
The below three commands solved it for me:
pip uninstall protobuf python3-protobuf
pip install --upgrade pip
pip install --upgrade protobuf
Hope this helps
