# MOSIP Repositories  Sequence for Release

* All the MOSIP repositories are needed to be prepared in a sequence as we have internal dependencies between then with respect to the artiifactories.
* If the sequence is not followed therewill be compilation issues due to depenencies between repositories.
* Below mentioned sequence in which the repos needed to be prepared and released.

| SL. NO | Repo Name                   | artifacts | dockerImage |
|--------|-----------------------------|---|---|
| 1      | commons                     | Yes | Yes |
| 2      | otp-manager                 | Yes | Yes |
| 3      | bio-utils                   | Yes | No  |
| 4      | converters                  | Yes | Yes |
| 5      | mosip-openid-bridge         | Yes | Yes |
| 6      | biosdk-client               | Yes | No  |
| 7      | biosdk-services             | Yes | Yes |
| 8      | mosip-mock-services         | Yes | Yes |
| 9      | audit-manager               | Yes | Yes |
| 10     | keymanager                  | Yes | Yes |
| 11     | khazana                     | Yes | No |
| 12     | packet-manager              | Yes | Yes |
| 13     | admin-services              | Yes | Yes |
| 14     | id-repository               | Yes | Yes |
| 15     | pre-registration            | Yes | Yes |
| 16     | id-authentication           | Yes | Yes |
| 17     | registration                | Yes | Yes |
| 18     | mosip-ref-impl              | Yes | Yes |
| 19     | resident-services           | Yes | Yes |
| 20     | admin-ui                    | Yes | Yes |
| 21     | registration-client         | Yes | Yes |
| 22     | partner-management-services | Yes | Yes |
| 23     | print                       | Yes | Yes |
| 24     | websub                      | Yes | Yes |
| 25     | durian                      | Yes | Yes |
| 26     | pre-registration-ui         | Yes | Yes |
| 27     | Partner-management-portal   | Yes | Yes |
| 28     | digital-card-service        | Yes | Yes |
| 29     | artifactory-ref-impl        | Yes | Yes |
| 30     | postgres-init               | No  | Yes |
| 31     | mosip-config                | No  | No  |
| 32     | reporting                   | No  | Yes |
| 33     | mosip-functional-tests      | No  | Yes |
| 34     | mosip-automation-tests      | No  | Yes |
| 35     | mosip-data                  | No  | No  |
| 36     | mosip-onboarding            | No  | Yes |
| 37     | mosip-file-server           | No  | Yes |
| 38     | keycloak                    | No  | Yes |
| 39     | tusd-server                 | No  | Yes |
| 40     | mock-smtp-sms               | No  | Yes |
| 41     | migration-utility           | Yes | Yes |
| 42     | mosip-helm                  | No  | No  |
| 43     | mosip-infra                 | No  | No  |
| 44     | k8s-infra                   | No  | No  |
| 45     | demosdk                     | Yes | No  |
| 46     | mosip-performance-tests-mt  | No  | No  |
| 47     | abis-testing-kit            | not sure | not sure |
| 48     | release-script              | No | No   |
| 49     | documentation               | No | No |
