# MOSIP Repositories  Sequence for Release

* All the MOSIP repositories are needed to be prepared in a sequence as we have internal dependencies between then with respect to the artiifactories.
* If the sequence is not followed therewill be compilation issues due to depenencies between repositories.
* Below mentioned sequence in which the repos needed to be prepared and released.

|SL. NO | Repo Name | artifacts | dockerImage |
|---|---|---|---|
| 1 | commons | Yes | Yes |
| 2 | mosip-openid-bridge | Yes | Yes |
| 3 | audit-manager | Yes | Yes |
| 4 | keymanager | Yes | Yes |
| 5 | khazana | Yes | Yes |
| 6 | packet-manager | Yes | Yes |
| 7 | admin-services | Yes | Yes |
| 8 | id-repository | Yes | Yes |
| 9 | pre-registration | Yes | Yes |
| 10 | id-authentication | Yes | Yes |
| 11 | registration | Yes | Yes |
| 12 | resident-services | Yes | Yes |
| 13 | admin-ui | Yes | Yes |
| 14 | registration-client | Yes | Yes |
| 15 | partner-management-services | Yes | Yes |
| 16 | print | Yes | Yes |
| 17 | websub | Yes | Yes |
| 18 | durian | Yes | Yes |
| 29 | pre-registration-ui | Yes | Yes |
| 20 | Partner-management-portal | Yes | Yes |
| 21 | bio-utils | Yes | Yes |
| 22 | mosip-ref-impl | Yes | Yes |
| 23 | mosip-mock-services | Yes | Yes |
| 24 | artifactory-ref-impl | Yes | Yes |
| 25 | mosip-config | No | No |
| 26 | reporting | No | No |
| 27 | release-script | No | No |
| 28 | mosip-functional-tests | No | No |
| 29 | mosip-data | No | No |
| 30 | mosip-helm | No | No |
| 31 | mosip-infra | No | No |
| 32 | mosip-performance-tests-mt | No | No |
| 33 | mosip-automation-tests | No | No |
| 34 | abis-testing-kit | not sure | not sure |
| 35 | documentation | No | No |
