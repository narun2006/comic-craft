"""Optional narrative refinement hook.

The Hugging Face version keeps the main generation to one text-model request
so the free allowance is not unnecessarily consumed.
"""


def refine_comic_narrative(comic):
    return comic
