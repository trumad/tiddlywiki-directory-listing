import os
import json
from datetime import datetime

def should_ignore_file(file_or_folder_path):
    list_of_files_to_ignore = ["folder.jpg",".apple.timemachine.",".ds_store", ".documentrevisions-v100", ".spotlight-v100", ".temporaryitems", ".trashes", ".fseventsd", ".localized", ".icloud", "._", "desktop.ini", "thumbs.db", "$recycle.bin", ".trash-", ".@__thumb", ".appledb", "@eaDir", ".stignore", ".stfolder", ".dropbox", ".bzvol", ".thumbnails","found.0","system volume information",".tmp"]
    for item in list_of_files_to_ignore:
        if item in file_or_folder_path.lower():
            return True
    return False

def calculate_file_size(file):
    file_size = os.path.getsize(file)
    file_size_mb = file_size / (1024 * 1024)
    file_size_mb = int(file_size_mb)
    file_size_mb = str(file_size_mb)
    return file_size_mb

def get_created_time(path):
    return datetime.fromtimestamp(os.path.getctime(path)).strftime("%Y%m%d%H%M%S%f")

def get_modified_time(path):
    return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y%m%d%H%M%S%f")

def create_parent_folder_breadcrumbs(file_or_folder_path):
    parent_folder = os.path.dirname(file_or_folder_path)
    parent_folder_parts = parent_folder.split("/")
    parent_folder_parts.pop(0)
    parent_folder_hyperlinks = []
    current_path = ""
    for p in parent_folder_parts:
        current_path = os.path.join(current_path, p)
        parent_folder_hyperlinks.append("[[" + p + "|" + current_path + "]]")
    
    parent_folder_hyperlinks = " / ".join(parent_folder_hyperlinks)
    return parent_folder_hyperlinks

def create_subfolder_and_file_list(file_or_folder_path):
    files_and_folders = os.listdir(file_or_folder_path)
    subfolder_titles = []
    file_titles = []
    for f in files_and_folders:
        full_path = os.path.join(file_or_folder_path, f)
        if os.path.isdir(full_path):
            subfolder_titles.append(f)
        else:
            file_titles.append(f)
    
    subfolder_titles.sort()
    file_titles.sort()
    
    subfolder_tiddlers = []
    subfolder_list = []
    for subfolder in subfolder_titles:
        if should_ignore_file(subfolder):
            continue
        subfolder_tiddler = create_tiddler(os.path.join(file_or_folder_path, subfolder))
        subfolder_list.append("📂 [[{}|{}]]".format(subfolder,subfolder_tiddler["title"]))
        subfolder_tiddlers.append(subfolder_tiddler)
    
    file_list = []
    for file_title in file_titles:
        if should_ignore_file(file_title):
            continue
        file_list.append("[[{}|{}]]".format(file_title,os.path.join(file_or_folder_path[1:], file_title)))
    
    subfolder_and_file_list = "* " + "\n* ".join(subfolder_list + file_list)
    return subfolder_and_file_list

def create_tiddler(file_or_folder_path):
    tiddler = {}
    tiddler["title"] = file_or_folder_path[1:]
    tiddler["created"] = get_created_time(file_or_folder_path)
    tiddler["modified"] = get_modified_time(file_or_folder_path)
    
    if os.path.isfile(file_or_folder_path):
        tiddler["tags"] = "file"
        parent_folder_hyperlinks = create_parent_folder_breadcrumbs(file_or_folder_path)
        tiddler["text"] = "/ {}".format(parent_folder_hyperlinks)
        tiddler["fileSize"] = calculate_file_size(file_or_folder_path)
    else:
        tiddler["tags"] = "folder"
        subfolder_and_file_list = create_subfolder_and_file_list(file_or_folder_path)
        parent_folder_hyperlinks = create_parent_folder_breadcrumbs(file_or_folder_path)
        tiddler["text"] = "/ {}\n\n{}".format(parent_folder_hyperlinks, subfolder_and_file_list)
    return tiddler

root = "." # You can specify an exact folder. don't include a trailing slash

tiddlers = []
tiddlers.append(create_tiddler(root))
for dirpath, dirnames, filenames in os.walk(root):
    for filename in filenames + dirnames:
        path = os.path.join(dirpath, filename)
        if should_ignore_file(path):
            continue
        print (path)
        tiddlers.append(create_tiddler(path))

with open("twDirectoryListing.json", "w") as f:
    json.dump(tiddlers, f)
