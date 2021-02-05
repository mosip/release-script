import os

branch_name = os.getenv("rs_branch_name")
release_name = os.getenv("rs_release_name")
maven_skip_tests = True if os.getenv("rs_maven_skip_tests") == 'y' else False
release_artifactory_url = os.getenv("rs_release_artifactory_url")


release_repo_identifier = 'https://oss.sonatype.org/service/local/staging/deploy/maven2'
push_trigger_path = '.github/workflows/push_trigger.yml'

# JSON print related
json_sort_keys = True
json_indent = 4

# MOSIP dependency keywords
mosip_dep_match_regex = [
    r'.*mosip.*'
]

# MOSIP property keywords
mosip_property_match_regex = [
    r'kernel.*',
    r'.*mosip.*'
]