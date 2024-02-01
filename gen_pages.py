import mkdocs_gen_files
import os


folder_structure = {}

root_directory = "./docs"
for root, dirs, files in os.walk(root_directory):
    relative_path = os.path.relpath(root, root_directory)

    # Split relative path into components
    components = relative_path.split(os.sep)

    # Initialize current dictionary to root of folder structure
    current_dict = folder_structure

    # Traverse the components to find the correct place in the dictionary
    for component in components:
        if component not in current_dict:
            current_dict[component] = {}
        current_dict = current_dict[component]

    # Add files to the dictionary
    current_dict["files"] = files


WHITELISTED_FOLDERS = ["Latein-amerikanisch", "Standard", "Weitere Tänze"]
# remove all folders that are not in the whitelist
for x in list(folder_structure):
    if x not in WHITELISTED_FOLDERS:
        del folder_structure[x]

# remove all files that are not markdown files
for Class in folder_structure:
    for Dance in folder_structure[Class]:
        if Dance == "files":
            continue
        for file in folder_structure[Class][Dance]["files"]:
            if not file.endswith(".md"):
                folder_structure[Class][Dance]["files"].remove(file)
            if file == "index.md":
                folder_structure[Class][Dance]["files"].remove(file)


def sort_dict(d):
    if isinstance(d, dict):
        return {k: sort_dict(v) for k, v in sorted(d.items())}
    elif isinstance(d, list):
        return [sort_dict(item) for item in d]
    else:
        return d


# sort dances and files alphabetically
folder_structure = sort_dict(folder_structure)


OriginalFile = open("docs/index.md", "r", encoding="utf-8")
OriginalContent = OriginalFile.read()

with mkdocs_gen_files.open("index.md", "w") as f:
    # replace {{{TOC}}} with the table of contents
    replace = ""
    for Class in folder_structure:
        replace += f"* [{Class}]({Class}/index.md)\n"
        replace += "    \n"
        for Dance in folder_structure[Class]:
            if Dance == "files":
                continue
            replace += f"    * [{Dance}]({Class}/{Dance}/index.md)\n\n"
            # for files in folder_structure[Class][Dance]["files"]:
            for file_index in range(len(folder_structure[Class][Dance]["files"])):
                file = folder_structure[Class][Dance]["files"][file_index]

                # get the title of the file from the first line
                file_title = ""
                with open(
                    f"docs/{Class}/{Dance}/{file}", "r", encoding="utf-8"
                ) as file_content:
                    file_title = (
                        file_content.readline().replace("# ", "").replace("\n", "")
                    )

                replace += f"""        {"- " if file_index == 0  else ""} [{file_title}]({Class}/{Dance}/{file}){"" if file_index == len(folder_structure[Class][Dance]["files"]) - 1  else ", "} """
            replace += "    \n\n"
        replace += "    \n\n"

    print(OriginalContent.replace("{{{TOC}}}", replace), file=f)
