# MOSIP Repositories  Sequence for Release

* All the MOSIP repositories are needed to be prepared in a sequence as we have internal dependencies between then with respect to the artiifactories.
* If the sequence is not followed therewill be compilation issues due to depenencies between repositories.
* Below mentioned sequence in which the repos needed to be prepared and released.

| SL. NO | Repo Name                   | artifacts | dockerImage |
|--------|-----------------------------|---|---|
| 1      | commons                     | Yes | Yes |
| 2      | mosip-openid-bridge         | Yes | Yes |
| 3      | audit-manager               | Yes | Yes |
| 4      | keymanager                  | Yes | Yes |
| 5      | khazana                     | Yes | No |
| 6      | packet-manager              | Yes | Yes |
| 7      | admin-services              | Yes | Yes |
| 8      | bio-utils                   | Yes | No |
| 9      | biosdk-client               | Yes | No |
| 10     | biosdk-services             | Yes | Yes |
| 11     | id-repository               | Yes | Yes |
| 12     | pre-registration            | Yes | Yes |
| 13     | id-authentication           | Yes | Yes |
| 14     | registration                | Yes | Yes |
| 15     | resident-services           | Yes | Yes |
| 16     | admin-ui                    | Yes | Yes |
| 17     | registration-client         | Yes | Yes |
| 18     | partner-management-services | Yes | Yes |
| 19     | print                       | Yes | Yes |
| 20     | websub                      | Yes | Yes |
| 21     | durian                      | Yes | Yes |
| 22     | pre-registration-ui         | Yes | Yes |
| 23     | Partner-management-portal   | Yes | Yes |
| 24     | mosip-ref-impl              | Yes | Yes |
| 25     | digital-card-service        | Yes | Yes |
| 26     | mosip-mock-services         | Yes | Yes |
| 27     | artifactory-ref-impl        | Yes | Yes |
| 28     | postgres-init               | Yes | No |
| 29     | mosip-config                | No | No |
| 30     | reporting                   | No | No |
| 31     | release-script              | No | No |
| 32     | mosip-functional-tests      | No | No |
| 33     | mosip-data                  | No | No |
| 34     | mosip-helm                  | No | No |
| 35     | mosip-infra                 | No | No |
| 36     | mosip-performance-tests-mt  | No | No |
| 37     | mosip-automation-tests      | No | No |
| 38     | abis-testing-kit            | not sure | not sure |
| 39     | documentation               | No | No |
