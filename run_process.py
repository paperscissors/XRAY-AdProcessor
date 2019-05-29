from AdProcessor import AdProcessor


def run_process(episode_id, preroll_id, postroll_id):
    # we need to query the database for matching ids to get the URIs for these assets
    process = AdProcessor("beervana.mp3", "one.mp3", "two.mp3") # postroll is totally optional
