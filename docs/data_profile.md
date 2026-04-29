# Data Profile

Dataset: `/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/MDM- Match and Merge data`

## Summary

- Party count: 100
- Current exact duplicate groups by address variants: 41
- Approximate duplicate-group rate: 41.0%

## Table row counts

- {'party': 100, 'individual': 352, 'electronic_address': 247, 'party_address': 100, 'party_postal_address': 350}

## Schema

- {'party': ['PARTY_ID', 'RECORD_NO', 'MDM_KEY', 'SOURCE_SYSTEM_CODE', 'SOURCE_KEY', 'PARTY_NAME', 'IMAGE_URL', 'DOMAIN_CODE', 'CUSTOMER_CODE', 'IS_REL_ORG_FLG', 'DS_REVIEW_FLG', 'PARTY_STATUS_CODE', 'PARTY_DQ_STATUS_CODE', 'CREATED_DT', 'CREATED_BY', 'LAST_UPDATED_DT', 'LAST_UPDATED_BY', 'DELETED_DT', 'DELETED_BY', 'ACTIVE_FLG', 'ISGR', 'REVIEW_MERGE', 'SINCE_DT', 'LEFT_DT'], 'individual': ['PARTY_ID', 'PREFIX_NAME', 'FIRST_NAME', 'MIDDLE_NAME', 'LAST_NAME', 'SUFFIX_NAME', 'FULL_NAME', 'BIRTH_DT', 'BIRTH_PLACE', 'TITLE', 'DRAFT_IND', 'MARTIAL_STATUS_TYPE', 'CREATED_DT', 'CREATED_BY', 'LAST_UPDATED_BY', 'LAST_UPDATED_DT', 'DELETED_DT', 'DELETED_BY', 'ACCOUNT_ID', 'ACCOUNT_NAME', 'GENDER_CODE', 'ACCOUNT_SYSTEM'], 'electronic_address': ['ELECTRONIC_ADDR_ID', 'ELECTRONIC_ADDR_TYPE_CODE', 'ELECTRONIC_ADDR_TEXT', 'CREATED_DT', 'CREATED_BY', 'LAST_UPDATED_DT', 'LAST_UPDATED_BY', 'DELETED_DT', 'DELETED_BY', 'ACTIVE_FLG', 'PARTY_ID'], 'party_address': ['PARTY_ADDRESS_ID', 'PARTY_ID', 'ADDRESS_USAGE_TYPE_CODE', 'PARTY_ADDR_START_DT', 'PARTY_ADDR_END_DT', 'IS_PRIMARY', 'CREATED_DT', 'CREATED_BY', 'LAST_UPDATED_DT', 'LAST_UPDATED_BY', 'DELETED_DT', 'DELETED_BY', 'PARTY_POSTAL_ADDR_ID'], 'party_postal_address': ['PARTY_POSTAL_ADDR_ID', 'REGISTERED_ADDR_IND', 'RESIDENTIAL_ADDR_IND', 'ADDR_LINE_ONE', 'ADDR_LINE_TWO', 'ADDR_LINE_THREE', 'ADDR_LINE_FOUR', 'ADDR_LINE_FIVE', 'STATE_CODE', 'COUNTRY_CODE', 'CITY', 'POSTAL_CODE', 'POSTAL_CODE_EXTN', 'POSTAL_BARCODE', 'COORDINATE_SYSTEM', 'LOC_COORDINATE_DESC', 'LATITUDE', 'LONGITUDE', 'IS_STARDARDIZED', 'STANDARDIZED_DT', 'CREATED_DT', 'CREATED_BY', 'LAST_UPDATED_DT', 'LAST_UPDATED_BY', 'DELETED_DT', 'DELETED_BY', 'STATE_VALUE', 'COUNTRY_NAME']}

## Variant distribution by party

- Name variants per party: {3: 48, 4: 52}
- Phone variants per party: {3: 47, 2: 53}
- Address variants per party: {3: 50, 4: 50}

## Known quality issues

- 100 party groups contain multiple individual-name variants.
- 100 party groups contain multiple phone variants.
- 100 party groups contain multiple address variants.
- 41 party groups already contain exact duplicate address variants.
