import os

branch_name = os.getenv("rs_branch_name")
release_name = os.getenv("rs_release_name")

# JSON print related
json_sort_keys = True
json_indent = 4

# MOSIP dependency keywords
mosip_dep_match_regex = [
    r'kernel',
    r'mosip'
]
