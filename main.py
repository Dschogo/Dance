def define_env(env):
    """
    This is the hook for the functions (new form)
    """

    @env.macro
    def youtube_hint(video_id, start=0):
        """
        Embed a video from a URL
        """
        return f"""??? youtube_vid "Video"\n    <iframe loading="lazy" class="iframe_16_9" src="//youtube.com/embed/{video_id}?start={start}"></iframe>"""
