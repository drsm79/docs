# Docs
Docs is a couchapp used to view markdown documents. Documents with a "content" field are emitted in a view and that field is rendered in the page using pagedown.

## Install
Run:

    python situp.py -d docs -e docs -s http://localhost:5984
    
in the top directory (assuming you want to push to your local CouchDB on http://localhost:5984)