import os


def define_env(env):
    """
    This is the hook for the functions (new form)
    """

    @env.macro
    def youtube_hint(video_id, start=0):
        """
        Embed a video from a URL
        """
        return f"""??? youtube_vid "Externe YT-Videos"\n    <iframe loading="lazy" class="iframe_16_9" src="//youtube.com/embed/{video_id}?start={start}" allowfullscreen="allowfullscreen"
            mozallowfullscreen="mozallowfullscreen" 
            msallowfullscreen="msallowfullscreen" 
            oallowfullscreen="oallowfullscreen" 
            webkitallowfullscreen="webkitallowfullscreen"></iframe>"""

    @env.macro
    def vid(relative_path):
        """
        Embed a video from a path, lazy load
        """
        # add proccesed site paths

        vids = []
        output = """??? local_vid "Videos"\n    <div class="grid cards" markdown>\n\n"""

        if isinstance(relative_path, str):
            vids.append(relative_path)
        else:
            vids = relative_path
        for vid, name in vids:
            if "assets" in vid:
                vid_path = f"../{vid}"
            else:
                vid_path = f"../assets/{vid}"

            output += f"""    -   __{name}__\n\n        ---\n        <video controls="controls" src="{vid_path}" preload="metadata" class="local_video"></video>\n\n"""

        output += """    </div>"""

        return output

    @env.macro
    def TOC():
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
            # alpabetically sort files
            current_dict["files"] = sorted(files)

        WHITELISTED_FOLDERS = ["Latein amerikanisch", "Standard", "Weitere Tänze"]
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

        # # sort dances and files alphabetically
        folder_structure = sort_dict(folder_structure)

        # get statuses from extra.css

        status_icons = {}
        with open("docs/extra.css", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(".md-status--"):
                    # .md-status--todo2 {
                    #     --md-status: url('data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><path d="M32 0C14.3 0 0 14.3 0 32S14.3 64 32 64V75c0 42.4 16.9 83.1 46.9 113.1L146.7 256 78.9 323.9C48.9 353.9 32 394.6 32 437v11c-17.7 0-32 14.3-32 32s14.3 32 32 32H64 320h32c17.7 0 32-14.3 32-32s-14.3-32-32-32V437c0-42.4-16.9-83.1-46.9-113.1L237.3 256l67.9-67.9c30-30 46.9-70.7 46.9-113.1V64c17.7 0 32-14.3 32-32s-14.3-32-32-32H320 64 32zM288 437v11H96V437c0-25.5 10.1-49.9 28.1-67.9L192 301.3l67.9 67.9c18 18 28.1 42.4 28.1 67.9z"/></svg>');
                    # }
                    status = line[12 : line.index("{")].strip()
                    # get the svg icon from --md-status property, which isnt always on the next line
                    for line in f:
                        if line.strip().startswith(
                            "--md-status: url('data:image/svg+xml;charset=utf-8,"
                        ):
                            # class twemoji is needed for the svg to be centered, defined by mcdocs
                            status_icons[status] = (
                                """<span class= "twemoji"> """
                                + line[line.index("<svg") : line.index("</svg>") + 6]
                                + """ </span>"""
                            )
                            break

            # replace {{{TOC}}} with the table of contents
            replace = ""

            for Class in folder_structure:
                # replace += f"## [{Class}]({Class}/index.md)\n---\n"
                replace += f"""??? dance-toc "[{Class}]({Class}/index.md)"\n"""
                replace += """    <div class="grid cards" markdown>\n\n"""
                for Dance in folder_structure[Class]:
                    if Dance == "files":
                        continue
                    replace += f"""    -   __[{Dance}]({Class}/{Dance}/index.md)__\n\n        ---\n\n"""
                    # for files in folder_structure[Class][Dance]["files"]:
                    for file_index in range(
                        len(folder_structure[Class][Dance]["files"])
                    ):
                        file = folder_structure[Class][Dance]["files"][file_index]

                        # get the title of the file from the first line
                        file_title = ""
                        with open(
                            f"docs/{Class}/{Dance}/{file}", "r", encoding="utf-8"
                        ) as file_content:
                            page_status = ""

                            # file title is the first heading in the file (#)
                            for line in file_content:
                                if page_status == "" and line.startswith("status: "):
                                    page_status = line[8:]
                                if line.startswith("# "):
                                    file_title = line[2:]
                                    break

                            # replace page_status with the svg icon
                            if page_status.strip() in status_icons:
                                page_status = f"{status_icons[page_status.strip()]}"

                            file_title = file_title.strip() + " " + page_status.strip()

                        replace += (
                            f"""        [{file_title}]({Class}/{Dance}/{file})\n\n"""
                        )
                replace += """    </div>\n"""

            return replace
