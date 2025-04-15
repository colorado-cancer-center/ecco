#!/usr/bin/env bash

# takes congress members HTML from stdin, and writes to stdout a CSV of Colorado
# congress members. each row includes the district number, member name,
# affiliation, and website

# use hq to extract the table then use jq (in several steps; optimize later?) to
# extract the data, annotate with some computed fields, and format it as CSV
hq 'array {
    //tbody//tr ->
    hash {
        member: $_/td[1]//span[1] | text,
        member_url: $_/td[1]//a/@href,
        affiliation: $_/td[2] | text,
        state: $_/td[3] | text,
        district: $_/td[4] | text
    }
}' \
    | jq '[ .[] | select(.state == "Colorado (CO)") | . + {district: .district | scan("[0-9]+") | tonumber} ] | sort_by(.district)' \
    | jq -r '(
        ["DistrictNum", "Member", "Affiliation", "Website"],
        (
            .[] | [
                .district,
                .member,
                .affiliation,
                "https://clerk.house.gov\( .member_url )"
            ]
        )
    ) | @csv'
