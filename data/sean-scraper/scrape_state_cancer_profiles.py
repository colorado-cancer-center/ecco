#!/usr/bin/env python

"""
This script scrapes the state cancer profiles website
and saves the results as csv files.

Author: Sean Davis
Gist URL: https://gist.github.com/seandavi/3d3136aaf66b0b58e2f1906085415312

The website is a bit of a mess, so this script is a bit of a mess.
It requires scraping the select options from the website
and then iterating over all the possible combinations of
select options to get the data.

The script is designed to be run from the command line
with the following command:

```
python scrape_statecancerprofiles.py
```

The script will create two csv files, one for incidence
and one for death. Each of these files is about 700k lines.


The script will also print out the url for each request
it makes. Note that the script will make a lot of requests
and take a long time to run (about 30 minutes or so, depending 
on bandwidth). We use a messy try-except block a lot
because the website is not very robust and some of the
options are not valid for some of the other options.

"""

import httpx
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

import contextlib
import sys


# --------------------------------------------------------
# ---- tqdm helpers
# --------------------------------------------------------

# allows for capturing stdout so it doesn't interrupt tqdm's rendering

class DummyFile(object):
  file = None
  def __init__(self, file):
    self.file = file

  def write(self, x):
    # Avoid print() second call (useless \n)
    if len(x.rstrip()) > 0:
        tqdm.write(x, file=self.file)

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = DummyFile(sys.stdout)
    yield
    sys.stdout = save_stdout


# --------------------------------------------------------
# ---- scraping
# --------------------------------------------------------

def get_select_options():
    soup = BeautifulSoup(
        httpx.get(
            "https://statecancerprofiles.cancer.gov/incidencerates/index.php"
        ).text,
        "html.parser",
    )
    select_dict = {}
    for s in soup.find_all("select"):
        option_dict = {}
        field = s.attrs.get("id")  # age, stage, ....
        for o in s.find_all("option"):
            txt = o.get_text()
            val = o.attrs.get("value")
            if not txt.startswith("---"):
                option_dict[o.attrs.get("value")] = o.get_text()
        if field == "age":
            # website is missing some age groups
            # since the developers tried to be clever
            # with javascript, apparently.

            # This is a hack to add the missing age groups
            # to the select options for pediatrics.
            option_dict["016"] = "Age < 15"
            option_dict["015"] = "Age < 20"
        select_dict[s.attrs.get("id")] = option_dict
    return select_dict


def column_text_replace(txt: str):
    return (
        txt.strip()
        .replace("[", "")
        .replace("]", "")
        .replace("(", "")
        .replace(")", "")
        .replace("*", "_")
        .replace(" ", "_")
        .replace("%", "pct")
        .replace("-", "_")
        .replace(",", "_")
        .replace(".", "_")
        .replace("?", "")
        .lower()
    )


def get_table(
    year: str = "0",
    stateFIPS: str = "00",  # 00 includes all states
    sex: str = "0",
    stage: str = "999",
    race: str = "00",
    cancer: str = "001",
    areatype: str = "county",
    age: str = "001",
    _type: str = "incd",
):
    if _type == "incd":
        rate_col = "age_adjusted_incidence_raterate_note___cases_per_100_000"
        url_insert = "incidencerates"
    else:
        rate_col = "age_adjusted_death_raterate_note___deaths_per_100_000"
        url_insert = "deathrates"

    url = (
        f"https://statecancerprofiles.cancer.gov/{url_insert}/index.php?stateFIPS={stateFIPS}"
        f"&areatype={areatype}&cancer={cancer}&race={race}"
        f"&stage={stage}&year={year}"
        f"&sex={sex}&age={age}&type={_type}&output=1"
    )
    print(url)
    import pandas as pd

    df = pd.read_csv(
        url,
        skiprows=8,
        low_memory=False,
        na_values=["*", "N/A", " N/A", "N/A ", " N/A "],
        skipinitialspace=True,
        dtype={"FIPS": str},
    )
    df.columns = [column_text_replace(c) for c in df.columns]
    select_opts = get_select_options()

    def get_text_from_select_id(group, id):
        return select_opts[group][id]

    df["year"] = get_text_from_select_id("year", year)
    df["sex"] = get_text_from_select_id("sex", sex)
    df["stage"] = get_text_from_select_id("stage", stage)
    df["race"] = get_text_from_select_id("race", race)
    df["cancer"] = get_text_from_select_id("cancer", cancer)
    df["areatype"] = get_text_from_select_id("areatype", areatype)
    df["age"] = get_text_from_select_id("age", age)
    df["state_fips"] = df["fips"].str[:2]
    df["measurement"] = _type
    df["locale_type"] = "other"
    df.loc[df["fips"].isna(), "fips"] = ""
    df.loc[df["fips"].str.endswith("000"), "locale_type"] = "state"
    df.loc[df["fips"].str.startswith("00"), "locale_type"] = "national"
    df.loc[df["county"].str.contains("County"), "locale_type"] = "county"
    df["_extracted_at"] = pd.Timestamp.now().isoformat()
    df["url"] = url.replace("&output=1", "")
    for numeric_column in [
        rate_col,
        "lower_95pct_confidence_interval",
        "upper_95pct_confidence_interval",
        "lower_ci_ci_rank",
        "upper_ci_ci_rank",
        "average_annual_count",
        "recent_5_year_trend_trend_note_in_incidence_rates",
        "lower_95pct_confidence_interval_1",
        "upper_95pct_confidence_interval_1",
    ]:
        try:
            df[numeric_column] = pd.to_numeric(df[numeric_column], errors="coerce")
        except:
            pass
    return df[df[rate_col].notna()]


# This function uses argparse to collect the command line arguments
# and then calls get_table() with those arguments.
# use last five years of data (year=0), all states (stateFIPS=00)
def master_table(year: str = "0", stateFIPS="00", _type="incd"):
    select_options = get_select_options()
    print(select_options)
    dflist = []
    
    cancers = list(select_options["cancer"].keys())[6:]

    for cancer in tqdm(cancers, file=sys.stdout):
        with nostdout():
            print(cancer)

            # The state cancer profiles folks in their
            # infinite wisdom decided to make the age
            # groups for cancer 515 and 516 (pediatrics) different
            # than the other cancers. So we have to
            # handle them separately.
            if cancer == "516":
                ages = ["016"]
            elif cancer == "515":
                ages = ["015"]
            else:
                ages = select_options["age"].keys()

            for age in ages:
                for sex in select_options["sex"].keys():
                    for race in select_options["race"].keys():
                        for stage in select_options["stage"].keys():
                            try:
                                df = get_table(
                                    stateFIPS=stateFIPS,
                                    cancer=cancer,
                                    age=age,
                                    sex=sex,
                                    race=race,
                                    stage=stage,
                                    _type=_type,
                                )
                                dflist.append(df)
                            except KeyboardInterrupt:
                                raise
                            except Exception as e:
                                print(e)
                                pass

    df = pd.concat(dflist)

    return df


# --------------------------------------------------------
# ---- entrypoint
# --------------------------------------------------------

def main():
    # narrow state to Colorado
    stateFIPS = "8"

    df = master_table(_type="incd", stateFIPS=stateFIPS)
    df.to_csv("state_cancer_profiles_incidence_state{stateFIPS}.csv.gz", index=False, compression="gzip")
    df = master_table(_type="death", stateFIPS=stateFIPS)
    df.to_csv("state_cancer_profiles_death_state{stateFIPS}.csv.gz", index=False, compression="gzip")


if __name__ == "__main__":
    print(main())
